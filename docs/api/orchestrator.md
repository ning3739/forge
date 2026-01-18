# GeneratorOrchestrator

The `GeneratorOrchestrator` class discovers, filters, sorts, and executes all registered generators.

## Location

```python
from core.generators.orchestrator import GeneratorOrchestrator
```

## Constructor

```python
GeneratorOrchestrator(project_path: Path, config_reader: ConfigReader)
```

**Parameters:**
- `project_path`: Path to the project being generated
- `config_reader`: ConfigReader instance for accessing configuration

## Methods

### execute_generators()

Discovers and executes all applicable generators.

```python
def execute_generators(self) -> None
```

This method:
1. Discovers all registered generators from `GENERATOR_REGISTRY`
2. Filters generators based on `enabled_when` conditions
3. Sorts generators by dependencies and priority
4. Executes each generator's `generate()` method

**Example:**
```python
from pathlib import Path
from core.config_reader import ConfigReader
from core.generators.orchestrator import GeneratorOrchestrator

project_path = Path("./my-project")
config_reader = ConfigReader(project_path)

orchestrator = GeneratorOrchestrator(project_path, config_reader)
orchestrator.execute_generators()
```

## Internal Process

### 1. Discovery

The orchestrator imports generator modules to trigger `@Generator` decorator registration:

```python
def _discover_generators(self):
    # Import all generator modules
    from core.generators.configs import *
    from core.generators.deployment import *
    from core.generators.templates.app import *
    from core.generators.templates.database import *
    # ... etc
    
    return list(GENERATOR_REGISTRY.values())
```

### 2. Filtering

Generators with `enabled_when` conditions are evaluated:

```python
def _filter_generators(self, generators):
    result = []
    for gen in generators:
        condition = gen.get("enabled_when")
        if condition is None or condition(self.config_reader):
            result.append(gen)
    return result
```

### 3. Dependency Resolution

The orchestrator builds a dependency graph and performs topological sorting:

```python
def _resolve_dependencies(self, generators):
    # Build adjacency list
    graph = {g["class"].__name__: g["requires"] for g in generators}
    
    # Topological sort
    sorted_names = self._topological_sort(graph)
    
    # Reorder generators
    name_to_gen = {g["class"].__name__: g for g in generators}
    return [name_to_gen[name] for name in sorted_names]
```

### 4. Priority Sorting

Within dependency constraints, generators are sorted by priority:

```python
def _sort_by_priority(self, generators):
    return sorted(generators, key=lambda g: g["priority"])
```

### 5. Execution

Each generator is instantiated and executed:

```python
def _execute(self, generators):
    for gen_info in generators:
        generator = gen_info["class"](
            self.project_path,
            self.config_reader
        )
        generator.generate()
```

## Error Handling

### Missing Dependency

If a generator requires another generator that doesn't exist:

```python
@Generator(requires=["NonExistentGenerator"])
class MyGenerator(BaseTemplateGenerator):
    ...
```

The orchestrator raises an error during dependency resolution.

### Circular Dependency

If generators have circular dependencies:

```python
@Generator(requires=["GeneratorB"])
class GeneratorA(BaseTemplateGenerator): ...

@Generator(requires=["GeneratorA"])
class GeneratorB(BaseTemplateGenerator): ...
```

The orchestrator detects the cycle and raises an error.

### Generator Failure

If a generator's `generate()` method raises an exception, the orchestrator stops execution and propagates the error.

## Usage in ProjectGenerator

The orchestrator is used by `ProjectGenerator`:

```python
# core/project_generator.py
class ProjectGenerator:
    def __init__(self, project_path: Path, config: dict):
        self.project_path = project_path
        self.config_reader = ConfigReader(project_path)
        self.structure_generator = StructureGenerator(project_path, self.config_reader)
        self.orchestrator = GeneratorOrchestrator(project_path, self.config_reader)
    
    def generate(self):
        # 1. Create directory structure
        self.structure_generator.create_project_structure()
        
        # 2. Execute all generators
        self.orchestrator.execute_generators()
```

## Execution Order Example

Given these generators:

```python
@Generator(category="config", priority=1)
class PyprojectGenerator: ...

@Generator(category="database", priority=30, requires=["ConfigDatabaseGenerator"])
class DatabaseConnectionGenerator: ...

@Generator(category="app_config", priority=15)
class ConfigDatabaseGenerator: ...

@Generator(category="model", priority=40, requires=["DatabaseConnectionGenerator"])
class UserModelGenerator: ...

@Generator(category="router", priority=80, requires=["UserModelGenerator"], enabled_when=lambda c: c.has_auth())
class AuthRouterGenerator: ...
```

With authentication enabled, execution order:

1. `PyprojectGenerator` (priority=1, no deps)
2. `ConfigDatabaseGenerator` (priority=15, no deps)
3. `DatabaseConnectionGenerator` (priority=30, requires ConfigDatabaseGenerator)
4. `UserModelGenerator` (priority=40, requires DatabaseConnectionGenerator)
5. `AuthRouterGenerator` (priority=80, requires UserModelGenerator, auth enabled)

With authentication disabled, `AuthRouterGenerator` is skipped.

## Debugging

### List Registered Generators

```python
from core.decorators import GENERATOR_REGISTRY

for name, info in sorted(GENERATOR_REGISTRY.items(), key=lambda x: x[1]["priority"]):
    print(f"{info['priority']:3d} | {info['category']:12s} | {name}")
```

### Check Generator Conditions

```python
from core.config_reader import ConfigReader

config_reader = ConfigReader(Path("./project"))

for name, info in GENERATOR_REGISTRY.items():
    condition = info.get("enabled_when")
    enabled = condition is None or condition(config_reader)
    print(f"{name}: {'enabled' if enabled else 'disabled'}")
```

### Trace Execution

Add logging to see execution order:

```python
def execute_generators(self):
    generators = self._get_sorted_generators()
    
    for gen_info in generators:
        print(f"Executing: {gen_info['class'].__name__}")
        generator = gen_info["class"](self.project_path, self.config_reader)
        generator.generate()
        print(f"Completed: {gen_info['class'].__name__}")
```
