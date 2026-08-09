import { z } from "zod"

export const BuildingOccupancyEnum = z.enum(["RESIDENTIAL", "COMMERCIAL", "INDUSTRIAL", "HOSPITAL", "SCHOOL", "ASSEMBLY", "OTHER"])
export const SeismicZoneEnum = z.enum(["1", "2", "3", "4"])
export const SoilClassEnum = z.enum(["SA", "SB", "SC", "SD", "SE", "SF"])
export const WindExposureEnum = z.enum(["A", "B", "C"])
export const FrameTypeEnum = z.enum(["SMRF", "IMRF", "OMRF", "SHEAR_WALL", "DUAL_SYSTEM"])
export const DesignCodeEnum = z.enum(["BNBC_2020", "ACI_318_19", "ACI_318_14"])
export const UnitSystemEnum = z.enum(["METRIC", "IMPERIAL"])

export const BuildingInfoSchema = z.object({
  occupancy_type: BuildingOccupancyEnum,
  number_of_stories: z.number().int().min(1, "Must have at least 1 story"),
  total_height: z.number().positive("Height must be positive"),
  frame_type: FrameTypeEnum,
  importance_factor: z.number().min(1.0).max(1.5),
})

export const SiteDataSchema = z.object({
  seismic_zone: SeismicZoneEnum,
  soil_class: SoilClassEnum,
  wind_exposure: WindExposureEnum,
  basic_wind_speed: z.number().positive("Wind speed must be positive"),
})

export const ProjectSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string().min(3, "Project name must be at least 3 characters").max(100),
  description: z.string().optional(),
  design_code: DesignCodeEnum,
  unit_system: UnitSystemEnum,
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  
  building_info: BuildingInfoSchema,
  site_data: SiteDataSchema,
})

export const GridDefinitionSchema = z.object({
  id: z.string().uuid().optional(),
  project_id: z.string().uuid().optional(),
  label: z.string().min(1, "Label is required"),
  direction: z.enum(["X", "Y"]),
  coordinate: z.number(),
})

export const FloorDefinitionSchema = z.object({
  id: z.string().uuid().optional(),
  project_id: z.string().uuid().optional(),
  name: z.string().min(1, "Floor name is required"),
  elevation: z.number(),
  height: z.number().positive(),
  is_master: z.boolean().default(false),
  similar_to_id: z.string().uuid().optional().nullable(),
})

export type BuildingInfo = z.infer<typeof BuildingInfoSchema>
export type SiteData = z.infer<typeof SiteDataSchema>
export type Project = z.infer<typeof ProjectSchema>
export type GridDefinition = z.infer<typeof GridDefinitionSchema>
export type FloorDefinition = z.infer<typeof FloorDefinitionSchema>
