import React from "react"
import { motion } from "framer-motion"
import { 
  MapPin, 
  Building2, 
  Shield, 
  ArrowRight,
  ClipboardList
} from "lucide-react"

export default function ProjectSetup() {
  const [step, setStep] = React.useState(1)

  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-20">
      {/* Step Indicator */}
      <section className="relative flex justify-between items-center px-4">
        <div className="absolute top-1/2 left-0 w-full h-px bg-border -z-10" />
        {[
          { label: "Basics", icon: ClipboardList },
          { label: "Location", icon: MapPin },
          { label: "Building", icon: Building2 },
          { label: "Standards", icon: Shield },
        ].map((s, idx) => (
          <div key={idx} className="flex flex-col items-center space-y-2">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-500 ${
              step > idx ? "bg-primary border-primary text-primary-foreground" : 
              step === idx + 1 ? "bg-background border-primary text-primary shadow-[0_0_15px_rgba(var(--primary),0.3)]" : 
              "bg-background border-border text-muted-foreground"
            }`}>
              <s.icon className="h-4 w-4" />
            </div>
            <span className={`text-[10px] uppercase font-black tracking-widest ${
              step >= idx + 1 ? "text-primary" : "text-muted-foreground"
            }`}>{s.label}</span>
          </div>
        ))}
      </section>

      {/* Form Content */}
      <motion.section 
        key={step}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="glass p-10 rounded-3xl space-y-8"
      >
        {step === 1 && (
          <div className="space-y-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-black">Project <span className="text-primary">Initialization</span></h2>
              <p className="text-muted-foreground">Start by defining the basic credentials of your structural project.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground ml-1">Project ID</label>
                <input type="text" placeholder="e.g. P-102" className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary transition-all text-sm outline-none" />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground ml-1">Project Name</label>
                <input type="text" placeholder="e.g. Skyline Apartments" className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary transition-all text-sm outline-none" />
              </div>
              <div className="md:col-span-2 space-y-2">
                <label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground ml-1">Description</label>
                <textarea placeholder="Brief overview of the project scope..." className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary transition-all text-sm outline-none h-32 resize-none" />
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-black">Site <span className="text-primary">Location</span></h2>
              <p className="text-muted-foreground">Identify where the building is located for seismic and wind load parameters.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground ml-1">City/Zone</label>
                <select className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary transition-all text-sm outline-none">
                  <option>Dhaka (Zone 2)</option>
                  <option>Chittagong (Zone 3)</option>
                  <option>Sylhet (Zone 4)</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-[10px] uppercase font-black tracking-widest text-muted-foreground ml-1">Soil Category</label>
                <select className="w-full bg-secondary/30 border border-border rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary transition-all text-sm outline-none">
                  <option>SA (Rock)</option>
                  <option>SB (Stiff Soil)</option>
                  <option>SC (Soft Soil)</option>
                  <option>SD (Very Soft Soil)</option>
                </select>
              </div>
            </div>
            <div className="p-6 rounded-2xl bg-primary/5 border border-primary/10 flex items-start space-x-4">
              <div className="p-2 rounded-lg bg-primary/20 text-primary">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm">Location Intelligence</h4>
                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">System will automatically apply BNBC 2020 seismic parameters Z=0.20 and peak ground acceleration values for this zone.</p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-6 border-t border-white/5">
          <button 
            onClick={() => setStep(Math.max(1, step - 1))}
            disabled={step === 1}
            className="px-6 py-2.5 rounded-full font-bold text-sm text-muted-foreground hover:text-foreground transition-colors disabled:opacity-0"
          >
            Back
          </button>
          <button 
            onClick={() => {
              if (step < 4) setStep(step + 1)
              else console.log("Finalize Setup")
            }}
            className="flex items-center bg-primary text-primary-foreground px-8 py-2.5 rounded-full font-bold text-sm hover:scale-105 transition-transform shadow-lg shadow-primary/20"
          >
            {step === 4 ? "Complete Setup" : "Next Step"}
            <ArrowRight className="ml-2 h-4 w-4" />
          </button>
        </div>
      </motion.section>

      {/* Quick Visualizer Preview Stub */}
      <section className="space-y-4">
        <h3 className="text-xs font-black tracking-widest text-muted-foreground uppercase ml-2 text-center">Environment Snapshot</h3>
        <div className="h-64 glass rounded-3xl relative overflow-hidden flex items-center justify-center group cursor-pointer">
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10" />
          <p className="z-20 font-mono text-[10px] text-white/50 group-hover:text-primary transition-colors">3D Visualization Preview Loading...</p>
          <Building2 className="absolute h-32 w-32 text-primary/10 -rotate-12 translate-x-1/2 group-hover:scale-110 transition-transform duration-700" />
        </div>
      </section>
    </div>
  )
}
