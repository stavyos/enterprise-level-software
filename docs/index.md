# Tech Learning Center

Welcome to the technical documentation for this monorepo. This center is designed to help you understand the technologies, tools, and patterns used throughout our software stack.

## Documentation Structure

### [Workflow Orchestration](./orchestration/prefect.md)
Learn how we use **Prefect 3.x** to manage distributed ETL pipelines using the **Dispatcher/Saver pattern**.

### [Monorepo Tooling](./tooling/nx-uv.md)
A guide to how we use **Nx** and **UV** to manage projects and dependencies in this monorepo.

### [Python Ecosystem](./python/overview.md)
Learn about the Python version we use, our modern type hinting standards, and the monorepo management tools like **Nx** and **UV**.
- [Design Patterns](./python/patterns.md): A guide to the advanced Python patterns used in this codebase.

### [Popular Packages](./python/packages/overview.md)
Detailed guides on the core libraries powering our services:
- **SQLAlchemy**: Database ORM.
- **Loguru**: Structured logging.
- **Requests**: HTTP interactions.
- **Pandas & PyArrow**: Data analysis and high-performance storage.

### [Database Architecture](./database/timescaledb.md)
Information about **TimescaleDB**, our time-series database choice, how we manage schemas, and the use of Hypertables for financial data.
- [SQL vs. NoSQL](./database/sql-vs-nosql.md): Understand the fundamental differences and a reference for **Popular SQL Queries**.

### [Quality Assurance](./quality/testing.md)
Learn about our testing strategy, including unit tests, integration tests, and linting standards.

### [Infrastructure & DevOps](./infrastructure/docker.md)
Learn about **Docker**, why we use containerization, and a quick reference for **Popular Docker Commands**.     

### [Source Control & Workflow](./source-control/git.md)
Understand **Git**, our version control standard, and a quick reference for **Popular Git Commands**.
- [GitHub Overview](./source-control/github.md): Learn about our collaboration platform and the importance of Pull Requests.

### [API & Authentication](./api/overview.md)
An introduction to APIs, what an API Key is, and how to safely manage credentials in this project.
- [EODHD Client Architecture](./api/eodhd-client.md): Deep dive into our specialized financial data client.

---
*Last updated: April 11, 2026*
