import React from "react"
import { Box, Layers } from "lucide-react"

interface ThreeViewerProps {
  mode: "geometry" | "results"
}

export default function ThreeViewer({ mode }: ThreeViewerProps) {
  // Mock CSS-based isometric 3D building visualizer
  // In a full R3F implementation, this would contain <Canvas><OrbitControls/><mesh>...</Canvas>
  
  return (
    <div className="w-full h-full bg-[#f8fafc] dark:bg-[#090b14] relative flex items-center justify-center overflow-hidden">
       {/* Background Grid Accent */}
       <div className="absolute inset-0" style={{ 
         backgroundImage: 'linear-gradient(rgba(100,100,100,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(100,100,100,0.1) 1px, transparent 1px)', 
         backgroundSize: '40px 40px' 
       }}></div>

       {/* Isometric Building Container */}
       <div className="relative transform rotate-x-[60deg] rotate-z-[-45deg] scale-150 transition-all duration-1000 origin-center select-none" style={{ transformStyle: 'preserve-3d' }}>
          
          {/* Base Grid Plane */}
          <div className="w-64 h-64 border-2 border-primary/20 grid grid-cols-4 grid-rows-4 relative shadow-2xl">
              {[...Array(16)].map((_, i) => (
                 <div key={i} className="border border-primary/10"></div>
              ))}
              
              {/* Columns */}
              {[...Array(25)].map((_, i) => {
                 const x = (i % 5) * 25
                 const y = Math.floor(i / 5) * 25
                 return (
                   <div key={`col-${i}`} className="absolute bg-slate-800 dark:bg-slate-300 w-1.5 shadow-[0_0_10px_rgba(0,0,0,0.5)]" 
                        style={{ left: `${x}%`, top: `${y}%`, height: '80px', transform: 'translateZ(0px) rotateX(-90deg)', transformOrigin: 'bottom' }}>
                   </div>
                 )
              })}
              
              {/* Floor Slab (Level 1) */}
              <div className="absolute w-full h-full border border-blue-500/50 bg-blue-500/10"
                   style={{ transform: 'translateZ(80px)' }}>
                 {/* Deformed shape overlay if results mode */}
                 {mode === "results" && (
                    <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/30 via-green-400/30 to-rose-500/40 opacity-70"></div>
                 )}
              </div>
              
              {/* Floor Slab (Level 2) - Smaller footprint */}
              <div className="absolute w-[75%] h-[75%] border border-blue-500/50 bg-blue-500/10 shadow-2xl"
                   style={{ top: '12.5%', left: '12.5%', transform: 'translateZ(160px)' }}>
                 {mode === "results" && (
                    <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/40 via-yellow-400/40 to-rose-500/50 opacity-80"></div>
                 )}
              </div>
          </div>
          
       </div>
       
       {/* UI Overlays */}
       <div className="absolute bottom-6 right-6 flex flex-col items-center opacity-50 space-y-2 pointer-events-none">
          <div className="w-16 h-16 border-2 border-muted-foreground/30 relative transform rotate-x-[60deg] rotate-z-[-45deg]">
             <div className="absolute top-0 left-0 w-full h-0.5 bg-red-500 origin-left" style={{transform: 'rotate(0deg)'}}></div>
             <div className="absolute top-0 left-0 w-0.5 h-full bg-green-500 origin-top" style={{transform: 'rotate(0deg)'}}></div>
             <div className="absolute top-0 left-0 w-0.5 h-full bg-blue-500 origin-top" style={{transform: 'rotate(-90deg) translate(-50%, -50%) rotateX(-90deg)'}}></div>
          </div>
          <span className="text-[10px] font-mono font-bold tracking-widest uppercase">Global Axes</span>
       </div>
       
       <div className="absolute top-4 right-4 bg-background/50 backdrop-blur-md px-3 py-1.5 rounded-full border shadow-sm font-semibold text-xs flex items-center">
          {mode === "geometry" ? <><Box className="w-3 h-3 mr-1.5 text-primary" /> Edit Mode</> : <><Layers className="w-3 h-3 mr-1.5 text-indigo-500" /> Results Render</>}
       </div>
    </div>
  )
}
