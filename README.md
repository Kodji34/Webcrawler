# PyCrawler Research Studio

Phase 3 adds a usable PDF ingestion and OCR layer on top of the Phase 1 foundation and the Phase 2 scientific connectors.

## Phase 3 scope

- keep the Phase 1 foundation and Phase 2 scientific search flow intact
- import PDFs from local folders, direct PDF URLs, and linked scientific imports when a direct PDF URL exists
- detect usable native text with PyMuPDF and pdfplumber
- fall back to OCR when requested or when auto mode recommends it
- preview extracted text before saving
- apply explicit PDF-only cleaning options chosen by the user
- store processed PDF metadata and text locally for single-user use

## Explicitly out of scope

- social media connectors
- advanced global corpus cleaning outside PDF scope
- TreeTagger lemmatization
- advanced IRaMuTeQ exports
- Phase 4 to Phase 6 work

## Supported scientific and PDF flows

Scientific sources remain:

- Crossref REST API
- OpenAlex API
- PubMed E-utilities
- HAL search API

Phase 3 PDF sources are:

- local directory scan
- direct remote PDF URLs
- direct PDF links attached to already imported scientific results

## PDF modes

Extraction modes:

- `native`: use embedded PDF text only
- `ocr`: use OCR only
- `auto`: try native extraction first and recommend or switch to OCR when the extracted text is too weak

The auto heuristic is intentionally simple:

- native extraction runs first with PyMuPDF and pdfplumber
- OCR is recommended when the document has no text or very little text
- in auto mode, OCR is used only when OCR dependencies are available
- the response always exposes the requested mode and the actual mode used

## PDF cleaning options

Cleaning is never applied unless the user asks for a cleaned output.

Available options:

- remove repeated headers
- remove repeated footers
- remove standalone page numbers
- trim bibliography or references after a detected heading
- normalize whitespace and line breaks

Cleaning heuristics are approximate by design and are documented as such in API responses and UI notes.

## API endpoints

Scientific search endpoints remain available:

- `GET /api/v1/scientific/sources`
- `POST /api/v1/scientific/search`
- `POST /api/v1/scientific/import-selection`
- `GET /api/v1/scientific/imports`

Phase 3 PDF endpoints:

- `POST /api/v1/pdf/import-local`
- `POST /api/v1/pdf/import-urls`
- `POST /api/v1/pdf/extract`
- `POST /api/v1/pdf/preview`
- `POST /api/v1/pdf/save-selection`
- `GET /api/v1/pdf/jobs/{job_id}`
- `GET /api/v1/pdf/items`

Example local folder import:

```json
{
  "directory_path": "C:/data/pdfs",
  "recursive": true,
  "language": "en"
}
```

Example direct URL import:

```json
{
  "entries": [
    {
      "url": "https://example.org/paper.pdf",
      "label": "paper.pdf"
    }
  ],
  "import_type": "remote"
}
```

Example extraction request:

```json
{
  "item_ids": ["pdf-item-id"],
  "extraction_mode": "auto",
  "cleaning_options": {
    "generate_cleaned_text": true,
    "remove_headers": true,
    "remove_page_numbers": true,
    "normalize_whitespace": true
  }
}
```

## Local persistence

Phase 3 keeps persistence intentionally simple in local single-user mode:

- scientific queries and imports are stored in `backend/data/scientific_store.json`
- PDF items, jobs, and saved PDF records are stored in `backend/data/pdf_store.json`
- downloaded remote PDFs are cached under `backend/data/pdf_cache/`
- no PostgreSQL domain models or multi-user access were added for this phase

## Required system dependencies

Python dependencies are installed from `pyproject.toml`, including:

- `PyMuPDF`
- `pdfplumber`
- `httpx`
- `pytesseract`
- `Pillow`

System tools:

- Tesseract OCR must be installed and available on `PATH` for OCR mode
- OCRmyPDF is optional and detected, but the current implementation uses `pytesseract` for OCR execution

If Tesseract is missing:

- the app still runs
- native extraction still works
- OCR mode reports a clear dependency-missing state

## Quick start

1. Copy `.env.example` to `.env`.
2. Optionally set `SCIENTIFIC_API_MAILTO` for APIs that recommend contact identification.
3. Ensure Tesseract is installed and available on `PATH` if you want OCR support.
4. Run `scripts\start-local.ps1` from PowerShell, or `scripts\start-local.bat` from Command Prompt.
5. Open `http://127.0.0.1:5173` and use both `Scientific Search` and `PDF Workspace`.

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

- OCR quality depends on the local Tesseract installation and the scanned PDF quality
- the bibliography trimming heuristic is approximate and based on heading detection
- repeated header and footer detection is frequency-based and may miss irregular layouts
- remote PDF import accepts only direct PDF resources and does not do website scraping
- PDF persistence is local JSON rather than full project database storage

## Phase 4 preview

Phase 4 should build on the saved PDF corpus with richer project workflows and broader corpus tooling, without changing the scope of the current Phase 3 deliverable. The Phase 3 PR draft lives in `docs/phase-3-pr.md`.
