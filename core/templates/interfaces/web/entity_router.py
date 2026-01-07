from abc import ABC
from typing import Generic, TypeVar

from .router import IRouter

_T = TypeVar("_T")
_P = TypeVar("_P")


class IEntityRouter(IRouter, Generic[_T, _P], ABC):
    """"""
