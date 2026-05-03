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

## 6. High-Efficiency Bulk Upserts (PostgreSQL ON CONFLICT)
To handle enterprise-scale datasets (e.g., 51K symbols or multi-decade backfills), we utilize PostgreSQL's native `INSERT ... ON CONFLICT DO UPDATE` (UPSERT) syntax via SQLAlchemy.

**Implementation Pattern:**
1. **Model Layer**: Define composite primary keys in models to identify unique records.
2. **DB Client**: The `bulk_upsert` method uses `sqlalchemy.dialects.postgresql.insert`.
3. **Execution**: It extracts all data from model instances and sends them to the database in a **single network round-trip**.

**Optimized Logic:**
```python
stmt = pg_insert(model_class).values(data)
upsert_stmt = stmt.on_conflict_do_update(
    index_elements=pk_columns,
    set_={col: stmt.excluded[col] for col in non_pk_columns}
)
conn.execute(upsert_stmt)
```

**Benefits**:
- **Drastic Speedup**: Reduces network overhead by 50,000x for large batches (50K+ rows).
- **Native Atomicity**: Leverages Postgres's internal conflict resolution for maximum data integrity.
- **Idempotency**: Safely re-running the same ETL flow will update existing records without creating duplicates.

## 7. Abstract Storage Pattern
For high-volume data not suitable for SQL, we use an abstract storage layer. This decouples the ETL logic from the underlying file system or cloud storage implementation.

**Implementation (`LocalParquetStorage`)**:
- Uses **PyArrow** and **Pandas** for efficient partitioning and compression.
- Enforces strict 1-minute intervals for intraday data to prevent redundancy.
- Supports native partitioning (e.g., `symbol=.../bus_date=...`) for high-speed data skipping during analysis.
