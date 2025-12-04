from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import  AsyncSession, create_async_engine
from app.core.dependencies import get_settings
from app.models.base import Base

settings = get_settings()

engine = create_async_engine(
    url = settings["DATABASE_URL"],
    echo = True,           
    future = True,
)

async def create_tables():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("created all tables")
        except Exception as e:
            print(f"{e}")

async def drop_tables():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
            print("dropped all tables")
        except Exception as e:
            print(f"{e}")

async def commit_to_db(session: AsyncSession):
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error: {e.orig}")
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
