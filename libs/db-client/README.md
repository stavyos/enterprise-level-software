# Database Client

Persistence layer for the enterprise stock system using SQLAlchemy and TimescaleDB.

## Features
- **SQLAlchemy Models**: Typed models for EOD, Adjusted EOD, Intraday, Dividends, Splits, Exchanges, and News.
- **Bulk Upsert Support**: Highly efficient `bulk_upsert()` method that processes multiple records in a single database session and transaction.
- **Automated Schema Management**: Automatically ensures all tables and hypertables exist on client initialization using `Base.metadata.create_all()`.
- **TimescaleDB Optimization**: Automated creation of Hypertables for all time-series data to ensure high-performance querying and storage.
- **Upsert Support**: Uses `session.merge()` to gracefully handle data updates and avoid primary key conflicts.
- **Connection Management**: Robust session handling and engine configuration for PostgreSQL.

## Core Models
- `StockEOD`: End-Of-Day historical data.
- `StockIntraday`: High-frequency intraday data.
- `MarketNews`: Financial news articles and metadata.
- `Exchange`: Global stock exchange information.

## Usage

```python
from datetime import date
from db_client.client import DBClient
from db_client.models import StockEOD

db = DBClient(dbname="postgres", user="user", password="pwd", host="localhost", port=5432)

# Single Insertion
db.insert_stock_data(bus_date=date.today(), symbol="AAPL.US", ...)

# Bulk Upsert (Highly Recommended for large datasets)
data = [StockEOD(symbol="MSFT.US", ...), StockEOD(symbol="TSLA.US", ...)]
db.bulk_upsert(data)
```

## Development

This project follows the monorepo's unified linting and formatting standards using **Ruff**.

- **Lint**: `npx nx run db-client:lint`
- **Format**: `npx nx run db-client:format`
- **Test**: `npx nx run db-client:test`
