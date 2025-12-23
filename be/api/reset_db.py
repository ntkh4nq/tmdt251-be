import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.utils import drop_tables, create_tables

if __name__ == "__main__":

    async def main():
        await drop_tables()
        await create_tables()

    asyncio.run(main())
