from functools import reduce


def identity(x):
    return x


def all_true(*funcs):
    def composite(elem):
        apply = lambda func: func(elem)
        return all(map(apply, funcs))

    return composite


def compose(*funcs):
    def compose_next(composed_func, next_func):
        lambda x: composed_func(next_func(x))

    return reduce(compose_next, funcs)
