import axios from "axios"
import type { Project } from "@/types/project"

const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
})

export const api = {
  createProject: async (projectData: Project): Promise<Project> => {
    const response = await apiClient.post("/projects", projectData)
    return response.data
  },

  getProjects: async (): Promise<Project[]> => {
    const response = await apiClient.get("/projects")
    return response.data
  },

  getProject: async (id: string): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}`)
    return response.data
  },

  runAnalysis: async (data: { project_id: string; analysis_type: string; config?: Record<string, unknown> }) => {
    const response = await apiClient.post(`/projects/${data.project_id}/analysis-runs`, {
      analysis_type: data.analysis_type,
      config: data.config ?? {},
    })
    return response.data
  },

  cancelAnalysis: async (data: { project_id: string; run_id: string }) => {
    const response = await apiClient.post(`/projects/${data.project_id}/analysis-runs/${data.run_id}/cancel`)
    return response.data
  },

  retryAnalysis: async (data: { project_id: string; run_id: string }) => {
    const response = await apiClient.post(`/projects/${data.project_id}/analysis-runs/${data.run_id}/retry`)
    return response.data
  },
}