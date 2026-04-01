# SEO Agent

Local-first SEO operations system focused on deterministic analysis, selective LLM use, and low-cost automation.

## Included in v0.1

- FastAPI control API
- Postgres schema via SQLAlchemy + Alembic
- Celery worker and scheduled job skeletons
- Core domain models for projects, pages, keywords, clusters, briefs, drafts, jobs, issues, and artifacts
- Technical audit, scoring, clustering, decay, and cannibalization service stubs
- LLM routing/caching contracts for future selective model use

## Quick start

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env` and adjust values.
3. For Postgres, run database migrations. For SQLite dev fallback, bootstrap the schema.
4. Start the API and worker.

## Commands

```bash
uvicorn app.main:app --reload
celery -A app.workers.celery_app.celery_app worker -Q critical,standard,bulk --loglevel=info
python -m app.scheduler.cron
alembic upgrade head
python -m app.bootstrap_db
```

## Local dev fallback

If Postgres and Redis are not available locally, you can use:

```bash
DATABASE_URL=sqlite:///./seo_agent.db
CELERY_TASK_ALWAYS_EAGER=true
```

Then initialize the schema with:

```bash
python -m app.bootstrap_db
```

With `CELERY_TASK_ALWAYS_EAGER=true`, enqueue endpoints execute synchronously in-process, which is useful for local verification before Redis is available.

## Currently working

- Create projects
- Upload crawl CSV artifacts
- Ingest crawl pages into the `pages` table
- Upload GSC CSV artifacts
- Ingest query/page performance into `query_metrics_daily`
- Run deterministic technical audits
- Compute first-pass SEO opportunities from crawl + GSC signals
- Group related opportunities into cluster-level planning units
- Generate deterministic SEO briefs from prioritized opportunity clusters
- Generate constrained drafts from opportunity briefs with QA metadata
- Review drafts with a publish gate and explicit revision requirements
- Generate revised draft versions from review feedback and re-run the gate
- Attach evidence to briefs so review failures can be resolved and drafts can clear the gate
- Persist and inspect issues
- Persist and inspect job lifecycle state through `/jobs` endpoints

## CSV inputs supported right now

### Crawl CSV

Expected columns are compatible with Screaming Frog-style exports:
- `Address`
- `Title 1`
- `H1-1`
- `Meta Robots 1`
- `Canonical Link Element 1`
- `Status Code`
- `Indexability`
- `Word Count`

### GSC CSV

Expected columns:
- `Query`
- `Page`
- `Date`
- `Clicks`
- `Impressions`
- `CTR`
- `Position`

## Next implementation targets

- Real GSC and crawl ingestion
- Technical audit rule implementations
- Opportunity scoring
- Keyword clustering
- SERP analysis and brief generation pipeline
