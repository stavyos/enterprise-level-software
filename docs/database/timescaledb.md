# Database Architecture

Our system uses **TimescaleDB**, an open-source extension of PostgreSQL, optimized for storing and querying financial time-series data at scale.

## Environment Separation
We maintain strict isolation between **Development** and **Production** data using separate containerized instances.

### Setup Mapping

| Environment | Port | Container Name | User | Volume |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `dev_user` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `prod_user` | `timescaledb_data_prod` |

## UI Management (pgAdmin)
We provide dedicated web interfaces for managing each database environment.

### Access Details

| Environment | URL | Admin Email | Password |
| :--- | :--- | :--- | :--- |
| **Development** | [http://localhost:5050](http://localhost:5050) | `admin@enterprise.dev` | `admin_pass` |
| **Production** | [http://localhost:5051](http://localhost:5051) | `admin@enterprise.prd` | `admin_pass` |

### Connecting to a Server in pgAdmin
Once logged into the UI, follow these steps to register the database:
1. Right-click **Servers** > **Register** > **Server...**
2. **General Tab**: Name it (e.g., "Enterprise Dev")
3. **Connection Tab**:
   - **Host name/address**: `timescaledb-dev` (for Dev UI) or `timescaledb-prod` (for Prod UI)
   - **Port**: `5432` (Note: Use internal port 5432 inside the network)
   - **Maintenance database**: `postgres`
   - **Username**: `dev_user` or `prod_user`
   - **Password**: `dev_pass` or `prod_pass`

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
