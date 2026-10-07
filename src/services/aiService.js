import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const aiService = {
  async getAnalysis(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.get(ENDPOINTS.CHALLENGES.AI_ANALYSIS(challengeId));
  },

  async triggerAnalysis(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.post(ENDPOINTS.CHALLENGES.TRIGGER_AI(challengeId));
  },
};
