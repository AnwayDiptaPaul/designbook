import { useState } from "react"
import { Wind, Activity, Layers, Download, Save } from "lucide-react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

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
    <form className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Gravity Loads</CardTitle>
          <CardDescription>Define uniform area loads (kN/m²) based on BNBC Table 8.2.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Live Load (LL)</Label>
              <Input type="number" step="0.1" {...register("liveLoad", { valueAsNumber: true })} />
            </div>
            <div className="space-y-2">
              <Label>Floor Finish (SDL)</Label>
              <Input type="number" step="0.1" {...register("floorFinish", { valueAsNumber: true })} />
            </div>
            <div className="space-y-2">
              <Label>Partition Wall (SDL)</Label>
              <Input type="number" step="0.1" {...register("partitionWall", { valueAsNumber: true })} />
            </div>
            <div className="space-y-2 flex items-center pt-8">
              <input type="checkbox" id="llr" className="mr-2" {...register("liveLoadReduction")} />
              <Label htmlFor="llr">Apply Live Load Reduction</Label>
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button type="button">
            <Save className="mr-2 h-4 w-4" /> Save Gravity Loads
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}

function LateralLoadForm() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center"><Wind className="mr-2 h-5 w-5 text-blue-500" /> Wind Load</CardTitle>
                <CardDescription>Auto-computed via BNBC Part 6 Ch.2</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-secondary/20 p-4 rounded-md text-sm">
              <p>Base Wind Speed: <span className="font-semibold">65.6 m/s</span></p>
              <p>Exposure Category: <span className="font-semibold">B (Urban)</span></p>
              <p>Gust Factor (G): <span className="font-semibold">0.85</span></p>
            </div>
            <Button variant="outline" className="w-full">
              <Download className="mr-2 h-4 w-4" /> Generate Wind Profile
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center"><Activity className="mr-2 h-5 w-5 text-red-500" /> Seismic Load</CardTitle>
                <CardDescription>Equivalent Static Force Method (ESFM)</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-secondary/20 p-4 rounded-md text-sm">
              <p>Seismic Zone: <span className="font-semibold">II (Z=0.15)</span></p>
              <p>Soil Class: <span className="font-semibold">SC (S=1.15)</span></p>
              <p>Frame Type: <span className="font-semibold">SMRF (R=8)</span></p>
            </div>
            <Button variant="outline" className="w-full">
              <Download className="mr-2 h-4 w-4" /> Calculate Base Shear
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Load Combinations</CardTitle>
          <CardDescription>Auto-generated standard ACI 318 / BNBC combinations.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm font-mono bg-muted p-4 rounded-md">
            <div>1.4 DL</div>
            <div>1.2 DL + 1.6 LL</div>
            <div>1.2 DL + 1.0 LL + 1.0 WX</div>
            <div>1.2 DL + 1.0 LL + 1.0 EQX</div>
            <div>1.2 DL + 1.0 LL - 1.0 WX</div>
            <div>1.2 DL + 1.0 LL - 1.0 EQX</div>
            <div>0.9 DL + 1.0 WX</div>
            <div>0.9 DL + 1.0 EQX</div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function LoadInput() {
  const [activeTab, setActiveTab] = useState<"gravity" | "lateral">("gravity")

  return (
    <div className="max-w-5xl mx-auto animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Load Definitions</h1>
        <p className="text-muted-foreground">Define and generate gravity, wind, and seismic loads. Load combintations are automatically handled.</p>
      </div>

      <div className="flex space-x-2 border-b border-border mb-6">
        <button
          className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
            activeTab === "gravity" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
          }`}
          onClick={() => setActiveTab("gravity")}
        >
          <Layers className="inline mr-2 h-4 w-4" />
          Gravity & Area Loads
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
            activeTab === "lateral" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
          }`}
          onClick={() => setActiveTab("lateral")}
        >
          <Activity className="inline mr-2 h-4 w-4" />
          Lateral & Seismic
        </button>
      </div>

      {activeTab === "gravity" && <GravityLoadForm />}
      {activeTab === "lateral" && <LateralLoadForm />}
    </div>
  )
}
