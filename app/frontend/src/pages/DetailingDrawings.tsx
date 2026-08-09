import { FileWarning, LockKeyhole } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function DetailingDrawings() {
  return (
    <div className="max-w-7xl mx-auto animate-in fade-in duration-500 pb-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Detailing Canvas</h1>
        <p className="text-muted-foreground">Detailing artifacts require reviewed design results and a snapshot-bound generator.</p>
      </div>
      <Card className="glass border-amber-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-500"><LockKeyhole className="h-5 w-5" /> Detailing is unavailable</CardTitle>
          <CardDescription>No approved reinforcement schedule or drawing artifact has been generated.</CardDescription>
        </CardHeader>
        <CardContent className="flex min-h-[280px] items-center justify-center text-center text-sm text-muted-foreground">
          <div><FileWarning className="mx-auto mb-4 h-10 w-10 opacity-50" /><p>Run and review a supported design before exporting drawings or schedules.</p></div>
        </CardContent>
      </Card>
    </div>
  )
}