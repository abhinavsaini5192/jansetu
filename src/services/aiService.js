import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { basicAiEngine } from "./basicAiEngine";

export const aiService = {
  async getAnalysis(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    try {
      const data = await apiClient.get(ENDPOINTS.CHALLENGES.AI_ANALYSIS(challengeId));
      if (data && (data.detected_domain || data.domain)) {
        return data;
      }
      // If backend returned empty or not analyzed, fall back to basic AI engine
      return basicAiEngine.analyzeChallengeById(challengeId);
    } catch (err) {
      console.warn("Backend AI endpoint unavailable. Operating on Basic AI Engine fallback:", err.message);
      // Fallback to local basic AI engine so UI never fails
      return basicAiEngine.analyzeChallengeById(challengeId);
    }
  },

  async triggerAnalysis(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    try {
      const data = await apiClient.post(ENDPOINTS.CHALLENGES.TRIGGER_AI(challengeId));
      if (data && (data.detected_domain || data.domain)) {
        return data;
      }
      return basicAiEngine.analyzeChallengeById(challengeId);
    } catch (err) {
      console.warn("Backend AI trigger unavailable. Using Basic AI Engine fallback:", err.message);
      // Simulated processing latency for rich UI feedback
      await new Promise(res => setTimeout(res, 600));
      return basicAiEngine.analyzeChallengeById(challengeId);
    }
  },
};
