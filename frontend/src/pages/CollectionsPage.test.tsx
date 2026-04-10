import { render, screen, waitFor } from '@testing-library/react'

import '../i18n/config'
import { CollectionsPage } from './CollectionsPage'

describe('CollectionsPage', () => {
  it('renders the corpus workspace', async () => {
    render(<CollectionsPage />)

    expect(await screen.findByText('Corpora')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Corpus title')).toBeInTheDocument()
      expect(screen.getByText('Available sources')).toBeInTheDocument()
    })
  })
})
