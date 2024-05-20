import random


class MemDict(dict):
    def reset(self):
        self.clear()

def hash_tree(tree):
    return tuple(tree.leaves())

def add_mem(f):
    def wrapper(self, tree, depth=0):
        assert hasattr(self, 'mem')

        hash_val = hash_tree(tree)

        if hash_val in self.mem:
            return self.mem[hash_val]

        result = f(self, tree, depth=depth)
        self.mem[hash_val] = result
        return result

    return wrapper

def random_sample(n: int, *args: list) -> tuple[list]:
    size = len(args[0])
    assert all(len(arg) == size for arg in args)

    indices = random.sample(range(size), n)
    return tuple([arg[i] for i in indices] for arg in args)
