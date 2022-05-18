from __future__ import annotations

import inspect
import sys
import types
from typing import Any, Mapping, TypeVar, overload

_Decorated = TypeVar("_Decorated")


class DuplicateExportName(ValueError):
    pass


class Exports:
    """A singleton instance that holds the exported members for all modules."""

    _namespaces: dict[types.ModuleType, dict[str, Any]] = {}

    def get_current_module(self) -> types.ModuleType:
        stack = inspect.stack()
        # stack[0] is this function, stack[1] is the caller export_var
        # stack[2] is the caller of export_var, stack[3] is the target module
        module = inspect.getmodule(stack[3][0])
        return module

    def export_var(self, name: str, value: Any) -> None:
        module = self.get_current_module()
        namespace = self._namespaces.setdefault(module, {})
        if name in namespace:
            raise DuplicateExportName(f"{name} has already been exported")
        namespace[name] = value
        if hasattr(module, "__all__"):
            module.__all__.append(name)
        self._replace_module(module)

    @overload
    def __call__(self, to_export: _Decorated) -> _Decorated:
        ...

    @overload
    def __call__(self, to_export: Mapping[str, Any]) -> None:
        ...

    def __call__(self, to_export: _Decorated | Mapping[str, Any]) -> Any:
        if isinstance(to_export, Mapping):
            for name, value in to_export.items():
                if not isinstance(name, str):
                    raise TypeError(f"Exported name {name} must be a string")
                self.export_var(name, value)
            return None
        if not hasattr(to_export, "__name__"):
            raise TypeError(
                "The exported object must be a mapping or have __name__ attribute"
            )
        self.export_var(to_export.__name__, to_export)
        return to_export

    def __setattr__(self, name: str, value: Any) -> None:
        self.export_var(name, value)

    def __setitem__(self, name: str, value: Any) -> None:
        self.export_var(name, value)

    def _replace_module(self, module: types.ModuleType) -> None:
        this = self
        if getattr(module, "__export__", False):
            return

        class _ExportsModule(types.ModuleType):
            # Set `__all__` to a KeyView to keep track of subsequent additions
            __all__ = list(this._namespaces.setdefault(module, {}))
            __export__ = True
            __file__ = module.__file__

            def __getattr__(self, name: str) -> Any:
                try:
                    return this._namespaces.get(self, {})[name]
                except KeyError:
                    raise AttributeError(
                        f"Module {self.__name__} has no attribute {name}"
                    ) from None

        newmodule = _ExportsModule(module.__name__, module.__doc__)
        this._namespaces[newmodule] = this._namespaces.pop(module, None)
        sys.modules[module.__name__] = newmodule


exports = Exports()
del Exports

__all__ = ["exports"]
