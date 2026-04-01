from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audits, briefs, clustering, clusters, health, ingestion, internal_links, jobs, opportunity_briefs, opportunity_drafts, opportunity_evidence, opportunity_publications, opportunity_revisions, opportunity_reviews, projects, publisher_configs, refresh, scoring
from app.logging import configure_logging

configure_logging()

app = FastAPI(title="SEO Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(publisher_configs.router)
app.include_router(ingestion.router)
app.include_router(audits.router)
app.include_router(clusters.router)
app.include_router(clustering.router)
app.include_router(briefs.router)
app.include_router(internal_links.router)
app.include_router(opportunity_briefs.router)
app.include_router(opportunity_drafts.router)
app.include_router(opportunity_evidence.router)
app.include_router(opportunity_publications.router)
app.include_router(opportunity_reviews.router)
app.include_router(opportunity_revisions.router)
app.include_router(refresh.router)
app.include_router(scoring.router)
app.include_router(jobs.router)
