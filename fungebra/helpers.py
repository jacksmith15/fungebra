from functools import lru_cache
from types import ModuleType
from typing import Any, Callable


class ModuleWrapper(ModuleType):
    """Wrap a module, decorating access to contained items.

    For example:
    ```
    # All callable items in the operator module returned as Functions.
    operator = ModuleWrapper(operator, iffy(callable, Function))
    ```
    """

    def __init__(self, obj: Any, decorate: Callable = lambda _: _):
        self._wrapped = obj
        self._decorate = decorate

    def __getattr__(self, attr: str) -> Any:
        if attr in self.__dict__:
            return getattr(self, attr)
        return self._decorate(getattr(self._wrapped, attr))


@lru_cache(maxsize=None)
def constant(name: str) -> object:
    """Return a placeholder singleton with its own type.

    Multiple calls with the same name return the same value.

    For example:
    ```
    def get_item(dictionary, key, default=constant("not_passed")):
        if default is constant("not_passed"):
            return dictionary[key]
        return dictionary.get(key, default)
    ```
    """
    return type(name, tuple(), dict())()
