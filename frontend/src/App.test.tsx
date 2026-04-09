import { render, screen } from '@testing-library/react'

import App from './App'

describe('App shell', () => {
  it('renders the dashboard and navigation', async () => {
    render(<App />)

    expect(
      await screen.findByRole('heading', {
        name: 'PyCrawler Research Studio',
        level: 2,
      }),
    ).toBeInTheDocument()
    expect(screen.getByText('Scientific Search')).toBeInTheDocument()
    expect(screen.getByText('Research Queue')).toBeInTheDocument()
    expect(screen.getByText('Collections')).toBeInTheDocument()
    expect(screen.getByText('Schedules')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })
})
