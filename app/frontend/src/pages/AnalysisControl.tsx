import { useState, useCallback } from "react"
import { Play, CheckCircle, Loader2, Server, UploadCloud, Layers } from "lucide-react"
import { useDropzone } from "react-dropzone"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useProjectStore } from "@/store/useProjectStore"
import { api } from "@/lib/api"

export default function AnalysisControl() {
  const currentProject = useProjectStore((state) => state.currentProject)
  
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle")
  const [logs, setLogs] = useState<string[]>([])
  
  // Dynamic Analysis State
  const [timeHistoryFile, setTimeHistoryFile] = useState<File | null>(null)
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setTimeHistoryFile(acceptedFiles[0])
    }
  }, [])
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: { 'text/csv': ['.csv'], 'text/plain': ['.txt'] } 
  })
  
  const addLog = (msg: string) => setLogs(prev => [...prev, `${new Date().toLocaleTimeString()} - ${msg}`])
  
  const runAnalysis = async (mode: "STATIC" | "DYNAMIC") => {
    if (!currentProject?.id) {
      addLog("ERROR: No active project saved.")
      setStatus("error")
      return
    }
    if (mode === "DYNAMIC" && !timeHistoryFile) {
      addLog("ERROR: Upload a ground-motion record first.")
      setStatus("error")
      return
    }
    setIsRunning(true)
    setStatus("running")
    setProgress(0)
    setLogs([])
    addLog(`Requesting ${mode.toLowerCase()} analysis from the backend...`)
    try {
      await api.runAnalysis({ project_id: currentProject.id, analysis_type: mode.toLowerCase() })
      setProgress(100)
      setStatus("success")
      addLog("Analysis completed by the backend.")
    } catch (error: any) {
      setStatus("error")
      setProgress(0)
      const detail = error?.response?.data?.detail ?? "Analysis execution is not currently available."
      addLog(`Analysis unavailable: ${detail}`)
    } finally {
      setIsRunning(false)
    }
  }
  return (
    <div className="max-w-5xl mx-auto animate-in fade-in duration-500 pb-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Analysis Control & Engine</h1>
        <p className="text-muted-foreground">Trigger standard solver tasks or execute advanced OpenSees Time History simulations.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <Tabs defaultValue="static" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-2 p-1 bg-secondary/30 rounded-xl">
              <TabsTrigger value="static" className="text-[10px] uppercase tracking-wider font-bold">Static/Modal</TabsTrigger>
              <TabsTrigger value="dynamic" className="text-[10px] uppercase tracking-wider font-bold">Dynamic (NTHA)</TabsTrigger>
            </TabsList>
            <TabsList className="grid w-full grid-cols-2 mb-6 p-1 bg-secondary/30 rounded-xl">
              <TabsTrigger value="pushover" className="text-[10px] uppercase tracking-wider font-bold">Pushover</TabsTrigger>
              <TabsTrigger value="vibration" className="text-[10px] uppercase tracking-wider font-bold">Vibration Periods</TabsTrigger>
            </TabsList>
            
            <TabsContent value="static" className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <Card className="glass border-white/5">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center"><Layers className="mr-2 h-4 w-4 text-primary" /> Static & Modal</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-xs text-muted-foreground p-3 bg-secondary/30 rounded-lg">
                    Preview only; no persisted solver run is currently enabled.
                  </div>
                  <ul className="text-xs space-y-2 font-medium">
                    <li className="flex items-center"><CheckCircle className="mr-2 h-3 w-3 text-muted-foreground" /> Gravity envelopes: unavailable</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-3 w-3 text-muted-foreground" /> BNBC wind/seismic: unavailable</li>
                    <li className="flex items-center"><CheckCircle className="mr-2 h-3 w-3 text-muted-foreground" /> P-Delta: unavailable</li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button onClick={() => runAnalysis("STATIC")} disabled={isRunning} className="w-full">
                    {isRunning ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                    Compute Static Run
                  </Button>
                </CardFooter>
              </Card>
            </TabsContent>
            
            <TabsContent value="dynamic" className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <Card className="glass border-primary/20 shadow-[0_0_15px_rgba(var(--primary),0.05)]">
                <CardHeader>
                  <CardTitle className="text-lg text-primary flex items-center">Advanced Dynamics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div 
                    {...getRootProps()} 
                    className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
                      isDragActive ? 'border-primary bg-primary/10 scale-[1.02]' : 'border-border hover:border-primary/50 bg-secondary/20'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <UploadCloud className={`mx-auto h-8 w-8 mb-3 transition-colors ${isDragActive ? 'text-primary' : 'text-muted-foreground'}`} />
                    <p className="text-sm font-medium">
                      {timeHistoryFile ? timeHistoryFile.name : 'Drop Ground Motion CSV'}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-2 rounded bg-secondary/20 border border-white/5">
                      <p className="text-[10px] text-muted-foreground uppercase font-bold">Sampling rate</p>
                      <p className="text-xs font-mono">0.02s (Auto)</p>
                    </div>
                    <div className="p-2 rounded bg-secondary/20 border border-white/5">
                      <p className="text-[10px] text-muted-foreground uppercase font-bold">Duration</p>
                      <p className="text-xs font-mono">30.0s</p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button onClick={() => runAnalysis("DYNAMIC")} disabled={isRunning || !timeHistoryFile} className="w-full bg-primary/20 text-primary hover:bg-primary hover:text-white border border-primary/30">
                    {isRunning ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                    Execute NTHA Sequence
                  </Button>
                </CardFooter>
              </Card>
            </TabsContent>

            <TabsContent value="pushover" className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <Card className="glass border-amber-500/20">
                <CardHeader>
                  <CardTitle className="text-lg text-amber-500 items-center flex">
                    <Server className="mr-2 h-4 w-4" /> Pushover Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase text-muted-foreground">Control Node</label>
                      <div className="p-2 rounded bg-secondary/20 border border-white/5 text-xs">Not configured</div>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold uppercase text-muted-foreground">Target Drift</label>
                      <div className="p-2 rounded bg-secondary/20 border border-white/5 text-xs text-amber-500">Not configured</div>
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/10 text-[11px] text-amber-200/70 leading-relaxed italic">
                    Pushover execution is not currently available; no backbone curve is generated.
                  </div>
                </CardContent>
                <CardFooter>
                  <Button onClick={() => runAnalysis("STATIC")} disabled={isRunning} className="w-full bg-amber-500/10 text-amber-500 border border-amber-500/20 hover:bg-amber-500 hover:text-black">
                    {isRunning ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                    Pushover unavailable
                  </Button>
                </CardFooter>
              </Card>
            </TabsContent>

            <TabsContent value="vibration" className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <Card className="glass border-indigo-500/20">
                <CardHeader>
                  <CardTitle className="text-lg text-indigo-400">Modal Dynamics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                   <div className="space-y-2">
                      <div className="rounded-lg border border-indigo-500/10 bg-indigo-500/5 p-4 text-xs text-muted-foreground">No modal periods are available until a backend analysis run completes.</div>
                   </div>
                   <div className="text-[10px] text-center text-muted-foreground">
                      Modal results appear here only after a completed backend run.
                   </div>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" onClick={() => runAnalysis("STATIC")} disabled={isRunning} className="w-full border-indigo-500/20 text-indigo-400 hover:bg-indigo-500/10">
                    Refresh Modal Run
                  </Button>
                </CardFooter>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="lg:col-span-2">
          <Card className="h-full flex flex-col glass border-white/5">
            <CardHeader className="border-b border-white/5 pb-4">
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center"><Server className="mr-2 h-4 w-4 text-primary" /> Multi-core Solver Output</span>
                {status === "success" && <span className="text-[10px] bg-green-500/20 text-green-500 px-2 py-1 rounded uppercase tracking-wider font-bold">Convergence Complete</span>}
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col pt-6">
              <Progress value={progress} className="h-1 mb-6 bg-secondary" />
              <div className="flex-1 bg-background/50 font-mono text-xs p-4 rounded-xl overflow-y-auto min-h-[400px] border border-white/5">
                {logs.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50">
                    <Server className="h-12 w-12 mb-4" />
                    <p>Awaiting payload assignment...</p>
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    {logs.map((log, i) => (
                      <div key={i} className="text-emerald-400">
                        <span className="text-muted-foreground mr-3">{log.split(" - ")[0]}</span>
                        {log.split(" - ")[1]}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

