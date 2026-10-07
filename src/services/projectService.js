import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const projectService = {
  async getProjects(params = {}) {
    return apiClient.get(ENDPOINTS.PROJECTS.LIST, params);
  },

  async getProjectById(id) {
    if (!id) throw new Error("Project ID is required");
    return apiClient.get(ENDPOINTS.PROJECTS.DETAIL(id));
  },

  async getProjectByChallengeId(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.get(ENDPOINTS.PROJECTS.BY_CHALLENGE(challengeId));
  },

  async createProject(projectData) {
    return apiClient.post(ENDPOINTS.PROJECTS.CREATE, projectData);
  },

  async updateMilestone(projectId, milestoneId, updates) {
    if (!projectId || !milestoneId) throw new Error("Project ID and Milestone ID are required");
    return apiClient.patch(ENDPOINTS.PROJECTS.UPDATE_MILESTONE(projectId, milestoneId), updates);
  },

  async updateTeam(projectId, teamMembers) {
    if (!projectId) throw new Error("Project ID is required");
    return apiClient.post(ENDPOINTS.PROJECTS.TEAM(projectId), { teamMembers });
  },
};
