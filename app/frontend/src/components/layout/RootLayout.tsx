import React from "react"
import { Outlet, NavLink, useLocation } from "react-router-dom"
import { 
  Layers, 
  Fullscreen, 
  Download, 
  Save, 
  Moon, 
  Sun, 
  LayoutDashboard,
  Settings,
  Box,
  Cylinder,
  Zap,
  Play,
  BarChart3,
  PenTool,
  FileText,
  TableProperties
} from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

const navItems = [
  { group: "PROJECT", items: [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Project Setup", path: "/setup", icon: Settings },
    { name: "Building Geometry", path: "/geometry", icon: Box },
    { name: "Structural Members", path: "/members", icon: Cylinder },
    { name: "Load Input", path: "/loads", icon: Zap },
  ]},
  { group: "ANALYSIS & DESIGN", items: [
    { name: "Analysis Control", path: "/analysis", icon: Play },
    { name: "Results Viewer", path: "/results", icon: BarChart3 },
    { name: "Design Module", path: "/design", icon: PenTool },
    { name: "Detailing Drawings", path: "/detailing", icon: TableProperties },
  ]},
  { group: "OUTPUT", items: [
    { name: "Reports", path: "/reports", icon: FileText },
    { name: "Excel Manager", path: "/excel", icon: TableProperties },
  ]}
]

export default function RootLayout() {
  const [isDark, setIsDark] = React.useState(true)
  const location = useLocation()

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
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col z-20">
        <div className="h-16 flex items-center px-6 border-b border-border font-bold text-xl">
          <Layers className="mr-2 h-6 w-6 text-primary" />
          <span className="text-gradient-primary">DesignBook</span>
        </div>
        
        <nav className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
          {navItems.map((group, idx) => (
            <div key={idx} className="space-y-1">
              <h3 className="px-3 text-xs font-bold text-muted-foreground uppercase tracking-widest mb-2">
                {group.group}
              </h3>
              {group.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      "group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                      isActive
                        ? "bg-primary/20 text-primary shadow-[0_0_20px_rgba(var(--primary),0.3)]"
                        : "hover:bg-secondary text-muted-foreground hover:text-foreground"
                    )
                  }
                >
                  <item.icon className={cn(
                    "mr-3 h-4 w-4 transition-colors",
                    location.pathname === item.path ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                  )} />
                  {item.name}
                  {location.pathname === item.path && (
                    <motion.div 
                      layoutId="active-indicator"
                      className="ml-auto w-1 h-4 bg-primary rounded-full"
                    />
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full bg-background relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/2 -z-10" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-primary/5 blur-[120px] rounded-full translate-y-1/2 -translate-x-1/2 -z-10" />

        {/* Top Toolbar */}
        <header className="h-16 border-b border-border bg-background/40 backdrop-blur-xl flex items-center justify-between px-6 z-10 w-full">
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-sm space-x-2">
              <span className="text-muted-foreground">Project:</span>
              <span className="font-semibold tracking-tight">P-101: G+5 Residential Building</span>
            </div>
            <div className="h-4 w-px bg-border" />
            <span className="px-2.5 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider border border-primary/20">
              BNBC 2020
            </span>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="flex items-center bg-secondary/50 rounded-lg p-1">
              <button 
                className="p-1.5 rounded-md hover:bg-background/50 hover:shadow-sm transition-all text-muted-foreground hover:text-foreground" 
                title="Save Project"
              >
                <Save className="h-3.5 w-3.5" />
              </button>
              <button 
                className="p-1.5 rounded-md hover:bg-background/50 hover:shadow-sm transition-all text-muted-foreground hover:text-foreground" 
                title="Export"
              >
                <Download className="h-3.5 w-3.5" />
              </button>
              <button className="p-1.5 rounded-md hover:bg-background/50 hover:shadow-sm transition-all text-muted-foreground hover:text-foreground" title="Fullscreen">
                <Fullscreen className="h-3.5 w-3.5" />
              </button>
            </div>
            
            <button 
              className="p-2 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors border border-border"
              title="Toggle Theme"
              onClick={() => setIsDark(!isDark)}
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>
        </header>

        {/* Dynamic Page Content with Entrance Animation */}
        <div className="flex-1 overflow-y-auto p-8 relative z-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10, scale: 0.99 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.99 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
        
        {/* Bottom Status Bar */}
        <footer className="h-10 border-t border-border bg-card/50 backdrop-blur-sm flex items-center px-6 text-[10px] uppercase font-bold tracking-widest text-muted-foreground justify-between z-10 w-full shrink-0">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)] mr-2 animate-pulse" />
              <span>System Online</span>
            </div>
            <div className="h-3 w-px bg-border" />
            <span>API Latency: 42ms</span>
          </div>
          <div className="flex items-center space-x-6">
            <span className="text-primary/80">BNBC-2020 Compliance: Verified</span>
            <span>v0.1.0-alpha</span>
          </div>
        </footer>
      </main>
    </div>
  )
}
