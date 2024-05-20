import pandas as pd
import os
import argparse
import pickle

from mwp.search import ProblemSpace, ThompsonOpt, make_model_reward
from mwp.model import ClaudeModel
from mwp.build import ProblemBuilder


args = argparse.ArgumentParser()

args.add_argument('output_path', type=str)

# specify trees
args.add_argument('--problem', type=str, default='jobs')
args.add_argument('--max_depth', type=int, default=12)
args.add_argument('--min_depth', type=int, default=0)
args.add_argument('--subsample_trees', type=int, default=None)

# specify samples from trees
args.add_argument('--n_samples', type=int, default=100)
args.add_argument('--problem_save', type=str, default='data/samples_10.pkl')

# define optimization parameters
args.add_argument('--budget', type=int, default=100)
args.add_argument('--samples_per_pull', type=int, default=10)

args = args.parse_args()

# read problems
if os.path.exists(args.problem_save):
    print('loading problems')
    df = pd.read_pickle(args.problem_save)
    print(f'found {len(df)} problems')
else:
    print('generating problems')
    problem = ProblemBuilder("jobs")
    df = problem.build_dataset(
        args.max_depth,
        args.n_samples,
        min_depth=args.min_depth,
        subsample=args.subsample_trees
    )
    
    print(f'sampled {len(df)} problems')

    df.to_pickle(args.problem_save)

# init model
model = ClaudeModel(model_name='claude-instant-v1.2')
reward_func = make_model_reward(model, max_tokens=1024, verbose=False)

# search for best and worst problems
def find_extrema(maximize: bool, save_file: str = None) -> tuple[list[int], dict[int, float]]:
    ps = ProblemSpace(df, replace=True)
    opt = ThompsonOpt(ps, reward_func, beta_prior=(1, 1))
    ranked_arms, arm_vals = opt.optimize(
        budget=args.budget,
        samples_per_pull=args.samples_per_pull,
        maximize=maximize,
        verbose=True
    )

    if save_file:
        opt.save(save_file)

    return ranked_arms, arm_vals, opt.get_logs()

print('finding minima')
worst_arms, est_success_w, logs_w = find_extrema(maximize=False, save_file='minima')

print('finding maxima')
best_arms, est_success_b, logs_b = find_extrema(maximize=True, save_file='maxima')

print('saving results')
with open(args.output_path, 'wb') as f:
    pickle.dump({
        'worst_arms': worst_arms,
        'est_success_w': est_success_w,
        'best_arms': best_arms,
        'est_success_b': est_success_b,
        'logs_w': logs_w,
        'logs_b': logs_b,
        'args': args
    }, f)
