from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings


DATABASE_URL = settings.DATABASE_URI

engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=0)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
