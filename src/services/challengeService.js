import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const challengeService = {
  async getChallenges(filters = {}) {
    return apiClient.get(ENDPOINTS.CHALLENGES.LIST, filters);
  },

  async getRecentChallenges(limit = 3) {
    return apiClient.get(ENDPOINTS.CHALLENGES.LIST, { limit, sortBy: "submittedAt", order: "desc" });
  },

  async getChallengeById(id) {
    if (!id) throw new Error("Challenge ID is required");
    return apiClient.get(ENDPOINTS.CHALLENGES.DETAIL(id));
  },

  async createChallenge(challengeData) {
    return apiClient.post(ENDPOINTS.CHALLENGES.CREATE, challengeData);
  },

  async updateChallenge(id, updates) {
    if (!id) throw new Error("Challenge ID is required");
    return apiClient.patch(ENDPOINTS.CHALLENGES.UPDATE(id), updates);
  },

  async deleteChallenge(id) {
    if (!id) throw new Error("Challenge ID is required");
    return apiClient.delete(ENDPOINTS.CHALLENGES.DELETE(id));
  },
};
