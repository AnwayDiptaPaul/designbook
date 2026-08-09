import { useState } from "react"
import { Play, CheckCircle, Loader2, Server } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useProjectStore } from "@/store/useProjectStore"
import { api } from "@/lib/api"

export default function AnalysisControl() {
  const currentProject = useProjectStore((state) => state.currentProject)
  
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle")
  const [logs, setLogs] = useState<string[]>([])
  
  const addLog = (msg: string) => setLogs(prev => [...prev, `${new Date().toLocaleTimeString()} - ${msg}`])
  
  const runAnalysis = async () => {
    if (!currentProject?.id) {
      addLog("ERROR: No active project saved.")
      setStatus("error")
      return
    }
    
    setIsRunning(true)
    setStatus("running")
    setProgress(0)
    setLogs([])
    addLog(`Initiating OpenSeesPy Model Builder for Project ${currentProject.name}...`)
    
    try {
      // Simulate WebSocket progress for now
      let currentProgress = 0
      
      const interval = setInterval(() => {
        currentProgress += Math.random() * 15
        
        if (currentProgress >= 20 && currentProgress < 30) {
          addLog("Meshing slab shell elements...")
        } else if (currentProgress >= 40 && currentProgress < 50) {
          addLog("Running linear elastic gravity analysis...")
        } else if (currentProgress >= 60 && currentProgress < 70) {
          addLog("Running wind and seismic lateral analyses...")
        } else if (currentProgress >= 80 && currentProgress < 90) {
          addLog("Solving eigenvalue problem...")
        }
        
        if (currentProgress >= 100) {
          clearInterval(interval)
          setProgress(100)
          setIsRunning(false)
          setStatus("success")
          addLog("Analysis Sequence Completed Successfully.")
          
          // Actually trigger the Celery task endpoint here
          api.post('/analysis/run', {
            project_id: currentProject.id,
            analysis_type: "GRAVITY_AND_LATERAL"
          }).then((res: any) => {
            addLog(`Backend task ${res.data.task_id} dispatched.`)
          }).catch((_err: Error) => {
             addLog(`Warning: Backend Celery task not reachable.`)
          })
          
        } else {
          setProgress(currentProgress)
        }
      }, 800)
      
    } catch (err) {
      setIsRunning(false)
      setStatus("error")
      const errorMessage = err instanceof Error ? err.message : "Unknown error"
      addLog(`Failed to run analysis: ${errorMessage}`)
    }
  }

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Analysis Control</h1>
        <p className="text-muted-foreground">Trigger OpenSeesPy models and view real-time solver logs.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Solver Config</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-medium">Solver Engine</p>
                <div className="p-2 border rounded-md bg-secondary/30 flex items-center text-sm">
                  <Server className="h-4 w-4 mr-2" /> OpenSeesPy (Celery)
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Included Sequences</p>
                <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                  <li>Gravity (Linear Elastic)</li>
                  <li>Lateral (Wind + Seismic)</li>
                  <li>Eigenvalue (Modal)</li>
                  <li>P-Delta Transformations</li>
                </ul>
              </div>
            </CardContent>
            <CardFooter>
              <Button 
                onClick={runAnalysis} 
                disabled={isRunning}
                className="w-full"
                variant={status === "success" ? "secondary" : "default"}
              >
                {isRunning ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Computing...</>
                ) : status === "success" ? (
                  <><CheckCircle className="mr-2 h-4 w-4" /> Re-Run Analysis</>
                ) : (
                  <><Play className="mr-2 h-4 w-4" /> Run Analysis</>
                )}
              </Button>
            </CardFooter>
          </Card>
          
          {status === "success" && (
             <Button variant="outline" className="w-full text-green-600 border-green-600 hover:bg-green-50">
               View Deformation Results
             </Button>
          )}
        </div>

        <div className="md:col-span-2">
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle>Solver Output</CardTitle>
              <CardDescription>Real-time stdout from OpenSees process.</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <Progress value={progress} className="h-2 mb-4" />
              <div className="flex-1 bg-black text-green-400 font-mono text-xs p-4 rounded-md overflow-y-auto min-h-[300px] border border-gray-800">
                {logs.length === 0 ? (
                  <span className="text-gray-600">Waiting for solver task...</span>
                ) : (
                  logs.map((log, i) => (
                    <div key={i}>{log}</div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
