from itertools import chain


def flatten(lists):
    return list(chain.from_iterable(lists))
