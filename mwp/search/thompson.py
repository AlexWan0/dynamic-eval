import pandas as pd
import numpy as np
from typing import Callable
from numpy.typing import ArrayLike


from .problems import ProblemSpace


class Optimizer():
    def ranked_arms(self, maxmize: bool = True) -> tuple[list[int], dict[int, float]]:
        theta_estimates = {}
        for i in range(self.num_arms):
            if self.pulls[i] == 0:
                continue

            theta_estimates[i] = self.successes[i] / self.pulls[i]

        return sorted(theta_estimates, key=lambda x: theta_estimates[x], reverse=maxmize), theta_estimates

    def optimize(self, budget: int, samples_per_pull: int, maximize: bool = True, verbose: bool = False) -> tuple[list[int], dict[int, float]]:
        raise NotImplementedError

    def save(self, path: str):
        np.savez(path, successes=self.successes, pulls=self.pulls)

    def load(self, path: str):
        data = np.load(path)
        self.successes = data['successes']
        self.pulls = data['pulls']
    
    def get_logs(self) -> list:
        return self.pull_logs
    
    def theta_extrema(self, theta: ArrayLike, k: int) -> str:
        result  = []
        
        argsort_vals = np.argsort(theta)

        # top k
        result.append('-- largest')
        for i in range(k):
            result.append(f'{argsort_vals[-i - 1]} => {theta[argsort_vals[-i - 1]]} ({self.successes[argsort_vals[-i - 1]]}/{self.pulls[argsort_vals[-i - 1]]})')
        
        # bottom k
        result.append('-- smallest')
        for i in range(k):
            result.append(f'{argsort_vals[i]} => {theta[argsort_vals[i]]} ({self.successes[argsort_vals[i]]}/{self.pulls[argsort_vals[i]]})')
        
        result.append('----')
        
        return '\n'.join(result)


# Based on https://arxiv.org/abs/2310.11324
class ThompsonOpt(Optimizer):
    def __init__(
            self,
            problems: ProblemSpace,
            reward_func: Callable[[pd.DataFrame], tuple[int, list]],
            beta_prior: tuple[float, float] = (1, 1)
        ):

        self.problems = problems
        self.reward_func = reward_func
        self.beta_prior = beta_prior

        self.num_arms = self.problems.num_arms()

        self.successes = np.zeros(self.num_arms)
        self.pulls = np.zeros(self.num_arms)

        self.pull_logs = [[] for _ in range(self.num_arms)]

    def sample_beta(self, success, total):
        return np.random.beta(self.beta_prior[0] + success, self.beta_prior[1] + total - success)
    
    def sample_beta_all(self):
        return np.array([self.sample_beta(self.successes[i], self.pulls[i]) for i in range(self.num_arms)])

    def optimize(self, budget: int, samples_per_pull: int, maximize: bool = True, verbose: bool = False) -> tuple[list[int], dict[int, float]]:
        assert budget % samples_per_pull == 0, 'budget must be divisible by samples_per_pull'

        num_pulls = budget // samples_per_pull

        for i in range(num_pulls):
            theta = self.sample_beta_all()

            if maximize:
                arm_idx = np.argmax(theta)
            else:
                arm_idx = np.argmin(theta)
            
            if verbose:
                print(f'{i}/{num_pulls}: theta vals\n{self.theta_extrema(theta, 5)}')
                print(f'{i}/{num_pulls}: pulling arm {arm_idx} with theta {theta[arm_idx]}')

            samples = self.problems.sample_arm(arm_idx, samples_per_pull)

            if verbose:
                print(f'{i}/{num_pulls}: calling reward function')
            
            reward, log_data = self.reward_func(samples)

            self.pull_logs[arm_idx].extend(log_data)

            if verbose:
                print(f'{i}/{num_pulls}: reward: {reward}')

            self.successes[arm_idx] += reward
            self.pulls[arm_idx] += samples_per_pull

            if verbose:
                print(f'{i}: arm {arm_idx} has {self.successes[arm_idx]} successes and {self.pulls[arm_idx]} pulls\n\n')
        
        return self.ranked_arms(maximize)


class UniformOpt(Optimizer):
    def __init__(
            self,
            problems: ProblemSpace,
            reward_func: Callable[[pd.DataFrame], tuple[int, list]]
        ):
        self.problems = problems
        self.reward_func = reward_func

        self.num_arms = self.problems.num_arms()

        self.successes = np.zeros(self.num_arms)
        self.pulls = np.zeros(self.num_arms)

        self.pull_logs = [[] for _ in range(self.num_arms)]
    
    def optimize(self, budget: int, samples_per_pull: int, maximize: bool = True, verbose: bool = False):
        assert budget % samples_per_pull == 0, 'budget must be divisible by samples_per_pull'

        num_pulls = budget // samples_per_pull

        for i in range(num_pulls):
            arm_idx = np.random.randint(self.num_arms)
            
            if verbose:
                print(f'{i}/{num_pulls}: pulling arm {arm_idx}')

            samples = self.problems.sample_arm(arm_idx, samples_per_pull)

            if verbose:
                print(f'{i}/{num_pulls}: calling reward function')
            
            reward, log_data = self.reward_func(samples)

            self.pull_logs[arm_idx].extend(log_data)

            if verbose:
                print(f'{i}/{num_pulls}: reward: {reward}')

            self.successes[arm_idx] += reward
            self.pulls[arm_idx] += samples_per_pull

            if verbose:
                print(f'{i}/{num_pulls}: arm {arm_idx} has {self.successes[arm_idx]} successes and {self.pulls[arm_idx]} pulls\n\n')
        
        return self.ranked_arms(maximize)
