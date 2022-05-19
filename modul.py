from __future__ import annotations

import inspect
import sys
import types
from typing import (
    Any,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
    TypeVar,
    overload,
)

_Decorated = TypeVar("_Decorated")


class DuplicateExportName(ValueError):
    pass


class Exports(MutableMapping[str, Any]):
    __namespace__: dict[str, Any]

    def __init__(self, namespace: dict[str, Any]) -> None:
        super().__setattr__("__namespace__", namespace)

    def __setitem__(self, name: str, value: Any) -> None:
        if not isinstance(name, str):
            raise TypeError(f"Exported name {name} must be a string")
        namespace = self.__namespace__
        if name in namespace:
            raise DuplicateExportName(f"{name} has already been exported")
        namespace[name] = value

    @overload
    def __call__(self, to_export: _Decorated) -> _Decorated:
        ...

    @overload
    def __call__(self, to_export: Mapping[str, Any]) -> None:
        ...

    def __call__(
        self,
        to_export: _Decorated | Mapping[str, Any],
    ) -> Any:
        if isinstance(to_export, Mapping):
            return self.update(to_export)
        if not hasattr(to_export, "__name__"):
            raise TypeError(
                "The exported object must be a mapping or have __name__ attribute"
            )
        self[to_export.__name__] = to_export
        return to_export

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __getitem__(self, name: str) -> Any:
        return self.__namespace__[name]

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __delitem__(self, name: str) -> None:
        del self.__namespace__[name]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__namespace__)

    def __len__(self) -> int:
        return len(self.__namespace__)

    def __repr__(self) -> str:
        return f"Exports({self.__namespace__!r})"


class SequenceProxy(Sequence[str]):
    def __init__(self, data: Collection) -> None:
        self.data = data

    def __getitem__(self, index: int) -> str:
        return list(self.data)[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"SequenceProxy({list(self.data)!r})"

    def __eq__(self, other: Any) -> bool:
        return list(self) == other


class _ExportedModule(types.ModuleType):
    __exported__ = True

    def __init__(
        self,
        name: str,
        doc: str | None = None,
        file: str | None = None,
        *,
        namespace: dict[str, Any] = None,
    ) -> None:
        super().__init__(name, doc)
        self.__file__ = file
        if namespace is None:
            namespace = {}
        self.__all__ = SequenceProxy(namespace)
        self.__namespace__ = namespace

    def __getattr__(self, name: str) -> Any:
        try:
            return self.__namespace__[name]
        except KeyError:
            raise AttributeError(f"Module {self.__name__!r} has no attribute {name!r}")

    def __dir__(self) -> Iterable[str]:
        return super().__dir__() + sorted(self.__namespace__)


class _ExportRegistry:
    """A singleton instance that holds the exported members for all modules."""

    def __init__(self) -> None:
        self.namespaces: dict[types.ModuleType, dict[str, Any]] = {}

    def get_current_module(self) -> types.ModuleType:
        stack = inspect.stack()
        # stack[0] is this method; stack[1] is the caller `__get__` / `__set__`
        # stack[2] is the target module
        module = inspect.getmodule(stack[2][0])
        if module is None:
            module = sys.modules["__main__"]
        return self._replace_module(module)

    def _replace_module(self, module: types.ModuleType) -> types.ModuleType:
        if getattr(module, "__exported__", False):
            return module

        namespace = self.namespaces.pop(module, {})
        newmodule = _ExportedModule(
            module.__name__,
            getattr(module, "__doc__", None),
            getattr(module, "__file__", None),
            namespace=namespace,
        )
        sys.modules[module.__name__] = newmodule
        self.namespaces[newmodule] = namespace
        return newmodule

    def __get__(self, instance: Any, owner: Any) -> Exports:
        if instance is None:
            return self
        module = self.get_current_module()
        namespace = self.namespaces.setdefault(module, {})
        return Exports(namespace)

    def __set__(self, instance: Any, value: Any) -> None:
        module = self.get_current_module()
        namespace = self.namespaces.setdefault(module, {})
        namespace.clear()
        if not isinstance(value, Mapping):
            raise TypeError("The value in the right hand must be a mapping")
        namespace.update(value)


class _ModuleExports(types.ModuleType):
    __file__ = __file__
    __all__ = ["exports"]
    exports = _ExportRegistry()


exports: Exports
sys.modules[__name__] = _ModuleExports(__name__, __doc__)
del _ModuleExports, _ExportRegistry
