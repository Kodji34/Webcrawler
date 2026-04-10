# Development Notes

## Local stack

- backend: FastAPI
- frontend: React + Vite + Material UI
- worker: Celery + Redis
- local persistence: JSON files in `backend/data/`

## Phase 3 PDF dependencies

Python packages:

- `PyMuPDF`
- `pdfplumber`
- `httpx`
- `pytesseract`
- `Pillow`

System tools:

- `tesseract` on `PATH` for OCR
- `ocrmypdf` optional, detected only

## Authorized full-text dependencies

Environment variables:

- `ELSEVIER_API_KEY` for ScienceDirect / Elsevier TDM
- `ELSEVIER_INSTTOKEN` when institutional entitlement requires it

Notes:

- Europe PMC / PMC uses official open access endpoints only
- HAL uses metadata plus deposited files exposed by the repository
- OpenEdition and Erudit attempt HTML retrieval only when the page remains openly accessible
- Cairn stays metadata-only in the current implementation

## Public web imports

The `Web Imports` screen accepts direct article/page URLs, one per line. This is not a general crawler:

- accepted schemes: `http` and `https`
- blocked sources return `not_authorized`
- non-HTML responses are stored as metadata-only
- PDF URLs should be handled by the PDF workspace
- no authenticated browser session or bypass is attempted

## Useful commands

Install:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e ".[dev]"
npm install --prefix frontend
```

Run backend:

```powershell
.venv\Scripts\python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Run frontend:

```powershell
npm run dev --prefix frontend -- --host 127.0.0.1 --port 5173
```

Run tests:

```powershell
.venv\Scripts\python -m pytest
npm run test --prefix frontend -- --run
npm run build --prefix frontend
```

## Phase 3 implementation notes

- local PDF scanning is path-based and intended for a local single-user workflow
- remote PDF import accepts direct PDF URLs only
- OCR uses `pytesseract` over rendered page images from PyMuPDF
- auto mode is heuristic-based and intentionally conservative
- cleaning options are opt-in and limited to PDF-specific heuristics
- authorized full-text acquisition keeps explicit outcomes: retrieved, not authorized, metadata only, or failed
- public web imports keep explicit outcomes: text retrieved, metadata only, not authorized, or failed
