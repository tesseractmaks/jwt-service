import json
import uuid

from auth import get_current_active_user, get_refresh_token
from core import logger
from crud import (
    create_user_db,
    delete_user_db,
    read_user_by_username_db,
    read_users_db,
    update_user_db,
)
from db import db_helper
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from passlib.context import CryptContext
from schemas import (
    UserCreateSchema,
    UserResponseSchema,
    UserSchema,
    UserUpdatePartialSchema,
    UserUpdateSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .depends_endps import user_by_id

router = APIRouter(tags=["Users"])


@logger.catch
@router.get("/", response_model=list[UserResponseSchema])
async def read_users(
    response: Response,
    access_token: str | None = Cookie(default=None),
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    logger.info("message success")
    users = await read_users_db(session=session)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            headers={"X-Error": "Url format wrong"},
        )
    return users


@logger.catch
@router.get("/{user_id}/", response_model=UserResponseSchema)
async def read_user_by_id(
    refresh=Depends(get_refresh_token), user: UserSchema = Depends(user_by_id)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            headers={"X-Error": "Url format wrong"},
        )
    return user


@logger.catch
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    user = await read_user_by_username_db(session=session, username=user_in.email)
    if user:
        await delete_user_db(user=user, session=session)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user_in.password = pwd_context.hash(user_in.password)
    user_in = UserCreateSchema(**user_in.__dict__)
    if user_in is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"X-Error": "Empty data"},
        )
    return await create_user_db(session=session, user_in=user_in)


@logger.catch
@router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_update: UserUpdateSchema,
    user: UserSchema = Depends(user_by_id),
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    if user_update is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"X-Error": "Empty data"},
        )
    return await update_user_db(session=session, user=user, user_update=user_update)


@logger.catch
@router.patch("/", response_model=UserResponseSchema)
async def update_user_partial(
    user_update: UserUpdatePartialSchema,
    user: UserSchema = Depends(user_by_id),
    current_user=Depends(get_refresh_token),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            headers={"X-Error": "Empty data"},
        )

    return await update_user_db(
        session=session, user=user, user_update=user_update, partial=True
    )


@logger.catch
@router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: UserSchema = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            headers={"X-Error": "Url format wrong"},
        )
    await delete_user_db(user=user, session=session)


@logger.catch
@router.patch("/admin_privilege", response_model=UserUpdatePartialSchema)
async def grant_admin_privilege(
    current_user=Depends(get_refresh_token),
    user: UserSchema = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if not current_user.is_super_admin and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.id == user.id:
        raise HTTPException(
            status_code=400, detail="Can not manage privileges of itself"
        )
    if user.is_admin or user.is_super_admin:
        raise HTTPException(
            status_code=409,
            detail=f"User with id {user.id} already promoted to admin/super admin",
        )
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id not found")
    updated_user_params = {"roles": user.add_admin_privileges_to_model()}
    updated_user_id = await update_user_db(
        session=session,
        user=user,
        user_update=UserUpdatePartialSchema(**updated_user_params),
        partial=True,
    )
    return updated_user_id


@logger.catch
@router.delete("/admin_privilege", response_model=UserResponseSchema)
async def revoke_admin_privilege(
    user: UserSchema = Depends(user_by_id),
    current_user=Depends(get_refresh_token),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    if not current_user.is_super_admin:
        try:
            raise HTTPException(status_code=403, detail="Forbidden.")
        except:
            pass
    if not current_user.is_super_admin and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.id == user.id:
        raise HTTPException(
            status_code=400, detail="Can not manage privileges of itself"
        )
    if not user.is_admin or user.is_super_admin:
        raise HTTPException(
            status_code=409,
            detail=f"User with id {user.id} already promoted to admin/super admin",
        )
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id  not found")
    updated_user_params = {"roles": user.remove_admin_privileges_from_model()}
    updated_user_id = await update_user_db(
        session=session,
        user=user,
        user_update=UserUpdatePartialSchema(**updated_user_params),
        partial=True,
    )

    return updated_user_id


class ConnectionManager:
    def __init__(self):
        self.active_connection: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        id_client = str(uuid.uuid4())
        self.active_connection[id_client] = websocket

    async def get_id(self, websocket: WebSocket):
        return websocket

    async def disconnect(self, websocket: WebSocket):
        id_client = await self.get_id(websocket)
        del self.active_connection[id_client]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, websocket: WebSocket, data: str):

        decoded_data = json.loads(data)
        for connection in self.active_connection.values():
            is_me = False
            if connection == websocket:
                is_me = True
            await connection.send_text(
                json.dumps(
                    {
                        "is_me": is_me,
                        "message": decoded_data["message"],
                        "username": decoded_data["username"],
                    }
                )
            )


manager = ConnectionManager()


@logger.catch
@router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = "1",
):
    await manager.connect(websocket)

    if client_id is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(websocket, data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
