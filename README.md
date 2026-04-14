# Enterprise Level Software

A robust, enterprise-grade financial data acquisition and processing system built with Python, Prefect, and TimescaleDB.

## Project Structure

This workspace is managed using [Nx](https://nx.dev) and is organized into applications and libraries.

### Apps (`apps/`)
- **`etl-service`**: Core ETL logic and Prefect flows for financial data acquisition.
- **`prefect-orchestrator`**: Management of the Prefect control plane (server and workers).

### Libs (`libs/`)
- **`eodhd-client`**: A high-performance, rate-limited Python client for the [EODHD API](https://eodhd.com).
- **`db-client`**: Database persistence layer using SQLAlchemy and TimescaleDB optimization (Hypertables).

## Core Capabilities

### EODHD Integration
The `eodhd-client` provides 100% coverage for essential API endpoints verified under production keys:
- **Stocks/ETFs**: EOD historical data, Intraday (up to 1-minute), Dividends, and Splits.
- **Exchanges**: List of supported exchanges and ticker symbols.
- **Bulk Data**: Daily bulk EOD, splits, and dividends for entire countries.
- **Real-Time Data**: Live (delayed) OHLCV data for multiple tickers.
- **Market News**: Financial news filtered by symbols and tags.
- **Search**: Advanced ticker and news search functionality.

### ETL Flows
Automated data pipelines managed by Prefect 3.x:
- **Dispatcher/Saver Pattern**: Ensures high scalability by splitting large data requests into parallel worker jobs.
- **Standardized Flows**: Dedicated flows for EOD, Intraday, News, Exchanges, and Bulk updates.
- **Batch Processing**: Highly optimized **Bulk Upserts** for all data-heavy flows to minimize DB round-trips.
- **Kubernetes Ready**: All flows are configured for containerized execution with fine-grained resource management.

### Persistence Layer
- **TimescaleDB**: Optimized for time-series data using Hypertables.
- **SQLAlchemy Models**: Structured models for EOD, Intraday, News, and Exchanges.
- **Auto-Schema**: Tables and Hypertables are automatically created on first use.
- **Upsert Logic**: Robust `session.merge()` implementation to handle data updates and avoid duplicates.


## Getting Started

### Prerequisites
- Python 3.11+
- Node.js (for Nx CLI)
- Docker (for Kubernetes/TimescaleDB)
- [uv](https://github.com/astral-sh/uv) for Python dependency management.
- `python-dotenv[cli]` for environment variable management.

### Configuration
1.  Copy `template.dev.env` to `dev.env`.
2.  Copy `template.prod.env` to `prod.env`.
3.  Provide your `EODHD_API_KEY` in both files.
4.  Configure your database credentials and Prefect API URLs as defined in the templates.

### Infrastructure Setup
Start all development and production databases (App + Metadata) using Docker Compose:
```bash
docker-compose up -d
```

### Key Development Commands

| Task | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **Install All** | `npm run install:all` | `npm run install:all` |
| **Start Prefect** | `npx nx run prefect-orchestrator:start:dev` | `npx nx run prefect-orchestrator:start:prod` |
| **Register Flows** | `npx nx run etl-service:deploy:dev` | `npx nx run etl-service:deploy:prod` |
| **Docker Build** | `npx nx run etl-service:docker-build:dev` | `npx nx run etl-service:docker-build:prod` |
| **Run Tests** | `npx nx run-many -t test` | `npx nx run-many -t test` |

### Pre-commit Hooks
This project uses `pre-commit` to ensure code quality before every commit.
1. Install hooks: `uvx pre-commit install`
2. Run on all files: `uvx pre-commit run --all-files`

## Documentation
For detailed architecture, setup guides, and API references, please visit the [Tech Learning Center](docs/index.md).
