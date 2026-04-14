# ETL Service

The core data acquisition and processing engine powered by Prefect 3.x.

## Architecture: Dispatcher/Saver Pattern
To handle massive data requests (e.g., fetching years of intraday data for thousands of tickers), the service uses a two-tier flow architecture:

1.  **Dispatcher**: Orchestrates the work by splitting large requests into smaller, manageable chunks.
2.  **Saver**: Parallel worker jobs that perform the actual API calls and database persistence for a specific chunk.

### Performance Optimizations
- **Bulk Upserts**: All flows use batch processing to minimize database round-trips and optimize performance.
- **Smart Logging**: Standardized log levels (`INFO` for summaries, `DEBUG` for individual rows) ensure observability without overwhelming the Prefect dashboard.

## Available Flows
- `main_saver_dispatcher`: Sequential tiered orchestration of all core ETLs.
- `exchanges_saver`: Global stock exchange data collection.
- `eod_saver_dispatcher`: Daily EOD data collection.
- `intraday_saver_dispatcher`: High-frequency data collection.
- `market_news_saver_dispatcher`: Financial news ingestion.
- `bulk_data_saver_dispatcher`: National bulk data updates (EOD, Splits, Dividends).

## Environment Specific Commands

| Task | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **Register Flows** | `npx nx run etl-service:deploy:dev` | `npx nx run etl-service:deploy:prod` |
| **Docker Build** | `npx nx run etl-service:docker-build:dev` | `npx nx run etl-service:docker-build:prod` |

## Configuration
This application uses `python-dotenv` to manage environment-specific configurations.
- Use `dev.env` for development.
- Use `prod.env` for production.

To run a single command with specific environment:
```bash
uv run dotenv -f ../../prod.env run -- python -m etl_service.etl.deploy_etls
```

## Development

This project follows the monorepo's unified linting and formatting standards using **Ruff**.

- **Lint**: `npx nx run etl-service:lint`
- **Format**: `npx nx run etl-service:format`
- **Test**: `npx nx run etl-service:test`
