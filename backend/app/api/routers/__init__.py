from fastapi import APIRouter
from app.api.routers.auth import router as auth_router
from app.api.routers.students import router as students_router
from app.api.routers.organizations import router as organizations_router
from app.api.routers.skills import router as skills_router
from app.api.routers.projects import router as projects_router
from app.api.routers.applications import router as applications_router
from app.api.routers.teams import router as teams_router
from app.api.routers.workspaces import router as workspaces_router
from app.api.routers.submissions import router as submissions_router
from app.api.routers.feedback import router as feedback_router
from app.api.routers.experience import router as experience_router
from app.api.routers.ai import router as ai_router
from app.api.routers.notifications import router as notifications_router
from app.api.routers.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(students_router)
api_router.include_router(organizations_router)
api_router.include_router(skills_router)
api_router.include_router(projects_router)
api_router.include_router(applications_router)
api_router.include_router(teams_router)
api_router.include_router(workspaces_router)
api_router.include_router(submissions_router)
api_router.include_router(feedback_router)
api_router.include_router(experience_router)
api_router.include_router(ai_router)
api_router.include_router(notifications_router)
api_router.include_router(admin_router)
