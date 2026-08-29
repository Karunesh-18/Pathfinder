import json
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure parent directory is in python path for ai_service import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.database import Base, engine, SessionLocal
from backend.models import Skill, SkillPrerequisite, Resource, ResourceSkill
from backend.routers import (
    chat, profile, recommend, path, progress, feedback, explain, dashboard
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(profile.router, prefix=settings.API_PREFIX)
app.include_router(recommend.router, prefix=settings.API_PREFIX)
app.include_router(path.router, prefix=settings.API_PREFIX)
app.include_router(progress.router, prefix=settings.API_PREFIX)
app.include_router(feedback.router, prefix=settings.API_PREFIX)
app.include_router(explain.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()

def seed_initial_data():
    """Populate database from data/ JSON fixtures if tables are empty."""
    db = SessionLocal()
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        skill_graph_path = os.path.join(data_dir, "skill_graph.json")
        resource_catalog_path = os.path.join(data_dir, "resource_catalog.json")

        if db.query(Skill).count() == 0 and os.path.exists(skill_graph_path):
            with open(skill_graph_path, "r", encoding="utf-8") as f:
                sg = json.load(f)
                domain = sg.get("domain", "Coding & Data Science")
                for s in sg.get("skills", []):
                    db.add(Skill(id=s["id"], domain=domain, name=s["name"]))
                for p in sg.get("prerequisites", []):
                    db.add(SkillPrerequisite(skill_id=p["skill_id"], prerequisite_id=p["prerequisite_id"]))
            db.commit()

        if db.query(Resource).count() == 0 and os.path.exists(resource_catalog_path):
            with open(resource_catalog_path, "r", encoding="utf-8") as f:
                rc = json.load(f)
                for r in rc:
                    res_obj = Resource(
                        id=r["id"],
                        domain=r.get("domain", "Coding & Data Science"),
                        title=r["title"],
                        provider=r.get("provider"),
                        url=r.get("url"),
                        description=r.get("description"),
                        difficulty=r.get("difficulty"),
                        est_hours=r.get("est_hours"),
                        format=r.get("format")
                    )
                    db.add(res_obj)
                    for sk in r.get("skills_addressed", []):
                        db.add(ResourceSkill(resource_id=r["id"], skill_id=sk))
            db.commit()
    except Exception as e:
        print(f"Data seeding warning: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
