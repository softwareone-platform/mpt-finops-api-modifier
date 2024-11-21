from fastapi import APIRouter

from app.datasources.api import router as datasource_router
from app.organizations.api import router as org_router
from app.users.api import router as user_router

api_router = APIRouter()

include_api = api_router.include_router
routers = (
    (user_router, "users", "users"),
    (org_router, "organizations", "organizations"),
    (datasource_router, "datasource", "datasource"),

)

for router_item in routers:
    router, prefix, tag = router_item

    if tag:
        include_api(router, prefix=f"/{prefix}", tags=[tag])
    else:
        include_api(router, prefix=f"/{prefix}")
