from typing import Self

from .service import IService


class IServiceSingleton(IService):
    _instance: Self = None
    """"""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
