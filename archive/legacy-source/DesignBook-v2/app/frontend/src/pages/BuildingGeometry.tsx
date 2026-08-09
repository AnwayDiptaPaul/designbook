import { useState } from "react"
import { useForm, useFieldArray } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Save, Plus, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

const GridArraySchema = z.object({
  xGrids: z.array(z.object({ label: z.string().min(1), coordinate: z.number() })).min(2, "At least 2 X grids required"),
  yGrids: z.array(z.object({ label: z.string().min(1), coordinate: z.number() })).min(2, "At least 2 Y grids required"),
})
type GridData = z.infer<typeof GridArraySchema>

export function GridDefinitionForm() {
  const { register, control, handleSubmit, formState: { errors } } = useForm<GridData>({
    resolver: zodResolver(GridArraySchema),
    defaultValues: {
      xGrids: [{ label: "A", coordinate: 0 }, { label: "B", coordinate: 5 }],
      yGrids: [{ label: "1", coordinate: 0 }, { label: "2", coordinate: 4 }],
    }
  })

  const { fields: xFields, append: appendX, remove: removeX } = useFieldArray({ control, name: "xGrids" })
  const { fields: yFields, append: appendY, remove: removeY } = useFieldArray({ control, name: "yGrids" })

  const onSubmit = (data: GridData) => {
    console.log("Grid Definitions Data", data)
    // TODO: Send to API
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>X-Direction Grids</CardTitle>
                <CardDescription>Vertical lines along X axis.</CardDescription>
              </div>
              <Button type="button" size="sm" variant="outline" onClick={() => appendX({ label: "", coordinate: 0 })}>
                <Plus className="h-4 w-4 mr-1" /> Add
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {xFields.map((field, index) => (
              <div key={field.id} className="flex space-x-2 items-center">
                <div className="w-20">
                  <Input placeholder="Label" {...register(`xGrids.${index}.label` as const)} />
                </div>
                <div className="flex-1">
                  <Input type="number" step="0.1" placeholder="Coordinate (m)" {...register(`xGrids.${index}.coordinate` as const, { valueAsNumber: true })} />
                </div>
                <Button type="button" variant="ghost" size="icon" onClick={() => removeX(index)} className="text-destructive">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            {errors.xGrids && <p className="text-sm text-destructive">{errors.xGrids.message}</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Y-Direction Grids</CardTitle>
                <CardDescription>Horizontal lines along Y axis.</CardDescription>
              </div>
              <Button type="button" size="sm" variant="outline" onClick={() => appendY({ label: "", coordinate: 0 })}>
                <Plus className="h-4 w-4 mr-1" /> Add
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {yFields.map((field, index) => (
              <div key={field.id} className="flex space-x-2 items-center">
                <div className="w-20">
                  <Input placeholder="Label" {...register(`yGrids.${index}.label` as const)} />
                </div>
                <div className="flex-1">
                  <Input type="number" step="0.1" placeholder="Coordinate (m)" {...register(`yGrids.${index}.coordinate` as const, { valueAsNumber: true })} />
                </div>
                <Button type="button" variant="ghost" size="icon" onClick={() => removeY(index)} className="text-destructive">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            {errors.yGrids && <p className="text-sm text-destructive">{errors.yGrids.message}</p>}
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-end">
        <Button type="submit">
          <Save className="h-4 w-4 mr-2" /> Save Grid
        </Button>
      </div>
    </form>
  )
}

const FloorArraySchema = z.object({
  floors: z.array(z.object({
    name: z.string().min(1),
    elevation: z.number(),
    height: z.number().positive(),
  })).min(1, "At least one floor is required")
})
type FloorData = z.infer<typeof FloorArraySchema>

export function FloorDefinitionForm() {
  const { register, control, handleSubmit, formState: { errors } } = useForm<FloorData>({
    resolver: zodResolver(FloorArraySchema),
    defaultValues: {
      floors: [
        { name: "Base", elevation: -1.5, height: 1.5 },
        { name: "Ground Floor", elevation: 0.0, height: 3.0 },
      ]
    }
  })

  const { fields, append, remove } = useFieldArray({ control, name: "floors" })

  const onSubmit = (data: FloorData) => {
    console.log("Floor Definitions Data", data)
    // TODO: persist via API
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Floor Definitions</CardTitle>
              <CardDescription>Story heights and elevations. Base must be below 0.</CardDescription>
            </div>
            <Button type="button" size="sm" variant="outline" onClick={() => append({ name: "", elevation: 0, height: 3.0 })}>
              <Plus className="h-4 w-4 mr-1" /> Add Floor
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-12 gap-2 text-sm font-medium text-muted-foreground mb-2">
            <div className="col-span-5">Story Name</div>
            <div className="col-span-3">Height (m)</div>
            <div className="col-span-3">Elevation (m)</div>
            <div className="col-span-1"></div>
          </div>
          {fields.map((field, index) => (
            <div key={field.id} className="grid grid-cols-12 gap-2 items-center">
              <div className="col-span-5">
                <Input placeholder="e.g. Floor 1" {...register(`floors.${index}.name` as const)} />
              </div>
              <div className="col-span-3">
                <Input type="number" step="0.1" placeholder="3.0" {...register(`floors.${index}.height` as const, { valueAsNumber: true })} />
              </div>
              <div className="col-span-3">
                <Input type="number" step="0.1" {...register(`floors.${index}.elevation` as const, { valueAsNumber: true })} />
              </div>
              <div className="col-span-1 text-right">
                <Button type="button" variant="ghost" size="icon" onClick={() => remove(index)} className="text-destructive">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          {errors.floors && <p className="text-sm text-destructive">{errors.floors.message}</p>}
        </CardContent>
      </Card>

      <div className="flex justify-end space-x-4">
        <Button type="button" variant="outline">
          Skip
        </Button>
        <Button type="submit">
          <Save className="h-4 w-4 mr-2" /> Save Floors
        </Button>
      </div>
    </form>
  )
}

export default function BuildingGeometry() {
  const [activeTab, setActiveTab] = useState<"grids" | "floors">("grids")

  return (
    <div className="max-w-5xl mx-auto animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Building Geometry</h1>
        <p className="text-muted-foreground">Define the structural grids and floor levels for your building.</p>
      </div>

      <div className="flex space-x-2 border-b border-border mb-6">
        <button
          className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
            activeTab === "grids" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
          }`}
          onClick={() => setActiveTab("grids")}
        >
          Grid Definitions
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
            activeTab === "floors" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
          }`}
          onClick={() => setActiveTab("floors")}
        >
          Floor & Story Levels
        </button>
      </div>

      {activeTab === "grids" && <GridDefinitionForm />}
      {activeTab === "floors" && <FloorDefinitionForm />}
    </div>
  )
}
