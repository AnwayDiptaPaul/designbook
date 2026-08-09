import React from "react"
import { Outlet, NavLink } from "react-router-dom"
import { Layers, Fullscreen, Download, Save, Moon, Sun } from "lucide-react"

export default function RootLayout() {
  const [isDark, setIsDark] = React.useState(true)

  React.useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark")
      document.documentElement.classList.remove("light")
    } else {
      document.documentElement.classList.add("light")
      document.documentElement.classList.remove("dark")
    }
  }, [isDark])

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col">
        <div className="h-14 flex items-center px-4 border-b border-border font-semibold text-lg text-primary">
          <Layers className="mr-2 h-5 w-5" />
          DesignBook
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {/* Phase 1 Setup Sidebar stub */}
          <div className="text-sm font-medium text-muted-foreground mb-2">PROJECT</div>
          <NavLink to="/" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Dashboard
          </NavLink>
          <NavLink to="/setup" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Project Setup
          </NavLink>
          <NavLink to="/geometry" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Building Geometry
          </NavLink>
          <NavLink to="/members" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Structural Members
          </NavLink>
          <NavLink to="/loads" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Load Input
          </NavLink>
          <NavLink to="/analysis" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Analysis Control
          </NavLink>
          
          <div className="text-sm font-medium text-muted-foreground mt-6 mb-2">ANALYSIS & DESIGN</div>
          <NavLink to="/analysis" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Analysis Control
          </NavLink>
          <NavLink to="/design" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Design Module
          </NavLink>
          <NavLink to="/results" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Results Viewer
          </NavLink>
          <NavLink to="/design" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Design Module
          </NavLink>
          <NavLink to="/detailing" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Detailing Drawings
          </NavLink>
          
          <div className="text-sm font-medium text-muted-foreground mt-6 mb-2">OUTPUT</div>
          <NavLink to="/reports" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Reports
          </NavLink>
          <NavLink to="/excel" className={({isActive}) => `block text-sm p-2 rounded-md cursor-pointer transition-colors ${isActive ? 'bg-secondary text-secondary-foreground font-medium' : 'hover:bg-secondary/50'}`}>
            Excel Manager
          </NavLink>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full bg-background relative">
        {/* Top Toolbar */}
        <header className="h-14 border-b border-border bg-card/50 backdrop-blur flex items-center justify-between px-4 z-10 w-full">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium tracking-wide">P-101: G+5 Residential Building</span>
            <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-semibold">
              BNBC 2020
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="p-2 rounded-md hover:bg-secondary/80 transition-colors" title="Save Project (Ctrl+S)">
              <Save className="h-4 w-4" />
            </button>
            <button className="p-2 rounded-md hover:bg-secondary/80 transition-colors" title="Export">
              <Download className="h-4 w-4" />
            </button>
            <button className="p-2 rounded-md hover:bg-secondary/80 transition-colors" title="Fullscreen">
              <Fullscreen className="h-4 w-4" />
            </button>
            <div className="w-px h-5 bg-border mx-2"></div>
            <button 
              className="p-2 rounded-md hover:bg-secondary/80 transition-colors" 
              title="Toggle Theme"
              onClick={() => setIsDark(!isDark)}
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
        
        {/* Bottom Status Bar */}
        <footer className="h-8 border-t border-border bg-card flex items-center px-4 text-xs text-muted-foreground justify-between z-10 w-full shrink-0">
          <div className="flex space-x-4">
            <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-success mr-2"></span> System Ready</span>
            <span>API: Connected</span>
          </div>
          <div className="flex space-x-4">
            <span>0 Warnings</span>
            <span>Autosaved 1 min ago</span>
          </div>
        </footer>
      </main>
    </div>
  )
}
