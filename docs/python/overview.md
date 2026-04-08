# Python Overview

This project is built using modern Python standards to ensure high performance, maintainability, and developer productivity.

## Core Language
- **Version**: Python **3.13.1**
- **Standards**: We follow PEP 8 for style and PEP 585/604 for modern type hinting.
- **Packages**: See our [Popular Packages](./packages/overview.md) guide for details on the core libraries we use.

## Monorepo Orchestration

### Nx
We use **Nx** as our build system and monorepo orchestrator. Nx allows us to:
- Manage multiple applications and libraries in one place.
- Run tasks (like `lint`, `test`, `build`) across the entire workspace or specific projects.
- Maintain a dependency graph between our code modules.

### UV
**UV** is an extremely fast Python package installer and resolver, written in Rust. It replaces traditional tools like `pip` and `poetry`.
- **Project Isolation**: UV creates a `.venv` for each project.
- **Locking**: Every project has a `uv.lock` file ensuring deterministic and reproducible builds.
- **Syncing**: Run `uv sync` to install all dependencies for a project instantly.

## Coding Standards

### Modern Type Hinting
We strictly use modern type hints available in newer Python versions:
- `list[str]` instead of `List[str]`
- `dict[str, int]` instead of `Dict[str, int]`
- `int | None` instead of `Optional[int]`

### Documentation (Docstrings)
Every class and method must have a Google-style docstring:
```python
def example_method(param1: int, param2: str) -> bool:
    \"\"\"
    A brief description of what the method does.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        bool: The result of the operation.
    \"\"\"
    return True
```
