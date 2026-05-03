from datetime import date, datetime

from loguru import logger
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import URL as PG_URL
from sqlalchemy.orm import sessionmaker

from .models import (
    Base,
    Exchange,
    MarketNews,
    StockAdjusted,
    StockDividends,
    StockEOD,
    StockSplits,
)


class DBClient:
    """
    Database client for managing stock data in a PostgreSQL database using SQLAlchemy.
    """

    def __init__(self, dbname: str, user: str, password: str, host: str, port: int):
        """
        Initializes the database client and creates an engine session.

        Args:
            dbname (str): Name of the database.
            user (str): Database user.
            password (str): Database password.
            host (str): Database host.
            port (int): Database port.
        """
        self.db_url = PG_URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host=host,
            port=port,
            database=dbname,
        )

        self.engine = create_engine(self.db_url)
        self._session = sessionmaker(bind=self.engine)

        # Ensure all tables defined in models are created in the database
        Base.metadata.create_all(self.engine)

        logger.info(f"DBClient initialized with database URL: {self.db_url}")

    def insert_stock_data(
        self,
        bus_date: date,
        symbol: str,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        adjusted_close_price: float,
        volume: int,
    ) -> bool:
        """
        Inserts or updates End-Of-Day (EOD) stock data.

        Args:
            bus_date (date): The business date.
            symbol (str): The ticker symbol.
            open_price (float): Opening price.
            high_price (float): Highest price.
            low_price (float): Lowest price.
            close_price (float): Closing price.
            adjusted_close_price (float): Adjusted closing price.
            volume (int): Trading volume.
        """
        with self._session() as session:
            try:
                stock_eod = StockEOD(
                    bus_date=bus_date,
                    symbol=symbol,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    adjusted_close=adjusted_close_price,
                    volume=volume,
                )
                session.merge(stock_eod)  # Use merge for ON CONFLICT (upsert) behavior
                session.commit()
                logger.debug(f"Inserted/Updated data for {symbol} at {bus_date}.")
                return True
            except Exception as e:
                session.rollback()
                logger.error(
                    f"Error inserting stock data for {symbol} at {bus_date}: {e}"
                )
                return False

    def insert_stock_adjusted_data(
        self,
        bus_date: date,
        symbol: str,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        adjusted_close_price: float,
        volume: int,
    ) -> bool:
        """
        Inserts or updates adjusted stock data.

        Args:
            bus_date (date): The business date.
            symbol (str): The ticker symbol.
            open_price (float): Opening price.
            high_price (float): Highest price.
            low_price (float): Lowest price.
            close_price (float): Closing price.
            adjusted_close_price (float): Adjusted closing price.
            volume (int): Trading volume.
        """
        with self._session() as session:
            try:
                stock_adjusted = StockAdjusted(
                    bus_date=bus_date,
                    symbol=symbol,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    adjusted_close=adjusted_close_price,
                    volume=volume,
                )
                session.merge(stock_adjusted)
                session.commit()
                logger.debug(
                    f"Inserted/Updated adjusted stock data for {symbol} at {bus_date}."
                )
                return True
            except Exception as e:
                session.rollback()
                logger.error(
                    f"Error inserting adjusted stock data for {symbol} at {bus_date}: {e}"
                )
                return False

    def get_stock_data(self, symbol: str, limit: int = 2) -> list[StockEOD] | None:
        """
        Retrieves EOD stock data for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            limit (int, optional): Maximum number of rows to return. Defaults to 2.

        Returns:
            list[StockEOD] | None: A list of StockEOD objects or None if an error occurs.
        """
        with self._session() as session:
            try:
                results = (
                    session.query(StockEOD)
                    .filter_by(symbol=symbol)
                    .order_by(StockEOD.bus_date.desc())
                    .limit(limit)
                    .all()
                )
                logger.debug(f"Query for {symbol} returned {len(results)} rows.")
                return results
            except Exception as e:
                session.rollback()
                logger.error(f"Error querying stock data for {symbol}: {e}")
                return None

    def get_stock_adjusted_data(
        self, symbol: str, limit: int = 2
    ) -> list[StockAdjusted] | None:
        """
        Retrieves adjusted stock data for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            limit (int, optional): Maximum number of rows to return. Defaults to 2.

        Returns:
            list[StockAdjusted] | None: A list of StockAdjusted objects or None if an error occurs.
        """
        with self._session() as session:
            try:
                results = (
                    session.query(StockAdjusted)
                    .filter_by(symbol=symbol)
                    .order_by(StockAdjusted.bus_date.desc())
                    .limit(limit)
                    .all()
                )
                logger.debug(f"Query for {symbol} returned {len(results)} rows.")
                return results
            except Exception as e:
                session.rollback()
                logger.error(f"Error querying adjusted stock data for {symbol}: {e}")
                return None

    def insert_stock_dividends_data(
        self,
        bus_date: date,
        symbol: str,
        declaration_bus_date: date,
        record_bus_date: date,
        payment_bus_date: date,
        period: str,
        value: float,
        unadjusted_value: float,
        currency: str,
    ) -> bool:
        """
        Inserts or updates stock dividend data.

        Args:
            bus_date (date): Ex-dividend date.
            symbol (str): The ticker symbol.
            declaration_bus_date (date): Date dividend was declared.
            record_bus_date (date): Date of record.
            payment_bus_date (date): Date of payment.
            period (str): Dividend period (e.g., 'Quarterly').
            value (float): Dividend value.
            unadjusted_value (float): Unadjusted dividend value.
            currency (str): Currency code.
        """
        with self._session() as session:
            try:
                stock_dividends = StockDividends(
                    bus_date=bus_date,
                    symbol=symbol,
                    declaration_bus_date=declaration_bus_date,
                    record_bus_date=record_bus_date,
                    payment_bus_date=payment_bus_date,
                    period=period,
                    value=value,
                    unadjusted_value=unadjusted_value,
                    currency=currency,
                )
                session.merge(stock_dividends)
                session.commit()
                logger.debug(
                    f"Inserted/Updated dividends data for {symbol} at {bus_date}."
                )
                return True
            except Exception as e:
                session.rollback()
                logger.error(
                    f"Error inserting dividends data for {symbol} at {bus_date}: {e}"
                )
                return False

    def get_stock_dividends_data(
        self, symbol: str, limit: int = 2
    ) -> list[StockDividends] | None:
        """
        Retrieves dividend data for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            limit (int, optional): Maximum number of rows to return. Defaults to 2.

        Returns:
            list[StockDividends] | None: A list of StockDividends objects or None if an error occurs.
        """
        with self._session() as session:
            try:
                results = (
                    session.query(StockDividends)
                    .filter_by(symbol=symbol)
                    .order_by(StockDividends.bus_date.desc())
                    .limit(limit)
                    .all()
                )
                logger.debug(f"Query for {symbol} returned {len(results)} rows.")
                return results
            except Exception as e:
                session.rollback()
                logger.error(f"Error querying dividends stock data for {symbol}: {e}")
                return None

    def insert_stock_splits_data(
        self,
        bus_date: date,
        symbol: str,
        split: str,
    ) -> bool:
        """
        Inserts or updates stock split data.

        Args:
            bus_date (date): The date of the split.
            symbol (str): The ticker symbol.
            split (str): Split ratio (e.g., '2:1').
        """
        with self._session() as session:
            try:
                stock_splits = StockSplits(
                    bus_date=bus_date,
                    symbol=symbol,
                    split=split,
                )
                session.merge(stock_splits)
                session.commit()
                logger.debug(
                    f"Inserted/Updated splits data for {symbol} at {bus_date}."
                )
                return True
            except Exception as e:
                session.rollback()
                logger.error(
                    f"Error inserting splits stock data for {symbol} at {bus_date}: {e}"
                )
                return False

    def get_stock_splits_data(
        self, symbol: str, limit: int = 2
    ) -> list[StockSplits] | None:
        """
        Retrieves stock split data for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            limit (int, optional): Maximum number of rows to return. Defaults to 2.

        Returns:
            list[StockSplits] | None: A list of StockSplits objects or None if an error occurs.
        """
        with self._session() as session:
            try:
                results = (
                    session.query(StockSplits)
                    .filter_by(symbol=symbol)
                    .order_by(StockSplits.bus_date.desc())
                    .limit(limit)
                    .all()
                )
                logger.debug(f"Query for {symbol} returned {len(results)} rows.")
                return results
            except Exception as e:
                session.rollback()
                logger.error(f"Error querying splits stock data for {symbol}: {e}")
                return None

    def insert_market_news(
        self,
        date: datetime,
        title: str,
        content: str,
        link: str,
        symbols: list[str],
        tags: list[str],
    ) -> bool:
        """Inserts or updates market news."""
        with self._session() as session:
            try:
                news = MarketNews(
                    date=date,
                    title=title,
                    content=content,
                    link=link,
                    symbols=symbols,
                    tags=tags,
                )
                session.merge(news)
                session.commit()
                logger.debug(f"Inserted/Updated news: {title}.")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error inserting news: {title}: {e}")
                return False

    def insert_exchange_data(
        self,
        code: str,
        name: str,
        country: str,
        currency: str,
        operating_mic: str | None,
        country_iso2: str | None,
        country_iso3: str | None,
    ) -> bool:
        """
        Inserts or updates exchange data.

        Args:
            code (str): Exchange code.
            name (str): Exchange name.
            country (str): Country name.
            currency (str): Currency code.
            operating_mic (str | None): Operating MIC.
            country_iso2 (str | None): ISO2 country code.
            country_iso3 (str | None): ISO3 country code.
        """
        with self._session() as session:
            try:
                exchange = Exchange(
                    code=code,
                    name=name,
                    country=country,
                    currency=currency,
                    operating_mic=operating_mic,
                    country_iso2=country_iso2,
                    country_iso3=country_iso3,
                )
                session.merge(exchange)
                session.commit()
                logger.debug(f"Inserted/Updated exchange: {name} ({code}).")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error inserting exchange {code}: {e}")
                return False

    def bulk_upsert(self, objects: list[Base]) -> bool:
        """
        Performs a high-performance bulk upsert of multiple objects using
        PostgreSQL's INSERT ... ON CONFLICT DO UPDATE syntax.

        Args:
            objects (list[Base]): List of SQLAlchemy model instances.
        """
        if not objects:
            return True

        # Assume all objects in the list are of the same type (same table)
        model_class = type(objects[0])

        # Extract data from objects into a list of dictionaries
        data = []
        for obj in objects:
            # Use inspector to get column names and current values
            mapper = inspect(model_class)
            data.append(
                {
                    col.key: getattr(obj, col.key)
                    for col in mapper.attrs
                    if hasattr(obj, col.key)
                }
            )

        with self.engine.connect() as conn:
            try:
                # 1. Create the base INSERT statement
                stmt = pg_insert(model_class).values(data)

                # 2. Identify Primary Key columns for the index_elements
                pk_columns = [col.name for col in inspect(model_class).primary_key]

                # 3. Identify columns to update (all non-PK columns)
                update_columns = {
                    col.name: stmt.excluded[col.name]
                    for col in inspect(model_class).columns
                    if not col.primary_key
                }

                # 4. Construct the UPSERT statement
                upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=pk_columns, set_=update_columns
                )

                # 5. Execute and commit
                conn.execute(upsert_stmt)
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                logger.error(
                    f"Error during optimized bulk upsert for {model_class.__tablename__}: {e}"
                )
                return False
