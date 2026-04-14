# Database Architecture

Our data persistence layer is designed for high-performance storage and retrieval of financial time-series data.

## TimescaleDB
We use **TimescaleDB**, an open-source database designed to make SQL scalable for time-series data. It is built as an extension of **PostgreSQL**.

### Key Features used in this project:
- **Hypertables**: We partition our stock data (EOD, Intraday) into "Hypertables" for consistent performance at scale.
- **Full SQL Support**: Standard SQL features and SQLAlchemy ORM support.

## Environment Separation

We maintain strict isolation between **Development** and **Production** data using separate containerized instances.

### Infrastructure Setup
The databases are managed via Docker Compose. From the project root, run:
```bash
docker-compose up -d
```

### Instance Configuration

| Environment | Port | Container Name | User | Password |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `dev_user` | `dev_pass` |
| **Production** | `5435` | `timescaledb-prod` | `prod_user` | `prod_pass` |

## Setup & Maintenance

### Schema Generation
We use SQLAlchemy models to generate our schema.
- **Script**: `libs/db-client/src/db_client/models/create_tables.py`
- **Output**: Generates `stocks.sql` with table and hypertable definitions.

### Bulk Loading
To optimize performance, ETL scripts use a **Bulk Upsert** pattern, committing thousands of data points in a single transaction.

### Schema Auto-Creation
The `DBClient` automatically ensures all required tables and hypertables exist upon initialization.
