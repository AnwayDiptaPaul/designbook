import { useState } from "react"
import { FileText, Download, FileSpreadsheet, FilePieChart, Printer, Calculator } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Reports() {
  const [isGenerating, setIsGenerating] = useState(false)
  
  const handleDownloadPDF = () => {
    setIsGenerating(true)
    setTimeout(() => {
      setIsGenerating(false)
      // Actually this would hit the backend PDF endpoint and trigger a browser download.
      alert("PDF Generated and Downloaded.")
    }, 1500)
  }

  return (
    <div className="max-w-5xl mx-auto animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Reports & Detailing</h1>
        <p className="text-muted-foreground">Export analytical outputs, SVG detailing templates, BOQ, and calculation PDFs.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center"><FileText className="mr-2 h-5 w-5 text-red-500" /> Master Calculation PDF</CardTitle>
            <CardDescription>Generates the complete 10-chapter structural report conforming to authority submissions.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-secondary/30 p-4 rounded-md text-sm mb-4 space-y-2">
              <div className="flex justify-between border-b pb-1"><span>Target Code:</span> <span className="font-mono">BNBC 2020</span></div>
              <div className="flex justify-between border-b pb-1"><span>Include Load Combos:</span> <span className="font-mono">Yes</span></div>
              <div className="flex justify-between pb-1"><span>Include PM Curves:</span> <span className="font-mono">Yes</span></div>
            </div>
            <Button onClick={handleDownloadPDF} disabled={isGenerating} className="w-full">
              {isGenerating ? "Processing Document..." : <><Download className="mr-2 h-4 w-4" /> Download Report.pdf</>}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center"><Calculator className="mr-2 h-5 w-5 text-emerald-500" /> Bill of Quantities (BOQ)</CardTitle>
            <CardDescription>Volume, steel metrics, and PWD cost schedule exports.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="border rounded-md p-3 text-center bg-secondary/10">
                <div className="text-2xl font-bold text-primary">345 <span className="text-sm font-normal text-muted-foreground">m³</span></div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground mt-1">Total Concrete</div>
              </div>
              <div className="border rounded-md p-3 text-center bg-secondary/10">
                <div className="text-2xl font-bold text-primary">42.5 <span className="text-sm font-normal text-muted-foreground">ton</span></div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground mt-1">Total Steel</div>
              </div>
            </div>
            <Button variant="outline" className="w-full">
               <FileSpreadsheet className="mr-2 h-4 w-4 text-green-600" /> Export Excel Estimate
            </Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center"><FilePieChart className="mr-2 h-5 w-5 text-indigo-500" /> Auto-Generated Detailing (SVG)</CardTitle>
            <CardDescription>Vector drawing exports computed from design module transverse/longitudinal steel ratios.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center p-8 border-2 border-dashed rounded-lg bg-muted/20">
               <div className="text-center text-muted-foreground">
                  <Printer className="mx-auto h-8 w-8 mb-3 opacity-50" />
                  <p>Detailing preview canvas (Phase 9 integration)</p>
                  <Button variant="secondary" size="sm" className="mt-4">Download All SVGs</Button>
               </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
