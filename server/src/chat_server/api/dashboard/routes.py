from fastapi.routing import APIRouter

from chat_server.api.dashboard import users


dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])
dashboard_router.include_router(users.router)
