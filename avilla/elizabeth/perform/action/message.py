from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.builtins.capability import CoreCapability
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageRevoke, MessageSend, MessageReceived
from avilla.core.message import Message
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from ...account import ElizabethAccount  # noqa
    from ...protocol import ElizabethProtocol  # noqa


class ElizabethMessageActionPerform((m := AccountCollector["ElizabethProtocol", "ElizabethAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.group")
    async def send_group_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.connection.call(
            "update",
            "sendGroupMessage",
            {
                "target": int(target.pattern["group"]),
                "messageChain": await self.account.staff.serialize_message(message),
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        if result["msg"] != "success" or result["messageId"] < 0:
            raise RuntimeError(f"Failed to send message to {target.pattern['group']}: {message}")
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(result["messageId"])

    @MessageSend.send.collect(m, "land.friend")
    async def send_friend_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        result = await self.account.connection.call(
            "update",
            "sendFriendMessage",
            {
                "target": int(target.pattern["friend"]),
                "messageChain": await self.account.staff.serialize_message(message),
                **({"quote": reply.pattern["message"]} if reply is not None else {}),
            },
        )
        if result["msg"] != "success" or result["messageId"] < 0:
            raise RuntimeError(f"Failed to send message to {target.pattern['friend']}: {message}")
        return Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message(result["messageId"])

    @MessageRevoke.revoke.collect(m, "land.group")
    async def revoke_group_message(self, message: Selector):
        await self.account.connection.call(
            "update",
            "recall",
            {
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["group"]),
            },
        )

    @MessageRevoke.revoke.collect(m, "land.friend")
    async def revoke_friend_message(self, message: Selector):
        await self.account.connection.call(
            "update",
            "recall",
            {
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["friend"]),
            },
        )

    @CoreCapability.pull.collect(m, "land.group.message", Message)
    async def get_group_message(self, message: Selector) -> Message:
        result = await self.account.connection.call(
            "fetch",
            "messageFromId",
            {
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["group"]),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to get message from {message.pattern['group']}: {message}")
        event = await self.account.staff.parse_event(result["data"]["type"], result["data"])
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)
        return event.message

    @CoreCapability.pull.collect(m, "land.friend.message", Message)
    async def get_friend_message(self, message: Selector) -> Message:
        result = await self.account.connection.call(
            "fetch",
            "messageFromId",
            {
                "messageId": int(message.pattern["message"]),
                "target": int(message.pattern["friend"]),
            },
        )
        if result is None:
            raise RuntimeError(f"Failed to get message from {message.pattern['friend']}: {message}")
        event = await self.account.staff.parse_event(result["data"]["type"], result["data"])
        if TYPE_CHECKING:
            assert isinstance(event, MessageReceived)
        return event.message
