import { useState } from "react"
import { Grid3X3, Layers, BoxSelect, Maximize, ChevronRight, Settings2, Anchor } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import ThreeViewer from "@/components/ThreeViewer"

export default function GeometryInput() {
  const [activeTab, setActiveTab] = useState("grids")
  const [advancedIsolators, setAdvancedIsolators] = useState(false)
  
  // Advanced Isolator States
  const [frictionCoeff, setFrictionCoeff] = useState(0.05)
  const [isolatorK] = useState(1500)

  const handleSaveBoundary = () => {
    const payload = {
      action: "UPDATE_BOUNDARY_CONDITIONS",
      type: advancedIsolators ? "ISOLATED_FRICTION_PENDULUM" : "FIXED_BASE",
      parameters: advancedIsolators ? {
        mu: frictionCoeff,
        k_vertical: isolatorK,
        element: "elastomericBearingPlasticity"
      } : { fixity: [1, 1, 1, 1, 1, 1] }
    }
    console.log(`[userlog.py simulation] Boundary Payload Saved: ${JSON.stringify(payload)}`)
    alert("Boundary conditions simulated dispatch to userlog.py!")
  }

  return (
    <div className="max-w-7xl mx-auto h-[calc(100vh-8rem)] flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent mb-2">
            Building Geometry
          </h1>
          <p className="text-muted-foreground flex items-center">
            <Settings2 className="w-4 h-4 mr-2" />
            Digital Twin modeling: Grids, levels, and structural member orchestration.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        <aside className="lg:col-span-4 h-full flex flex-col min-h-0">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-4 bg-secondary/50 backdrop-blur-md p-1 rounded-xl">
              <TabsTrigger value="grids" className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm text-[10px] sm:text-xs">
                <Grid3X3 className="w-3 h-3 mr-1" /> Grids
              </TabsTrigger>
              <TabsTrigger value="levels" className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm text-[10px] sm:text-xs">
                <Layers className="w-3 h-3 mr-1" /> Levels
              </TabsTrigger>
              <TabsTrigger value="members" className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm text-[10px] sm:text-xs">
                <BoxSelect className="w-3 h-3 mr-1" /> Members
              </TabsTrigger>
              <TabsTrigger value="boundary" className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm text-[10px] sm:text-xs">
                <Anchor className="w-3 h-3 mr-1" /> Boundary
              </TabsTrigger>
            </TabsList>
            
            <div className="flex-1 overflow-hidden mt-4">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.2 }}
                  className="h-full"
                >
                  <Card className="glass-light border-primary/10 h-full flex flex-col shadow-2xl overflow-hidden">
                    <TabsContent value="grids" className="m-0 h-full flex flex-col outline-none">
                      <CardHeader className="pb-4">
                        <CardTitle className="text-xl font-bold font-heading">Grid Matrix</CardTitle>
                        <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Orthogonal Alignment</p>
                      </CardHeader>
                      <CardContent className="space-y-6 flex-1 overflow-y-auto">
                        <div className="space-y-4">
                          <Label className="text-sm font-bold text-primary flex items-center">
                            <ChevronRight className="w-4 h-4 mr-1" /> Longitudinal (X-Axis)
                          </Label>
                          <div className="space-y-2">
                            {['A', 'B', 'C'].map((label, i) => (
                              <div key={label} className="group flex gap-3 items-center bg-background/40 p-2 rounded-lg border border-transparent hover:border-primary/20 transition-all">
                                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary border border-primary/20">
                                  {label}
                                </div>
                                <Input 
                                  readOnly
                                  value={i === 0 ? "0.0" : i === 1 ? "5.0" : "4.5"} 
                                  className="flex-1 bg-transparent border-none focus-visible:ring-0 h-8 font-mono" 
                                />
                                <span className="text-[10px] text-muted-foreground mr-2 font-mono">meters</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </CardContent>
                    </TabsContent>
                    
                    <TabsContent value="levels" className="m-0 h-full flex flex-col outline-none">
                      <CardHeader className="pb-4">
                        <CardTitle className="text-xl font-bold font-heading">Story Management</CardTitle>
                        <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Vertical Stratification</p>
                      </CardHeader>
                      <CardContent className="space-y-3 flex-1 overflow-y-auto">
                        {[
                          { name: "Roof", elev: "9.6", color: "bg-indigo-500" },
                          { name: "Level 2", elev: "6.4", color: "bg-blue-500" },
                          { name: "Level 1", elev: "3.2", color: "bg-cyan-500" },
                          { name: "Ground", elev: "0.0", color: "bg-emerald-500" }
                        ].map((lvl) => (
                          <div key={lvl.name} className="flex items-center gap-4 p-4 rounded-xl glass hover:bg-secondary/20 transition-colors border-primary/5">
                            <div className={`w-1.5 h-10 rounded-full ${lvl.color}`} />
                            <div className="flex-1">
                              <p className="text-sm font-bold">{lvl.name}</p>
                              <p className="text-[10px] text-muted-foreground">Floor Elevation</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Input defaultValue={lvl.elev} className="w-16 h-8 text-right bg-background/50 border-none font-mono" />
                            </div>
                          </div>
                        ))}
                      </CardContent>
                    </TabsContent>
                    
                    <TabsContent value="members" className="m-0 h-full flex flex-col outline-none">
                      <CardHeader className="pb-4">
                        <CardTitle className="text-xl font-bold font-heading">Section Assignment</CardTitle>
                        <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Library Members</p>
                      </CardHeader>
                      <CardContent className="space-y-2">
                          <div className="p-4 rounded-lg bg-primary/5 border border-primary/10 text-xs italic text-muted-foreground">
                            Assignment matrix visible on 3D canvas interaction.
                          </div>
                      </CardContent>
                    </TabsContent>

                    <TabsContent value="boundary" className="m-0 h-full flex flex-col outline-none">
                      <CardHeader className="pb-4 border-b border-primary/5">
                        <CardTitle className="text-xl font-bold font-heading">Foundation & Soil</CardTitle>
                        <CardDescription className="text-[10px]">Configure foundation-to-soil interaction and seismic isolation.</CardDescription>
                      </CardHeader>
                      <CardContent className="pt-4 flex-1 overflow-y-auto">
                        <Tabs defaultValue="restraints" className="w-full">
                          <TabsList className="grid w-full grid-cols-3 bg-secondary/30 p-1 mb-6 rounded-lg">
                            <TabsTrigger value="restraints" className="text-[10px] uppercase font-bold">Restraints</TabsTrigger>
                            <TabsTrigger value="isolators" className="text-[10px] uppercase font-bold">Isolators</TabsTrigger>
                            <TabsTrigger value="soil" className="text-[10px] uppercase font-bold">Soil SSI</TabsTrigger>
                          </TabsList>

                          <TabsContent value="restraints" className="space-y-4 animate-in fade-in duration-300">
                             <div className="p-4 rounded-xl bg-background/40 border border-border flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <Anchor className="h-5 w-5 text-primary" />
                                  <span className="text-sm font-medium">Standard Fixity</span>
                                </div>
                                <span className="text-[10px] bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded font-bold uppercase">Fixed (ENC)</span>
                             </div>
                             <div className="p-3 bg-secondary/10 rounded-lg border border-white/5 space-y-2">
                                <p className="text-[10px] font-bold uppercase text-muted-foreground tracking-tight">Active DOFs</p>
                                <div className="flex gap-1">
                                  {['Ux', 'Uy', 'Uz', 'Rx', 'Ry', 'Rz'].map(dof => (
                                    <div key={dof} className="flex-1 text-center py-1 text-[9px] bg-emerald-500/20 text-emerald-500 rounded border border-emerald-500/20 font-bold">{dof}</div>
                                  ))}
                                </div>
                             </div>
                          </TabsContent>

                          <TabsContent value="isolators" className="space-y-4 animate-in fade-in duration-300">
                             <div className="flex items-center justify-between p-2 bg-primary/5 rounded border border-primary/10 mb-4">
                                <span className="text-[10px] font-bold uppercase">Seismic Isolation Mode</span>
                                <Switch checked={advancedIsolators} onCheckedChange={setAdvancedIsolators} />
                             </div>
                             
                             {advancedIsolators && (
                               <div className="space-y-4">
                                 <div className="space-y-2">
                                    <Label className="text-[10px] uppercase font-bold text-muted-foreground">Isolator Type</Label>
                                    <div className="grid grid-cols-2 gap-2">
                                      <Button variant="outline" size="sm" className="text-[10px] border-primary/20 bg-primary/5">Friction Pendulum</Button>
                                      <Button variant="outline" size="sm" className="text-[10px] border-white/10 opacity-50">Lead Rubber (LRB)</Button>
                                    </div>
                                 </div>
                                 <div className="space-y-3">
                                   <div className="space-y-1">
                                     <div className="flex justify-between">
                                       <Label className="text-[10px] uppercase">Friction (μ)</Label>
                                       <span className="text-[10px] font-mono text-primary">{frictionCoeff}</span>
                                     </div>
                                     <Input type="range" min="0.01" max="0.1" step="0.01" value={frictionCoeff} onChange={(e) => setFrictionCoeff(parseFloat(e.target.value))} className="h-4 accent-primary" />
                                   </div>
                                   <div className="space-y-1">
                                     <Label className="text-[10px] uppercase">Effective Radius (m)</Label>
                                     <Input type="number" defaultValue="2.5" className="h-8 text-xs font-mono bg-background/50" />
                                   </div>
                                 </div>
                               </div>
                             )}
                          </TabsContent>

                          <TabsContent value="soil" className="space-y-4 animate-in fade-in duration-300">
                             <Label className="text-[10px] uppercase font-bold text-muted-foreground">Winkler Foundation (SSI)</Label>
                             <div className="space-y-3">
                                <div className="grid grid-cols-3 gap-2">
                                   {['Hard Rock', 'Stiff Soil', 'Soft Clay'].map(type => (
                                     <Button key={type} variant="outline" size="sm" className={`text-[9px] px-1 ${type === 'Stiff Soil' ? 'border-primary/50 bg-primary/5' : 'border-white/5 opacity-50'}`}>{type}</Button>
                                   ))}
                                </div>
                                <div className="space-y-2">
                                   <div className="flex justify-between">
                                      <Label className="text-[10px]">Subgrade Modulus (kN/m³)</Label>
                                      <span className="text-[10px] font-mono text-primary">15000</span>
                                   </div>
                                   <div className="p-3 rounded-lg bg-indigo-500/5 border border-indigo-500/10 text-[9px] text-muted-foreground italic">
                                      Maps to `zeroLength` soil springs using UI-derived stiffness coefficients ($K_x, K_y, K_z$).
                                   </div>
                                </div>
                             </div>
                          </TabsContent>
                        </Tabs>
                      </CardContent>
                      <CardFooter className="pt-2">
                         <Button onClick={handleSaveBoundary} className="w-full shadow-lg shadow-primary/20 bg-primary hover:bg-primary-hover text-white">Save Foundation Map</Button>
                      </CardFooter>
                    </TabsContent>
                  </Card>
                </motion.div>
              </AnimatePresence>
            </div>
          </Tabs>
        </aside>

        <main className="lg:col-span-8 h-full flex flex-col relative rounded-3xl overflow-hidden border-2 border-primary/10 shadow-2xl bg-black/40 group">
           <div className="absolute top-6 left-6 z-20 flex gap-2">
              <div className="glass-light p-1 rounded-xl flex shadow-xl border border-white/10">
                <Button variant="ghost" size="sm" className="rounded-lg h-8 px-3 text-xs font-bold text-primary">3D Model</Button>
                <Button variant="ghost" size="sm" className="rounded-lg h-8 px-3 text-xs font-bold text-muted-foreground hover:text-foreground">Floor Plan</Button>
                <Button variant="ghost" size="sm" className="rounded-lg h-8 px-3 text-xs font-bold text-muted-foreground hover:text-foreground">Elevation</Button>
              </div>
              <Button size="icon" variant="ghost" className="glass-light rounded-xl h-10 w-10 shadow-xl border border-white/10">
                <Maximize className="h-4 w-4" />
              </Button>
           </div>
           
           <ThreeViewer mode="geometry" />
        </main>
      </div>
    </div>
  )
}
