from collections.abc import Mapping
from functools import partial, reduce, update_wrapper
import operator
from typing import Callable, Union


def compose(*functions: Callable) -> Callable:
    """Composes arbitrary number of functions."""

    def _compose_pair(outer: Callable, inner: Callable) -> Callable:
        return lambda *args, **kwargs: outer(inner(*args, **kwargs))

    return reduce(_compose_pair, functions, lambda _: _)


class Function:
    """Function wrapper with composition methods."""

    def __init__(self, func: Union[Callable, "Function"]):
        self._func: Callable = func.func if isinstance(func, Function) else func
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

    def __pos__(self):
        return self

    def compose(self, *others):
        return Function(compose(self, *others))

    def __add__(self, func):
        return self.compose(func)

    def __radd__(self, func):
        return Function(func).compose(self)

    def pipe(self, func):
        return Function(func).compose(self)

    def __or__(self, other):
        return self.pipe(other)

    def __ror__(self, other):
        if callable(other):
            return Function(other).pipe(self)
        if isinstance(other, Args):
            return self(*other.args, **other.kwargs)
        return self(other)

    def __pow__(self, other):
        return self.pipe(other)

    def __rpow__(self, other):
        return Function(other).pipe(self)

    def partial(self, *args, **kwargs):
        return Function(partial(self.func, *args, **kwargs))

    def rpartial(self, *args, **kwargs):
        return Function(lambda *a, **kw: self.func(*a, *args, **kw, **kwargs))

    def __lshift__(self, input_args):
        return Function._as_args(self.partial, input_args)

    def __rshift__(self, input_args):
        return Function._as_args(self.rpartial, input_args)

    @property
    def map(self):
        return Function(map).partial(self)

    @property
    def lmap(self):
        return self.map.pipe(list)

    def __neg__(self):
        return self.map

    def __sub__(self, other):
        return self.pipe(Function(other).map)

    def __rsub__(self, other):
        return Function(other).pipe(self.map)

    def filter(self, filter_func: Callable = None):
        if filter_func:
            return self | Function(filter).partial(filter_func)
        return Function(partial(filter, self))

    def __lt__(self, other):
        return self.filter(other)

    def __le__(self, other):
        return self.map.filter(other)

    def reduce(self, reduce_func: Callable = None):
        if reduce_func:
            return self | Function(reduce).partial(reduce_func)
        return Function(partial(reduce, self))

    def __gt__(self, other):
        return self.reduce(other)

    def __ge__(self, other):
        return self.map.reduce(other)

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


identity: Callable = Function(lambda _: _)


@Function
def pipeline(*funcs):
    """Construct a pipeline from passed functions."""
    return reduce(operator.add, map(Function, reversed(funcs)), identity)
