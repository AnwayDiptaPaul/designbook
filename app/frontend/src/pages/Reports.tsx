import { FileText, Download, FileSpreadsheet, FilePieChart, Printer, Calculator, CheckCircle2, History, Share2 } from "lucide-react"
import { motion } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Reports() {
const handleDownloadPDF = () => {
    alert("PDF report generation is not currently available; no document was generated.")
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-6xl mx-auto h-[calc(100vh-8rem)] flex flex-col gap-8 duration-700"
    >
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent mb-2">
            Reports & Documentation
          </h1>
          <p className="text-muted-foreground flex items-center text-sm font-medium">
            <CheckCircle2 className="w-4 h-4 mr-2 text-emerald-500" />
            Review-oriented reporting; generation is enabled only after a completed analysis run.
          </p>
        </div>
        <div className="flex gap-2">
           <Button variant="outline" size="sm" className="glass h-10 rounded-xl px-4 text-xs font-bold border-white/10">
             <History className="w-3.5 h-3.5 mr-2" /> History
           </Button>
           <Button variant="outline" size="sm" className="glass h-10 rounded-xl px-4 text-xs font-bold border-white/10">
             <Share2 className="w-3.5 h-3.5 mr-2" /> Share
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 overflow-y-auto pr-1">
        <div className="md:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="glass-light border-primary/10 shadow-2xl overflow-hidden flex flex-col group">
            <CardHeader className="bg-primary/5 pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-red-500/10 text-red-500 transition-transform group-hover:rotate-12">
                  <FileText className="h-6 w-6" />
                </div>
                <div>
                  <CardTitle className="text-xl font-bold">Structural Calculation</CardTitle>
                  <CardDescription className="text-[10px] uppercase font-bold tracking-widest text-primary/60">Comprehensive Report</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-6 flex-1">
              <div className="space-y-3 mb-6 bg-background/40 p-4 rounded-2xl border border-white/5 shadow-inner">
                {[
                  { label: "Compliance Code", val: "BNBC 2020", active: true },
                  { label: "Load Combinations", val: "BNBC/ACI", active: false },
                  { label: "Detailing Chapter", val: "Included", active: false },
                  { label: "P-M Interaction", val: "Appended", active: false },
                ].map(item => (
                  <div key={item.label} className="flex justify-between items-center py-1.5 border-b border-white/5 last:border-0">
                    <span className="text-xs text-muted-foreground">{item.label}</span>
                    <span className={`text-[11px] font-mono font-bold ${item.active ? 'text-primary' : ''}`}>{item.val}</span>
                  </div>
                ))}
              </div>
              <Button onClick={handleDownloadPDF} className="w-full h-12 rounded-xl shadow-lg shadow-primary/20 bg-primary font-bold">
                <><Download className="mr-2 h-4 w-4" /> Request PDF Report</>
              </Button>
            </CardContent>
          </Card>

          <Card className="glass border-emerald-500/10 shadow-xl overflow-hidden flex flex-col group">
            <CardHeader className="bg-emerald-500/5 pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-500 transition-transform group-hover:scale-110">
                  <Calculator className="h-6 w-6" />
                </div>
                <div>
                  <CardTitle className="text-xl font-bold">Bill of Quantities</CardTitle>
                  <CardDescription className="text-[10px] uppercase font-bold tracking-widest text-emerald-500/60">Cost & Material Estimations</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-6 space-y-6 flex-1">
              <div className="grid grid-cols-2 gap-4">
                <div className="glass-light rounded-2xl p-4 text-center border border-white/5 shadow-lg group-hover:border-emerald-500/20 transition-all">
                  <div className="text-2xl font-black text-emerald-500 font-mono tracking-tighter">345 <span className="text-[10px] font-normal text-muted-foreground">m³</span></div>
                  <div className="text-[9px] uppercase tracking-widest text-muted-foreground mt-1 font-bold">Concrete</div>
                </div>
                <div className="glass-light rounded-2xl p-4 text-center border border-white/5 shadow-lg group-hover:border-emerald-500/20 transition-all">
                  <div className="text-2xl font-black text-emerald-500 font-mono tracking-tighter">42.5 <span className="text-[10px] font-normal text-muted-foreground">ton</span></div>
                  <div className="text-[9px] uppercase tracking-widest text-muted-foreground mt-1 font-bold">Steel</div>
                </div>
              </div>
              <Button variant="outline" className="w-full h-12 rounded-xl border-emerald-500/20 hover:bg-emerald-500/5 text-emerald-600 font-bold transition-all">
                 <FileSpreadsheet className="mr-2 h-4 w-4" /> Export CSV / Excel
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-4 flex flex-col gap-6">
          <Card className="glass border-primary/10 shadow-2xl overflow-hidden flex-1 group">
            <CardHeader className="pb-4 border-b border-primary/5">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-500">
                  <FilePieChart className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-lg">Detailing Output</CardTitle>
                  <CardDescription className="text-[10px]">SVG Generation Engine</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-6">
               <div className="flex flex-col gap-4">
                  <div className="aspect-square rounded-2xl border-2 border-dashed border-primary/10 bg-muted/20 flex flex-col items-center justify-center text-center p-6 group-hover:bg-primary/5 transition-all">
                     <Printer className="h-10 w-10 text-muted-foreground opacity-30 mb-4 group-hover:opacity-60 transition-opacity" />
                     <p className="text-[10px] font-bold text-muted-foreground opacity-60 leading-relaxed">
                       VECTOR ENGINE READY.<br/>
                       Drafting templates pending finalize.
                     </p>
                  </div>
                  <Button variant="secondary" className="w-full rounded-xl bg-indigo-500/10 text-indigo-500 hover:bg-indigo-500/20 border border-indigo-500/20 font-bold">
                    Acquire Vector Pack
                  </Button>
               </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  )
}
