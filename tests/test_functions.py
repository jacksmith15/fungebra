import functools
from itertools import chain

import pytest

from fungebra.functions import (
    iffy,
    taker,
    raiser,
    suppress,
    equals,
    greater,
    collect,
    constantly,
    expand,
    itemgetter,
    caller,
    less,
    is_,
    fnot,
    identity,
    attrgetter,
    methodcaller,
)


def test_collect():
    assert collect(sum).partial(1)(2, 3) == 6


def test_expand():
    data = [{"foo": [1, 2]}, {"foo": [3, 4]}]
    assert (itemgetter("foo").map | expand(chain) | list)(data) == [1, 2, 3, 4]


def test_caller():
    even = lambda x: not x % 2
    negative = less(0)
    checkers = [even, negative]
    assert caller(2).lmap(checkers) == [True, False]


def test_constantly():
    assert constantly(True).lmap([1, 2, 3]) == [True, True, True]


def test_is_():
    assert is_(2).lmap([1, 2, 3]) == [False, True, False]


def test_equals():
    assert equals(2).lmap([1, 2, 3]) == [False, True, False]


def test_less():
    assert less(2).lmap([1, 2, 3]) == [True, False, False]


def test_greater():
    assert greater(2).lmap([1, 2, 3]) == [False, False, True]


def test_fnot():
    assert fnot(identity).lmap([True, False]) == [False, True]


def test_greater_or_equal():
    greater_or_equal = less | fnot
    assert greater_or_equal(2).lmap([1, 2, 3]) == [False, True, True]


class TestItemGetter:
    @staticmethod
    @pytest.mark.parametrize(
        "getter", [itemgetter("foo"), itemgetter("foo", None)]
    )
    def test_itemgetter_with_no_default_valid(getter):
        assert getter({"foo": "bar"}) == "bar"

    @staticmethod
    def test_itemgetter_raises_with_no_key_and_no_default():
        getter = itemgetter("foo")
        with pytest.raises(KeyError):
            getter({"bar": "baz"})

    @staticmethod
    def test_itemgetter_returns_default_with_no_key():
        assert itemgetter("foo", None)({"bar": "baz"}) is None


class TestAttrGetter:
    @staticmethod
    @pytest.mark.parametrize(
        "getter", [attrgetter("reduce"), attrgetter("reduce", None)]
    )
    def test_attrgetter_with_no_default_valid(getter):
        assert getter(functools) is functools.reduce

    @staticmethod
    def test_attrgetter_raises_with_no_attr_and_no_default():
        getter = attrgetter("map")
        with pytest.raises(AttributeError):
            getter(functools)

    @staticmethod
    def test_attrgetter_returns_default_with_no_key():
        assert attrgetter("map", None)(functools) is None


def test_methodcaller():
    assert methodcaller("split", "2")("123") == ["1", "3"]


def test_taker():
    assert (taker(less(3)) | list)(range(6)) == [0, 1, 2]


def test_iffy():
    truncate_negative = iffy(less(0), constantly(0))
    assert truncate_negative.lmap([-1, 2, 4]) == [0, 2, 4]


class TestRaiser:
    validate = iffy(equals(2), raiser(ValueError, "must not equal 2"))

    def test_raiser_doesnt_raise_when_not_hit(self):
        assert self.validate(1) == 1

    def test_raiser_raises_correct_exception_when_hit(self):
        with pytest.raises(ValueError) as excinfo:
            self.validate(2)
        assert str(excinfo.value) == "must not equal 2"


def test_suppress():
    validate = iffy(equals(2), raiser(ValueError))
    assert suppress(ValueError)(validate).lmap([1, 2, 3]) == [1, None, 3]
