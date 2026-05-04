from typing import Any

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable, DropIndex, DropTable

from db_client.models.news import MarketNews
from db_client.models.stocks import (
    Base,
    Exchange,
    StockAdjusted,
    StockDividends,
    StockEOD,
    StockSplits,
    Ticker,
)


def generate_all_tables_sql(base: Any) -> str:
    """
    Generates SQL statements for creating all tables defined in the SQLAlchemy Base metadata.
    Includes TimescaleDB extension and hypertable creation for specific tables.

    Args:
        base (Any): The SQLAlchemy declarative base containing metadata.

    Returns:
        str: A string containing the full SQL script.
    """
    tables_sql = ["CREATE EXTENSION IF NOT EXISTS timescaledb;"]

    dialect = postgresql.dialect()  # engine.dialect

    sorted_tables = base.metadata.sorted_tables

    # Iterate over all tables in the metadata
    # The highlighted line in the image has a condition to exclude views
    for table in [
        t for t in sorted_tables if "view" not in t.name and "View" not in t.name
    ]:
        # Generate DROP TABLE IF EXISTS statement
        drop_table_sql = (
            str(DropTable(table, if_exists=True).compile(dialect=dialect)).strip() + ";"
        )
        tables_sql.append(drop_table_sql)

        # Generate CREATE TABLE statement
        create_table_sql = (
            str(CreateTable(table).compile(dialect=dialect)).strip() + ";"
        )
        tables_sql.append(create_table_sql)

        # Generate CREATE HYPERTABLE statement for TimescaleDB
        if table.name in [
            StockEOD.__tablename__,
            StockAdjusted.__tablename__,
            StockDividends.__tablename__,
            StockSplits.__tablename__,
        ]:
            tables_sql.append(
                f"SELECT create_hypertable('{table.name}', 'bus_date', if_not_exists => TRUE);"
            )
        elif table.name == MarketNews.__tablename__:
            tables_sql.append(
                f"SELECT create_hypertable('{table.name}', 'date', if_not_exists => TRUE);"
            )

        # Iterate over all indexes of the table
        for index in table.indexes:
            drop_index_sql = (
                str(DropIndex(index, if_exists=True).compile(dialect=dialect)).strip()
                + ";"
            )
            tables_sql.append(drop_index_sql)

            # create_index_sql = str(index.compile(dialect=engine.dialect)).strip() + ';'
            create_index_sql = (
                str(CreateIndex(index).compile(dialect=dialect)).strip() + ";"
            )
            tables_sql.append(create_index_sql)

    return "\n".join(tables_sql)


def generate(
    base: Any,
    save: bool = True,
    file_name: str | None = None,
) -> str:
    """
    Generates and optionally saves the SQL schema to a file.

    Args:
        base (Any): The SQLAlchemy declarative base.
        save (bool, optional): Whether to save the output to a file. Defaults to True.
        file_name (str | None, optional): The name of the file to save to. Defaults to None.

    Returns:
        str: The generated SQL script.
    """
    sql = generate_all_tables_sql(base=base)

    if save:
        with open(file_name, "w") as f:
            f.write(sql)

    return sql


if __name__ == "__main__":
    generate(base=Base, file_name="stocks.sql")

