import uuid

from models import RefreshKey
from schemas import RefreshKeySchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession


async def read_refresh_db(session: AsyncSession) -> list[RefreshKeySchema]:
    query = select(RefreshKey).order_by(RefreshKey.expired)
    result: AsyncResult = await session.execute(query)
    refreshes = result.scalars().all()
    return list(refreshes)


async def read_refresh_by_id_db(
    session: AsyncSession, refresh_id: uuid.uuid4
) -> RefreshKeySchema | None:
    return await session.get(RefreshKey, refresh_id)


async def create_refresh_db(
    session: AsyncSession,
    refresh_in: dict,
) -> RefreshKey:
    refresh = RefreshKey(**refresh_in)
    session.add(refresh)
    await session.commit()
    return refresh_in


async def read_refresh_by_name_db(
    session: AsyncSession, refresh_name: str
) -> RefreshKeySchema | None:
    query = select(RefreshKey).where(RefreshKey.refresh == refresh_name)
    result: AsyncResult = await session.execute(query)
    name = result.unique().scalar()
    return name


async def read_refresh_by_user_name_db(
    session: AsyncSession, username: str
) -> RefreshKeySchema | None:
    query = select(RefreshKey).where(RefreshKey.sub == username)
    result: AsyncResult = await session.execute(query)
    name = result.unique().scalar()
    return name


async def update_refresh_db(
    session: AsyncSession,
    refresh: RefreshKeySchema,
    refresh_update: dict,
    partial: bool = True,
) -> RefreshKeySchema:
    refresh_update = RefreshKeySchema(**refresh_update)
    for name, value in refresh_update.model_dump(exclude_unset=partial).items():
        setattr(refresh, name, value)
    await session.commit()
    return refresh_update


async def delete_refresh_db(session: AsyncSession, refresh: RefreshKeySchema) -> None:
    await session.delete(refresh)
    await session.commit()
