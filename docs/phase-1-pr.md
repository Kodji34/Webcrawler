# Phase 1 PR Draft

## Title

`feat: scaffold PyCrawler Research Studio phase 1 foundation`

## Summary

- initialize the repository around backend, frontend, worker, infra, scripts, and docs
- scaffold FastAPI, React + Vite + Material UI, and a Celery-ready worker
- add French and English localization, placeholder screens, and local startup scripts
- prepare PostgreSQL and Redis local configuration, tests, README, and licensing

## Validation

- `python -m pytest`
- `npm run test --prefix frontend -- --run`
- `npm run build --prefix frontend`

## Out of scope

- authentication and user accounts
- crawler execution pipelines
- source management CRUD
- persistence beyond local infrastructure configuration

## Phase 2 plan

1. add SQLAlchemy models and Alembic migrations for projects, sources, runs, and schedules
2. connect the frontend screens to real backend endpoints instead of placeholder content
3. implement source intake, crawl orchestration, and worker task flows on Redis-backed Celery queues
4. introduce authentication, role boundaries, and audit-friendly activity logging
