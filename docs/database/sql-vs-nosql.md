# SQL vs. NoSQL

In the world of data persistence, there are two primary architectures: **SQL (Relational)** and **NoSQL (Non-Relational)**. Understanding the strengths of each is critical for choosing the right tool for the job.

## 1. What is SQL?
**SQL (Structured Query Language)** is the standard language used to interact with **Relational Database Management Systems (RDBMS)**. 

Relational databases organize data into tables with predefined rows and columns. Relationships between these tables are established using "keys" (Primary and Foreign keys).

## 2. Key Differences

| Feature | SQL (Relational) | NoSQL (Non-Relational) |
| :--- | :--- | :--- |
| **Data Model** | Table-based (Rows/Columns) | Document, Key-Value, Graph, or Wide-column |
| **Schema** | **Predefined/Fixed**: You must define your structure before adding data. | **Dynamic/Flexible**: You can add data without a predefined schema. |
| **Scalability** | **Vertical**: Scale by adding more power (CPU/RAM) to the server. | **Horizontal**: Scale by adding more servers to a cluster. |
| **Transactions** | **ACID compliant**: Focuses on high reliability and data integrity. | **BASE compliant**: Focuses on availability and "eventual consistency." |
| **Querying** | Uses SQL (Standardized). | Varies by database (e.g., JSON-like queries in MongoDB). |

## 3. SQL Databases (e.g., PostgreSQL, MySQL, SQL Server)
SQL databases are best for projects where:
- Data integrity is paramount (Financial transactions).
- The data structure is consistent and predictable.
- You need to perform complex queries involving many table "joins."

**Our Choice**: We use **PostgreSQL** (via TimescaleDB) because financial stock data is highly structured and requires strict consistency.

## Popular SQL Commands & Queries
SQL uses a standard set of commands to interact with data. Here are the ones you will see most often:

### Data Definition (The "Structure")
| Command | Description | Example |
| :--- | :--- | :--- |
| `CREATE TABLE` | Create a new table. | `CREATE TABLE stocks (symbol TEXT, price FLOAT);` |
| `DROP TABLE` | Delete a table and all its data. | `DROP TABLE stock_eod;` |
| `ALTER TABLE` | Modify an existing table. | `ALTER TABLE stocks ADD COLUMN currency TEXT;` |

### Data Manipulation (The "Content")
| Command | Description | Example |
| :--- | :--- | :--- |
| `SELECT` | Retrieve data from a table. | `SELECT * FROM stock_eod WHERE symbol = 'AAPL';` |
| `INSERT` | Add new rows to a table. | `INSERT INTO stocks (symbol, price) VALUES ('TSLA', 150.0);` |
| `UPDATE` | Change data in existing rows. | `UPDATE stocks SET price = 155.0 WHERE symbol = 'TSLA';` |
| `DELETE` | Remove rows from a table. | `DELETE FROM stocks WHERE symbol = 'TSLA';` |

### Common Analysis Queries
- **Counting rows**: `SELECT COUNT(*) FROM stock_eod;`
- **Filtering and Sorting**: `SELECT * FROM stock_eod WHERE bus_date > '2025-01-01' ORDER BY bus_date DESC;`
- **Joins (Combining Tables)**: 
  ```sql
  SELECT e.symbol, e.close, d.value as dividend 
  FROM stock_eod e 
  JOIN stock_dividends d ON e.symbol = d.symbol AND e.bus_date = d.bus_date;
  ```

## 4. NoSQL Databases (e.g., MongoDB, Redis, Cassandra)
NoSQL databases are best for projects where:
- You are handling massive volumes of unstructured data (Social media feeds, IoT sensor logs).
- You need to scale horizontally across many servers easily.
- Your data structure changes frequently or isn't well-defined.

## Why we use SQL in this Project
For a stock market application, **SQL** is the superior choice for several reasons:
1. **Consistency**: When recording a stock price or a dividend, we cannot afford "eventual consistency." The data must be accurate and available immediately.
2. **Relationships**: Stock symbols, exchanges, and historical prices are deeply related. SQL handles these relationships natively and efficiently.
3. **Complex Analysis**: Calculating moving averages, adjusted prices, and volume trends requires complex queries that SQL is built to handle.
4. **Time-Series optimization**: By using **TimescaleDB** (a SQL extension), we get the scalability of NoSQL for time-series data while keeping the power and familiarity of standard SQL.
