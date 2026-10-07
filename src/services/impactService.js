import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const impactService = {
  async getImpactByChallengeId(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.get(ENDPOINTS.IMPACT.BY_CHALLENGE(challengeId));
  },

  async submitEvidence(challengeId, evidenceData) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.post(ENDPOINTS.IMPACT.SUBMIT_EVIDENCE(challengeId), evidenceData);
  },

  async verifyImpact(impactId, verificationData) {
    if (!impactId) throw new Error("Impact ID is required");
    return apiClient.post(ENDPOINTS.IMPACT.VERIFY(impactId), verificationData);
  },
};
