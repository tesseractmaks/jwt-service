import os
import time
from datetime import datetime, timedelta

from crud import (
    create_refresh_db,
    delete_refresh_db,
    read_refresh_by_name_db,
    read_refresh_by_user_name_db,
    read_user_by_username_db,
)
from db.db_helper import db_helper
from dotenv import load_dotenv
from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from schemas import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

# SECRET_KEY = os.getenv('SECRET_KEY')
SECRET_KEY = "$2b$12$cZmHQ5w9KXng0Q/XWCn4ReMfPh5JqwzpI6oaEY/XS1ERCHSbJceC."
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 14
REFRESH_TOKEN_EXPIRE_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(
    username: str, password: str, session: AsyncSession
) -> UserSchema | bool:
    user = await read_user_by_username_db(session=session, username=username)

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def check_refresh(refresh_token: str, session: AsyncSession) -> bool:
    if refresh_token:
        refresh_key = await read_refresh_by_name_db(
            session=session, refresh_name=refresh_token["body"]
        )
        unix_time = time.mktime(datetime.utcnow().timetuple())
        if refresh_key:
            if refresh_token["exp"] > unix_time:
                return True
            await delete_refresh_db(session=session, refresh=refresh_key)
            return False
        return False


async def get_username(
    refresh_token: str | None = Cookie(default=None),
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not validate credentials",
        headers={"WWW-Authenticate": "Bearer "},
    )

    try:
        refresh_token_clean = str(refresh_token).replace("Bearer ", "")
        payload = jwt.decode(refresh_token_clean, SECRET_KEY, algorithms=[ALGORITHM])
        refresh_token = {"body": str(refresh_token_clean), "exp": payload.get("exp")}
        refresh_key = await check_refresh(session=session, refresh_token=refresh_token)
        username: str = payload.get("sub")
        if not refresh_key:
            return False
        return username
    except JWTError:
        raise credential_exception


async def get_current_active_user(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    username: UserSchema = Depends(get_username),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):

    current_user = await read_user_by_username_db(session=session, username=username)
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    await create_token(
        data={"sub": current_user.email},
        session=session,
        response=response,
        refresh_token=refresh_token,
        flag=True,
    )
    return current_user


async def get_refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not validate credentials",
        headers={"WWW-Authenticate": "Bearer "},
    )

    if refresh_token:
        try:
            refresh_token_clean = str(refresh_token).replace("Bearer ", "")
            payload = jwt.decode(
                refresh_token_clean, SECRET_KEY, algorithms=[ALGORITHM]
            )
            refresh_token_ = {
                "body": str(refresh_token_clean),
                "exp": payload.get("exp"),
            }
            refresh_key = await check_refresh(
                session=session, refresh_token=refresh_token_
            )
            username: str = payload.get("sub")
            if not refresh_key:
                return False
        except JWTError:
            raise credential_exception

        jwt_access, new_refresh = await create_token(
            data={"sub": username},
            session=session,
            response=response,
            refresh_token=refresh_token,
            flag=True,
        )
        return new_refresh


async def get_current_active_user_admin(
    username: UserSchema = Depends(get_username),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    current_user = await read_user_by_username_db(session=session, username=username)
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_token(
    data: dict,
    session: AsyncSession,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    flag=False,
):

    tokens = {
        "access_expires": timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "refresh_expires": timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    }

    access_to_encode = data.copy()
    refresh_to_encode = data.copy()

    expire_access = datetime.utcnow() + tokens["access_expires"]
    expire_refresh = datetime.utcnow() + tokens["refresh_expires"]

    access_to_encode.update({"exp": expire_access})
    jwt_access = jwt.encode(access_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    refresh_to_encode.update({"exp": expire_refresh})
    jwt_refresh = jwt.encode(refresh_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    refresh_token_db = {
        "refresh": jwt_refresh,
        "exp": expire_refresh,
        "sub": data["sub"],
    }

    response.set_cookie(
        key="access_token", samesite=None, value=f"Bearer {jwt_access}", secure=True
    )
    response.set_cookie(
        key="refresh_token",
        samesite=None,
        value=f"Bearer {jwt_refresh}",
        secure=True,
        httponly=True,
    )
    if isinstance(refresh_token, dict):
        refresh_token = refresh_token["body"]
    if flag:
        refresh_token_clean = refresh_token.replace("Bearer ", "")
        refresh_key = await read_refresh_by_name_db(
            session=session, refresh_name=refresh_token_clean
        )
        await delete_refresh_db(session=session, refresh=refresh_key)
        await create_refresh_db(session=session, refresh_in=refresh_token_db)
        return jwt_access, jwt_refresh
    else:
        refresh_key = await read_refresh_by_user_name_db(
            session=session, username=data["sub"]
        )
        if refresh_key:
            if refresh_key.__dict__["exp"] < datetime.utcnow():
                await delete_refresh_db(session=session, refresh=refresh_key)
                await create_refresh_db(session=session, refresh_in=refresh_token_db)
                return jwt_access, jwt_refresh
        await create_refresh_db(session=session, refresh_in=refresh_token_db)
        return jwt_access, jwt_refresh
