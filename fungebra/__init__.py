from collections.abc import Mapping
from functools import partial, reduce, update_wrapper
import operator
from typing import Callable, Iterable, Union


__version__ = "0.0.0"


def compose(*functions: Callable) -> Callable:
    """Composes arbitrary number of functions."""

    def _compose_pair(outer: Callable, inner: Callable) -> Callable:
        return lambda *args, **kwargs: outer(inner(*args, **kwargs))

    return reduce(_compose_pair, functions, lambda _: _)


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

    def __repr__(self):
        return f"Function({repr(self.func)})"

    def partial(self, *args, **kwargs):
        return F(partial(self.func, *args, **kwargs))

    def rpartial(self, *args, **kwargs):
        return F(lambda *a, **kw: self.func(*a, *args, **kw, **kwargs))

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
        if isinstance(other, Args):
            return self(*other.args, **other.kwargs)
        return self(other)

    def __lshift__(self, input_args):
        return self._as_args(self.partial, input_args)

    def __rshift__(self, input_args):
        return self._as_args(self.rpartial, input_args)

    def __pos__(self):
        return self.map

    def __truediv__(self, other):
        return self.reduce(other)

    def __rtruediv__(self, other):
        return F(other).reduce(self)

    def __mod__(self, other):
        return self.filter(other)

    def __rmod__(self, other):
        return F(other).filter(self)

    @staticmethod
    def _as_args(function, input_args):
        if isinstance(input_args, Args):
            return function(*input_args.args, **input_args.kwargs)
        if isinstance(input_args, Mapping):
            return function(**input_args)
        return function(*input_args)


class Args:
    """Dataclass representing arguments passed to a function."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


# Allow options for importing.
F = Func = Function  # pylint: disable=invalid-name


identity: Callable = F(lambda _: _)

# Allow options for importing.
I = identity  # pylint: disable=invalid-name


def pipeline(*funcs):
    """Construct a pipeline from passed functions."""
    return reduce(operator.or_, map(F, funcs), I)
