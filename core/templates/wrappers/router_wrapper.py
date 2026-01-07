from typing import Optional, List, Callable, Type, TypeVar

from pydantic import Field
from typing_extensions import ParamSpec

from ..interfaces.entity import IEntity
from ..interfaces.web.router import IRouter


class RouterDefinition(IEntity):
    model_config = {"arbitrary_types_allowed": True}
    tags: Optional[List[str]] = Field(default_factory=list)
    router: IRouter
    require_auth: bool


ROUTERS: dict[str, List[RouterDefinition]] = {}


def Router(path="", tags: List[str] = None, require_auth: bool = True) -> Callable:
    if tags is None:
        tags = []
    if path != "" and path.endswith("/"):
        raise ValueError("path must not end with '/' if not empty")

    def wrapper(cls: Type[IRouter]):
        if path not in ROUTERS:
            ROUTERS[path] = []
        ROUTERS[path].append(RouterDefinition(
            tags=tags,
            router=cls(),
            require_auth=require_auth,
        ))
        return cls

    return wrapper
