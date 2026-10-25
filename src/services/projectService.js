import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { SEED_ACTIVE_PROJECT } from "../data/seedData";
import { basicAiEngine } from "./basicAiEngine";

const STORAGE_KEY = "jansetu_offline_projects";

function getLocalProjects() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [SEED_ACTIVE_PROJECT];
  } catch (e) {
    return [SEED_ACTIVE_PROJECT];
  }
}

function saveLocalProject(project) {
  try {
    const existing = getLocalProjects();
    const updated = [project, ...existing.filter(p => p.id !== project.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (e) {
    console.warn("Storage error", e);
  }
}

export const projectService = {
  async getProjects(params = {}) {
    try {
      const data = await apiClient.get(ENDPOINTS.PROJECTS.LIST, params);
      const items = Array.isArray(data) ? data : (data?.items || []);
      if (items.length > 0) return data;
      return getLocalProjects();
    } catch (err) {
      console.warn("Backend projects endpoint unavailable. Using seed project state.");
      return getLocalProjects();
    }
  },

  async getProjectById(id) {
    if (!id) throw new Error("Project ID is required");
    try {
      return await apiClient.get(ENDPOINTS.PROJECTS.DETAIL(id));
    } catch (err) {
      const local = getLocalProjects();
      const found = local.find(p => p.id === id || p.code === id);
      if (found) return found;
      return { ...SEED_ACTIVE_PROJECT, id };
    }
  },

  async getProjectByChallengeId(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    try {
      return await apiClient.get(ENDPOINTS.PROJECTS.BY_CHALLENGE(challengeId));
    } catch (err) {
      console.warn(`Backend project by challenge '${challengeId}' unavailable. Providing active project lifecycle.`);
      const local = getLocalProjects();
      const found = local.find(p => p.challengeId === challengeId);
      if (found) return found;

      // Synthesize project state with real seasonal risk intelligence
      const project = {
        ...SEED_ACTIVE_PROJECT,
        challengeId,
        risks: basicAiEngine.getProjectRiskIntelligence(SEED_ACTIVE_PROJECT)
      };
      saveLocalProject(project);
      return project;
    }
  },

  async createProject(projectData) {
    try {
      const res = await apiClient.post(ENDPOINTS.PROJECTS.CREATE, projectData);
      if (res?.id) return res;
    } catch (err) {
      console.warn("Backend project creation unavailable. Recording proposal locally.");
    }

    const newProject = {
      id: `proj-${Date.now().toString(36)}`,
      code: `PRJ-2026-${Math.random().toString(36).substring(2, 6).toUpperCase()}`,
      name: projectData.name || "Societal Research Prototype",
      challengeId: projectData.challengeId,
      institutionName: projectData.institutionName || "Higher Education Institution",
      leadFaculty: projectData.leadFaculty || "Principal Investigator",
      studentLead: projectData.studentLead || "Lead Student Researcher",
      budget: projectData.budget || "₹10,00,000",
      summary: projectData.summary || "",
      currentStage: "PROPOSAL_ACCEPTED",
      milestones: SEED_ACTIVE_PROJECT.milestones,
      risks: basicAiEngine.getProjectRiskIntelligence(projectData)
    };
    saveLocalProject(newProject);
    return newProject;
  },

  async updateMilestone(projectId, milestoneId, updates) {
    if (!projectId || !milestoneId) throw new Error("Project ID and Milestone ID are required");
    try {
      return await apiClient.patch(ENDPOINTS.PROJECTS.UPDATE_MILESTONE(projectId, milestoneId), updates);
    } catch (err) {
      console.warn("Backend milestone update unavailable. Updating locally.");
      const current = await this.getProjectById(projectId);
      if (current && Array.isArray(current.milestones)) {
        current.milestones = current.milestones.map(m => m.id === milestoneId ? { ...m, ...updates } : m);
        saveLocalProject(current);
      }
      return { success: true, milestoneId, updates };
    }
  },

  async updateTeam(projectId, teamMembers) {
    if (!projectId) throw new Error("Project ID is required");
    try {
      return await apiClient.post(ENDPOINTS.PROJECTS.TEAM(projectId), { teamMembers });
    } catch (err) {
      return { success: true, projectId, teamMembers };
    }
  },
};
