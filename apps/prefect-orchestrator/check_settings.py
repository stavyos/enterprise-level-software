import asyncio

from prefect.settings import (
    PREFECT_API_DATABASE_CONNECTION_URL,
    PREFECT_API_URL,
    PREFECT_HOME,
)


async def check_settings():
    print(f"DEBUG: PREFECT_API_URL = {PREFECT_API_URL.value()}")
    print(f"DEBUG: PREFECT_HOME = {PREFECT_HOME.value()}")
    print(
        f"DEBUG: PREFECT_API_DATABASE_CONNECTION_URL = {PREFECT_API_DATABASE_CONNECTION_URL.value()}"
    )


if __name__ == "__main__":
    asyncio.run(check_settings())
