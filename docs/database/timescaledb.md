# Database Architecture

Our system uses **TimescaleDB**, an open-source extension of PostgreSQL, optimized for storing and querying financial time-series data at scale.

## Schema Architecture
Our schema is designed for high-performance time-series analysis while maintaining relational integrity for metadata.

### Core Tables

| Table Name | Primary Key | Type | Purpose |
| :--- | :--- | :--- | :--- |
| `stock_eod` | `symbol`, `bus_date` | Hypertable | Daily historical prices. |
| `stock_adjusted` | `symbol`, `bus_date` | Hypertable | Dividend/Split adjusted daily data. |
| `stock_dividends` | `symbol`, `bus_date` | Hypertable | Historical dividend payouts. |
| `stock_splits` | `symbol`, `bus_date` | Hypertable | Stock split history. |
| `market_news` | `id`, `date` | Hypertable | Financial news sentiment analysis. |
| `exchanges` | `code` | Relational | Metadata for global exchanges. |
| `tickers` | `code`, `exchange_code` | Relational | Master symbol list for discovery. |

## Schema Management
The database schema is managed programmatically via the `create_tables.py` script in `libs/db-client`.

- **Automatic Table Generation**: The script iterates through all SQLAlchemy models and generates the corresponding `CREATE TABLE` and `SELECT create_hypertable()` commands.
- **SQL Source of Truth**: The `stocks.sql` file in `libs/db-client` is the verified export of the current schema, used for container initialization and migrations.

## High-Efficiency Persistence
To handle large metadata sets (e.g., 51K+ tickers), we use PostgreSQL's **`ON CONFLICT`** logic. This ensures that symbol discovery flows remain idempotent and performant, updating metadata if it exists or inserting it if new.

## Environment Separation
We maintain strict isolation between **Development** and **Production** data using separate containerized instances.

### Setup Mapping

| Environment | Port | Container Name | User | Volume |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `dev_user` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `prod_user` | `timescaledb_data_prod` |

## UI Management (CloudBeaver)
We provide a modern web interface for managing both database environments using a single **CloudBeaver** instance.

### Access Details

| Service | URL |
| :--- | :--- |
| **Database UI** | [http://localhost:8978](http://localhost:8978) |

### Connecting to Servers in CloudBeaver
CloudBeaver allows you to manage both Dev and Prod from one dashboard:
1. Open [http://localhost:8978](http://localhost:8978).
2. Click **Connection** > **Manual** > **PostgreSQL**.
3. Create two separate connections using these details:

| Connection Name | Host | Port | User |
| :--- | :--- | :--- | :--- |
| **Enterprise-Dev** | `timescaledb-dev` | `5432` | `dev_user` |
| **Enterprise-Prod** | `timescaledb-prod` | `5432` | `prod_user` |

4. Use the passwords defined in the [Environment Separation](#environment-separation) table.

## Infrastructure Management
The databases are managed through Docker Compose from the project root:
```bash
# Start instances
docker-compose up -d

# Stop instances
docker-compose down
```

## Hybrid Storage Strategy

As the volume of intraday data grows, we transition from a pure relational model to a **Hybrid Storage Strategy**:

- **Metadata & EOD**: Remains in TimescaleDB for fast relational queries and trend analysis.
- **Intraday Data**: Persisted as partitioned **Parquet files** in host storage (e.g., Google Drive or local SSD).

This approach prevents database "bloat," reduces backup times, and leverages the performance of columnar storage for high-resolution 1-minute data. See [Storage Client](../python/packages/storage-client.md) for implementation details.

## Schema Creation
The `DBClient` automatically handles schema generation. If a table or hypertable does not exist upon initialization, the client will create it using the SQLAlchemy models defined in `libs/db-client`.
