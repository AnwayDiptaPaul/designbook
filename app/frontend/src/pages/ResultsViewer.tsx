import { BarChart3, LockKeyhole } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ResultsViewer() {
  return (
    <div className="max-w-7xl mx-auto animate-in fade-in duration-500 pb-12">
      <div className="mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">Analysis Results</h1>
        <p className="text-muted-foreground">Result plots and tables are available only for a completed backend run.</p>
      </div>
      <Card className="glass border-amber-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-500"><LockKeyhole className="h-5 w-5" /> No result set selected</CardTitle>
          <CardDescription>There is no snapshot-bound analysis result to display.</CardDescription>
        </CardHeader>
        <CardContent className="flex min-h-[280px] items-center justify-center text-center text-sm text-muted-foreground">
          <div><BarChart3 className="mx-auto mb-4 h-10 w-10 opacity-50" /><p>Complete a supported analysis run before viewing diagrams, drift, forces, or displacements.</p></div>
        </CardContent>
      </Card>
    </div>
  )
}