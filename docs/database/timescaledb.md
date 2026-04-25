# Database Architecture

Our system uses **TimescaleDB**, an open-source extension of PostgreSQL, optimized for storing and querying financial time-series data at scale.

## Environment Separation
We maintain strict isolation between **Development** and **Production** data using separate containerized instances.

### Setup Mapping

| Environment | Port | Container Name | User | Volume |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `dev_user` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `prod_user` | `timescaledb_data_prod` |

### Infrastructure Management
The databases are managed through Docker Compose from the project root:
```bash
# Start instances
docker-compose up -d

# Stop instances
docker-compose down
```

## Optimization Features

### Hypertables
We use Hypertables to automatically partition our `stock_eod` and `stock_intraday` data by time. This ensures that as our history grows into millions of records, query performance remains high and predictable.

### Bulk Upserts
To maximize write throughput, all ETL flows implement a **Bulk Upsert** pattern. Instead of row-by-row inserts, data is collected in memory and persisted in large batches within a single database transaction.

## Schema Creation
The `DBClient` automatically handles schema generation. If a table or hypertable does not exist upon initialization, the client will create it using the SQLAlchemy models defined in `libs/db-client`.
