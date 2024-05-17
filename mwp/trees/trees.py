import nltk
from nltk import CFG
from nltk.parse.generate import generate
from nltk.tree import Tree
import random
from tqdm.auto import tqdm

from .utils import add_mem, MemDict, hash_tree


op_map = {
    '*': (lambda x, y: x * y),
    '+': (lambda x, y: x + y),
    '-': (lambda x, y: x - y),
    '/': (lambda x, y: x / y),
}


def get_max_depth(tree):
    if isinstance(tree, Tree):
        return 1 + max(get_max_depth(child) for child in tree)
    else:
        return 0

def grammar_to_trees(grammar, max_depth, min_depth=0) -> tuple:
    grammar = CFG.fromstring(grammar)
    parser = nltk.ChartParser(grammar)

    results = []

    for expr in generate(grammar, depth=max_depth):
        tree = parser.parse(expr)
        results.append((expr, list(tree)))

        tree_depth = get_max_depth(tree)

        if tree_depth < min_depth:
            continue

    exprs, trees = zip(*results)

    return exprs, trees

class ValuesSampler():
    def __init__(self, val_range: tuple[int, int]):
        self.val_range = val_range

        self.mem = MemDict()
        self.mem_backtrack = MemDict()
    
    def node_constraints(self, n):
        '''
        Check that n is in the specified range, and that it is an integer.
        '''
        in_range = self.val_range[0] <= n < self.val_range[1]
        is_integer = True if isinstance(n, int) else (n.is_integer() if isinstance(n, float) else False)
        return in_range and is_integer

    @add_mem
    def populate(self, tree, depth=0):
        if tree.label() == 'S':
            return self.populate(tree[0], depth + 1)

        if tree.label() == 'N':
            return set(
                n for n in range(self.val_range[0], self.val_range[1])
                if self.node_constraints(n)
            )

        if tree.label() == 'E': # skip to get to the actual expression
            return self.populate(tree[1], depth + 1)

        assert len(tree) == 3 # two args and one operator
        op = op_map[tree[1]]
        left_possible = self.populate(tree[0], depth + 1)
        right_possible = self.populate(tree[2], depth + 1)

        tree_hash = hash_tree(tree)
        tree_calcs = self.mem_backtrack[tree_hash] = {}

        possible = set()
        for l in left_possible:
            for r in right_possible:
                calc = op(l, r)
                if self.node_constraints(calc):
                    possible.add(int(calc))

                    if calc not in tree_calcs:
                        tree_calcs[calc] = []

                    self.mem_backtrack[tree_hash][calc].append((l, r))

        assert len(possible) < (self.val_range[1] - self.val_range[0])

        assert len(possible) > 0

        return possible
    
    def pick_values(self, tree, target_val=None, depth=0):
        if target_val is None:
            valid_vals = list(self.mem[hash_tree(tree)])
            assert len(valid_vals) > 0
            target_val = random.choice(valid_vals)

        if tree.label() == 'S':
            return self.pick_values(tree[0], target_val=target_val, depth=depth + 1)

        if tree.label() == 'N':
            return ['NUM', target_val], str(target_val), target_val

        if tree.label() == 'E': # skip to get to the actual expression
            return self.pick_values(tree[1], target_val=target_val, depth=depth + 1)

        assert len(tree) == 3 # two args and one operator
        op = op_map[tree[1]]
        left_tree, right_tree = tree[0], tree[2]
        tree_hash = hash_tree(tree)
        tree_calcs = self.mem_backtrack[tree_hash]

        valid_vals = tree_calcs[target_val]
        assert len(valid_vals) > 0
        chosen_path = random.choice(valid_vals)

        left_val, left_str, left_target = self.pick_values(
            left_tree,
            target_val=chosen_path[0],
            depth=depth + 1
        )

        right_val, right_str, right_target = self.pick_values(
            right_tree,
            target_val=chosen_path[1],
            depth=depth + 1
        )
        
        assert int(op(left_target, right_target)) == target_val

        return [tree[1], [left_val, right_val]], f"({left_str} {tree[1]} {right_str})", target_val
    
    def pick_values_dset(self, trees, n_samples=25, pbar=True):
        iterator_mem = tqdm(trees, desc='Populating mem values') if pbar else trees
        # populat mem
        for tree_lst in iterator_mem:
            assert len(tree_lst) == 1
            tree = tree_lst[0]

            self.populate(tree)

        # sample values from mem
        iterator_sample = tqdm(trees, desc='Sampling values') if pbar else trees

        results_vals = []
        for tree_lst in iterator_sample:
            assert len(tree_lst) == 1
            tree = tree_lst[0]

            tree_samples = []

            for _ in range(n_samples):
                tree_vals, tree_str, target_val = self.pick_values(tree)

                tree_samples.append((tree_vals, tree_str, target_val))
            
            results_vals.append(
                tuple(zip(*tree_samples))
            )

        return results_vals
