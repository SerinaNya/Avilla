from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull

if TYPE_CHECKING:
    from graia.amnesia.message import __message_chain_class__

    from avilla.core.context import Context
    from avilla.spec.core.message import MessageRevoke
    from avilla.spec.core.message.event import MessageReceived

    from ..account import ElizabethAccount
    from ..protocol import ElizabethProtocol

with bounds("group.message"):

    @implement(MessageRevoke.revoke)
    async def revoke_group_message(ctx: Context, message_selector: Selector):
        await ctx.account.call(
            "recall",
            {
                "__method__": "update",
                "messageId": int(message_selector.last_value),
                "target": int(message_selector["group"]),
            },
        )

    @pull(Message)
    async def get_message_from_id(ctx: Context, message_selector: Selector):
        if TYPE_CHECKING:
            assert isinstance(ctx.account, ElizabethAccount)
            assert isinstance(ctx.protocol, ElizabethProtocol)
        result = await ctx.account.call(
            "messageFromId",
            {
                "__method__": "fetch",
                "messageId": int(message_selector["message"]),
                "target": int(message_selector["group"]),
            },
        )
        event, event_context = await ctx.protocol.parse_event(ctx.account, result["data"])
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)
        ctx.cache["meta"].update(event_context.cache["meta"])
        return event.message
