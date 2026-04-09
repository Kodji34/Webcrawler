import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

import '../i18n/config'
import { ScientificSearchPage } from './ScientificSearchPage'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('ScientificSearchPage', () => {
  it('renders the scientific search form after sources load', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
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
    })

    vi.stubGlobal('fetch', fetchMock)

    render(<ScientificSearchPage />)

    expect(await screen.findByText('Scientific search')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Source')).toBeInTheDocument()
      expect(screen.getByLabelText('Keyword or simple query')).toBeInTheDocument()
    })
  })
})
