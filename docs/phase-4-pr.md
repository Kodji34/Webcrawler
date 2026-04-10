# Phase 4 PR Draft

## Summary

- add local corpus creation from already imported PDF, authorized full-text, and public web article texts
- add source discovery, corpus creation, corpus listing, corpus detail, and plain text export endpoints
- replace the placeholder Collections page with a real corpus workspace
- add simple corpus statistics for document count, word count, character count, source types, and languages

## Validation

- `python -m pytest backend/tests/test_corpus_routes.py backend/tests/test_web_routes.py backend/tests/test_fulltext_routes.py`
- `npm run test --prefix frontend -- --run`
- `npm run build --prefix frontend`

## Out of scope

- TreeTagger lemmatization
- advanced IRaMuTeQ exports
- advanced global corpus cleaning
- social media connectors
- multi-user project storage
