# Phase 3 PR Draft

## Title

`feat: add phase 3 pdf ingestion, extraction, and ocr workflow`

## Summary

- add modular PDF connectors for local folders and direct remote PDF URLs
- add a PDF ingestion service with local JSON persistence for items, jobs, and saved selections
- add native text extraction with PyMuPDF and pdfplumber plus OCR fallback through pytesseract
- add explicit PDF cleaning options and text preview before save
- add a FR/EN PDF workspace in the frontend with import, preview, bulk processing, and save
- add a simple bridge from imported scientific results when a direct PDF URL is available

## Validation

- `python -m pytest`
- `npm run test --prefix frontend -- --run`
- `npm run build --prefix frontend`

## Out of scope

- social media connectors
- advanced corpus cleaning outside PDF scope
- TreeTagger lemmatization
- advanced IRaMuTeQ exports
- Phase 4 to Phase 6 work
