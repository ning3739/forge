from abc import ABC, abstractmethod
from typing import List, Any, Tuple

from fastapi import APIRouter


class IRouter(ABC):
    _router: APIRouter
    _external_args: Tuple[Any, ...]
    _external_kwargs: dict
    _end_point: str = ""

    def __init__(self, *args, **kwargs):
        self._router = APIRouter()
        self._external_args = args
        self._external_kwargs = kwargs
        self._set_impl()

    @abstractmethod
    def _set_impl(self):
        pass

    @property
    def router(self):
        return self._router

    @property
    def end_point(self):
        return self._end_point
