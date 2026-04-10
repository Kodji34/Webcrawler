import { fireEvent, render, screen } from '@testing-library/react'

import App from './App'

describe('App shell', () => {
  it('renders the dashboard and navigation', async () => {
    render(<App />)

    expect(
      await screen.findByRole('heading', {
        name: 'Overview',
        level: 4,
      }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Dashboard',
        level: 6,
      }),
    ).toBeInTheDocument()

    fireEvent.click(screen.getAllByRole('button')[0])

    expect(await screen.findByText('PyCrawler Research Studio')).toBeInTheDocument()
    expect(screen.getByText('Scientific Search')).toBeInTheDocument()
    expect(screen.getByText('PDF Workspace')).toBeInTheDocument()
    expect(screen.getByText('Web Imports')).toBeInTheDocument()
    expect(screen.getByText('Research Queue')).toBeInTheDocument()
    expect(screen.getByText('Collections')).toBeInTheDocument()
    expect(screen.getByText('Schedules')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })
})
