import React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate } from "react-router-dom"
import { Save, AlertCircle } from "lucide-react"

import type { Project } from "@/types/project"
import { ProjectSchema, DesignCodeEnum, UnitSystemEnum, BuildingOccupancyEnum, FrameTypeEnum, SoilClassEnum } from "@/types/project"
import { useProjectStore } from "@/store/useProjectStore"
import { api } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { FormField } from "@/components/FormField"

export default function ProjectSetup() {
  const navigate = useNavigate()
  const { currentProject, setProject } = useProjectStore()
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [submitError, setSubmitError] = React.useState<string | null>(null)

  const defaultValues: Partial<Project> = currentProject || {
    name: "",
    description: "",
    design_code: "BNBC_2020",
    unit_system: "METRIC",
    building_info: {
      occupancy_type: "RESIDENTIAL",
      number_of_stories: 5,
      total_height: 15.0,
      frame_type: "SMRF",
      importance_factor: 1.0,
    },
    site_data: {
      seismic_zone: "2",
      soil_class: "SC",
      wind_exposure: "A",
      basic_wind_speed: 65,
    }
  }

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Project>({
    resolver: zodResolver(ProjectSchema),
    defaultValues: defaultValues as any,
  })

  // We need wrapper components for native Select that integrate with forms or simply use register
  const onSubmit = async (data: Project) => {
    setIsSubmitting(true)
    setSubmitError(null)
    try {
      // API call to create or update project
      const savedProject = await api.createProject(data)
      setProject(savedProject)
      
      // Navigate to geometry next
      navigate("/geometry")
      
    } catch (error: any) {
      console.error("Failed to save project:", error)
      setSubmitError(error.response?.data?.detail || "An unexpected error occurred while saving.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Project Setup</h1>
        <p className="text-muted-foreground">Define general requirements, building information, and site parameters.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {submitError && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md flex items-center border border-destructive/20">
            <AlertCircle className="h-5 w-5 mr-2" />
            <p className="text-sm font-medium">{submitError}</p>
          </div>
        )}

        <Card>
          <CardHeader>
            <CardTitle>General Information</CardTitle>
            <CardDescription>Basic identifiers and global settings.</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              label="Project Name"
              name="name"
              register={register}
              errors={errors}
              placeholder="e.g. G+10 Commercial Plaza"
            />
            <FormField
              label="Description (Optional)"
              name="description"
              register={register}
              errors={errors}
              placeholder="Brief description of the structure"
            />
            
            <div className="space-y-2">
              <Label>Design Code</Label>
              <Select {...register("design_code")}>
                {DesignCodeEnum.options.map(o => <option key={o} value={o}>{o.replace(/_/g, " ")}</option>)}
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Unit System</Label>
              <Select {...register("unit_system")}>
                {UnitSystemEnum.options.map(o => <option key={o} value={o}>{o}</option>)}
              </Select>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Building Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Occupancy Type</Label>
                <Select {...register("building_info.occupancy_type")}>
                  {BuildingOccupancyEnum.options.map(o => <option key={o} value={o}>{o}</option>)}
                </Select>
              </div>
              
              <FormField
                label="Number of Stories"
                name="building_info.number_of_stories"
                type="number"
                register={register}
                errors={errors}
                min={1}
              />
              
              <FormField
                label="Total Height (m)"
                name="building_info.total_height"
                type="number"
                step="0.1"
                register={register}
                errors={errors}
              />
              
              <div className="space-y-2">
                <Label>Lateral Frame System</Label>
                <Select {...register("building_info.frame_type")}>
                  {FrameTypeEnum.options.map(o => <option key={o} value={o}>{o.replace(/_/g, " ")}</option>)}
                </Select>
              </div>
              
              <FormField
                label="Importance Factor (I)"
                name="building_info.importance_factor"
                type="number"
                step="0.05"
                register={register}
                errors={errors}
              />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Site Data & Exposures</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Seismic Zone</Label>
                <Select {...register("site_data.seismic_zone")}>
                  <option value="1">Zone 1 (Z = 0.12)</option>
                  <option value="2">Zone 2 (Z = 0.20)</option>
                  <option value="3">Zone 3 (Z = 0.28)</option>
                  <option value="4">Zone 4 (Z = 0.36)</option>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Soil Class (Site condition)</Label>
                <Select {...register("site_data.soil_class")}>
                  {SoilClassEnum.options.map(o => <option key={o} value={o}>Type {o}</option>)}
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Wind Exposure Category</Label>
                <Select {...register("site_data.wind_exposure")}>
                  <option value="A">Exposure A (Urban/City)</option>
                  <option value="B">Exposure B (Suburban)</option>
                  <option value="C">Exposure C (Open/Flat)</option>
                </Select>
              </div>
              
              <FormField
                label="Basic Wind Speed (m/s)"
                name="site_data.basic_wind_speed"
                type="number"
                step="0.1"
                register={register}
                errors={errors}
              />
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end space-x-4">
          <Button variant="outline" type="button" onClick={() => navigate("/")}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : <><Save className="h-4 w-4 mr-2" /> Save & Continue</>}
          </Button>
        </div>
      </form>
    </div>
  )
}
