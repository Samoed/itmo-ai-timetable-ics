from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from itmo_ai_timetable.settings import Settings


class SessionManager:
    _instance: Optional["SessionManager"] = None
    _engine: AsyncEngine | None = None
    _session_maker: async_sessionmaker[AsyncSession] | None = None

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        settings = Settings()
        self._engine = create_async_engine(settings.database_uri, echo=True, future=True)
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError("SessionManager not initialized")
        return self._session_maker

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("SessionManager not initialized")
        return self._engine


def with_async_session(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        session_maker = SessionManager().session_maker
        async with session_maker() as session:
            try:
                return await func(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return wrapper
