# False positive on overloaded operators.
# pylint: disable=comparison-with-callable
from collections import namedtuple
import operator

from fungebra import Args, F, Function, identity, pipeline


def add(*args):
    return sum(args)


def double(number):
    return number * 2


def increment(number):
    return number + 1


def even(number):
    return not number % 2


def test_positive_returns_self():
    assert (+F(even)).func is even


class TestPartialApplication:
    @staticmethod
    def test_full_arguments_with_chaining():
        assert F(add).partial(1).partial(2, 3).partial(4)() == 10

    @staticmethod
    def test_partial_arguments_with_chaining():
        assert F(add).partial(1).partial(2, 3)(4) == 10

    @staticmethod
    def test_partial_application_using_lshift_operator():
        func = F(add) << (1, 2, 3, 4)
        assert func() == 10

    @staticmethod
    def test_lshift_partial_application_chaining():
        func = F(add) << (1, 2) << (3, 4)
        assert func() == 10

    @staticmethod
    def test_lshift_partial_application_argument_ordering():
        func = F(operator.sub) << (1,) << (3,)
        assert func() == -2

    @staticmethod
    def test_lshift_partial_application_with_kwargs_from_dict():
        reverse_sorted = F(sorted) << {"key": operator.neg}
        assert reverse_sorted([1, 2, 3]) == [3, 2, 1]

    @staticmethod
    def test_lshift_partial_application_with_kwargs_in_args_object():
        func = F(sorted) << Args([1, 2, 3], key=operator.neg)
        assert func() == [3, 2, 1]

    @staticmethod
    def test_rshift_partial_application_chaining():
        func = F(add) >> (3, 4) >> (1, 2)
        assert func() == 10

    @staticmethod
    def test_rshift_partial_application_argument_ordering():
        func = F(operator.sub) >> (3,) >> (1,)
        assert func() == -2

    @staticmethod
    def test_rshift_partial_application_with_kwargs_from_dict():
        reverse_sorted = F(sorted) >> {"key": operator.neg}
        assert reverse_sorted([1, 2, 3]) == [3, 2, 1]

    @staticmethod
    def test_rshift_partial_application_with_kwargs_in_args_object():
        func = F(sorted) >> Args([1, 2, 3], key=operator.neg)
        assert func() == [3, 2, 1]


class TestFunctionComposition:
    @staticmethod
    def test_function_composition_via_method():
        double_sum = F(double).compose(sum)
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_left_add_operator():
        double_sum = F(double) + sum
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_right_add_operator():
        double_sum = double + F(sum)
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_pipe_method():
        double_sum = F(sum).pipe(double)
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_left_pipe_operator():
        double_sum = F(sum) | double
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_right_pipe_operator():
        double_sum = sum | F(double)
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_pipeline():
        double_sum = pipeline(double, sum)
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_left_pow():
        double_sum = F(double) ** sum
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_function_composition_via_right_pow():
        double_sum = double ** F(sum)
        assert double_sum([1, 2, 3]) == 12


class TestMapFilterReduce:
    @staticmethod
    def test_map_property():
        map_double = F(double).map | list
        assert map_double([1, 2, 3]) == [2, 4, 6]

    @staticmethod
    def test_filter_on_self():
        filter_func = F(even).filter() | list
        assert filter_func([1, 2, 3]) == [2]

    @staticmethod
    def test_filter_with_other():
        filter_func = F(identity).filter(even) | list
        assert filter_func([1, 2, 3]) == [2]

    @staticmethod
    def test_reduce_on_self():
        reduce_func = F(operator.add).reduce()
        assert reduce_func([1, 2, 3]) == 6

    @staticmethod
    def test_reduce_with_other():
        reduce_func = F(identity).reduce(operator.add)
        assert reduce_func([1, 2, 3]) == 6

    @staticmethod
    def test_map_chained_to_filter():
        map_filter = F(increment).map.filter(even) | list
        assert map_filter([1, 2, 3]) == [2, 4]

    @staticmethod
    def test_map_chained_to_reduce():
        map_reduce = F(double).map.reduce(operator.add)
        assert map_reduce([1, 2, 3]) == 12

    @staticmethod
    def test_map_filter_reduce():
        map_filter_reduce = F(increment).map.filter(even).reduce(operator.add)
        assert map_filter_reduce([1, 2, 3]) == 6


class TestArgumentPipeline:
    @staticmethod
    def test_piping_single_argument():
        assert [3, 2, 1] | F(sorted) == [1, 2, 3]

    @staticmethod
    def test_piping_multiple_arguments_via_args_object():
        assert Args([1, 2, 3], key=operator.neg) | F(sorted) == [3, 2, 1]

    @staticmethod
    def test_piping_arguments_into_pipeline_function():
        func = pipeline(F(double).map, sum, str)
        assert [1, 2, 3] | func == "12"

    @staticmethod
    def test_piping_arguments_into_pipeline_expression():
        assert [1, 2, 3] | (F(double).map | sum | str) == "12"


def test_decorator_usage():
    @F
    def negative(number):
        return -number

    func = negative.map.filter(even) | next
    assert func([1, 2, 3]) == -2


def test_hash_of_wrapped_function_is_the_same():
    assert hash(F(sum)) == hash(sum)


def test_repr_of_wrapped_function_is_as_expected():
    assert repr(F(sum)) == "Function(<built-in function sum>)"


class TestMapFilterReduceOperators:
    @staticmethod
    def test_unary_map_operator():
        double_each = -F(double) | list
        assert double_each([1, 2, 3]) == [2, 4, 6]

    @staticmethod
    def test_left_map_operator():
        sort_double = F(sorted) - double | list
        assert sort_double([3, 2, 1]) == [2, 4, 6]

    @staticmethod
    def test_right_map_operator():
        sort_double = sorted - F(double) | list
        assert sort_double([3, 2, 1]) == [2, 4, 6]

    @staticmethod
    def test_reduce_operator():
        double_sum = -F(double) > operator.add
        assert double_sum([1, 2, 3]) == 12

    @staticmethod
    def test_filter_operator():
        increment_filter = list + (F(increment).map < even)
        assert increment_filter([1, 2, 3]) == [2, 4]

    @staticmethod
    def test_map_filter_operator():
        map_filter = list + (F(increment) <= even)
        assert map_filter([1, 2, 3]) == [2, 4]

    @staticmethod
    def test_map_reduce_operator():
        map_reduce = F(double) >= operator.add
        assert map_reduce([1, 2, 3]) == 12


def test_requests_example():
    @Function
    def requests_get(_url, headers=None):
        return namedtuple("response", ["json", "headers"])(
            json=lambda: {
                "total": 10,
                "hits": [{"value": val} for val in range(10)],
            },
            headers=headers,
        )

    get_json = requests_get >> dict(
        headers={"ACCEPT": "application/json"}
    ) | operator.methodcaller("json")

    get_key = lambda key: F(operator.itemgetter(key))

    get_total_records = get_json | get_key("total")

    assert get_total_records("/posts") == 10

    get_even_record_values = list + (
        get_json | get_key("hits") - get_key("value") < F(even)
    )

    assert get_even_record_values("/posts") == [0, 2, 4, 6, 8]

    get_total_record_values = (
        get_json | get_key("hits") - get_key("value") > operator.add
    )

    assert get_total_record_values("/posts") == 45
