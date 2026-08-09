/**
 * App.tsx — DesignBook Root Component
 * 
 * This file is not directly used in the routing architecture.
 * All routing is handled by main.tsx → RootLayout.tsx → Outlet.
 * This file is kept as a fallback entry if the router provider is disabled.
 */
import RootLayout from './components/layout/RootLayout'

function App() {
  return <RootLayout />
}

export default App
