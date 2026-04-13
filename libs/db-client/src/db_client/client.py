from datetime import date, datetime

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import URL as PG_URL
from sqlalchemy.orm import sessionmaker

from .models import (
    MarketNews,
    StockAdjusted,
    StockDividends,
    StockEOD,
    StockIntraday,
    StockSplits,
    TechnicalIndicator,
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
                logger.info(
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
                logger.info(
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

    def insert_stock_intraday_data(
        self,
        timestamp: int,
        symbol: str,
        bus_date: date,
        gmt_offset: int,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        volume: int,
    ) -> bool:
        """
        Inserts or updates intraday stock data.

        Args:
            timestamp (int): Unix timestamp.
            symbol (str): The ticker symbol.
            bus_date (date): The business date.
            gmt_offset (int): GMT offset in seconds.
            open_price (float): Opening price.
            high_price (float): Highest price.
            low_price (float): Lowest price.
            close_price (float): Closing price.
            volume (int): Trading volume.
        """
        with self._session() as session:
            try:
                stock_intraday = StockIntraday(
                    timestamp=timestamp,
                    symbol=symbol,
                    bus_date=bus_date,
                    gmt_offset=gmt_offset,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                )
                session.merge(stock_intraday)
                session.commit()
                logger.info(
                    f"Inserted/Updated intraday data for {symbol} at {bus_date}."
                )
                return True
            except Exception as e:
                session.rollback()
                logger.error(
                    f"Error inserting intraday stock data for {symbol} at {bus_date}: {e}"
                )
                return False

    def get_stock_intraday_data(
        self, symbol: str, limit: int = 2
    ) -> list[StockIntraday] | None:
        """
        Retrieves intraday stock data for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            limit (int, optional): Maximum number of rows to return. Defaults to 2.

        Returns:
            list[StockIntraday] | None: A list of StockIntraday objects or None if an error occurs.
        """
        with self._session() as session:
            try:
                results = (
                    session.query(StockIntraday)
                    .filter_by(symbol=symbol)
                    .order_by(StockIntraday.timestamp.desc())
                    .limit(limit)
                    .all()
                )
                logger.debug(f"Query for {symbol} returned {len(results)} rows.")
                return results
            except Exception as e:
                session.rollback()
                logger.error(f"Error querying intraday stock data for {symbol}: {e}")
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

    def insert_technical_indicator(
        self, bus_date: date, symbol: str, indicator_name: str, value: float
    ) -> bool:
        """Inserts or updates a technical indicator."""
        with self._session() as session:
            try:
                ti = TechnicalIndicator(
                    bus_date=bus_date,
                    symbol=symbol,
                    indicator_name=indicator_name,
                    value=value,
                )
                session.merge(ti)
                session.commit()
                logger.debug(
                    f"Inserted/Updated technical indicator {indicator_name} for {symbol}."
                )
                return True
            except Exception as e:
                session.rollback()
                logger.error(
                    f"Error inserting technical indicator {indicator_name} for {symbol}: {e}"
                )
                return False
