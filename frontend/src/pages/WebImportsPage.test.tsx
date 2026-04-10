import { render, screen, waitFor } from '@testing-library/react'

import '../i18n/config'
import { WebImportsPage } from './WebImportsPage'

describe('WebImportsPage', () => {
  it('renders the web import workspace after existing items load', async () => {
    render(<WebImportsPage />)

    expect(await screen.findByText('Web imports')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Article URLs')).toBeInTheDocument()
      expect(screen.getByText('Import links')).toBeInTheDocument()
    })
  })
})
