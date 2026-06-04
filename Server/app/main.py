from fastapi import FastAPI

from app.api.admin.v1.users import router as admin_users_router
from app.api.health import router as health_router
from app.api.mobile.v1.app_bootstrap import router as app_bootstrap_router
from app.api.mobile.v1.auth import router as mobile_auth_router
from app.api.mobile.v1.chat import router as mobile_chat_router
from app.api.mobile.v1.date_events import router as mobile_date_events_router
from app.api.webhooks.v1.billing import router as billing_webhook_router
from app.config import Settings, get_settings
from app.logging import configure_logging
from app.middleware.request_id import RequestIdMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(app_settings)

    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        debug=app_settings.debug,
    )
    app.state.settings = app_settings

    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router)
    app.include_router(mobile_auth_router, prefix="/api/mobile/v1")
    app.include_router(app_bootstrap_router, prefix="/api/mobile/v1")
    app.include_router(mobile_chat_router, prefix="/api/mobile/v1")
    app.include_router(mobile_date_events_router, prefix="/api/mobile/v1")
    app.include_router(admin_users_router, prefix="/api/admin/v1")
    app.include_router(billing_webhook_router, prefix="/api/webhooks/v1")

    return app


app = create_app()
