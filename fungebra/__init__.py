from collections.abc import Mapping
from functools import partial, reduce, update_wrapper
import operator
from types import ModuleType
from typing import Any, Callable, Iterable, Union

from fungebra.functions import iffy
from fungebra.helpers import ModuleWrapper
from fungebra.model import Function, Args, identity, pipeline


__version__ = "0.0.0"


# Allow options for importing.
F = Func = Function  # pylint: disable=invalid-name


# Allow options for importing.
I = identity  # pylint: disable=invalid-name


# This is a wrapped module for re-export.
# pylint: disable=invalid-name
operator = ModuleWrapper(operator, iffy(callable, F))
