from functools import partial, reduce, update_wrapper
import operator
from typing import Callable, Iterable, Union


__version__ = "0.0.0"


identity: Callable = lambda _: _


def compose(*functions: Callable) -> Callable:
    """Composes passed functions."""
    def _compose_pair(outer: Callable, inner: Callable) -> Callable:
        return lambda *args, **kwargs: outer(inner(*args, **kwargs))
    return reduce(_compose_pair, functions, identity)


class Function:
    """Function wrapper with composition methods."""

    def __init__(self, func: Union[Callable, "Function"]):
        self._func: Callable = func.func if isinstance(func, F) else func
        update_wrapper(self, func)

    @property
    def func(self):
        return self._func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __hash__(self):
        return hash(self.func)

    def partial(self, *args, **kwargs):
        return F(partial(self, *args, **kwargs))

    @property
    def map(self):
        return F(map).partial(self)

    def filter(self, filter_func: Callable = None):
        if filter_func:
            return self | F(filter).partial(filter_func)
        return F(partial(filter, self))

    def reduce(self, reduce_func: Callable = None):
        if reduce_func:
            return self | F(reduce).partial(reduce_func)
        return F(partial(reduce, self))

    def compose(self, *others):
        return F(compose(*others, self))

    def pipe(self, func):
        return self | func

    def __add__(self, func):
        return F(func).compose(self)

    def __radd__(self, func):
        return self | func

    def __or__(self, func):
        return self.compose(func)

    def __ror__(self, other):
        if callable(other):
            return self + other
        if isinstance(other, expand):
            return self(*other.wrapped)
        return self(other)

    def __eq__(self, other):
        return self.func == F(other).func


class expand:
    def __init__(self, args: Iterable):
        self.wrapped = args

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.wrapped, attr)


# Allow options for importing.
F = Func = Function  # pylint: disable=invalid-name


def pipeline(*funcs):
    return reduce(operator.or_, map(F, funcs), F(identity))


if __name__ == "__main__":
    def add(*args):
        return sum(args)

    def double(number):
        return number * 2

    assert F(add).partial(1).partial(2, 3).partial(4)() == 10
    assert F(add).partial(1).partial(2, 3)(4) == 10

    assert F(add).compose(double)(1, 2, 3, 4) == 20
    add_then_double: Callable = F(double) + add
    assert add_then_double(1, 2, 3, 4) == 20
    double_then_sum: Callable = F(double).map.partial([1, 2, 3, 4]).compose(sum)() == 20

    assert F(add).reduce()([1, 2, 3, 4]) == 10
    assert F(double).map.partial([1, 2, 3, 4]).compose(F(add).reduce())() == 20
    assert F(double).map.reduce(operator.add)([1, 2, 3, 4]) == 20

    test_pipeline: Callable = pipeline(F(double).map, F(add).reduce())
    assert test_pipeline([1, 2, 3, 4]) == 20

    assert (F(double) + sum)([1, 2, 3, 4]) == 20
    assert (double + F(sum))([1, 2, 3, 4]) == 20
    assert (F(sum) | double)([1, 2, 3, 4]) == 20
    assert (sum | F(double))([1, 2, 3, 4]) == 20

    get_double_sum_string: Callable = F(identity) | F(double).map | sum | str
    assert get_double_sum_string([1, 2, 3, 4]) == "20"

    def even(number):
        return not number % 2

    assert (F(even).filter() | sum)([1, 2, 3, 4]) == 6

    @F
    def negative(number):
        return -number

    assert negative.map.reduce(operator.add)([1, 2, 3, 4]) == -10
    assert negative.map.filter(even).reduce(operator.add)([1, 2, 3, 4]) == -6

    assert (negative.map | F(operator.add).reduce())([1, 2, 3, 4]) == -10
    assert [1, 2, 3, 4] | (negative.map | list) == [-1, -2, -3, -4]

    try:
        [1, 2, 3, 4] | F(add)
    except TypeError:
        pass
    else:
        assert False
    assert expand([1, 2, 3, 4]) | F(add) == 10
