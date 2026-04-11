# Database Architecture

Our data persistence layer is designed for high-performance storage and retrieval of financial time-series data.

## TimescaleDB
We use **TimescaleDB**, which is an open-source database designed to make SQL scalable for time-series data. It is built as an extension of **PostgreSQL**.

### Key Features used in this project:
- **Hypertables**: We partition our stock data (EOD, Intraday) into "Hypertables". These automatically partition data by time, ensuring that as our dataset grows into millions of rows, performance remains consistent.
- **Full SQL Support**: Since it's built on Postgres, we can use all standard SQL features and the SQLAlchemy ORM.

## Setup & Maintenance

### Docker
The database is containerized for easy local development. You can start a fresh instance with:
```bash
docker run -d --name timescaledb -p 5430:5432 -e POSTGRES_PASSWORD=postgres timescale/timescaledb-ha:pg17
```

### Schema Generation
Instead of writing SQL by hand, we use SQLAlchemy models to generate our schema.
- **Script**: `libs/db-client/src/db_client/models/create_tables.py`
- **Output**: Generates a `stocks.sql` file that includes both table definitions and the commands to transform them into Hypertables.

## Data Models
We maintain several core tables:
1. `stock_eod`: Standard daily historical data.
2. `stock_intraday`: High-frequency data partitioned by timestamp.
3. `stock_dividends` & `stock_splits`: Corporate actions.
4. `stock_adjusted`: Pre-calculated adjusted pricing for research.
5. `market_news`: Financial articles, tags, and sentiment data (Hypertable).
6. `technical_indicators`: Persisted calculations like RSI and SMA (Hypertable).

### Why use Hypertables for News?
While news articles are text-heavy, they are inherently time-series data. Storing them in a Hypertable allows us to:
- Efficiently fetch "latest news" using time-based partitioning.
- Use TimescaleDB's **Retention Policies** to automatically drop news older than X years, keeping the database lean.
