# PyCrawler Research Studio

Phase 4 adds a local corpus workflow on top of the Phase 1 foundation, Phase 2 scientific connectors, and Phase 3 PDF/OCR pipeline. The scientific workflow also includes an authorized full-text acquisition layer that only uses official APIs, open repositories, or licensed TDM access.

## Phase 4 scope

- keep Phase 1 to Phase 3 flows intact
- assemble local corpora from already imported PDF, authorized full-text, and public web article texts
- show simple corpus statistics: documents, words, characters, source types, languages
- provide a basic plain text export
- avoid advanced global cleaning, TreeTagger, and advanced IRaMuTeQ exports

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

Authorized full-text acquisition sources are:

- Europe PMC / PMC for open access full text when the official endpoint exposes it
- ScienceDirect / Elsevier through the official TDM API with credentials
- HAL deposited files when repository metadata exposes a direct accessible file
- OpenEdition Journals metadata via OAI, with HTML body retrieval only when the page is openly accessible and a license signal is present
- Cairn as bibliographic metadata only in this phase
- Erudit when the article page is openly accessible and readable without bypassing restrictions

Phase 3 PDF sources are:

- local directory scan
- direct remote PDF URLs
- direct PDF links attached to already imported scientific results

Additional public web imports are available for press articles or HTML pages supplied directly by the user:

- one URL per line from the `Web Imports` screen
- public HTTP(S) pages only
- no authenticated browser session
- no access bypass
- blocked pages are stored as `not_authorized`
- PDF URLs are not extracted there and should be sent to the PDF workspace

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

Authorized full-text endpoints:

- `GET /api/v1/fulltext/sources`
- `GET /api/v1/fulltext/items`
- `POST /api/v1/fulltext/acquire-imports`

Public web import endpoints:

- `POST /api/v1/web/import-urls`
- `GET /api/v1/web/items`

Phase 4 corpus endpoints:

- `GET /api/v1/corpus/sources`
- `POST /api/v1/corpus/create`
- `GET /api/v1/corpus/items`
- `GET /api/v1/corpus/items/{corpus_id}`
- `GET /api/v1/corpus/items/{corpus_id}/export-text`

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
- full-text acquisition attempts and outcomes are stored in `backend/data/fulltext_store.json`
- PDF items, jobs, and saved PDF records are stored in `backend/data/pdf_store.json`
- downloaded remote PDFs are cached under `backend/data/pdf_cache/`
- public web article imports are stored in `backend/data/web_store.json`
- local corpora are stored in `backend/data/corpus_store.json`
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
3. Set `ELSEVIER_API_KEY` and, if your institution requires it, `ELSEVIER_INSTTOKEN` for licensed ScienceDirect TDM access.
4. Ensure Tesseract is installed and available on `PATH` if you want OCR support.
5. Run `scripts\start-local.ps1` from PowerShell, or `scripts\start-local.bat` from Command Prompt.
6. Open `http://127.0.0.1:5173` and use both `Scientific Search` and `PDF Workspace`.

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

- authorized full-text acquisition does not bypass paywalls and never scrapes blocked pages
- Elsevier full text works only when official credentials are configured and the institution is entitled
- Cairn stays metadata-only in this phase because no public official automated full-text path is configured here
- OpenEdition and Erudit HTML extraction is heuristic and runs only when the article page is directly readable
- web article imports are URL-based and public-page only; they do not use logged-in accounts
- OCR quality depends on the local Tesseract installation and the scanned PDF quality
- the bibliography trimming heuristic is approximate and based on heading detection
- repeated header and footer detection is frequency-based and may miss irregular layouts
- remote PDF import accepts only direct PDF resources and does not do website scraping
- PDF persistence is local JSON rather than full project database storage

## Phase 5 preview

Phase 5 can build on local corpora with more advanced corpus preparation once its scope is explicitly defined. TreeTagger, advanced IRaMuTeQ exports, and global corpus cleaning remain out of the current Phase 4 boundary.
