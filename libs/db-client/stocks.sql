CREATE EXTENSION IF NOT EXISTS timescaledb;
DROP TABLE IF EXISTS exchanges;
CREATE TABLE exchanges (
	code TEXT NOT NULL,
	name TEXT,
	country TEXT,
	currency TEXT,
	operating_mic TEXT,
	country_iso2 TEXT,
	country_iso3 TEXT,
	PRIMARY KEY (code)
);
DROP TABLE IF EXISTS market_news;
CREATE TABLE market_news (
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	title TEXT NOT NULL,
	content TEXT,
	link TEXT,
	symbols JSON,
	tags JSON,
	PRIMARY KEY (date, title)
);
SELECT create_hypertable('market_news', 'date', if_not_exists => TRUE);
DROP TABLE IF EXISTS stock_adjusted;
CREATE TABLE stock_adjusted (
	bus_date DATE NOT NULL,
	symbol TEXT NOT NULL,
	open FLOAT,
	high FLOAT,
	low FLOAT,
	close FLOAT,
	adjusted_close FLOAT,
	volume INTEGER,
	PRIMARY KEY (bus_date, symbol)
);
SELECT create_hypertable('stock_adjusted', 'bus_date', if_not_exists => TRUE);
DROP TABLE IF EXISTS stock_dividends;
CREATE TABLE stock_dividends (
	bus_date DATE NOT NULL,
	symbol TEXT NOT NULL,
	declaration_bus_date DATE,
	record_bus_date DATE,
	payment_bus_date DATE,
	period TEXT,
	value FLOAT,
	unadjusted_value FLOAT,
	currency TEXT,
	PRIMARY KEY (bus_date, symbol)
);
SELECT create_hypertable('stock_dividends', 'bus_date', if_not_exists => TRUE);
DROP TABLE IF EXISTS stock_eod;
CREATE TABLE stock_eod (
	bus_date DATE NOT NULL,
	symbol TEXT NOT NULL,
	open FLOAT,
	high FLOAT,
	low FLOAT,
	close FLOAT,
	adjusted_close FLOAT,
	volume INTEGER,
	PRIMARY KEY (bus_date, symbol)
);
SELECT create_hypertable('stock_eod', 'bus_date', if_not_exists => TRUE);
DROP TABLE IF EXISTS stock_splits;
CREATE TABLE stock_splits (
	bus_date DATE NOT NULL,
	symbol TEXT NOT NULL,
	split TEXT,
	PRIMARY KEY (bus_date, symbol)
);
SELECT create_hypertable('stock_splits', 'bus_date', if_not_exists => TRUE);
