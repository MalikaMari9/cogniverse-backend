from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import init_db

init_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# --- CORS (temporary open; restrict later) ---
origins = [
    "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # exact origins
    allow_credentials=True,         # ✅ needed for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simple root endpoint ---
@app.get("/")
def root():
    return {"message": f"{settings.app_name} v{settings.app_version} is running 🚀"}


# --- Optional: DB connectivity check endpoint ---
@app.get("/ping-db")
def ping_db():
    from sqlalchemy import text
    from db.database import engine
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()"))
            return {"status": "ok", "time": str(result.scalar())}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

from app.routes import auth_routes
app.include_router(auth_routes.router)

from app.routes import user_profile_routes
app.include_router(user_profile_routes.router)

from app.routes import project_routes
app.include_router(project_routes.router)

from app.routes import agent_routes
app.include_router(agent_routes.router)

from app.routes import projectagent_routes
app.include_router(projectagent_routes.router)

from app.routes import agentrelation_routes
app.include_router(agentrelation_routes.router)

from app.routes import scenario_routes
app.include_router(scenario_routes.router)

from app.routes import result_routes
app.include_router(result_routes.router)

from app.routes import system_log_routes
app.include_router(system_log_routes.router)

from app.routes import config_routes
app.include_router(config_routes.router)

from app.routes import contact_routes
app.include_router(contact_routes.router)

from app.routes import announcement_routes
app.include_router(announcement_routes.router)

from app.routes import notification_routes
app.include_router(notification_routes.router)

from app.routes import access_control_routes
app.include_router(access_control_routes.router)

from app.routes import revoked_token_routes
app.include_router(revoked_token_routes.router)

from app.routes import memory_routes
app.include_router(memory_routes.router)

from app.routes import weaver_routes
app.include_router(weaver_routes.router)