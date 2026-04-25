import asyncio

from prefect import get_client


async def main():
    async with get_client() as client:
        runs = await client.read_flow_runs(limit=200)
        for r in runs:
            print(f"{r.id} | {r.state_name} | {r.name}")


if __name__ == "__main__":
    asyncio.run(main())
