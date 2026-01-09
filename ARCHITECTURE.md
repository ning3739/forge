# Forge Architecture

## 1. Overall Flow

```mermaid
flowchart TB
    subgraph User["User"]
        A[forge init]
    end

    subgraph CLI["CLI Layer"]
        B[main.py<br/>Typer CLI]
        C[commands/init.py<br/>Interactive Config Collection]
    end

    subgraph Config["Configuration Layer"]
        D[".forge/config.json<br/>Project Configuration"]
        E[ConfigReader<br/>Config Reading & Validation]
    end

    subgraph Generator["Generator Layer"]
        F[ProjectGenerator<br/>Project Generator]
        G[StructureGenerator<br/>Directory Structure]
        H[GeneratorOrchestrator<br/>Generator Orchestrator]
    end

    subgraph Decorators["Decorator System"]
        I["@Generator Decorator<br/>Auto Registration"]
        J["GENERATORS Global Registry"]
    end

    subgraph Generators["40+ Code Generators"]
        K[ConfigGenerators<br/>pyproject, env, readme]
        L[DatabaseGenerators<br/>mysql, postgresql, sqlite]
        M[TemplateGenerators<br/>models, routers, services]
        N[DeploymentGenerators<br/>dockerfile, compose]
        O[TestGenerators<br/>conftest, test_*]
    end

    subgraph Output["Output"]
        P[Generated FastAPI Project]
    end

    A --> B
    B --> C
    C -->|Collect User Choices| D
    D --> E
    E --> F
    F --> G
    F --> H
    H --> I
    I --> J
    J --> K & L & M & N & O
    G --> P
    K & L & M & N & O --> P
```

## 2. Core Component Relationships

```mermaid
classDiagram
    class main_py {
        +Typer app
        +main()
        +version_callback()
    }

    class init_command {
        +execute_init()
        +collect_project_name()
        +collect_database_config()
        +collect_features()
        +generate_project()
    }

    class ProjectGenerator {
        -project_path: Path
        -config_reader: ConfigReader
        -structure_generator: StructureGenerator
        -orchestrator: GeneratorOrchestrator
        +generate()
    }

    class ConfigReader {
        -config: Dict
        -config_file: Path
        +load_config()
        +validate_config()
        +get_database_type()
        +has_auth()
        +has_redis()
        +has_celery()
        +has_testing()
    }

    class StructureGenerator {
        -project_path: Path
        -config_reader: ConfigReader
        +create_project_structure()
        -create_directories()
        -create_init_files()
    }

    class GeneratorOrchestrator {
        -project_path: Path
        -config_reader: ConfigReader
        -generators: List
        +generate()
        -import_all_generators()
        -filter_enabled_generators()
        -resolve_dependencies()
    }

    class Generator_Decorator {
        +category: str
        +priority: int
        +requires: List
        +enabled_when: Callable
        +GENERATORS: Dict
    }

    class BaseTemplateGenerator {
        #project_path: Path
        #config_reader: ConfigReader
        #file_ops: FileOperations
        +generate()*
    }

    main_py --> init_command : registers
    init_command --> ProjectGenerator : creates
    ProjectGenerator --> ConfigReader : uses
    ProjectGenerator --> StructureGenerator : uses
    ProjectGenerator --> GeneratorOrchestrator : uses
    GeneratorOrchestrator --> Generator_Decorator : reads registry
    GeneratorOrchestrator --> BaseTemplateGenerator : instantiates
    BaseTemplateGenerator --> ConfigReader : queries config
```

## 3. Generator Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant CLI as main.py
    participant Init as init_command
    participant PG as ProjectGenerator
    participant CR as ConfigReader
    participant SG as StructureGenerator
    participant Orch as Orchestrator
    participant Gen as Generators

    User->>CLI: forge init
    CLI->>Init: execute_init()
    
    rect rgb(200, 220, 250)
        Note over Init: Interactive Config Collection
        Init->>Init: collect_project_name()
        Init->>Init: collect_database_config()
        Init->>Init: collect_features()
    end
    
    Init->>Init: save_config_file()
    Init->>PG: ProjectGenerator(path)
    
    PG->>CR: load_config()
    CR->>CR: validate_config()
    
    PG->>SG: create_project_structure()
    SG->>SG: create_directories()
    SG->>SG: create_init_files()
    
    PG->>Orch: GeneratorOrchestrator()
    
    rect rgb(250, 220, 200)
        Note over Orch: Generator Orchestration
        Orch->>Orch: import_all_generators()
        Orch->>Orch: filter_enabled_generators()
        Orch->>Orch: resolve_dependencies()
        Orch->>Orch: topological_sort()
    end
    
    Orch->>Gen: generate() [in order]
    Gen-->>User: Generated Project Files
```

## 4. @Generator Decorator Mechanism

```mermaid
flowchart LR
    subgraph Definition["Generator Definition"]
        A["@Generator(<br/>category='auth',<br/>priority=5,<br/>requires=['UserModel'],<br/>enabled_when=lambda c: c.has_auth()<br/>)"]
        B[class AuthRouterGenerator]
    end

    subgraph Registry["Global Registry"]
        C["GENERATORS = {<br/>'AuthRouterGenerator': GeneratorDefinition<br/>}"]
    end

    subgraph Orchestrator["Orchestrator Processing"]
        D[filter_enabled_generators]
        E[resolve_dependencies]
        F[topological_sort]
        G[instantiate & execute]
    end

    A --> B
    B -->|Auto Registration| C
    C --> D
    D -->|enabled_when check| E
    E -->|requires resolution| F
    F -->|priority sorting| G
```

## 5. Generator Dependencies & Priority

```mermaid
flowchart TB
    subgraph P1["Priority 1-10: Base Config"]
        A1[PyprojectGenerator<br/>priority=1]
        A2[GitignoreGenerator<br/>priority=2]
        A3[EnvGenerator<br/>priority=3]
    end

    subgraph P2["Priority 11-30: Core Modules"]
        B1[ConfigBaseGenerator<br/>priority=11]
        B2[DatabaseConnectionGenerator<br/>priority=15]
        B3[SecurityGenerator<br/>priority=20]
    end

    subgraph P3["Priority 31-50: Business Modules"]
        C1[UserModelGenerator<br/>priority=40]
        C2[TokenModelGenerator<br/>priority=41]
        C3[AuthServiceGenerator<br/>priority=45]
    end

    subgraph P4["Priority 51-70: API Layer"]
        D1[AuthRouterGenerator<br/>priority=55]
        D2[UserRouterGenerator<br/>priority=56]
        D3[MainGenerator<br/>priority=60]
    end

    subgraph P5["Priority 71-90: Test & Deploy"]
        E1[TestMainGenerator<br/>priority=80]
        E2[DockerfileGenerator<br/>priority=85]
    end

    B2 -->|requires| C1
    C1 -->|requires| C2
    B3 -->|requires| C3
    C1 -->|requires| C3
    C3 -->|requires| D1
    C1 -->|requires| D2
    D1 & D2 -->|requires| D3
```

## 6. Conditional Enabling Mechanism

```mermaid
flowchart TB
    subgraph Config["User Config (config.json)"]
        A["database.type: 'MySQL'"]
        B["features.redis: true"]
        C["features.celery: true"]
        D["features.testing: true"]
        E["features.docker: true"]
    end

    subgraph Conditions["enabled_when Conditions"]
        F["c.get_db_type() == 'MySQL'"]
        G["c.has_redis()"]
        H["c.has_celery()"]
        I["c.has_testing()"]
        J["c.has_docker()"]
    end

    subgraph Generators["Enabled Generators"]
        K[DatabaseMySQLGenerator]
        L[RedisConfigGenerator]
        M[CeleryAppGenerator]
        N[TestMainGenerator]
        O[DockerfileGenerator]
    end

    A --> F --> K
    B --> G --> L
    C --> H --> M
    D --> I --> N
    E --> J --> O
```

## 7. Project Structure Generation

```mermaid
flowchart TB
    subgraph Input["Input Config"]
        A[".forge/config.json"]
    end

    subgraph Structure["StructureGenerator"]
        B[Create app/ directories]
        C[Create __init__.py files]
        D[Initialize Alembic]
    end

    subgraph Orchestrator["GeneratorOrchestrator"]
        E[Generate config files]
        F[Generate database code]
        G[Generate business code]
        H[Generate test code]
        I[Generate deployment config]
    end

    subgraph Output["Generated Project"]
        J["my-project/
        ├── .forge/
        ├── app/
        │   ├── core/
        │   ├── models/
        │   ├── routers/
        │   └── main.py
        ├── tests/
        ├── alembic/
        ├── Dockerfile
        └── pyproject.toml"]
    end

    A --> B & C & D
    B & C & D --> E & F & G & H & I
    E & F & G & H & I --> J
```

## 8. UI Component Structure

```mermaid
classDiagram
    class ui_colors {
        +get_colors() Colors
        +get_gradients() Gradients
        +console: Console
    }

    class ui_components {
        +create_questionary_style() Style
        +create_highlighted_panel() Panel
        +create_gradient_bar() void
    }

    class ui_logo {
        +show_logo() void
    }

    class Rich {
        Panel
        Text
        Progress
        Console
    }

    class Questionary {
        select()
        confirm()
        text()
        Style
    }

    ui_components --> ui_colors : uses colors
    ui_components --> Rich : creates components
    ui_components --> Questionary : creates styles
    ui_logo --> ui_colors : uses colors
    ui_logo --> Rich : renders logo
```

## Design Patterns Summary

| Pattern | Location | Description |
|---------|----------|-------------|
| **Decorator** | `@Generator` | Auto-registers generators to global registry |
| **Strategy** | Various Generators | Different generators for different DB/features |
| **Template Method** | `BaseTemplateGenerator` | Defines base class with `generate()` interface |
| **Dependency Injection** | `ConfigReader` | All generators share config reader instance |
| **Topological Sort** | `Orchestrator` | Resolves dependencies, determines execution order |
| **Configuration-First** | `.forge/config.json` | Save config first, then generate code based on it |
