import { useState } from "react"
import { Grid3X3, Layers, BoxSelect, Maximize, Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import ThreeViewer from "@/components/ThreeViewer"

export default function GeometryInput() {
  const [activeTab, setActiveTab] = useState("grids")

  return (
    <div className="max-w-7xl mx-auto animate-in fade-in duration-500 h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Building Geometry</h1>
        <p className="text-muted-foreground">Define grids, floor levels, and place structural members.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        <div className="lg:col-span-1 h-full flex flex-col">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-3 mb-4">
              <TabsTrigger value="grids"><Grid3X3 className="w-4 h-4 mr-2" /> Grids</TabsTrigger>
              <TabsTrigger value="levels"><Layers className="w-4 h-4 mr-2" /> Levels</TabsTrigger>
              <TabsTrigger value="members"><BoxSelect className="w-4 h-4 mr-2" /> Members</TabsTrigger>
            </TabsList>
            
            <Card className="flex-1 overflow-y-auto">
              <TabsContent value="grids" className="m-0 mt-2 h-full">
                <CardHeader className="py-4">
                  <CardTitle className="text-lg">Grid Definition</CardTitle>
                  <CardDescription>Orthogonal X and Y spacing.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-secondary/20 p-4 rounded-md border border-dashed space-y-3">
                    <Label className="font-semibold text-primary">X-Direction (Alphabetic)</Label>
                    <div className="flex gap-2 items-center">
                       <Input value="A" className="w-12 text-center" readOnly />
                       <span className="text-muted-foreground text-xs">0.0m</span>
                    </div>
                    <div className="flex gap-2 items-center">
                       <Input value="B" className="w-12 text-center" readOnly />
                       <Input value="5.0" type="number" />
                       <span className="text-muted-foreground text-xs">m</span>
                    </div>
                    <div className="flex gap-2 items-center">
                       <Input value="C" className="w-12 text-center" readOnly />
                       <Input value="4.5" type="number" />
                       <span className="text-muted-foreground text-xs">m</span>
                    </div>
                    <Button variant="ghost" size="sm" className="w-full text-xs text-muted-foreground"><Plus className="w-3 h-3 mr-1" /> Add X Grid</Button>
                  </div>
                  
                  <div className="bg-secondary/20 p-4 rounded-md border border-dashed space-y-3">
                    <Label className="font-semibold text-primary">Y-Direction (Numeric)</Label>
                    <div className="flex gap-2 items-center">
                       <Input value="1" className="w-12 text-center" readOnly />
                       <span className="text-muted-foreground text-xs">0.0m</span>
                    </div>
                    <div className="flex gap-2 items-center">
                       <Input value="2" className="w-12 text-center" readOnly />
                       <Input value="5.5" type="number" />
                       <span className="text-muted-foreground text-xs">m</span>
                    </div>
                    <Button variant="ghost" size="sm" className="w-full text-xs text-muted-foreground"><Plus className="w-3 h-3 mr-1" /> Add Y Grid</Button>
                  </div>
                </CardContent>
              </TabsContent>
              
              <TabsContent value="levels" className="m-0 mt-2">
                <CardHeader className="py-4">
                  <CardTitle className="text-lg">Story Levels</CardTitle>
                  <CardDescription>Floor to floor elevations.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {["Roof", "Level 2", "Level 1", "Ground"].map((lvl, i) => (
                    <div key={lvl} className="flex justify-between items-center p-3 border rounded-md bg-background">
                      <span className="font-medium text-sm">{lvl}</span>
                      <div className="flex items-center gap-2">
                         <Input value={i === 3 ? "0.0" : i===2 ? "3.2" : i===1 ? "6.4" : "9.6"} className="w-20 text-right" />
                         <span className="text-xs text-muted-foreground">m</span>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full"><Plus className="w-4 h-4 mr-2"/> Add Story</Button>
                </CardContent>
              </TabsContent>
              
              <TabsContent value="members" className="m-0 mt-2">
                <CardHeader className="py-4">
                  <CardTitle className="text-lg">Structural Members</CardTitle>
                  <CardDescription>Assign Sections.</CardDescription>
                </CardHeader>
                <CardContent>
                   <p className="text-sm text-muted-foreground mb-4">Select items in the 3D view to assign or modify sections.</p>
                   <div className="space-y-2">
                      <Button variant="secondary" className="w-full justify-start">Columns (C300x300)</Button>
                      <Button variant="secondary" className="w-full justify-start">Beams (B250x400)</Button>
                      <Button variant="secondary" className="w-full justify-start">Slabs (S150)</Button>
                      <Button variant="secondary" className="w-full justify-start border-dashed border-primary/50 text-primary">Draw Shear Wall</Button>
                   </div>
                </CardContent>
              </TabsContent>
            </Card>
          </Tabs>
        </div>

        <div className="lg:col-span-2 h-full flex flex-col relative rounded-lg overflow-hidden border border-border shadow-inner bg-black/5 dark:bg-black/20">
           <div className="absolute top-4 left-4 z-10 bg-background/80 backdrop-blur-sm border rounded-md p-2 flex gap-1 shadow-sm">
              <Button variant="ghost" size="icon" className="h-8 w-8"><Maximize className="h-4 w-4" /></Button>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-primary font-bold">3D</Button>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground font-bold">XY</Button>
           </div>
           
           <div className="absolute bottom-4 left-4 z-10 bg-background/80 backdrop-blur-sm border rounded-md px-3 py-1.5 text-xs font-mono shadow-sm">
              X: 12.4m | Y: 8.2m | Z: 3.2m (Level 1)
           </div>

           <ThreeViewer mode="geometry" />
        </div>
      </div>
    </div>
  )
}
