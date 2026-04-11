# Modern Python Patterns

This project adheres to modern Python standards (3.13+) and utilizes several advanced design patterns to maintain a clean, scalable codebase.

## 1. Structural Pattern Matching (PEP 634)
We use `match/case` statements for complex branching logic, particularly in our deployment mappers. This is more readable and performant than long `if/elif` chains.

**Example from `mapper.py`:**
```python
def map_deployment_to_settings(deployment: PrefectDeployment) -> AbstractDeploymentSettings:
    match deployment:
        case PrefectDeployment.EOD:
            return DeploymentEOD()
        case PrefectDeployment.MARKET_NEWS:
            return DeploymentNews()
        case _:
            raise NotImplementedError(...)
```

## 2. Lazy-Loaded Properties
To keep our main API client (`EODHDClientBase`) lightweight, specialized clients are initialized only when first accessed. This prevents unnecessary memory allocation and circular import issues.

**Pattern:**
```python
@property
def news(self):
    from .news_client import NewsClient  # Local import to avoid circularity
    if self._news is None:
        self._news = NewsClient(self.api_key)
    return self._news
```

## 3. Composition over Inheritance
While we use a base class for common logic (HTTP, Rate Limiting), the system favors composition. The `EODHDClientBase` acts as a "hub" that composes multiple specialized clients, making the library modular and easy to test.

## 4. Modern Type Hinting (PEP 585/604)
We use the latest type hinting syntax for clarity and static analysis support:
- `list[str]` instead of `List[str]`
- `int | None` instead of `Optional[int]`
- `dict[str, Any]` for complex data structures.

## 5. Standardized Logging
We use **Loguru** across all libraries and apps. It provides:
- Automatic context capture (e.g., Prefect `run_id`).
- Pre-formatted, color-coded CLI output.
- Easy integration with external monitoring tools.
