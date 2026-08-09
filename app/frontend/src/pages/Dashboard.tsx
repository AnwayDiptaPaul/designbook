import { motion } from "framer-motion"
import { 
  Plus, 
  Search, 
  ArrowUpRight, 
  ShieldCheck, 
  Box, 
  Activity,
  History,
  TrendingUp,
  Files,
  Zap
} from "lucide-react"

'type RecentProject = {
  name: string
  location: string
  type: string
  status: string
  drift: string
}

const recentProjects: RecentProject[] = []'

export default function Dashboard() {
  return (
    <div className="space-y-8 pb-12">
      {/* Welcome Header */}
      <section className="flex justify-between items-end">
        <div>
          <motion.h1 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-4xl font-black tracking-tighter"
          >
            Engineering <span className="text-primary">Dashboard</span>
          </motion.h1>
          <p className="text-muted-foreground mt-1">No active design projects are loaded. Create or select a project to begin.</p>
        </div>
        <button className="flex items-center bg-primary text-primary-foreground px-6 py-2.5 rounded-full font-bold text-sm hover:scale-105 transition-transform shadow-lg shadow-primary/20">
          <Plus className="mr-2 h-4 w-4" />
          New Project
        </button>
      </section>

      {/* Stats Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: "Active Project", value: "—", sub: "No project selected", icon: Box, color: "text-blue-500" },
          { label: "Design Status", value: "—", sub: "Awaiting completed analysis", icon: ShieldCheck, color: "text-green-500" },
          { label: "Max Story Drift", value: "—", sub: "No analysis result", icon: Activity, color: "text-purple-500" },
          { label: "Analysis Runs", value: "0", sub: "No persisted runs", icon: TrendingUp, color: "text-orange-500" },
        ].map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="glass p-6 rounded-2xl relative overflow-hidden group hover:border-primary/50 transition-colors"
          >
            <div className={`p-2 rounded-lg bg-white/5 w-fit ${stat.color} mb-4`}>
              <stat.icon className="h-5 w-5" />
            </div>
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-black tracking-widest text-muted-foreground">{stat.label}</span>
              <div className="text-2xl font-bold tracking-tight">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.sub}</p>
            </div>
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 blur-3xl -z-10 group-hover:bg-primary/10 transition-colors" />
          </motion.div>
        ))}
      </section>

      {/* Main Grid: Recent Projects & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Projects Table */}
        <section className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold flex items-center">
              <History className="mr-2 h-5 w-5 text-primary" />
              Recent Analysis Sessions
            </h2>
            <button className="text-xs text-primary hover:underline font-bold">View History</button>
          </div>
          
          <div className="glass rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="border-b border-white/5 bg-white/5">
                  <tr className="text-[10px] uppercase tracking-widest text-muted-foreground">
                    <th className="px-6 py-4 font-bold">Project Name</th>
                    <th className="px-6 py-4 font-bold">Status</th>
                    <th className="px-6 py-4 font-bold">Max Drift</th>
                    <th className="px-6 py-4 font-bold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {recentProjects.map((project, idx) => (
                    <tr key={idx} className="hover:bg-white/5 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="font-semibold">{project.name}</div>
                        <div className="text-[10px] text-muted-foreground">{project.location} • {project.type}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          project.status.includes("Complete") || project.status.includes("Generated") 
                          ? "bg-green-500/10 text-green-500" 
                          : "bg-orange-500/10 text-orange-500"
                        }`}>
                          {project.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono text-sm">{project.drift}</td>
                      <td className="px-6 py-4 text-right">
                        <button className="p-2 rounded-lg hover:bg-primary/10 transition-colors text-muted-foreground hover:text-primary">
                          <ArrowUpRight className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Sidebar Widgets */}
        <section className="space-y-6">
          {/* Quick Search */}
          <div className="glass p-6 rounded-2xl space-y-4">
            <h3 className="text-sm font-bold flex items-center">
              <Search className="mr-2 h-4 w-4 text-primary" />
              Quick Search
            </h3>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Find project, member or analysis log..." 
                className="w-full bg-secondary/50 border border-border rounded-lg pl-9 pr-4 py-2 text-xs focus:ring-2 focus:ring-primary focus:outline-none transition-all"
              />
            </div>
          </div>

          {/* Quick Shortcuts */}
          <div className="glass p-6 rounded-2xl space-y-4">
            <h3 className="text-sm font-bold flex items-center">
              <Zap className="mr-2 h-4 w-4 text-warning" />
              Quick Shortcuts
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { name: "Input Load", icon: TrendingUp },
                { name: "Gen Reports", icon: Files },
                { name: "View 3D", icon: Box },
                { name: "Design RCC", icon: ShieldCheck },
              ].map((item, idx) => (
                <button key={idx} className="flex flex-col items-center justify-center p-4 rounded-xl bg-white/5 hover:bg-primary/10 border border-white/5 hover:border-primary/20 transition-all group">
                  <item.icon className="h-6 w-6 mb-2 text-muted-foreground group-hover:text-primary transition-colors" />
                  <span className="text-[10px] font-bold uppercase tracking-tighter text-muted-foreground group-hover:text-foreground">{item.name}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
