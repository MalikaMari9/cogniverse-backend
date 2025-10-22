from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import init_db
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.middleware.logging_middleware import LoggingMiddleware #added for logging middleware
from app.db.database import get_db
from app.db.seed.access_control_seed import seed_access_controls
from app.db.seed.config_seed import seed_configs
from app.db.seed.maintenance_seed import seed_maintenance

init_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# --- CORS (temporary open; restrict later) ---
origins = [

    "http://localhost:5173",   # Vite frontend
    "http://127.0.0.1:5173",
]

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

# -----------------------------------------------
# ✅ CONFIG DEBUG: Test DB connection + config fetch
# -----------------------------------------------
from app.db.database import get_db
from app.services.utils.config_helper import get_config_value
from sqlalchemy.orm import Session

@app.on_event("startup")
def debug_config_startup():
    print("🧩 [CONFIG DEBUG] Checking config_tbl values...")
    try:
        db: Session = next(get_db())
        company = get_config_value(db, "companyName", "DefaultName")
        access_exp = get_config_value(db, "accessTokenExpiryMinutes", "N/A")
        print(f"🧩 companyName = {company}")
        print(f"🧩 accessTokenExpiryMinutes = {access_exp}")
    except Exception as e:
        print(f"❌ CONFIG DEBUG ERROR: {e}")
    finally:
        db.close()


# 🆕 ADD THIS: Debug endpoint to test if users router is working
@app.get("/debug-routes")
def debug_routes():
    """List all registered routes to debug the 404 issue"""
    routes = []
    for route in app.routes:
        route_info = {
            "path": getattr(route, "path", "N/A"),
            "methods": getattr(route, "methods", "N/A"),
            "name": getattr(route, "name", "N/A")
        }
        routes.append(route_info)
    return {"registered_routes": routes}

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
    
# Mount static files directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 🆕 ADD THIS: Print debug info when routes are included
print("🔄 Registering routes...")

try:
    from app.routes import auth_routes
    app.include_router(auth_routes.router)
    print("✅ Auth routes registered")
except Exception as e:
    print(f"❌ Auth routes failed: {e}")

try:
    from app.routes import user_profile_routes
    app.include_router(user_profile_routes.router)
    print("✅ User profile routes registered")
except Exception as e:
    print(f"❌ User profile routes failed: {e}")

# ... rest of your route imports
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

from app.routes import maintenance_routes
app.include_router(maintenance_routes.router)

from app.routes import permissions_routes
app.include_router(permissions_routes.router)


print("🎯 All routes registered!")

# ✅ Seed default access control records (runs once at startup)
@app.on_event("startup")
def seed_defaults():
    try:
        db = next(get_db())
        seed_access_controls(db)
        seed_configs(db)
        seed_maintenance(db)
    except Exception as e:
        print(f"❌ Access Control seeding failed: {e}")
    finally:
        db.close()


@app.get("/debug-all-routes")
def debug_all_routes():
    """Debug endpoint to see ALL registered routes and methods"""
    routes_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "N/A")
            }
            routes_info.append(route_info)
    
    # Filter for /users/profile routes specifically
    profile_routes = [r for r in routes_info if "/users/profile" in r["path"]]
    
    return {
        "all_routes": routes_info,
        "profile_routes": profile_routes  # Focus on the problematic route
    }