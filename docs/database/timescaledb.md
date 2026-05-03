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

## Schema Integrity

To maintain data robustness across high-volume assets and historical backfills, we adhere to the following standards:

### 1. Numeric Precision (BigInteger)
Standard `Integer` columns (max 2.1B) are insufficient for the `volume` column of high-activity stocks like AAPL, which can reach 7.4B+ in daily volume.
- **Mandate**: All `volume` columns in EOD and Adjusted EOD tables MUST use `BigInteger` (SQL `BIGINT`).

### 2. Reference Data Policy
Reference data tables (like `exchanges`) store the current global state of metadata.
- **Tracking**: These tables should NOT include a `bus_date` in the primary key unless the source API supports point-in-time historical snapshots.
- **Workflow**: Redundant date parameters should be removed from the flow signatures to prevent implying historical tracking where none exists.

## Hybrid Storage Strategy

As the volume of intraday data grows, we transition from a pure relational model to a **Hybrid Storage Strategy**:

- **Metadata & EOD**: Remains in TimescaleDB for fast relational queries and trend analysis.
- **Intraday Data**: Persisted as partitioned **Parquet files** in host storage (e.g., Google Drive or local SSD).

This approach prevents database "bloat," reduces backup times, and leverages the performance of columnar storage for high-resolution 1-minute data. See [Storage Client](../python/packages/storage-client.md) for implementation details.

## Schema Creation
The `DBClient` automatically handles schema generation. If a table or hypertable does not exist upon initialization, the client will create it using the SQLAlchemy models defined in `libs/db-client`.
