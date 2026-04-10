import { render, screen, waitFor } from '@testing-library/react'

import '../i18n/config'
import { PdfWorkspacePage } from './PdfWorkspacePage'

describe('PdfWorkspacePage', () => {
  it('renders the PDF workspace and loads empty state', async () => {
    render(<PdfWorkspacePage />)

    expect(await screen.findByText('PDF workspace')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Local folder')).toBeInTheDocument()
      expect(screen.getByLabelText('PDF URL list')).toBeInTheDocument()
    })
  })
})
