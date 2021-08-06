from typing import Type, Union

from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop

from avilla.builtins.profile import MemberProfile
from avilla.entity import Entity
from avilla.group import Group
from avilla.profile import BaseProfile
from avilla.relationship import Relationship


def useCtx(*ctxs: Union[Type[Group], Type[Entity]]):
    def wrapper(rs: Relationship):
        for ctx in ctxs:
            if isinstance(rs.ctx, ctx):
                return
        else:
            raise ExecutionStop

    return Depend(wrapper)


def useCtxProfile(ctx_type: Union[Type[Group], Type[Entity]], profile_type: Type[BaseProfile]):
    def wrapper(rs: Relationship):
        if isinstance(rs.ctx, ctx_type):
            if isinstance(rs.ctx.profile, profile_type):
                return
            raise ExecutionStop

    return Depend(wrapper)


def useCtxId(ctx_type: Union[Type[Group], Type[Entity]], id: str):
    def wrapper(rs: Relationship):
        if isinstance(rs.ctx, ctx_type):
            if rs.ctx.id == id:
                return
            raise ExecutionStop

    return Depend(wrapper)


def useGroupInMemberProfile(*group_ids: str) -> Depend:
    def wrapper(rs: Relationship):
        if (
            isinstance(rs.ctx, Entity)
            and isinstance(rs.ctx.profile, MemberProfile)
            and isinstance(rs.ctx.profile.group, Group)
            and rs.ctx.profile.group.id in group_ids
        ):
            return
        raise ExecutionStop

    return Depend(wrapper)
