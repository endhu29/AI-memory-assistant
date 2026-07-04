import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import create_tables
from app.services.scheduler import start_scheduler

# ── Import all routers ────────────────────────────────────────────────
from app.routes.auth         import router as auth_router
from app.routes.dashboard    import router as dashboard_router
from app.routes.appointments import router as appointments_router
from app.routes.medicines    import router as medicines_router
from app.routes.health_log   import router as health_log_router
from app.routes.alerts       import router as alerts_router
from app.routes.profile      import router as profile_router
from app.routes.api          import router as api_router

# ── Create FastAPI app ────────────────────────────────────────────────
app = FastAPI(
    title="ElderCare Assistant",
    description="Elderly care web application — v1.0",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI (bonus — free with FastAPI!)
    redoc_url="/redoc",
)

# ── Static files & templates ──────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── Register all routers ──────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(appointments_router)
app.include_router(medicines_router)
app.include_router(health_log_router)
app.include_router(alerts_router)
app.include_router(profile_router)
app.include_router(api_router)

# ── Startup: create DB tables + start scheduler ───────────────────────
@app.on_event("startup")
def on_startup():
    create_tables()
    start_scheduler(app)
    print("✅ ElderCare Assistant started — http://localhost:8000")

# ── Error handlers ────────────────────────────────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Redirect unauthenticated users to login
    if exc.status_code == 401:
        return RedirectResponse(url="/login", status_code=302)
    if exc.status_code == 404:
        return templates.TemplateResponse("errors/404.html",
            {"request": request, "user": None}, status_code=404)
    return templates.TemplateResponse("errors/500.html",
        {"request": request, "user": None}, status_code=exc.status_code)


# ── Run directly ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)