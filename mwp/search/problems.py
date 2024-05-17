import pandas as pd


class ProblemSpace():
    def __init__(self, problems: pd.DataFrame, replace: bool = False):
        self.problems = problems
        self.replace = replace

        if not self.replace:
            self.picked_map = {}

        self.problems['expression_str'] = self.problems['expression'].apply(lambda x: str(x))
        
        self.arms = self.problems['expression_str'].unique()

        print(f'num arms: {len(self.arms)}')

        self.problem_map = {}
        for tree_s in self.arms:
            problem_rows = self.problems[self.problems['expression_str'] == tree_s]

            self.problem_map[tree_s] = problem_rows

    def can_sample(self, arm_idx: int, n: int) -> bool:
        arm = self.arms[arm_idx]
        
        if self.replace:
            return len(self.problem_map[arm]) >= n
        else:
            if arm not in self.picked_map:
                self.picked_map[arm] = []

            return len(self.problem_map[arm]) - len(self.picked_map[arm]) >= n

    def sample_arm(self, arm_idx: int, n: int) -> pd.DataFrame:
        arm = self.arms[arm_idx]
        
        if self.replace:
            return self.problem_map[arm].sample(n, replace=True)
        else:
            if arm not in self.picked_map:
                self.picked_map[arm] = []

            sampled = self.problem_map[arm].drop(self.picked_map[arm]).sample(n, replace=False)

            self.picked_map[arm] += list(sampled.index)

            return sampled
    
    def num_arms(self) -> int:
        return len(self.arms)
