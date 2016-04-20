from collections import defaultdict

class Struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def tree():
    return defaultdict(tree)
