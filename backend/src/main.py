from src.core.application import create_app
from src.core.utils import init_day
from src.routers import (clients_router, advertisers_router, campaigns_router,
                         system_router, files_router, ads_router, stats_router)


app = create_app(
    routers=[
        clients_router,
        advertisers_router,
        campaigns_router,
        system_router,
        files_router,
        ads_router,
        stats_router
    ],
    startup_tasks=[
        init_day
    ],
    shutdown_tasks=[],
    ignoring_log_endpoints=[
        ("/system/ping", "GET"),
        ("/metrics", "GET")
    ],
    root_path=""
)