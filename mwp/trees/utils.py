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
