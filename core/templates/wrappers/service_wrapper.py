from typing import TypeVar, Type, Dict, Any, Optional

from loguru import logger

from ..interfaces.service_singleton import IServiceSingleton

_services: Dict[str, Any] = {}
_service_types: Dict[Type, Any] = {}
_T = TypeVar("_T", bound=IServiceSingleton)


def service(service_type: Type[_T], *args: object, **kwargs: object) -> type[_T]:
    try:
        _instance = service_type(*args, **kwargs)
        _services[service_type.__name__] = _instance
        _service_types[service_type] = _instance
        setattr(service_type, "_is_service", True)
    except Exception as e:
        logger.error(f"Failed to register service {service_type.__name__}: {e}")
    return service_type


def get_service(service_type: Type[_T], *args, **kwargs) -> _T:  # lazyload
    try:
        _service = _service_types.get(service_type)
        if _service:
            return _service
        else:
            _instance = service_type(*args, **kwargs)
            _services[service_type.__name__] = _instance
            _service_types[service_type] = _instance
            return _instance
    except Exception as e:
        logger.error(f"Failed to get service {service_type.__name__}: {e}")
        raise e


def get_service_by_name(service_name: str) -> _T:
    return _services.get(service_name)
