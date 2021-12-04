from typing import Any, Dict, Generic, TypeVar, cast

T = TypeVar("T")
A = TypeVar("A")


class SelectorKey(Generic[A, T]):
    selector: str
    key: str
    past: Dict[str, Any]

    def __init__(self, selector: str, key: str, past: Dict[str, Any] = None):
        self.selector = selector
        self.key = key
        self.past = past or {}

    def __getitem__(self, value: T) -> A:
        instance = Selector(self.selector, self.past)
        instance.path[self.key] = value
        return cast(A, instance)

    def __getattr__(self, addition_name: str):
        self.key += "." + addition_name
        return self

    def __repr__(self):
        return f"<{self.selector}>.{self.key}"


class SelectorMeta(type):
    def __getattr__(cls, key: str) -> "SelectorKey":
        return SelectorKey(cls.scope, key)  # type: ignore


S = TypeVar("S", bound=str)


class Selector(Generic[S], metaclass=SelectorMeta):
    scope: S
    path: Dict[str, Any]

    def __init__(self, scope: S, path: Dict[str, Any] = None) -> None:
        self.scope = scope
        self.path = path or {}

    def to_dict(self):
        return self.path

    def last(self) -> Any:
        return list(self.path.items())[-1]

    def keypath(self) -> str:
        return ".".join([k for k in self.path.keys()])

    def __repr__(self) -> str:
        return f"<{self.scope}>.{'.'.join([f'{k}[{v}]' for k, v in self.path.items()])}"

    def __getitem__(self, value: str):
        return self.path[value]

    def __getattr__(self, key: str) -> "SelectorKey":
        return SelectorKey(self.scope, key)