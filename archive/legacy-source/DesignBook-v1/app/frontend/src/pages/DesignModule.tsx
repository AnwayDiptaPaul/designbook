import { useState } from "react"
import { CheckCircle2, XCircle, ChevronRight, Activity, Zap, RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

type MemberType = "Beam" | "Column" | "Slab" | "Wall" | "Footing"

interface MemberResult {
  id: string
  label: string
  type: MemberType
  status: "Pass" | "Fail" | "Warning" | "Pending"
  utilization: number
  details: {
    M_u?: number
    V_u?: number
    P_u?: number
    As_req?: number
    As_prov?: number
    critical_ratio?: number
    notes?: string
  }
}

const mockMembers: MemberResult[] = [
  { id: "B1", label: "Beam B-1 (Grid A-B/1)", type: "Beam", status: "Pass", utilization: 0.85, details: { M_u: 156.4, V_u: 85.2, As_req: 1250, As_prov: 1520, notes: "Flexure controlled." } },
  { id: "B2", label: "Beam B-2 (Grid B-C/1)", type: "Beam", status: "Fail", utilization: 1.15, details: { M_u: 340.2, V_u: 145.0, As_req: 2800, As_prov: 2500, notes: "Exceeds max steel ratio. Increase section depth." } },
  { id: "C1", label: "Column C-1 (Grid B/2)", type: "Column", status: "Warning", utilization: 0.95, details: { P_u: 2500, M_u: 35.5, critical_ratio: 0.95, notes: "Nearing P-M envelope boundary." } },
  { id: "S1", label: "Slab S-1 (Level 1)", type: "Slab", status: "Pass", utilization: 0.60, details: { M_u: 45.2, As_req: 500, As_prov: 628, notes: "Minimum temperature steel governs." } }
]

export default function DesignModule() {
  const [selectedMember, setSelectedMember] = useState<MemberResult | null>(mockMembers[0])
  const [isIterating, setIsIterating] = useState(false)
  const [progress, setProgress] = useState(0)

  const runDesignLoop = () => {
    setIsIterating(true)
    setProgress(0)
    
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval)
          setIsIterating(false)
          return 100
        }
        return p + 10
      })
    }, 500)
  }

  return (
    <div className="max-w-6xl mx-auto animate-in fade-in duration-500 h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Member Design & Auto-Iteration</h1>
          <p className="text-muted-foreground">Review ACI 318 / BNBC 2020 design capacities and run logic loops.</p>
        </div>
        <Button onClick={runDesignLoop} disabled={isIterating} className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
          {isIterating ? <><RefreshCw className="mr-2 h-4 w-4 animate-spin" /> Iterating Design...</> : <><Zap className="mr-2 h-4 w-4" /> Run Design Loop</>}
        </Button>
      </div>
      
      {isIterating && (
        <div className="mb-6">
           <div className="flex justify-between text-xs mb-1 text-muted-foreground">
             <span>Auto-sizing failing members...</span>
             <span>Iteration 2/5</span>
           </div>
           <Progress value={progress} className="h-2" />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1 min-h-0">
        <Card className="flex flex-col h-full overflow-hidden">
          <CardHeader className="py-4 border-b">
            <CardTitle className="text-base">Structural Elements</CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex-1 overflow-y-auto">
            <div className="divide-y">
              {mockMembers.map(member => (
                <div 
                  key={member.id} 
                  className={`p-4 cursor-pointer hover:bg-secondary/50 transition-colors flex items-center justify-between ${selectedMember?.id === member.id ? 'bg-secondary' : ''}`}
                  onClick={() => setSelectedMember(member)}
                >
                  <div>
                    <div className="font-medium text-sm flex items-center">
                      {member.status === "Pass" && <CheckCircle2 className="mr-2 h-4 w-4 text-emerald-500" />}
                      {member.status === "Fail" && <XCircle className="mr-2 h-4 w-4 text-rose-500" />}
                      {member.status === "Warning" && <Activity className="mr-2 h-4 w-4 text-amber-500" />}
                      {member.label}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Utilization: {(member.utilization * 100).toFixed(0)}%</div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2 flex flex-col h-full overflow-hidden">
          <CardHeader className="py-4 border-b bg-secondary/10">
            <div className="flex justify-between items-start">
               <div>
                  <CardTitle>{selectedMember?.label || "Select a member"}</CardTitle>
                  <CardDescription className="mt-1">Detailed calculation report (ACI 318-19)</CardDescription>
               </div>
               {selectedMember && (
                 <span className={`px-2 py-1 rounded text-xs font-semibold ${
                   selectedMember.status === 'Pass' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' :
                   selectedMember.status === 'Fail' ? 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400' :
                   'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
                 }`}>
                   {selectedMember.status}
                 </span>
               )}
            </div>
          </CardHeader>
          <CardContent className="p-6 flex-1 overflow-y-auto bg-muted/10 font-mono text-sm">
            {selectedMember ? (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 border-b pb-1">Design Forces</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedMember.details.M_u !== undefined && <div>M_u (Ultimate Moment): {selectedMember.details.M_u} kN-m</div>}
                    {selectedMember.details.V_u !== undefined && <div>V_u (Ultimate Shear): {selectedMember.details.V_u} kN</div>}
                    {selectedMember.details.P_u !== undefined && <div>P_u (Ultimate Axial): {selectedMember.details.P_u} kN</div>}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 border-b pb-1">Capacities & Reinforcement</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedMember.details.As_req !== undefined && <div>As required: {selectedMember.details.As_req} mm²</div>}
                    {selectedMember.details.As_prov !== undefined && <div>As provided: {selectedMember.details.As_prov} mm²</div>}
                    {selectedMember.details.critical_ratio !== undefined && <div>Critical D/C Ratio: {selectedMember.details.critical_ratio.toFixed(2)}</div>}
                  </div>
                </div>

                <div className="bg-secondary/30 p-4 rounded-md border border-border">
                  <span className="font-semibold text-foreground">Design Note: </span> 
                  <span className="text-muted-foreground">{selectedMember.details.notes}</span>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                Select a member to view detailed calculations.
              </div>
            )}
          </CardContent>
          {selectedMember?.status === 'Fail' && (
            <CardFooter className="bg-rose-500/10 border-t border-rose-500/20 p-4">
              <Button variant="destructive" size="sm" className="w-full">Auto-Resize Section & Re-Analyze</Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  )
}
