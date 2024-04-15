import nltk
from nltk import CFG
from nltk.parse.generate import generate
import random
from tqdm.auto import tqdm

from .utils import add_mem, MemDict, hash_tree


op_map = {
    '*': (lambda x, y: x * y),
    '+': (lambda x, y: x + y),
    '-': (lambda x, y: x - y),
    '/': (lambda x, y: x / y),
}

def grammar_to_trees(grammar, depth) -> tuple:
    grammar = CFG.fromstring(grammar)
    parser = nltk.ChartParser(grammar)

    results = []

    for expr in generate(grammar, depth=depth):
        tree = parser.parse(expr)
        results.append((expr, list(tree)))

    exprs, trees = zip(*results)

    return exprs, trees

class ValuesSampler():
    def __init__(self, val_range: tuple[int, int]):
        self.val_range = val_range

        self.mem = MemDict()
        self.mem_backtrack = MemDict()
    
    def node_constraints(self, n):
        return self.val_range[0] <= n < self.val_range[1]

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
                    possible.add(calc)

                    if calc not in tree_calcs:
                        tree_calcs[calc] = []

                    self.mem_backtrack[tree_hash][calc].append((l, r))

        return possible
    
    def pick_values(self, tree, target_val=None, depth=0):
        if target_val is None:
            target_val = random.choice(list(self.mem[hash_tree(tree)]))

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
        chosen_path = random.choice(tree_calcs[target_val])

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
        
        assert op(left_target, right_target) == target_val

        return [tree[1], [left_val, right_val]], f"({left_str} {tree[1]} {right_str})", target_val
    
    def pick_values_dset(self, trees, n_samples=25, pbar=True):
        # populat mem
        for tree_lst in trees:
            assert len(tree_lst) == 1
            tree = tree_lst[0]

            self.populate(tree)
        
        iterator = tqdm(trees, desc='Sampling values:') if pbar else trees

        # sample values from mem
        results_vals = []
        for tree_lst in iterator:
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
