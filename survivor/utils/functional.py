from functools import reduce
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def identity(x: Any):
    return x


def always(result: T) -> Callable[[], T]:
    return lambda: result


def complement(f: Callable[[T], bool]) -> Callable[[T], bool]:
    return lambda x: not f(x)


def all_true(*funcs):
    def composite(elem):
        apply = lambda func: func(elem)
        return all(map(apply, funcs))

    return composite


def compose(*funcs):
    def compose_next(composed_func, next_func):
        lambda x: composed_func(next_func(x))

    return reduce(compose_next, funcs)
