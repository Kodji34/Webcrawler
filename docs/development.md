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
