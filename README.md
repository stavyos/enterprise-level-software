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
- **Technical Indicators**: Automated fetching of RSI, SMA, EMA, and other technical functions.
- **Real-Time Data**: Live (delayed) OHLCV data for multiple tickers.
- **Market News**: Financial news filtered by symbols and tags.
- **Search**: Advanced ticker and news search functionality.

### ETL Flows
Automated data pipelines managed by Prefect 3.x:
- **Dispatcher/Saver Pattern**: Ensures high scalability by splitting large data requests into parallel worker jobs.
- **Standardized Flows**: Dedicated flows for EOD, Intraday, News, Technical Indicators, and Bulk updates.      
- **Kubernetes Ready**: All flows are configured for containerized execution with fine-grained resource management.

### Persistence Layer
- **TimescaleDB**: Optimized for time-series data using Hypertables.
- **SQLAlchemy Models**: Structured models for EOD, Intraday, News, and Technical Indicators.
- **Upsert Logic**: Robust `session.merge()` implementation to handle data updates and avoid duplicates.      

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js (for Nx CLI)
- Docker (for Kubernetes/TimescaleDB)
- [uv](https://github.com/astral-sh/uv) for Python dependency management.

### Configuration
1. Copy `.env.example` to `.env`.
2. Provide your `EODHD_API_KEY`.
3. Configure your database connection details.

### Development Commands
- **Install all dependencies**: `npm run install:all`
- **Run all tests**: `npx nx run-many -t test`
- **Lint the project**: `npx nx run-many -t lint` (Uses **Ruff**)
- **Format the project**: `npx nx run-many -t format` (Uses **Ruff**)
- **Build Docker images**: `npx nx run etl-service:docker-build`
- **Register Flows**: `npx nx run etl-service:deploy`
- **Start Prefect Server**: `npx nx run prefect-orchestrator:run` (Ensure `my-k8s-pool` worker is running)
- **Start Prefect Worker**: `npx nx run prefect-orchestrator:worker`

### Pre-commit Hooks
This project uses `pre-commit` to ensure code quality before every commit.
1. Install hooks: `uvx pre-commit install`
2. Run on all files: `uvx pre-commit run --all-files`

## Documentation
For detailed architecture, setup guides, and API references, please visit the [Tech Learning Center](docs/index.md).
