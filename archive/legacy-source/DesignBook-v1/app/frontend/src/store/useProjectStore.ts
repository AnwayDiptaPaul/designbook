import { create } from 'zustand'
import type { Project } from '@/types/project'

interface ProjectState {
  currentProject: Project | null
  activeFloorId: string | null
  
  // Actions
  setProject: (project: Project | null) => void
  updateProjectSettings: (settings: Partial<Project>) => void
  setActiveFloor: (floorId: string | null) => void
}

export const useProjectStore = create<ProjectState>((set) => ({
  currentProject: null,
  activeFloorId: null,
  
  setProject: (project) => set({ currentProject: project }),
  
  updateProjectSettings: (settings) => set((state) => {
    if (!state.currentProject) return state
    return {
      currentProject: {
        ...state.currentProject,
        ...settings,
      }
    }
  }),
  
  setActiveFloor: (floorId) => set({ activeFloorId: floorId })
}))
