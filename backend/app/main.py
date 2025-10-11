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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
