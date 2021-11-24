from functools import reduce
from itertools import chain
from typing import Callable, TypeVar

from .functional import identity

T = TypeVar("T")
U = TypeVar("U")


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


def count(lst, predicate=identity):
    return len([elem for elem in lst if predicate(elem)])


def append(lst, elem):
    return lst + [elem]


def map_list(fun: Callable[[T], U], lst: list[T]):
    return list(map(fun, lst))


def filter_list(predicate: Callable[[T], bool], lst: list[T]):
    return list(filter(predicate, lst))


def first(lst: list[T], predicate: Callable[[T], bool], default: T | None = None):
    return next((elem for elem in lst if predicate(elem)), default)


def last(lst: list[T], predicate: Callable[[T], bool], default: T | None = None):
    return first(reversed(lst), predicate, default)


def groupby(lst: list[T], key: Callable[[T], U]) -> dict[U, list[T]]:
    def add_to_dict(groups: dict, elem):
        elem_key = key(elem)

        if not elem_key in groups:
            groups[elem_key] = []

        groups[elem_key].append(elem)
        return groups

    return reduce(add_to_dict, lst, {})


def indexes(lst: list[T], value: T, index_from: int = 0) -> list[int]:
    return [i + index_from for (i, elem) in enumerate(lst) if elem == value]
