import { useState } from "react"
import { Plus, Maximize, Layers, Square, AlertCircle, Settings2, ShieldAlert } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"

export default function StructuralMembers() {
  const [activeType, setActiveType] = useState<"columns" | "beams" | "slabs" | "walls">("columns")
  const [advancedMode, setAdvancedMode] = useState(false)

  const [confinementRatio, setConfinementRatio] = useState(1.3)
  const [yieldStrain, setYieldStrain] = useState(0.002)

  const handleSaveAdvancedProperties = () => {
    const payload = {
      action: "UPDATE_FIBER_MATERIAL",
      memberType: activeType,
      parameters: {
        concrete: "Concrete02",
        steel: "Steel01",
        Kcc: confinementRatio,
        eps_y: yieldStrain
      }
    }
    console.log(`[userlog.py simulation] Advanced Payload Saved: ${JSON.stringify(payload)}`)
    alert("Nonlinear properties simulated dispatch to userlog.py!")
  }

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-500 pb-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center">
            Structural Members {advancedMode && <span className="ml-3 text-xs bg-primary/20 text-primary px-2 py-1 rounded-full uppercase tracking-wider font-bold shadow-[0_0_10px_rgba(var(--primary),0.2)]">Nonlinear Mode Active</span>}
          </h1>
          <p className="text-muted-foreground">Define and place columns, beams, slabs, and shear walls across the grid.</p>
        </div>
        <Button 
          variant={advancedMode ? "default" : "outline"} 
          className={`transition-all ${advancedMode ? 'shadow-[0_0_15px_rgba(var(--primary),0.3)]' : ''}`}
          onClick={() => setAdvancedMode(!advancedMode)}
        >
          <Settings2 className="mr-2 h-4 w-4" /> 
          Advanced Mode
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Sidebar for choosing member type */}
        <div className="md:col-span-1 space-y-2">
          <Button 
            variant={activeType === "columns" ? "default" : "secondary"} 
            className="w-full justify-start"
            onClick={() => setActiveType("columns")}
          >
            <Maximize className="mr-2 h-4 w-4" /> Columns
          </Button>
          <Button 
            variant={activeType === "beams" ? "default" : "secondary"} 
            className="w-full justify-start"
            onClick={() => setActiveType("beams")}
          >
            <Layers className="mr-2 h-4 w-4" /> Beams
          </Button>
          <Button 
            variant={activeType === "slabs" ? "default" : "secondary"} 
            className="w-full justify-start"
            onClick={() => setActiveType("slabs")}
          >
            <Square className="mr-2 h-4 w-4" /> Slabs
          </Button>
          <Button 
            variant={activeType === "walls" ? "default" : "secondary"} 
            className="w-full justify-start"
            onClick={() => setActiveType("walls")}
          >
            <Maximize className="mr-2 h-4 w-4 rotate-90" /> Shear Walls
          </Button>
        </div>

        {/* Main interactive area */}
        <div className="md:col-span-3 space-y-6">
          <Card className="glass border-white/5">
            <CardHeader className="flex flex-row items-center justify-between pb-2 border-b border-border">
              <div>
                <CardTitle className="capitalize">{activeType}</CardTitle>
                <CardDescription>
                  {activeType === "columns" && "Define dimension (b x h) and place vertically."}
                  {activeType === "beams" && "Connect grid points to place beams."}
                  {activeType === "slabs" && "Select perimeter grids to place slab panels."}
                  {activeType === "walls" && "Define wall thickness and place between nodes."}
                </CardDescription>
              </div>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" /> Add {activeType.slice(0, -1)}
              </Button>
            </CardHeader>
            <CardContent className="flex-1 flex items-center justify-center p-6 bg-secondary/5 min-h-[300px]">
              <div className="text-center space-y-4 max-w-sm">
                <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                  <AlertCircle className="h-6 w-6" />
                </div>
                <h3 className="font-medium text-lg">Interactive Canvas Pending</h3>
                <p className="text-sm text-muted-foreground">
                  The interactive grid canvas for visually placing {activeType} will be integrated here using a 2D rendering library.
                </p>
                <Button variant="outline" className="mt-4">
                  Switch to Table View
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* ADVANCED NONLINEAR SETTINGS REVEALED */}
          {advancedMode && (
            <Card className="animate-in slide-in-from-top-4 duration-500 border-primary/30 bg-primary/5 shadow-2xl">
              <CardHeader className="pb-3 border-b border-primary/10">
                <CardTitle className="text-primary flex items-center">
                  <ShieldAlert className="mr-2 h-5 w-5" />
                  {activeType === "walls" ? "Shear Wall Modeling (MVLEM)" : "Nonlinear Member Definitions"}
                </CardTitle>
                <CardDescription>
                  {activeType === "walls" ? "Configuring Multiple-Vertical-Line-Element-Model for Flexure-Critical Walls." : "Configure OpenSeesPy `Concrete02` and `Steel01` material plasticity maps."}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6 space-y-6">
                 <div className="grid grid-cols-2 gap-8">
                   <div className="space-y-3">
                     <div className="flex justify-between items-center">
                       <label className="text-sm font-medium text-foreground">Confinement Ratio (Kcc)</label>
                       <span className="text-xs bg-secondary px-2 py-1 rounded text-primary">{confinementRatio.toFixed(2)}</span>
                     </div>
                     <input 
                       type="range" 
                       min="1.0" max="1.8" step="0.05" 
                       value={confinementRatio} 
                       onChange={(e) => setConfinementRatio(parseFloat(e.target.value))}
                       className="w-full accent-primary" 
                     />
                     <p className="text-[10px] text-muted-foreground">Mander model parameter representing the strength increase of core concrete due to transverse tie bars.</p>
                   </div>
                   
                   <div className="space-y-3">
                     <div className="flex justify-between items-center">
                       <label className="text-sm font-medium text-foreground">Yield Strain (eps_y)</label>
                       <span className="text-xs bg-secondary px-2 py-1 rounded text-primary">{yieldStrain.toFixed(4)}</span>
                     </div>
                     <input 
                       type="range" 
                       min="0.001" max="0.005" step="0.0005" 
                       value={yieldStrain} 
                       onChange={(e) => setYieldStrain(parseFloat(e.target.value))}
                       className="w-full accent-primary" 
                     />
                     <p className="text-[10px] text-muted-foreground">Defines the elastic limit of longitudinal reinforcement before strain hardening occurs.</p>
                   </div>
                 </div>

                 {(activeType === "columns" || activeType === "beams") && (
                    <div className="p-4 rounded-xl bg-orange-500/5 border border-orange-500/10 space-y-3">
                       <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-orange-400 uppercase tracking-wider">Plastic Hinge Properties</span>
                          <Switch defaultChecked />
                       </div>
                       <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-1">
                             <p className="text-[10px] text-muted-foreground">Hinge Type</p>
                             <p className="text-xs">Modified IMK (Bilin)</p>
                          </div>
                          <div className="space-y-1">
                             <p className="text-[10px] text-muted-foreground">Hinge Length</p>
                             <p className="text-xs">0.10·L</p>
                          </div>
                       </div>
                    </div>
                 )}
                 
                 <div className="pt-4 flex justify-end">
                    <Button onClick={handleSaveAdvancedProperties} className="bg-primary hover:bg-primary/90 text-background font-bold px-8">
                       Save Parameters
                    </Button>
                 </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
