import { useState } from "react"
import { Wind, Activity, Layers, Download, Save, Info, AlertCircle, ChevronRight } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

const GravityLoadSchema = z.object({
  liveLoad: z.number().min(0),
  floorFinish: z.number().min(0),
  partitionWall: z.number().min(0),
  liveLoadReduction: z.boolean()
})
type GravityLoadData = z.infer<typeof GravityLoadSchema>

function GravityLoadForm() {
  const { register } = useForm<GravityLoadData>({
    resolver: zodResolver(GravityLoadSchema),
    defaultValues: {
      liveLoad: 3.0,
      floorFinish: 1.2,
      partitionWall: 2.0,
      liveLoadReduction: true,
    }
  })

  return (
    <motion.form 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <Card className="glass-light border-primary/10 shadow-2xl overflow-hidden">
        <CardHeader className="bg-primary/5 border-b border-primary/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              <Layers className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-xl">Gravity Load Matrix</CardTitle>
              <CardDescription>Uniform area loads (kN/m²) based on BNBC/ACI specifications.</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="space-y-3">
                <Label className="text-sm font-bold flex items-center justify-between">
                  <span>Live Load (LL)</span>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger><Info className="h-3 w-3 text-muted-foreground" /></TooltipTrigger>
                      <TooltipContent><p className="text-[10px]">Occupancy based loads (BNBC Table 8.2)</p></TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </Label>
                <div className="relative group">
                  <Input type="number" step="0.1" className="bg-background/50 border-primary/10 group-hover:border-primary/30 transition-colors h-12 pl-4 text-xl font-bold font-mono" {...register("liveLoad", { valueAsNumber: true })} />
                  <span className="absolute right-4 top-3 text-xs text-muted-foreground font-bold tracking-widest">kN/m²</span>
                </div>
              </div>

              <div className="space-y-3">
                <Label className="text-sm font-bold">Super Imposed Dead Loads (SDL)</Label>
                <div className="grid grid-cols-1 gap-4">
                  <div className="flex items-center gap-4 bg-secondary/20 p-3 rounded-xl border border-primary/5">
                    <div className="flex-1">
                      <p className="text-[10px] font-bold uppercase text-muted-foreground">Floor Finish</p>
                      <Input type="number" step="0.1" className="h-8 border-none bg-transparent font-mono font-bold text-lg p-0" {...register("floorFinish", { valueAsNumber: true })} />
                    </div>
                    <span className="text-[10px] bg-background/50 px-2 py-1 rounded-md">kN/m²</span>
                  </div>
                  <div className="flex items-center gap-4 bg-secondary/20 p-3 rounded-xl border border-primary/5">
                    <div className="flex-1">
                      <p className="text-[10px] font-bold uppercase text-muted-foreground">Partition Wall</p>
                      <Input type="number" step="0.1" className="h-8 border-none bg-transparent font-mono font-bold text-lg p-0" {...register("partitionWall", { valueAsNumber: true })} />
                    </div>
                    <span className="text-[10px] bg-background/50 px-2 py-1 rounded-md">kN/m²</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-6">
               <div className="bg-primary/5 rounded-2xl p-6 border border-primary/10 space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="p-1.5 rounded-full bg-blue-500/20 text-blue-500 mt-1">
                      <AlertCircle className="h-3 w-3" />
                    </div>
                    <div className="flex-1">
                      <p className="text-xs font-bold text-blue-500 uppercase tracking-wider">Note on Reductions</p>
                      <p className="text-[11px] text-muted-foreground leading-relaxed mt-1">
                         Live load reduction applies to members supporting large areas (BNBC 6.2.13). Reductions are auto-calculated during member design loops.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-background/40 rounded-xl border border-primary/5 hover:border-primary/20 transition-all cursor-pointer">
                    <input type="checkbox" id="llr" className="h-4 w-4 rounded border-primary/20 text-primary focus:ring-primary" {...register("liveLoadReduction")} />
                    <Label htmlFor="llr" className="text-sm font-medium cursor-pointer">Enable Reduction Algorithms</Label>
                  </div>
               </div>

               <div className="p-4 rounded-xl border-2 border-dashed border-primary/10 bg-muted/5 flex items-center justify-center text-center">
                  <div className="text-[10px] text-muted-foreground">
                    <p>Total Gravity Pressure (Service)</p>
                    <p className="text-2xl font-black text-foreground font-mono mt-1 tracking-tighter">6.2 kN/m²</p>
                  </div>
               </div>
            </div>
          </div>
        </CardContent>
        <CardFooter className="bg-secondary/10 p-4 flex justify-end">
          <Button type="button" className="shadow-lg shadow-primary/20 px-8 h-12 rounded-xl">
            <Save className="mr-2 h-4 w-4" /> Finalize Load Model
          </Button>
        </CardFooter>
      </Card>
    </motion.form>
  )
}

function LateralLoadForm() {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="glass shadow-xl border-blue-500/10 overflow-hidden group">
          <CardHeader className="bg-blue-500/5 pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500 transition-transform group-hover:scale-110">
                  <Wind className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-lg">Dynamic Wind Force</CardTitle>
                  <CardDescription className="text-[10px] flex items-center gap-1">
                    <ChevronRight className="w-3 h-3" /> BNBC Part 6 Ch.2 Specification
                  </CardDescription>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-3">
               {[
                 { label: "Base Velocity", val: "65.6 m/s", active: true },
                 { label: "Exposure", val: "Cat. B", active: false },
                 { label: "Gust Factor", val: "0.85 G", active: false },
                 { label: "Impt. Factor", val: "1.0", active: false },
               ].map(stat => (
                 <div key={stat.label} className="p-3 bg-secondary/20 rounded-xl border border-primary/5">
                    <p className="text-[9px] font-bold text-muted-foreground uppercase">{stat.label}</p>
                    <p className={`text-sm font-black mt-0.5 ${stat.active ? 'text-blue-500' : 'text-foreground/80'}`}>{stat.val}</p>
                 </div>
               ))}
            </div>
            <Button variant="outline" className="w-full h-10 border-blue-500/20 hover:bg-blue-500/5 text-blue-500 font-bold text-xs uppercase tracking-widest">
              <Download className="mr-2 h-3.5 w-3.5" /> Recalculate Wind Profile
            </Button>
          </CardContent>
        </Card>

        <Card className="glass shadow-xl border-red-500/10 overflow-hidden group">
          <CardHeader className="bg-red-500/5 pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-red-500/10 text-red-500 transition-transform group-hover:scale-110">
                  <Activity className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-lg">Seismic Command</CardTitle>
                  <CardDescription className="text-[10px] flex items-center gap-1 text-red-500/80">
                    <ChevronRight className="w-3 h-3" /> ESFM Analysis Logic
                  </CardDescription>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-3">
               {[
                 { label: "Seismic Zone", val: "II (Z=0.15)", active: true },
                 { label: "Soil Class", val: "Type SC", active: false },
                 { label: "R-Factor", val: "8 (SMRF)", active: false },
                 { label: "Cd-Factor", val: "5.5", active: false },
               ].map(stat => (
                 <div key={stat.label} className="p-3 bg-rose-500/5 rounded-xl border border-red-500/10">
                    <p className="text-[9px] font-bold text-red-500/60 uppercase">{stat.label}</p>
                    <p className="text-sm font-black mt-0.5 text-red-500">{stat.val}</p>
                 </div>
               ))}
            </div>
            <Button variant="outline" className="w-full h-10 border-red-500/20 hover:bg-red-500/5 text-red-500 font-bold text-xs uppercase tracking-widest">
              <Download className="mr-2 h-3.5 w-3.5" /> Execute Seismic Probe
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card className="glass shadow-2xl border-primary/10 overflow-hidden">
        <CardHeader className="py-4 bg-secondary/30">
          <CardTitle className="text-sm font-bold uppercase tracking-widest">Active Permutations</CardTitle>
          <CardDescription className="text-[10px]">Standard Strength & Service Combinations (ACI 318)</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
             {[
               "1.4 DL", "1.2 DL + 1.6 LL", "1.2 DL + 1.0 LL + 1.0 WX", "1.2 DL + 1.0 LL + 1.0 EQX",
               "1.2 DL + 1.0 LL - 1.0 WX", "1.2 DL + 1.0 LL - 1.0 EQX", "0.9 DL + 1.0 WX", "0.9 DL + 1.0 EQX"
             ].map(combo => (
               <div key={combo} className="p-3 bg-background/40 border border-primary/5 rounded-lg text-[11px] font-mono text-center hover:border-primary/20 transition-colors">
                 {combo}
               </div>
             ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default function LoadInput() {
  const [activeTab, setActiveTab] = useState<"gravity" | "lateral">("gravity")

  return (
    <div className="max-w-6xl mx-auto h-[calc(100vh-8rem)] flex flex-col gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent mb-2">
            Load Definitions
          </h1>
          <p className="text-muted-foreground flex items-center text-sm font-medium">
            <Info className="w-4 h-4 mr-2" />
            Establish gravity states and lateral dynamic profiles for analysis.
          </p>
        </div>
      </div>

      <div className="flex p-1 bg-secondary/50 backdrop-blur-xl rounded-2xl w-fit border border-white/5">
        <button
          className={`relative px-6 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center gap-2 ${
            activeTab === "gravity" 
              ? "bg-background text-primary shadow-xl ring-1 ring-primary/10" 
              : "text-muted-foreground hover:text-foreground"
          }`}
          onClick={() => setActiveTab("gravity")}
        >
          <Layers className={`h-4 w-4 ${activeTab === "gravity" ? "text-primary" : "opacity-50"}`} />
          Gravity & Area
          {activeTab === "gravity" && (
            <motion.div layoutId="tab-pill" className="absolute inset-0 rounded-xl border-2 border-primary/20" transition={{ type: "spring", bounce: 0.2, duration: 0.6 }} />
          )}
        </button>
        <button
          className={`relative px-6 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center gap-2 ${
            activeTab === "lateral" 
              ? "bg-background text-primary shadow-xl ring-1 ring-primary/10" 
              : "text-muted-foreground hover:text-foreground"
          }`}
          onClick={() => setActiveTab("lateral")}
        >
          <Activity className={`h-4 w-4 ${activeTab === "lateral" ? "text-red-500" : "opacity-50"}`} />
          Lateral & Seismic
          {activeTab === "lateral" && (
            <motion.div layoutId="tab-pill" className="absolute inset-0 rounded-xl border-2 border-red-500/20" transition={{ type: "spring", bounce: 0.2, duration: 0.6 }} />
          )}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-1">
        <AnimatePresence mode="wait">
          {activeTab === "gravity" ? (
            <GravityLoadForm key="gravity" />
          ) : (
            <LateralLoadForm key="lateral" />
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

