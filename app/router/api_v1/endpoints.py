from fastapi import APIRouter
from app.users.api import router as user_router

api_router = APIRouter()

include_api = api_router.include_router
routers = (
    (user_router, "users", "users"),
)

for router_item in routers:
    router, prefix, tag = router_item

    if tag:
        include_api(router, prefix=f"/{prefix}", tags=[tag])
    else:
        include_api(router, prefix=f"/{prefix}")
