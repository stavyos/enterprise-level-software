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

## 5. Flow Integrity & Error Handling

To ensure orchestration accuracy, all ETL flows follow a **Fail-Fast** policy:

- **Explicit Failures**: If a critical operation (API call, DB upsert, Parquet persistence) fails for any item in a batch, the script will log the error and **raise a RuntimeError** at the end of the run.
- **Prefect Observability**: By raising exceptions instead of silently logging errors, we ensure that Prefect correctly marks flow runs as `Failed`. This prevents "ghost successes" where a flow appears completed but data is missing.
- **Verification**: Before merging any storage or acquisition logic, you must verify that invalid inputs (e.g., non-existent tickers or invalid date ranges) correctly result in a `Failed` state in the Prefect dashboard.
