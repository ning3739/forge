from ..interfaces.str_enum import IStrEnum


class RedisPrefix(IStrEnum):
    user = "user:"
    post = "post:"
    comment = "comment:"
