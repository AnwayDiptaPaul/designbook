import { Box, LockKeyhole } from "lucide-react"

interface ThreeViewerProps {
  mode: "geometry" | "results"
}

export default function ThreeViewer({ mode }: ThreeViewerProps) {
  return (
    <div className="relative flex h-full min-h-[260px] w-full items-center justify-center overflow-hidden bg-[#f8fafc] dark:bg-[#090b14]">
      <div className="absolute inset-0 opacity-30" style={{ backgroundImage: "linear-gradient(rgba(100,100,100,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(100,100,100,0.1) 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
      <div className="relative z-10 max-w-sm px-6 text-center text-muted-foreground">
        <LockKeyhole className="mx-auto mb-4 h-10 w-10 opacity-50" />
        <p className="font-semibold">No {mode === "geometry" ? "project geometry" : "analysis result"} loaded</p>
        <p className="mt-2 text-xs">The viewer will render only server-backed, snapshot-bound model data.</p>
      </div>
      <div className="absolute bottom-4 right-4 flex items-center rounded-full border bg-background/50 px-3 py-1.5 text-xs font-semibold shadow-sm backdrop-blur-md">
        <Box className="mr-1.5 h-3 w-3 text-primary" /> {mode === "geometry" ? "Geometry view" : "Results view"}
      </div>
    </div>
  )
}