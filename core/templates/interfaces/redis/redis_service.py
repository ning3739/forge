from abc import ABC
from typing import TypeVar, Generic

from ..entity import IEntity
from ..service_singleton import IServiceSingleton
from ...enums.redis_prefix import RedisPrefix

_R = TypeVar("_R", bound=IEntity)


class IRedisService(IServiceSingleton, ABC, Generic[_R]):
    _prefix: RedisPrefix

    @property
    def prefix(self) -> str:
        """Get the prefix for the redis key."""
        if not self._prefix:
            raise NotImplementedError("Please implement the prefix property.")
        return self._prefix
