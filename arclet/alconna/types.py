import inspect
from typing import Type, Union, Dict

from avilla.core.message import Element


class pattern:
    digit = r"(\d+)"
    string = r"(.+)"
    boolean = r"(true|false)"
    ip = r"(\d+)\.(\d+)\.(\d+)\.(\d+)"
    url = r"(http[s]?://.+)"


class Args:
    args: Dict[str, Type[Element]]
    defaults: Dict[str, Union[str, Element]]

    def __init__(self, **kwargs):
        self.args = kwargs
        self.defaults = {}

    def default(self, **kwargs):
        self.defaults = {k: v for k, v in kwargs.items() if k not in ("name", "type")}
        return self

    def check(self, keyword: str):
        if keyword in self.defaults:
            if self.defaults[keyword] is None:
                return inspect.Signature.empty
            return self.defaults[keyword]

    def __iter__(self):
        for k, v in self.args.items():
            yield k, v

    def __len__(self):
        return len(self.args)

    def __repr__(self):
        if not self.args:
            return "Args()"
        repr_string = "Args({0})"
        repr_args = ", ".join(
            [
                f"{name}: {argtype}" + (f" = {name}" if name in self.defaults else "")
                for name, argtype in self.args.items()
            ]
        )
        return repr_string.format(repr_args)