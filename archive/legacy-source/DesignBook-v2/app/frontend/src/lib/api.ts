import axios from "axios"
import type { Project } from "@/types/project"

const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
})

export const api = {
  // Projects
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
  
  // Stubs for future grid/floor management
  // ...
}
