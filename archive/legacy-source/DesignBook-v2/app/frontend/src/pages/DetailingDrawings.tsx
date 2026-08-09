import { useState } from "react"
import { PlaySquare, Download, Code, Share2, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function DetailingDrawings() {
  const [activeElement, setActiveElement] = useState("B1")

  return (
    <div className="max-w-7xl mx-auto animate-in fade-in duration-500 h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Detailing Canvas</h1>
          <p className="text-muted-foreground">Interactive SVG generation for rebar scheduling and drafting.</p>
        </div>
        <div className="flex gap-2">
           <Button variant="outline"><Code className="mr-2 h-4 w-4" /> Export DXF</Button>
           <Button><Download className="mr-2 h-4 w-4" /> Export All SVGs</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        <div className="lg:col-span-1 h-full flex flex-col space-y-4">
           <Card className="flex-1 overflow-hidden flex flex-col">
             <CardHeader className="py-4 border-b">
               <CardTitle className="text-base">Structural Schedule</CardTitle>
             </CardHeader>
             <div className="p-3 border-b">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input type="search" placeholder="Search mark..." className="pl-9 h-9" />
                </div>
             </div>
             <CardContent className="p-0 flex-1 overflow-y-auto">
                <div className="divide-y">
                   <div 
                     className={`p-3 text-sm cursor-pointer hover:bg-secondary/50 flex justify-between items-center ${activeElement === "B1" ? 'bg-secondary font-medium' : ''}`}
                     onClick={() => setActiveElement("B1")}
                   >
                     <span><span className="text-muted-foreground mr-1">Beam</span> B-1</span>
                     <span className="text-xs px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500">Pass</span>
                   </div>
                   <div 
                     className={`p-3 text-sm cursor-pointer hover:bg-secondary/50 flex justify-between items-center ${activeElement === "C1" ? 'bg-secondary font-medium' : ''}`}
                     onClick={() => setActiveElement("C1")}
                   >
                     <span><span className="text-muted-foreground mr-1">Column</span> C-1</span>
                     <span className="text-xs px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500">Pass</span>
                   </div>
                   <div className="p-3 text-sm cursor-pointer hover:bg-secondary/50 flex justify-between items-center">
                     <span><span className="text-muted-foreground mr-1">Slab</span> S-1</span>
                     <span className="text-xs px-1.5 py-0.5 rounded-full bg-amber-500/10 text-amber-500">Warn</span>
                   </div>
                </div>
             </CardContent>
           </Card>
        </div>

        <div className="lg:col-span-3 h-full flex flex-col relative rounded-lg border shadow-inner overflow-hidden bg-background">
           <div className="p-4 border-b flex justify-between items-center bg-secondary/10">
              <div>
                 <h3 className="font-semibold text-lg">{activeElement === "B1" ? "Beam B-1 (250x400) - Level 1" : "Column C-1 (400x400) - Grid A/1"}</h3>
                 <p className="text-xs text-muted-foreground">Generated from `rebar_detailing.py` engine</p>
              </div>
              <Tabs defaultValue="section" className="w-[300px]">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="section">Cross-Section</TabsTrigger>
                  <TabsTrigger value="elevation">Elevation</TabsTrigger>
                </TabsList>
              </Tabs>
           </div>
           
           <div className="flex-1 overflow-auto bg-muted/5 flex items-center justify-center p-8 relative">
               {/* 
                 Fake SVG representation matching the python core generator logic.
                 In real life we would dangerouslySetInnerHTML or use an svg component. 
               */}
               <div className="bg-white p-8 border shadow-sm rounded-sm">
                  <svg width="400" height="450" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 550" className="max-w-full h-auto">
                    <rect x="50" y="50" width="250" height="400" fill="#f8fafc" stroke="#334155" strokeWidth="4"/>
                    
                    {/* Stirrup */}
                    <rect x="90" y="90" width="170" height="320" fill="none" stroke="#2563eb" strokeWidth="10" rx="15" ry="15"/>
                    <path d="M 90 120 L 130 90 M 260 120 L 220 90" stroke="#2563eb" strokeWidth="10" fill="none" />
                    
                    {/* Top Bars (2-16 dia) */}
                    <circle cx="110" cy="110" r="16" fill="#1e293b"/>
                    <circle cx="240" cy="110" r="16" fill="#1e293b"/>
                    
                    {/* Bottom Bars (3-20 dia) */}
                    <circle cx="110" cy="390" r="20" fill="#0f172a"/>
                    <circle cx="175" cy="390" r="20" fill="#0f172a"/>
                    <circle cx="240" cy="390" r="20" fill="#0f172a"/>
                    
                    {/* Measurement Lines */}
                    <line x1="50" y1="30" x2="300" y2="30" stroke="#94a3b8" strokeWidth="2" />
                    <line x1="50" y1="20" x2="50" y2="40" stroke="#94a3b8" strokeWidth="2" />
                    <line x1="300" y1="20" x2="300" y2="40" stroke="#94a3b8" strokeWidth="2" />
                    <text x="175" y="20" fill="#64748b" textAnchor="middle" fontSize="24">250 mm</text>
                    
                    <line x1="330" y1="50" x2="330" y2="450" stroke="#94a3b8" strokeWidth="2" />
                    <line x1="320" y1="50" x2="340" y2="50" stroke="#94a3b8" strokeWidth="2" />
                    <line x1="320" y1="450" x2="340" y2="450" stroke="#94a3b8" strokeWidth="2" />
                    <text x="350" y="250" fill="#64748b" textAnchor="middle" transform="rotate(-90 350,250)" fontSize="24">400 mm</text>
                    
                    {/* Reinforcement Callouts */}
                    <path d="M 175 110 L 175 60 L 380 60" fill="none" stroke="#ef4444" strokeWidth="2" />
                    <text x="390" y="65" fill="#ef4444" fontSize="20">2 - 16∅ Top</text>
                    
                    <path d="M 175 390 L 175 500 L 380 500" fill="none" stroke="#ef4444" strokeWidth="2" />
                    <text x="390" y="505" fill="#ef4444" fontSize="20">3 - 20∅ Bottom</text>

                    <path d="M 90 250 L 30 250 L 30 150 L 380 150" fill="none" stroke="#2563eb" strokeWidth="2" />
                    <text x="390" y="155" fill="#2563eb" fontSize="20">10∅ @ 150 c/c Ties</text>
                  </svg>
               </div>
           </div>
        </div>
      </div>
    </div>
  )
}
