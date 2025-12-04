#chạy file này để xóa hết bảng
import asyncio
from app.services.utils import drop_tables

if __name__ == "__main__":
    asyncio.run(drop_tables())