import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

import '../i18n/config'
import { PdfWorkspacePage } from './PdfWorkspacePage'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('PdfWorkspacePage', () => {
  it('renders the PDF workspace and loads empty state', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
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
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })

    vi.stubGlobal('fetch', fetchMock)

    render(<PdfWorkspacePage />)

    expect(await screen.findByText('PDF workspace')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Local folder')).toBeInTheDocument()
      expect(screen.getByLabelText('PDF URL list')).toBeInTheDocument()
    })
  })
})
