"""Script for saving fundamental data."""

from datetime import date
import os
from eodhd_client.client import EODHDClientBase
from db_client.client import DBClient
from loguru import logger


def fundamentals_saver(updated_at: date, tickers: list[dict], run_id: str) -> None:
    """Core logic for saving fundamental data.

    Args:
        updated_at (date): The date the data was retrieved/updated.
        tickers (list[dict]): List of ticker dictionaries with 'symbol' and 'exchange'.
        run_id (str): Unique identifier for the run.
    """
    api_key = os.getenv("EODHD_API_KEY")
    client = EODHDClientBase(api_key).fundamentals
    
    db_client = DBClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    for ticker_info in tickers:
        symbol = ticker_info["symbol"]
        exchange = ticker_info["exchange"]
        try:
            data = client.get_fundamentals(symbol=symbol, exchange=exchange)
            if data:
                db_client.insert_fundamentals_data(
                    symbol=symbol,
                    exchange=exchange,
                    updated_at=updated_at,
                    general=data.get("General"),
                    highlights=data.get("Financials"),
                    valuation=data.get("MarketValuation"),
                    shares_stats=data.get("ShareholderData"),
                    technicals=data.get("TechnicalPerformance"),
                    splits_dividends=data.get("SplitsAndDividends"),
                    analyst_ratings=data.get("AnalystRatings"),
                    holders=data.get("InstitutionalHolders"),
                    insider_transactions=data.get("InsiderTransactions"),
                    earnings=data.get("Earnings"),
                    financials=data.get("FinancialReports"),
                )
        except Exception as e:
            logger.error(f"Error processing fundamentals for {symbol}: {e}")
