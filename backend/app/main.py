from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.battery import router as battery_router
from app.api.routes.health import router as health_router
from app.api.routes.assets import router as assets_router


app = FastAPI(
    title="CogniCycle EV",
    description="AI-driven EV e-waste contextual triage platform",
    version="0.1.0",
)

# Enable CORS for the frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(battery_router)
app.include_router(assets_router)