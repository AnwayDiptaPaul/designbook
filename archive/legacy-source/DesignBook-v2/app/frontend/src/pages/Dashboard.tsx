import { Building2, Plus, ArrowRight, FolderOpen, Activity, FileSpreadsheet } from "lucide-react"

export default function Dashboard() {
  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-500">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Projects</h1>
          <p className="text-muted-foreground">Manage your structural design projects and analysis models.</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-primary text-primary-foreground font-medium rounded-md hover:bg-primary/90 transition-colors shadow-sm">
          <Plus className="mr-2 h-4 w-4" />
          New Project
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="col-span-1 md:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col justify-between relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -translate-y-1/2 translate-x-1/3 group-hover:scale-110 transition-transform duration-700 pointer-events-none"></div>
          
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="p-2 bg-primary/10 rounded-lg text-primary">
                <Building2 className="h-6 w-6" />
              </div>
              <h2 className="text-xl font-semibold">P-101: G+5 Residential Building</h2>
            </div>
            <p className="text-muted-foreground mb-6 max-w-md">Modified 2 hours ago. Currently designing floor 3 beams. Analysis converged with 0.8% drift.</p>
          </div>
          
          <div className="flex items-center justify-between border-t border-border pt-4">
            <div className="flex space-x-4 text-sm text-muted-foreground">
              <span className="flex items-center"><Activity className="mr-1 h-3 w-3 text-success" /> OK</span>
              <span>120 Nodes</span>
              <span>BNBC 2020</span>
            </div>
            <button className="text-sm font-medium text-primary flex items-center hover:underline">
              Continue Working <ArrowRight className="ml-1 h-3 w-3" />
            </button>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-4">
               <div className="p-2 bg-accent/20 rounded-lg text-accent-foreground">
                  <FileSpreadsheet className="h-6 w-6" />
               </div>
               <h3 className="font-semibold text-lg">Excel Manager</h3>
            </div>
            <p className="text-sm text-muted-foreground relative z-10">Access 34 enhanced calculation sheets for manual checks.</p>
          </div>
          <button className="w-full mt-4 py-2 border border-border rounded-md text-sm font-medium hover:bg-secondary/50 transition-colors">
            Open Sheets
          </button>
        </div>
      </div>

      <h2 className="text-lg font-semibold mb-4 flex items-center">
        <FolderOpen className="mr-2 h-5 w-5 text-muted-foreground" />
        Recent Projects
      </h2>
      
      <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-sm text-left">
          <thead className="bg-secondary/30 text-muted-foreground border-b border-border">
            <tr>
              <th className="px-6 py-3 font-medium">Name</th>
              <th className="px-6 py-3 font-medium">Location</th>
              <th className="px-6 py-3 font-medium">Code</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium text-right">Last Modified</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            <tr className="hover:bg-secondary/20 transition-colors cursor-pointer">
              <td className="px-6 py-4 font-medium">P-098: Factory Shed</td>
              <td className="px-6 py-4 text-muted-foreground">Gazipur, Dhaka</td>
              <td className="px-6 py-4">BNBC 2020</td>
              <td className="px-6 py-4"><span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success/10 text-success">Completed</span></td>
              <td className="px-6 py-4 text-right text-muted-foreground">Feb 24, 2026</td>
            </tr>
            <tr className="hover:bg-secondary/20 transition-colors cursor-pointer">
              <td className="px-6 py-4 font-medium">P-099: Commercial Complex</td>
              <td className="px-6 py-4 text-muted-foreground">Banani, Dhaka</td>
              <td className="px-6 py-4">ACI 318-19</td>
              <td className="px-6 py-4"><span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-warning/10 text-warning-foreground">Designing</span></td>
              <td className="px-6 py-4 text-right text-muted-foreground">Mar 10, 2026</td>
            </tr>
            <tr className="hover:bg-secondary/20 transition-colors cursor-pointer">
              <td className="px-6 py-4 font-medium">P-100: Retaining Wall Check</td>
              <td className="px-6 py-4 text-muted-foreground">Sylhet</td>
              <td className="px-6 py-4">BNBC 2020</td>
              <td className="px-6 py-4"><span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success/10 text-success">Completed</span></td>
              <td className="px-6 py-4 text-right text-muted-foreground">Mar 12, 2026</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
