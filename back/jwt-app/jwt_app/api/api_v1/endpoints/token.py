from auth import authenticate_user, create_token, get_refresh_token
from core import logger, make_ticket
from crud import (
    delete_refresh_db,
    delete_user_db,
    read_refresh_by_name_db,
    read_user_by_username_db,
)
from db import db_helper
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas import Token
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Token"])


@logger.catch
@router.post("/auth/logout")
async def logout_for_access_token(
    response: Response,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    refresh_token: str | None = Cookie(default=None),
):
    refresh_token_clean = refresh_token.replace("Bearer ", "")
    refresh_key = await read_refresh_by_name_db(
        session=session, refresh_name=refresh_token_clean
    )
    if refresh_key.__dict__["sub"] == "one@mail.ru1":
        user = await read_user_by_username_db(
            session=session, username=str(refresh_key.__dict__["sub"])
        )
        await delete_user_db(user=user, session=session)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    refresh_token_clean = str(refresh_token).replace("Bearer ", "")
    refresh_key = await read_refresh_by_name_db(
        session=session, refresh_name=refresh_token_clean
    )
    await delete_refresh_db(session=session, refresh=refresh_key)
    return {"access_token": ""}


@logger.catch
@router.post("/", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    if form_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"X-Error": "Empty data"},
        )

    user = await authenticate_user(
        form_data.username,
        form_data.password,
        session=session,
    )

    access_token, refresh_token = await create_token(
        data={"sub": user.email},
        session=session,
        response=response,
    )
    refr = refresh_token[len(refresh_token) - 10 :]
    img = make_ticket(str(refr))
    response = Response(content=img, media_type="image/jpeg")
    response.set_cookie(
        key="access_token", samesite=None, value=f"Bearer {access_token}", secure=True
    )
    response.set_cookie(
        key="refresh_token",
        samesite=None,
        value=f"Bearer {refresh_token}",
        secure=True,
        httponly=True,
    )
    return response


@router.get("/refresh")
async def refresh_token(
    num: str,
    jwt_refresh=Depends(get_refresh_token),
):
    refr = jwt_refresh[len(jwt_refresh) - 10 :]
    img = make_ticket(str(refr), num)
    response = Response(content=img, media_type="image/jpeg")
    response.set_cookie(
        key="refresh_token", samesite=None, value=f"Bearer {jwt_refresh}", httponly=True
    )
    return response
