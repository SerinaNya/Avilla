from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageRevoke, MessageSend, MessageReceived, MessageSent
from graia.amnesia.builtins.memcache import Memcache, MemcacheService
from graia.amnesia.message import MessageChain

if TYPE_CHECKING:
    from avilla.red.account import RedAccount  # noqa
    from avilla.red.protocol import RedProtocol  # noqa


class RedMessageActionPerform((m := AccountCollector["RedProtocol", "RedAccount"]())._):
    m.post_applying = True

    async def handle_reply(self, target: Selector):
        cache: Memcache = self.protocol.avilla.launch_manager.get_component(MemcacheService).cache
        reply_msg = await cache.get(f"red/account({self.account.route['account']}).message({target.pattern['message']})")
        if reply_msg:
            return {
                "elementType": 7,
                "replyElement": {
                    # "sourceMsgIdInRecords": reply_msg["msgId"],
                    "replayMsgSeq": reply_msg["msgSeq"],
                    #"senderUid": reply_msg["senderUid"],
                },
            }
        logger.warning(f"Unknown message {target.pattern['message']} for reply")
        return None

    @MessageSend.send.collect(m, "land.group")
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        msg = await self.account.staff.serialize_message(message)
        if reply and (reply_msg := await self.handle_reply(reply)):
            msg.insert(0, reply_msg)
        resp = await self.account.websocket_client.call_http(
            "post", "api/message/send",
            {
                "peer": {
                    "chatType": 2,
                    "peerUin": target.pattern["group"],
                    "guildId": None,
                },
                "elements": msg,
            },
        )
        if "msgId" in resp:
            msg_id = resp["msgId"]
            event = await self.account.staff.ext({"connection": self.account.websocket_client}).parse_event("message::recv", resp)
            if TYPE_CHECKING:
                assert isinstance(event, MessageReceived)
            event.context = self.account.get_context(target.member(self.account.route["account"]))
            event.message.scene = target
            event.message.sender = target.member(self.account.route["account"])
            self.protocol.post_event(MessageSent(event.context, event.message, self.account))
        else:
            msg_id = "unknown"
        return Selector().land(self.account.route["land"]).group(target.pattern["group"]).message(msg_id)

    @MessageSend.send.collect(m, "land.friend")
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        msg = await self.account.staff.serialize_message(message)
        if reply and (reply_msg := await self.handle_reply(reply)):
            msg.insert(0, reply_msg)
        resp = await self.account.websocket_client.call_http(
            "post", "api/message/send",
            {
                "peer": {
                    "chatType": 1,
                    "peerUin": target.pattern["friend"],
                    "guildId": None,
                },
                "elements": msg,
            },
        )
        if "msgId" in resp:
            msg_id = resp["msgId"]
            event = await self.account.staff.ext({"connection": self.account.websocket_client}).parse_event("message::recv", resp)
            if TYPE_CHECKING:
                assert isinstance(event, MessageReceived)
            event.context = self.account.get_context(target, via=self.account.route)
            event.message.scene = target
            event.message.sender = self.account.route
            self.protocol.post_event(MessageSent(event.context, event.message, self.account))
        else:
            msg_id = "unknown"
        return Selector().land(self.account.route["land"]).friend(target.pattern["friend"]).message(msg_id)

    @MessageRevoke.revoke.collect(m, "land.group.message")
    async def revoke_group_msg(
        self,
        target: Selector,
    ) -> None:
        await self.account.websocket_client.call_http(
            "post",
            "api/message/recall",
            {
                "peer": {
                    "chatType": 2,
                    "peerUid": target.pattern["group"],
                    "guildId": None,
                },
                "msgId": [target.pattern["message"]],
            },
        )

    @MessageRevoke.revoke.collect(m, "land.friend.message")
    async def revoke_friend_msg(
        self,
        target: Selector,
    ) -> None:
        await self.account.websocket_client.call_http(
            "post",
            "api/message/recall",
            {
                "peer": {
                    "chatType": 1,
                    "peerUid": target.pattern["friend"],
                    "guildId": None,
                },
                "msgId": [target.pattern["message"]],
            },
        )
