import { render, screen, waitFor } from '@testing-library/react'

import '../i18n/config'
import { ScientificSearchPage } from './ScientificSearchPage'

describe('ScientificSearchPage', () => {
  it('renders the scientific search form after sources load', async () => {
    render(<ScientificSearchPage />)

    expect(await screen.findByText('Scientific search')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Source')).toBeInTheDocument()
      expect(screen.getByLabelText('Keyword or simple query')).toBeInTheDocument()
      expect(screen.getByText('Authorized full text')).toBeInTheDocument()
    })
  })
})
