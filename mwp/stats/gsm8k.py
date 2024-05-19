from datasets import load_dataset
import re
import pandas as pd


class Node:
    def __init__(self, value, ops, children):
        self.value = value
        self.ops = ops
        self.children = [child if isinstance(child, Node) else Constant(child) for child in children]

    def __str__(self, depth=1, sp='\t'):
        children_str = '[' + ', '.join([c.__str__(depth=depth+1) for c in self.children]) + ']'
        return f'Node(\n{sp*depth}v={self.value},op={self.ops},\n{sp*depth}c={children_str}\n{sp*(depth-1)})'
    
    def __repr__(self):
        return str(self)
    
    def child_values(self):
        return [child.value for child in self.children]

    def get_size(self):
        size = 1

        for child in self.children:
            if isinstance(child, Node) and not isinstance(child, Constant):
                size += child.get_size()

        return size

    def is_binary(self):
        if len(self.children) != 2:
            return False
        
        for child in self.children:
            if not isinstance(child, Constant):
                if not child.is_binary():
                    return False
        
        return True
    
    def get_binary_tree_as_list(self):
        assert len(self.ops) == 1

        return [
            self.ops[0],
            self.children[0].get_binary_tree_as_list(),
            self.children[1].get_binary_tree_as_list()
        ]        

    def binarize(self):
        if len(self.children) <= 2:
            return
        
        assert len(self.ops) == len(self.children) - 1

        left = self.children[0]
        left.binarize()

        # TODO: this breaks order of operations/distributing operations
        # we'll just set ops to None for now
        right_ops = [None] * len(self.ops[1:])
        right = Node(None, right_ops, self.children[1:])
        right.binarize()

        self.ops = self.ops[:1]
        self.children = [left, right]

class Constant(Node):
    def __init__(self, value):
        self.value = value
        
        super().__init__(value, [], [])

    def __str__(self, depth=0):
        return f'C({self.value})'
    
    def __repr__(self):
        return str(self)
    
    def get_binary_tree_as_list(self):
        return ['NUM', self.value]

def extract_brackets(text, format=r'<<(.+)>>'):
    matches = re.findall(format, text)
    return matches

def parse_ops(text, format=r'\(?([-+]?[\d\.]+)\)?(([\+\-\/\*]\(?([-+]?[\d\.]+)\)*)+)=([-+]?[\d\.]+)'):
    text = text.strip()
    match = re.match(format, text)

    if not match:
        return None

    args = [match.group(1)]
    ops = []

    args_rest = match.group(2)
    args_rest_matches = re.findall(r'([\+\-\/\*])([+-]?[\d\.]+)', args_rest)
    for m in args_rest_matches:
        ops.append(m[0])
        args.append(m[1])

    rhs = match.group(5)

    return {
        'args': [float(x) for x in args],
        'ops': ops,
        'rhs': float(rhs)
    }

def is_connected(node_list):
    if len(node_list) == 0:
        return False, None

    largest_tree = max(node_list, key=lambda x: x.get_size())
    return len(node_list) == largest_tree.get_size(), largest_tree

def make_tree(parsed_vals):
    nodes = []
    for vals in parsed_vals:
        if vals is None:
            return None

        nodes.append(Node(vals['rhs'], vals['ops'], vals['args']))

    for i, n in enumerate(nodes):
        for j in nodes[i+1:]:
            if n.value in j.child_values():
                j.children[j.child_values().index(n.value)] = n

    connected, tree = is_connected(nodes)

    if not connected:
        return None
    
    return tree

def load_and_parse(split='train'):
    data = load_dataset("gsm8k", ignore_verifications=True)

    df = pd.DataFrame(data[split])

    df['operations'] = df['answer'].apply(extract_brackets)

    df['parsed_ops'] = df['operations'].apply(lambda x: [parse_ops(op) for op in x])

    df['tree'] = df['parsed_ops'].apply(make_tree)
    
    df_binary = df[df['tree'].apply(lambda x: x is not None and x.is_binary())].copy()
    df_binary['tree_vals'] = df_binary['tree'].apply(lambda x: x.get_binary_tree_as_list())

    return df_binary
