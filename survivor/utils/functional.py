def identity(x):
    return x


def all_true(*funcs):
    def composite(elem):
        apply = lambda func: func(elem)
        return all(map(apply, funcs))

    return composite
