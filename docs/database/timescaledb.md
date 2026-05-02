# Database Architecture

Our system uses **TimescaleDB**, an open-source extension of PostgreSQL, optimized for storing and querying financial time-series data at scale.

## Environment Separation
We maintain strict isolation between **Development** and **Production** data using separate containerized instances.

### Setup Mapping

| Environment | Port | Container Name | User | Volume |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `dev_user` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `prod_user` | `timescaledb_data_prod` |

## UI Management (CloudBeaver)
We provide a modern web interface for managing each database environment using **CloudBeaver**.

### Access Details

| Environment | URL |
| :--- | :--- |
| **Development** | [http://localhost:8978](http://localhost:8978) |
| **Production** | [http://localhost:8979](http://localhost:8979) |

### Connecting to a Server in CloudBeaver
CloudBeaver is a sleek, zero-config web UI. To see your data:
1. Open the relevant URL above.
2. Click **Connection** > **Manual**.
3. Choose **PostgreSQL**.
4. **Host**: `timescaledb-dev` (for Dev UI) or `timescaledb-prod` (for Prod UI).
5. **Port**: `5432`.
6. **Database**: `postgres`.
7. **User/Password**: Use the credentials from the [Environment Separation](#environment-separation) table.
8. Click **Connect**.

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
