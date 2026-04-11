# Testing Strategy

Maintaining high reliability in financial systems requires a robust and automated testing strategy.

## 1. Unit Testing (Libraries)
All libraries (`libs/`) must have 100% coverage for core logic. We use **Pytest** as our testing framework.

### Mocking API Calls
Since our system interacts with external services (EODHD), we use the `responses` library or `pytest-mock` to mock API responses. This ensures:
- Tests are fast and don't require internet access.
- We don't consume our production API quota during testing.
- We can simulate edge cases like API failures (401, 429, 500).

## 2. Integration Testing (Apps)
ETL flows in `apps/etl-service` are tested to ensure the **Dispatcher/Saver** pattern works correctly.
- We test that the Dispatcher correctly chunks ticker lists.
- We test that the Saver correctly calls the DB client methods.

## 3. Running Tests with Nx
Instead of navigating into each folder, we use Nx to run tests globally or per project.

**Run specific project tests:**
```bash
npx nx run eodhd-client:test
```

**Run all tests in the workspace:**
```bash
npx nx run-many -t test
```

## 4. Code Quality & Linting
In addition to functional tests, we enforce strict styling and linting standards:
- **Black**: Code formatting.
- **Isort**: Import sorting.
- **Flake8**: Style guide enforcement.
- **Mypy**: Static type checking (where applicable).

These tools are integrated into the Nx `lint` target:
```bash
npx nx run-many -t lint
```
