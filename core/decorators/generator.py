"""Generator decorator - for automatic registration and management of generators"""
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class GeneratorDefinition:
    """Generator definition"""
    name: str
    category: str
    priority: int
    requires: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    enabled_when: Optional[Callable] = None
    generator_class: type = None
    description: str = ""


# Global generator registry
GENERATORS: Dict[str, GeneratorDefinition] = {}


def Generator(
    category: str,
    priority: int = 10,
    requires: List[str] = None,
    conflicts: List[str] = None,
    enabled_when: Callable[[Any], bool] = None,
    description: str = ""
):
    """
    Generator decorator - automatically registers generators to global registry
    
    Args:
        category: Generator category (config, database, auth, deployment, test, etc.)
        priority: Priority (lower numbers execute first, 1-100)
        requires: List of required generator names (dependencies)
        conflicts: List of conflicting generator names
        enabled_when: Condition function that receives config_reader and returns bool
        description: Generator description
    
    Example:
        @Generator(
            category="auth",
            priority=5,
            requires=["UserModelGenerator", "DatabaseConnectionGenerator"],
            enabled_when=lambda config: config.has_auth()
        )
        class AuthRouterGenerator(BaseTemplateGenerator):
            def generate(self):
                ...
    """
    if requires is None:
        requires = []
    if conflicts is None:
        conflicts = []
    
    def wrapper(cls):
        name = cls.__name__
        
        # Register to global dictionary
        GENERATORS[name] = GeneratorDefinition(
            name=name,
            category=category,
            priority=priority,
            requires=requires,
            conflicts=conflicts,
            enabled_when=enabled_when,
            generator_class=cls,
            description=description or cls.__doc__ or ""
        )
        
        return cls
    
    return wrapper


def get_generators_by_category(category: str) -> List[GeneratorDefinition]:
    """Get all generators of specified category"""
    return [
        gen_def for gen_def in GENERATORS.values()
        if gen_def.category == category
    ]


def get_generator(name: str) -> Optional[GeneratorDefinition]:
    """Get generator definition by name"""
    return GENERATORS.get(name)
