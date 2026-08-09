import { Activity, BarChart2, MousePointerClick, Wind } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import ThreeViewer from "@/components/ThreeViewer"

export default function ResultsViewer() {
  return (
    <div className="max-w-7xl mx-auto animate-in fade-in duration-500 h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Analysis Results</h1>
          <p className="text-muted-foreground">Visualize deflections, force diagrams, and modal shapes.</p>
        </div>
        <div className="flex items-center gap-3">
           <Select defaultValue="combo1">
             <SelectTrigger className="w-[200px] border-primary/50">
               <SelectValue placeholder="Load Case" />
             </SelectTrigger>
             <SelectContent>
               <SelectItem value="dead">Dead (DL)</SelectItem>
               <SelectItem value="live">Live (LL)</SelectItem>
               <SelectItem value="wind_x">Wind X (WL_X)</SelectItem>
               <SelectItem value="eq_x">Seismic X (EQ_X)</SelectItem>
               <SelectItem value="combo1" className="font-semibold text-primary">1.2 DL + 1.6 LL</SelectItem>
             </SelectContent>
           </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        <div className="lg:col-span-1 h-full flex flex-col space-y-4">
          <Card className="flex-1 overflow-y-auto">
             <CardHeader className="py-4 border-b">
               <CardTitle className="text-base flex items-center"><BarChart2 className="w-4 h-4 mr-2" /> Diagram Types</CardTitle>
             </CardHeader>
             <CardContent className="p-4 space-y-2">
                <Button variant="secondary" className="w-full justify-start border border-primary/20 bg-primary/10 text-primary">
                  <Activity className="w-4 h-4 mr-2" /> Deformed Shape
                </Button>
                <Button variant="ghost" className="w-full justify-start text-muted-foreground">
                  Axial Force (P)
                </Button>
                <Button variant="ghost" className="w-full justify-start text-muted-foreground">
                  Shear Force (V2)
                </Button>
                <Button variant="ghost" className="w-full justify-start text-muted-foreground">
                  Bending Moment (M3)
                </Button>
                <Button variant="ghost" className="w-full justify-start text-muted-foreground">
                  <Wind className="w-4 h-4 mr-2" /> Shell Stress (S_xx)
                </Button>
             </CardContent>
          </Card>
          
          <Card>
             <CardHeader className="py-3 border-b bg-secondary/10">
               <CardTitle className="text-sm flex items-center"><MousePointerClick className="w-4 h-4 mr-2"/> Selection Info</CardTitle>
             </CardHeader>
             <CardContent className="p-4 font-mono text-xs space-y-2">
                <div className="flex justify-between"><span>Node ID:</span> <span>104</span></div>
                <div className="flex justify-between"><span>Ux:</span> <span className="text-rose-500">2.4 mm</span></div>
                <div className="flex justify-between"><span>Uy:</span> <span>-0.1 mm</span></div>
                <div className="flex justify-between"><span>Uz:</span> <span className="text-blue-500">-12.8 mm</span></div>
             </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-3 h-full flex flex-col relative rounded-lg border shadow-inner overflow-hidden">
           {/* Color Scale Legend */}
           <div className="absolute top-4 right-4 z-10 bg-background/90 backdrop-blur-sm border rounded-md p-3 shadow-md w-32">
              <div className="text-[10px] uppercase font-bold text-muted-foreground mb-2 text-center">Displacement (mm)</div>
              <div className="space-y-1">
                 <div className="flex items-center text-xs justify-between"><div className="w-4 h-4 bg-rose-500 rounded-sm mr-2"></div> 15.0</div>
                 <div className="flex items-center text-xs justify-between"><div className="w-4 h-4 bg-orange-400 rounded-sm mr-2"></div> 10.0</div>
                 <div className="flex items-center text-xs justify-between"><div className="w-4 h-4 bg-yellow-300 rounded-sm mr-2"></div> 5.0</div>
                 <div className="flex items-center text-xs justify-between"><div className="w-4 h-4 bg-green-400 rounded-sm mr-2"></div> 0.0</div>
                 <div className="flex items-center text-xs justify-between"><div className="w-4 h-4 bg-blue-500 rounded-sm mr-2"></div> -15.0</div>
              </div>
           </div>

           <ThreeViewer mode="results" />
        </div>
      </div>
    </div>
  )
}
