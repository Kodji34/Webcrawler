# PyCrawler Research Studio

Phase 2 adds real scientific connectors on top of the Phase 1 foundation.

## Phase 2 scope

- official scientific source search through Crossref, OpenAlex, PubMed, and HAL
- normalized metadata retrieval through a connector-based backend architecture
- FR/EN scientific search UI with filters, preview, multi-selection, and local import
- local single-user persistence for launched queries and imported records

## Explicitly out of scope

- PDF or OCR extraction
- social media connectors
- advanced corpus cleaning
- advanced IRaMuTeQ exports
- phases 3 to 6

## Supported sources

- Crossref REST API
- OpenAlex API
- PubMed E-utilities
- HAL search API

## Normalized result model

Each scientific result exposes:

- `source`
- `title`
- `authors`
- `publication_date`
- `url`
- `language`
- `document_type`
- `doi`
- `pmid` when available
- `abstract` when available
- `journal` or venue when available
- `keyword_used`

## Search parameters

The backend and UI support:

- keyword or simple query
- selected source
- max results
- date range where the source supports it
- language where the source supports it
- DOI, PMID, or source-specific identifier where the source supports it

## API endpoints

- `GET /api/v1/scientific/sources`
- `POST /api/v1/scientific/search`
- `POST /api/v1/scientific/import-selection`

Example search payload:

```json
{
  "source": "crossref",
  "query": "machine learning",
  "start_date": "2022-01-01",
  "end_date": "2024-12-31",
  "max_results": 10
}
```

Example import payload:

```json
{
  "project_name": "Local Research Project",
  "results": [
    {
      "source": "pubmed",
      "title": "Example title",
      "authors": ["Ada Lovelace"],
      "publication_date": "2024-01-01",
      "url": "https://pubmed.ncbi.nlm.nih.gov/123456/",
      "language": "en",
      "document_type": "article",
      "doi": "10.1000/example",
      "pmid": "123456",
      "abstract": "Short abstract",
      "journal": "Example Journal",
      "keyword_used": "machine learning"
    }
  ]
}
```

## Local persistence

Phase 2 keeps persistence intentionally simple in local single-user mode:

- launched queries are stored in `backend/data/scientific_store.json`
- imported records are stored in the same file
- no project database, authentication, or advanced indexing is added yet

## Quick start

1. Copy `.env.example` to `.env`.
2. Optionally set `SCIENTIFIC_API_MAILTO` for APIs that recommend contact identification.
3. Run `scripts\start-local.ps1` from PowerShell, or `scripts\start-local.bat` from Command Prompt.
4. Open `http://127.0.0.1:5173` and use the `Scientific Search` screen.

## Manual run

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e ".[dev]"
npm install --prefix frontend
docker compose -f infra/docker-compose.local.yml up -d
```

Backend:

```powershell
.venv\Scripts\python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Worker:

```powershell
.venv\Scripts\python -m celery -A worker.app.celery_app.celery_app worker --loglevel=info --pool=solo
```

Frontend:

```powershell
npm run dev --prefix frontend -- --host 127.0.0.1 --port 5173
```

## Tests

```powershell
.venv\Scripts\python -m pytest
npm run test --prefix frontend -- --run
npm run build --prefix frontend
```

## Current limitations

- HAL field coverage depends on the official search index fields returned by the API
- PubMed metadata normalization stays intentionally lightweight and XML-based
- imported records are stored locally in JSON rather than PostgreSQL models
- no deduplication, saved search management, PDF retrieval, or full project workflow yet

## Phase 3 preview

Phase 3 should add richer project-aware persistence, saved search management, stronger local indexing, and broader orchestration around the scientific connector layer. The PR draft for the current phase lives in `docs/phase-2-pr.md`.
