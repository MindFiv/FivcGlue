from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

T = TypeVar("T")


class LazyValue(Generic[T]):
    """A lazily-evaluated transparent proxy.

    - Accepts a zero-arg getter. The value is computed on first access and cached.
    - Behaves like the underlying value for most common operations via delegation.
    - Keeps backward compatibility: calling the proxy with no args returns the value.
      If the underlying is callable, calling with args forwards the call.
    Limitations: Python looks up many special methods on the class, not the instance,
    so full operator overloading parity would require adding more dunder methods.
    """

    __slots__ = ("_getter", "_has_value", "_value")

    def __init__(self, getter: Callable[[], T]) -> None:
        object.__setattr__(self, "_getter", getter)
        object.__setattr__(self, "_has_value", False)
        object.__setattr__(self, "_value", None)

    def _ensure(self) -> T:
        if not object.__getattribute__(self, "_has_value"):
            value = object.__getattribute__(self, "_getter")()
            object.__setattr__(self, "_value", value)
            object.__setattr__(self, "_has_value", True)
        return object.__getattribute__(self, "_value")

    # Callable: keep backward compatibility when previous API was a function
    @overload
    def __call__(self) -> T: ...

    @overload
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        value = self._ensure()
        if args or kwargs:
            if callable(value):
                return value(*args, **kwargs)
            raise TypeError("Underlying value is not callable")
        return value

    # Transparent attribute access
    def __getattr__(self, name: str) -> Any:
        return getattr(self._ensure(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_getter", "_has_value", "_value") or name.startswith("__"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._ensure(), name, value)

    def __delattr__(self, name: str) -> None:
        if name in ("_getter", "_has_value", "_value") or name.startswith("__"):
            object.__delattr__(self, name)
        else:
            delattr(self._ensure(), name)

    def __dir__(self) -> list[str]:
        try:
            return sorted(set(dir(type(self)) + dir(self._ensure())))
        except Exception:
            return dir(type(self))

    # Common container and iteration semantics
    def __getitem__(self, key: Any) -> Any:
        return self._ensure()[key]

    def __setitem__(self, key: Any, val: Any) -> None:
        self._ensure()[key] = val

    def __delitem__(self, key: Any) -> None:
        del self._ensure()[key]

    def __iter__(self) -> Any:
        return iter(self._ensure())

    def __len__(self) -> int:
        try:
            return len(self._ensure())
        except TypeError:
            # Not sized
            raise

    def __contains__(self, key: Any) -> bool:
        try:
            return key in self._ensure()
        except TypeError:
            # Not container
            return False

    def __bool__(self) -> bool:
        return bool(self._ensure())

    # Context manager delegation
    def __enter__(self) -> Any:
        value = self._ensure()
        if hasattr(value, "__enter__"):
            return value.__enter__()
        return value

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        value = self._ensure()
        if hasattr(value, "__exit__"):
            return value.__exit__(exc_type, exc, tb)
        return False

    # Async delegation (best-effort)
    def __await__(self) -> Any:
        value = self._ensure()
        if hasattr(value, "__await__"):
            return value.__await__()
        raise TypeError("Underlying value is not awaitable")

    def __aiter__(self) -> Any:
        value = self._ensure()
        if hasattr(value, "__aiter__"):
            return value.__aiter__()
        raise TypeError("Underlying value is not async iterable")

    # Representation
    def __repr__(self) -> str:
        if object.__getattribute__(self, "_has_value"):
            return f"LazyValue({self._ensure()!r})"
        return "LazyValue(<uninitialized>)"

    def __str__(self) -> str:
        return str(self._ensure())

    # Equality delegates to underlying
    def __eq__(self, other: Any) -> bool:
        return self._ensure() == (other._ensure() if isinstance(other, LazyValue) else other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
