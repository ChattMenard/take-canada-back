from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, func, select

from . import __version__, storage
from .config import settings
from .database import get_session, init_db
from .models import Entity, Evidence, Relationship_, TimelineEvent
from .routers import auth, entities, evidence, export, economic, relationships, seal, timeline, wealth_gap, historical_parallels, transparency, government_wealth
from .schemas import Stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    summary="Open-source engine for collecting and preserving tamper-evident public-record evidence.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evidence.router)
app.include_router(entities.router)
app.include_router(relationships.router)
app.include_router(timeline.router)
app.include_router(seal.router)
app.include_router(export.router)
app.include_router(economic.router)
app.include_router(wealth_gap.router)
app.include_router(historical_parallels.router)
app.include_router(transparency.router)
app.include_router(government_wealth.router)
app.include_router(auth.router)


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok", "version": __version__}


@app.get("/api/stats", response_model=Stats, tags=["meta"])
def stats(session: Session = Depends(get_session)):
    def count(model) -> int:
        return session.exec(select(func.count()).select_from(model)).one()

    return Stats(
        evidence_count=count(Evidence),
        entity_count=count(Entity),
        relationship_count=count(Relationship_),
        timeline_count=count(TimelineEvent),
        storage_bytes=storage.disk_usage_bytes(),
    )
