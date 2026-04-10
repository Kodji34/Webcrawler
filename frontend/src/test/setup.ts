import '@testing-library/jest-dom/vitest'
import { beforeEach, vi } from 'vitest'

function pathFromInput(input: RequestInfo | URL) {
  const rawUrl =
    typeof input === 'string'
      ? input
      : input instanceof URL
        ? input.toString()
        : input.url
  return new URL(rawUrl, 'http://127.0.0.1:5173').pathname
}

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: RequestInfo | URL) => {
      const path = pathFromInput(input)

      if (path === '/api/v1/health') {
        return {
          ok: true,
          json: async () => ({
            phase: {
              number: 3,
              name: 'Phase 3 ready',
              focus: 'Scientific search, PDF extraction, and local imports are ready.',
            },
            services: {
              api: 'http://127.0.0.1:8000',
              frontend: 'http://127.0.0.1:5173',
              postgres: 'postgresql+psycopg://postgres:postgres@127.0.0.1:5432/pycrawler',
              redis: 'redis://127.0.0.1:6379/0',
              celery_broker: 'redis://127.0.0.1:6379/0',
              celery_queue: 'research-default',
            },
          }),
        }
      }

      if (path === '/api/v1/scientific/sources') {
        return {
          ok: true,
          json: async () => [
            {
              key: 'crossref',
              label: 'Crossref',
              description: 'Official API',
              official_api_url: 'https://api.crossref.org',
              supports_date_range: true,
              supports_language: false,
              supported_identifiers: ['doi'],
              max_results_limit: 50,
            },
          ],
        }
      }

      if (path === '/api/v1/scientific/imports') {
        return {
          ok: true,
          json: async () => [],
        }
      }

      if (path === '/api/v1/fulltext/items') {
        return {
          ok: true,
          json: async () => ({ items: [] }),
        }
      }

      if (path === '/api/v1/fulltext/sources') {
        return {
          ok: true,
          json: async () => [],
        }
      }

      if (path === '/api/v1/pdf/items') {
        return {
          ok: true,
          json: async () => ({
            items: [],
            dependency_status: {
              pymupdf_available: true,
              pdfplumber_available: true,
              pytesseract_available: false,
              tesseract_available: false,
              ocrmypdf_available: false,
              messages: ['Tesseract missing'],
            },
          }),
        }
      }

      if (path === '/api/v1/web/items') {
        return {
          ok: true,
          json: async () => ({ items: [] }),
        }
      }

      return {
        ok: false,
        status: 404,
        json: async () => ({ detail: `Unhandled test endpoint: ${path}` }),
      }
    }),
  )
})
