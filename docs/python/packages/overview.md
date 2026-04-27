# Popular Packages

This project leverages several industry-standard packages to handle database management, logging, networking, and data processing.

## 1. SQLAlchemy
**SQLAlchemy** is the Python SQL toolkit and Object Relational Mapper (ORM) that gives us the full power and flexibility of SQL.
- **Why we use it**: It allows us to define our database tables as Python classes (Models), making it easier to manage data across different database types.
- **Location in project**: Check `libs/db-client` for our model definitions.

## 2. Loguru
**Loguru** is a library that aims to make logging in Python enjoyable.
- **Why we use it**: It provides structured logging out of the box, simple configuration, and beautiful, readable terminal output.
- **Key feature**: In this project, we use Loguru to automatically redact sensitive information like API tokens in our logs.

## 3. Requests
**Requests** is the de facto standard library for making HTTP requests in Python.
- **Why we use it**: It is simple, robust, and handles everything from simple GET requests to complex session management and authentication.
- **Usage**: Used primarily in `libs/eodhd-client` to communicate with the EODHD servers.

## 4. Pandas & PyArrow
These libraries are used for high-performance data manipulation.
- **Pandas**: Used for structured data analysis (DataFrames).
- **PyArrow**: A cross-language development platform for in-memory data that allows us to process large financial datasets extremely quickly.
- **Usage**: Found in our data ingestion pipelines to clean and transform stock data.

## 5. Storage Client (Custom)
The `storage-client` is our internal library for handling file-based storage.
- **Why we use it**: It provides a clean, abstract interface for saving heavy datasets to Parquet files, keeping our TimescaleDB instance lean.
- **Location in project**: Check `libs/storage-client`.
