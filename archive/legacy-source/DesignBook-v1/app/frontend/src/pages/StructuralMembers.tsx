import { useState } from "react"
import { Plus, Maximize, Layers, Square, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function StructuralMembers() {
  const [activeType, setActiveType] = useState<"columns" | "beams" | "slabs" | "walls">("columns")

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Structural Members</h1>
        <p className="text-muted-foreground">Define and place columns, beams, slabs, and shear walls across the grid.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Sidebar for choosing member type */}
        <div className="md:col-span-1 space-y-2">
          <Button 
            variant={activeType === "columns" ? "default" : "outline"} 
            className="w-full justify-start"
            onClick={() => setActiveType("columns")}
          >
            <Maximize className="mr-2 h-4 w-4" /> Columns
          </Button>
          <Button 
            variant={activeType === "beams" ? "default" : "outline"} 
            className="w-full justify-start"
            onClick={() => setActiveType("beams")}
          >
            <Layers className="mr-2 h-4 w-4" /> Beams
          </Button>
          <Button 
            variant={activeType === "slabs" ? "default" : "outline"} 
            className="w-full justify-start"
            onClick={() => setActiveType("slabs")}
          >
            <Square className="mr-2 h-4 w-4" /> Slabs
          </Button>
          <Button 
            variant={activeType === "walls" ? "default" : "outline"} 
            className="w-full justify-start"
            onClick={() => setActiveType("walls")}
          >
            <Maximize className="mr-2 h-4 w-4 rotate-90" /> Shear Walls
          </Button>
        </div>

        {/* Main interactive area placeholder */}
        <div className="md:col-span-3">
          <Card className="h-[600px] flex flex-col">
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
            <CardContent className="flex-1 flex items-center justify-center p-6 bg-secondary/10">
              <div className="text-center space-y-4 max-w-sm">
                <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                  <AlertCircle className="h-6 w-6" />
                </div>
                <h3 className="font-medium text-lg">Interactive Canvas Pending</h3>
                <p className="text-sm text-muted-foreground">
                  The interactive grid canvas for visually placing {activeType} will be integrated here using a 2D rendering library. For now, you can switch to the table view.
                </p>
                <Button variant="outline" className="mt-4">
                  Switch to Table View
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
