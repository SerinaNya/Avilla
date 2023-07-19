from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from loguru import logger

from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.ryanvk.descriptor.event import EventParse
from avilla.core.selector import Selector
from avilla.red.collector.connection import ConnectionCollector
# from avilla.red.utils import pre_deserialize
from avilla.standard.core.message import MessageReceived
from graia.amnesia.message import MessageChain, Text

if TYPE_CHECKING:
    ...


class RedEventMessagePerform((m := ConnectionCollector())._):
    m.post_applying = True

    @EventParse.collect(m, "message::recv")
    async def message(self, raw_event: dict):
        account = self.connection.account
        if account is None:
            logger.warning(f"Unknown account received message {raw_event}")
            return
        payload = raw_event[0]
        group = Selector().land(account.route["land"]).group(str(payload["peerUid"]))
        member = group.member(str(payload.get("senderUin", "senderUid")))
        context = Context(
            account,
            member,
            group,
            group,
            group.member(account.route["account"]),
        )
        text = payload["elements"][0]["textElement"]
        message = MessageChain([Text(text["content"] if text else "")])
        # TODO: deserialize message
        #message = await account.staff.x({"context": context}).deserialize_message(raw_event["message"])
        return MessageReceived(
            context,
            Message(
                id=f'{payload["msgId"]}|{payload["msgRandom"]}|{payload["msgSeq"]}',
                scene=group,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(int(payload["msgTime"])),
            ),
        )