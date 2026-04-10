import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'

import { AppShell } from '../layouts/AppShell'
import { CollectionsPage } from '../pages/CollectionsPage'
import { DashboardPage } from '../pages/DashboardPage'
import { PdfWorkspacePage } from '../pages/PdfWorkspacePage'
import { ResearchQueuePage } from '../pages/ResearchQueuePage'
import { SchedulesPage } from '../pages/SchedulesPage'
import { ScientificSearchPage } from '../pages/ScientificSearchPage'
import { SettingsPage } from '../pages/SettingsPage'
import { WebImportsPage } from '../pages/WebImportsPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'scientific-search', element: <ScientificSearchPage /> },
      { path: 'pdf-workspace', element: <PdfWorkspacePage /> },
      { path: 'web-imports', element: <WebImportsPage /> },
      { path: 'research-queue', element: <ResearchQueuePage /> },
      { path: 'collections', element: <CollectionsPage /> },
      { path: 'schedules', element: <SchedulesPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])

export function AppRouter() {
  return <RouterProvider router={router} />
}
