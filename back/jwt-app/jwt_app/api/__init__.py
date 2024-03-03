from fastapi import APIRouter

from .api_v1.endpoints.token import router as token_router
from .api_v1.endpoints.user import router as user_router

router = APIRouter()
router_token = APIRouter()
router.include_router(router=user_router, prefix="/users")
router_token.include_router(router=token_router, prefix="/token")