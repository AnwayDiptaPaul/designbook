import { AlertTriangle, FileCheck2, LockKeyhole } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function DesignModule() {
  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-500 pb-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Member Design & Review</h1>
        <p className="text-muted-foreground">
          Design checks are shown only from a completed, snapshot-bound analysis run.
        </p>
      </div>

      <Card className="glass border-amber-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-500">
            <LockKeyhole className="h-5 w-5" /> No completed analysis result
          </CardTitle>
          <CardDescription>
            Member capacities, utilization ratios, reinforcement, and governing combinations are not available yet.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-5 text-sm text-muted-foreground">
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-500" />
              <p>
                No sample pass/fail values or auto-sizing progress are displayed. Run a supported backend analysis with a
                frozen project snapshot, then return here for engineer review.
              </p>
            </div>
          </div>
          <Button variant="outline" disabled>
            <FileCheck2 className="mr-2 h-4 w-4" /> Review completed design results
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}