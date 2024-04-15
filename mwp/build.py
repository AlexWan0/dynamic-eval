# import numexpr
from mwp.problems.base import Constant, Operation
# from mwp.trees_old.parsers import PARSERS
from mwp.problems.problems import PROBLEMS
from mwp.trees import grammar_to_trees, ValuesSampler

import pandas as pd
from tqdm.auto import tqdm
tqdm.pandas()


class ProblemBuilder:
    def __init__(
            self,
            problem_name: str,
            # parser_name: str
        ):
        self.op_map, self.problem = PROBLEMS[problem_name]()
        # self.parser = PARSERS[parser_name]()
        self.grammar = self.problem['grammar']
        self.sampler = ValuesSampler(self.problem['val_range'])

    def get_trees(self, max_depth) -> tuple:
        return grammar_to_trees(self.grammar, max_depth)

    def get_tree_values(self, trees, n_samples) -> list[tuple]:
        return self.sampler.pick_values_dset(trees, n_samples)

    def _build_from_tree(self, parse_tree, used_vals):
        if not isinstance(parse_tree[1], list):
            const_type = parse_tree[0]
            assert const_type == 'NUM', const_type
            node = Constant(parse_tree[1])
            return node, [node]
        
        op = parse_tree[0]
        args = [self._build_from_tree(arg, used_vals) for arg in parse_tree[1]]
        
        if op not in self.op_map:
            raise ValueError(f'Unknown operation: {op}')
        
        node = self.op_map[op](*[arg[0] for arg in args], used_vals=used_vals)
        node.update_used_vals(used_vals)
        
        node_list = [arg for arg_list in args for arg in arg_list[1]] + [node]

        return node, node_list
    
    def build_from_tree(self, parse_tree):
        return self._build_from_tree(parse_tree, {})

    def get_problem_text(self, root, node_list):
        problem_text = ' '.join([
            node.get_utt() for node in node_list
            if isinstance(node, Operation)
        ])
        target_value = root.get_value()
        target_question = self.problem['question'].format(query=target_value)

        return problem_text, target_question

    def build_dataset(self, max_depth, n_samples) -> pd.DataFrame:
        exprs, trees = self.get_trees(max_depth)
        print('num trees:', len(trees))

        # num_trees sized list[tuple(tree_vals, tree_strs, target_vals)]
        tree_samples = self.get_tree_values(trees, n_samples)

        assert len(exprs) == len(trees) == len(tree_samples)

        rows = []
        for expr, tree, samples in zip(exprs, trees, tree_samples):
            tree_vals, tree_strs, target_vals = samples
            
            for tree_val, tree_str, target_val in zip(tree_vals, tree_strs, target_vals):
                rows.append({
                    'expression': expr,
                    'tree': tree,
                    'tree_vals': tree_val,
                    'tree_str': tree_str,
                    'target_val': target_val
                })
        
        print('num samples:', len(rows))

        df = pd.DataFrame(rows)

        def _add_problem_text(row):
            root, node_list = self.build_from_tree(row['tree_vals'])
            problem, question = self.get_problem_text(root, node_list)
            row['problem'] = problem
            row['question'] = question
            return row
        
        df = df.progress_apply(_add_problem_text, axis=1)

        print('dataframe:', df.columns)

        return df

    # def problem_from_exp(self, expression):
    #     solution = numexpr.evaluate(expression)

    #     parsed = self.parser.parse(expression)
    #     root, node_list = self.build_from_tree(parsed, {})

    #     problem_text = ' '.join([
    #         node.get_utt() for node in node_list
    #         if isinstance(node, Operation)
    #     ])
    #     target_value = root.get_value()
    #     target_question = self.problem['question'].format(query=target_value)

    #     return problem_text, target_question, solution

if __name__ == '__main__':
    problem = ProblemBuilder('jobs')
    df = problem.build_dataset(10, 5)
    print(df.head())