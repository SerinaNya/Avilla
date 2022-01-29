from typing import TYPE_CHECKING

from avilla.core.context import ctx_relationship
from avilla.core.execution import MessageSend
from avilla.core.message import Message
from avilla.core.relationship import Relationship
from avilla.core.utilles import Registrar
from avilla.core.utilles.exec import ExecutionHandler
from avilla.core.selectors import mainline as mainline_selector
from avilla.onebot.utilles import raise_for_obresp
from avilla.core.selectors import message as message_selector

if TYPE_CHECKING:
    from avilla.onebot.protocol import OnebotProtocol

registrar = Registrar()


@registrar.decorate("handlers")
class OnebotExecutionHandler(ExecutionHandler["OnebotProtocol"]):
    @registrar.register(MessageSend)
    @staticmethod
    async def send_message(protocol: "OnebotProtocol", exec: MessageSend):
        rs = ctx_relationship.get()
        if rs is None:
            raise RuntimeError("No relationship")
        conn = protocol.service.accounts[rs.self]
        if isinstance(exec.target, mainline_selector):
            keypath = exec.target.keypath()
            if keypath == "group":
                message = await protocol.serialize_message(exec.message)
                if exec.reply:
                    message  = [{"type": "reply", "data": {"id": exec.reply}}] + message
                resp = await conn.action(
                    "send_group_message",
                    {
                        "group_id": int(exec.target.path["group"]),
                        # v12 中应该直接传，但 v11 的类型还是 number.
                        "message": message,
                    },
                )
                raise_for_obresp(resp)
                return message_selector.mainline[exec.target]._[str(resp["message_id"])]
            elif keypath == "channel.guild":
                # TODO: gocq 相关, 发频道消息
                raise NotImplementedError
            elif keypath == "friend":
                message = await protocol.serialize_message(exec.message)
                if exec.reply:
                    message  = [{"type": "reply", "data": {"id": exec.reply}}] + message
                resp = await conn.action(
                    "send_private_msg",  # 莫名其妙，感觉这东西只是拿来 friend msg 的
                    {
                        "user_id": int(exec.target.path["friend"]),
                        # v12 中应该直接传，但 v11 的类型还是 number.
                        "message": message,
                    },
                )
                raise_for_obresp(resp)
                return message_selector.mainline[exec.target]._[str(resp["message_id"])]
            else:
                raise NotImplementedError(f"unknown mainline/entity to send: {exec.target}")