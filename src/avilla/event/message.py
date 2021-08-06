from datetime import datetime
from typing import Literal, Union

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from pydantic import Field

from avilla.context import ctx_relationship
from avilla.entity import Entity
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.protocol import T_Profile

from . import AvillaEvent


class MessageEvent(AvillaEvent[T_Profile]):
    message: MessageChain
    message_id: str

    current_id: str = Field(default_factory=lambda: ctx_relationship.get().current.id)
    time: datetime = Field(default_factory=lambda: datetime.now())
    subtype: Literal["common", "anonymous", "notice"] = Field(default="common")

    # sender: see [AvillaEvent]

    def __init__(
        self,
        ctx: Union[Entity[T_Profile], Group],
        message: MessageChain,
        message_id: str,
        current_id: str = None,
        time: datetime = None,
    ) -> None:
        super().__init__(
            ctx=ctx,
            message=message,
            message_id=message_id,
            current_id=current_id,
            time=time,
        )

    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: "DispatcherInterface"):
            pass
