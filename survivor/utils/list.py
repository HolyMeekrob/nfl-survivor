from functools import reduce
from itertools import chain
from .functional import identity


def flatten(lists):
    return list(chain.from_iterable(lists))


def split_by(lst, predicate):
    """Split a list by a given predicate

    The predicate is applied to every element in the list. If the result
    of the application is true, the element is placed in the first list.
    Otherwise, it is placed in the second list. The result is a tuple
    of the two lists.

    Args:
        lst: the list to split
        predicate: a function that takes an element of the list and
            return a boolean value
    """
    results = ([], [])

    for elem in lst:
        if predicate(elem):
            results[0].append(elem)
        else:
            results[1].append(elem)

    return results


def difference(xs, ys):
    return list(set(xs).difference(set(ys)))


def any(lst, predicate=identity):
    return any([predicate(elem) for elem in lst])


def all(lst, predicate=identity):
    return all([predicate(elem) for elem in lst])


def map_list(lst, fun):
    return list(map(lst, fun))


def filter_list(lst, predicate):
    return list(filter(lst, predicate))


def first(lst, predicate, default=None):
    return next((elem for elem in lst if predicate(elem)), default)


def groupby(lst, key):
    def add_to_dict(groups: dict, elem):
        elem_key = key(elem)

        if not elem_key in groups:
            groups[elem_key] = []

        groups[elem_key].append(elem)
        return groups

    return reduce(add_to_dict, lst, {})
