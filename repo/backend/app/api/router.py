from fastapi import APIRouter

from app.api.v1 import admin, audit, auth, declarations, deliveries, downloads, imports_exports, notifications, plans, profiles, reviews, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(declarations.router, prefix="/declarations", tags=["declarations"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["deliveries"])
api_router.include_router(downloads.router, prefix="/downloads", tags=["downloads"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(imports_exports.router, tags=["imports-exports"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
