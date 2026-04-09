# Phase 2 PR Draft

## Title

`feat: add phase 2 scientific connectors and import workflow`

## Summary

- add official scientific connectors for Crossref, OpenAlex, PubMed, and HAL
- normalize scientific metadata through a connector-based backend architecture
- expose scientific search, sources listing, and import-selection endpoints
- add a real FR/EN scientific search screen with preview and multi-selection import
- persist launched queries and imported records locally for single-user usage

## Validation

- `python -m pytest`
- `npm run test --prefix frontend -- --run`
- `npm run build --prefix frontend`

## Out of scope

- PDF or OCR extraction
- social media connectors
- advanced corpus cleaning
- advanced IRaMuTeQ exports
- phases 3 to 6

## Phase 3 preview

1. project-aware persistence beyond local JSON storage
2. richer source ingestion workflows and saved search sets
3. deeper connector options and better local indexing
4. authentication and multi-user concerns only when the roadmap explicitly opens them
