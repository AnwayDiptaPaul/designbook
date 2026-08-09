import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'

import RootLayout from './components/layout/RootLayout'
import Dashboard from './pages/Dashboard'
import ProjectSetup from './pages/ProjectSetup'
import StructuralMembers from './pages/StructuralMembers'
import LoadInput from './pages/LoadInput'
import AnalysisControl from './pages/AnalysisControl'
import DesignModule from './pages/DesignModule'
import Reports from './pages/Reports'
import GeometryInput from './pages/GeometryInput'
import ResultsViewer from './pages/ResultsViewer'
import DetailingDrawings from './pages/DetailingDrawings'

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />
      },
      // Placeholders for Phase 1 routing
      {
        path: 'setup',
        element: <ProjectSetup />
      },
      {
        path: 'geometry',
        element: <GeometryInput />
      },
      {
        path: 'members',
        element: <StructuralMembers />
      },
      {
        path: 'loads',
        element: <LoadInput />
      },
      {
        path: 'analysis',
        element: <AnalysisControl />
      },
      {
        path: 'results',
        element: <ResultsViewer />
      },
      {
        path: 'design',
        element: <DesignModule />
      },
      {
        path: 'detailing',
        element: <DetailingDrawings />
      },
      {
        path: 'reports',
        element: <Reports />
      },
      {
        path: 'excel',
        element: <div className="p-8 text-center text-muted-foreground">Excel Manager (Phase 3)</div>
      }
    ]
  }
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
