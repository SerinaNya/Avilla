import typing
from contextvars import Token
from datetime import datetime
from types import TracebackType
from typing import Dict, Generic, Optional, Union

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from pydantic import BaseModel  # pylint: ignore

from avilla.entity import Entity
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship, T_Profile

from ..context import ctx_protocol, ctx_relationship


class AvillaEvent(BaseModel, Dispatchable, Generic[T_Profile]):
    ctx: Union[Entity[T_Profile], Group]

    current_id: str  # = Field(default_factory=lambda: ctx_relationship.get().current.id)
    time: datetime  # = Field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {' '.join([f'{k}={v.__repr__()}' for k, v in vars(self).items()])}>"


_Dispatcher_Tokens: "Dict[int, Token[Relationship]]" = {}


class RelationshipDispatcher(BaseDispatcher):  # Avilla 将自动注入...哦, 看起来没这个必要.
    @staticmethod
    async def beforeExecution(interface: "DispatcherInterface"):
        rs = await ctx_protocol.get().get_relationship(interface.event.ctx)  # type: ignore
        token = ctx_relationship.set(rs)
        _Dispatcher_Tokens[id(interface.event)] = token

    @staticmethod
    async def afterExecution(
        interface: "DispatcherInterface",
        exception: Optional[Exception],
        tb: Optional[TracebackType],
    ):
        del _Dispatcher_Tokens[id(interface.event)]

    @staticmethod
    async def catch(interface: "DispatcherInterface"):
        if (
            typing.get_origin(interface.annotation) is Relationship
            or interface.annotation is Relationship
        ):
            return ctx_relationship.get()


class MessageChainDispatcher(BaseDispatcher):
    @staticmethod
    async def catch(interface: "DispatcherInterface"):
        from avilla.event.message import MessageEvent

        if interface.annotation is MessageChain and isinstance(interface.event, MessageEvent):
            return interface.event.message
