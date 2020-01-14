import operator as original_operator

from fungebra import operator, F, ModuleWrapper


def test_that_operator_module_functions_are_reexported():
    assert isinstance(operator.add, F)


def test_can_access_wrapped_object():
    wrapped = operator.__getattr__("_wrapped")
    assert wrapped is original_operator


def test_default_module_wrapper_does_not_decorate():
    assert not isinstance(ModuleWrapper(original_operator).add, F)
