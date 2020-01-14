from itertools import takewhile
import operator
from typing import Any, Callable, Iterable, Iterator, Tuple, Type, Union

from fungebra.helpers import constant
from fungebra.model import Function, identity


SingleArgCallable = Callable[[Any], Any]


# Function manipulation


@Function
def collect(function: Callable) -> Callable:
    """Collect multiple args as a single iterable before passing.

    For example:
    ```
    collect(sum).partial(1)(2, 3) == 6
    ```
    """
    return Function(lambda *args: function(args))


@Function
def expand(function: Callable) -> Callable:
    """Expand single argument to multiple positional arguments.

    For example:
    ```
    data = [
        {"foo": [1,2]},
        {"foo": [3,4]}
    ]
    (itemgetter("foo").map | expand(chain) | list)(data) == [1,2,3,4]
    ```
    """
    return Function(lambda args: function(*args))


@Function
def caller(*args, **kwargs) -> Callable[[Callable], Any]:
    """Pass provided arguments to subsequent functions.

    For example:
    ```
    data = 2
    checkers = [even, negative]
    caller(data).lmap.(checkers) | list == [True, False]
    ```
    """
    return Function(lambda function: function(*args, **kwargs))


@Function
def constantly(const: Any):
    """Function which returns a constant regardless of the arguments.

    For example:
    ```
    constantly(True).lmap([1, 2, 3]) == [True, True, True]
    ```
    """
    return Function(lambda *_a, **_kw: const)


# Data comparison functions


@Function
def is_(value: Any) -> Callable[[Any], bool]:
    """Return a function checking if its argument is value.

    For example:
    ```
    is_(2).lmap([1, 2, 3]) == [False, True, False]
    ```
    """
    return Function(operator.is_).partial(value)


@Function
def equals(value: Any) -> Callable[[Any], bool]:
    """Return a function checking if its argument equals value.

    For example:
    ```
    equals(2).lmap([1, 2, 3]) == [False, True, False]
    ```
    """
    return Function(operator.eq).partial(value)


@Function
def less(value: Any) -> Callable[[Any], bool]:
    """Return a function checking if its argument is less than value.

    For example:
    ```
    less(2).lmap([1, 2, 3]) == [True, False, False]
    ```
    """
    return Function(operator.gt).partial(value)


@Function
def greater(value: Any) -> Callable[[Any], bool]:
    """Return a function checking if its argument is greater than value.

    For example:
    ```
    greater(2).lmap([1, 2, 3]) == [False, False, True]
    ```
    """
    return Function(operator.lt).partial(value)


@Function
def fnot(function: Callable) -> Callable:
    """Inverse of composing a function with bool.

    For example:
    ```
    fnot(identity)(True) == False
    fnot(identity)(False) == True
    greater_or_equal_to = less | fnot
    greater_or_equal_to(2).lmap([1, 2, 3]) == [False, True, True]
    ```
    """
    return Function(lambda *a, **kw: not function(*a, **kw))


# Data manipulation functions


@Function
def itemgetter(
    key: Any, default: Any = constant("not_passed")
) -> Callable[[Any], Any]:
    """Similar to `operator.itemgetter`, but produces `Function`.

    For example:
    ```
    itemgetter("foo")({"foo": "bar"}) == "bar"
    itemgetter("foo")({"bar": "baz"})  # KeyError
    itemgetter("foo", None)({"bar": "baz"}) == None
    ```
    """
    return Function(
        iffy(
            is_(constant("not_passed")),
            constantly(lambda val: val[key]),
            constantly(lambda val: val.get(key, default)),
        )(default)
    )


@Function
def attrgetter(
    attr: str, default: Any = constant("not_passed")
) -> Callable[[Any], Any]:
    """Similar to `operator.attrgetter`, but produces `Function`.

    For example:
    ```
    attrgetter("reduce")(functools) is functools.reduce
    attrgetter("map")(functools)  # AttributeError
    attrgetter("map", None)(functools) == None
    ```
    """
    return Function(
        iffy(
            is_(constant("not_passed")),
            constantly(lambda val: getattr(val, attr)),
            constantly(lambda val: getattr(val, attr, default)),
        )(default)
    )


@Function
def methodcaller(method: str, *args, **kwargs) -> Callable[[Any], Any]:
    """Similar to `operator.methodcaller`, but produces `Function`.

    For example:
    ```
    methodcaller("split", "2")("123") == ["1", "3"]
    ```
    """
    return attrgetter(method) | caller(*args, **kwargs)


@Function
def taker(predicate: Callable[[Any], Any]) -> Callable[[Iterable], Iterator]:
    """Partially applied takewhile.

    For example:
    ```
    (taker(less(3)) | list)(range(6)) == [0, 1, 2]
    ```
    """
    return Function(takewhile).partial(predicate)


# Control flow functions


@Function
def iffy(
    predicate: SingleArgCallable,
    func: SingleArgCallable,
    default: SingleArgCallable = identity,
) -> Callable:
    """Return a function which calls a func if a predicate returns true.

    For example:
    ```
    bound_negative = iffy(lambda x: x < 0, constantly(0))
    bound_negative.lmap([-1, 2, 4]) == [0, 2, 4]
    ```
    """
    return Function(lambda arg: func(arg) if predicate(arg) else default(arg))


@Function
def raiser(exception_class: Type[Exception], *args, **kwargs) -> Callable:
    """Function which raises given exception type with provided args.

    For example:
    ```
    validate = iffy(equals(2), raiser(ValueError))
    validate(1) == 1
    validate(2)  # Raises ValueError
    ```
    """

    def _raise(*_, **__):
        raise exception_class(*args, **kwargs)

    return _raise


@Function
def suppress(
    exception_classes: Union[Exception, Tuple[Exception, ...]],
    default: Any = None,
) -> Callable[[Callable], Callable]:
    """Decorate function to suppress exceptions and return default value.

    For example:
    ```
    validate = iffy(equals(2), raiser(ValueError))
    suppress(ValueError)(validate).lmap([1, 2, 3]) == [1, None, 3]
    ```
    """

    @Function
    def _decorate(function: Callable) -> Callable:
        @Function
        def _wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exception_classes:
                return default

        return _wrapper

    return _decorate
