# ETL Service

The core data acquisition and processing engine powered by Prefect 3.x.

## Architecture: Dispatcher/Saver Pattern
To handle massive data requests (e.g., fetching years of intraday data for thousands of tickers), the service uses a two-tier flow architecture:

1.  **Dispatcher**: Orchestrates the work by splitting large requests into smaller, manageable chunks.
2.  **Saver**: Parallel worker jobs that perform the actual API calls and database persistence for a specific chunk.

This pattern allows for horizontal scaling across Kubernetes nodes.

## Available Flows
- `eod_saver_dispatcher`: Daily EOD data collection.
- `intraday_saver_dispatcher`: High-frequency data collection.
- `market_news_saver_dispatcher`: Financial news ingestion.
- `technical_indicators_saver_dispatcher`: Technical indicator calculation and storage.
- `bulk_data_saver_dispatcher`: National bulk data updates (EOD, Splits, Dividends).

## Deployment
Flows are automatically registered with Prefect using:
```bash
npx nx run etl-service:deploy
```

All flows are Kubernetes-ready with pre-configured resource requests and limits defined in `deployments_settings/`.
