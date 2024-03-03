from typing import Annotated

from crud import read_user_by_id_db
from db.db_helper import db_helper
from fastapi import Depends, HTTPException, Path, status
from schemas import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession


async def user_by_id(
    user_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserSchema:

    user = await read_user_by_id_db(session=session, user_id=user_id)
    if user is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found...")
