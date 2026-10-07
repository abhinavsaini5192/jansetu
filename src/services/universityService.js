import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const universityService = {
  async getUniversities(params = {}) {
    return apiClient.get(ENDPOINTS.UNIVERSITIES.LIST, params);
  },

  async getUniversityById(id) {
    if (!id) throw new Error("University ID is required");
    return apiClient.get(ENDPOINTS.UNIVERSITIES.DETAIL(id));
  },

  async getMatchesForChallenge(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.get(ENDPOINTS.CHALLENGES.MATCHES(challengeId));
  },

  async assignChallengeToUniversity(challengeId, universityId) {
    if (!challengeId || !universityId) throw new Error("Challenge ID and University ID are required");
    return apiClient.post(ENDPOINTS.CHALLENGES.ASSIGN_HEI(challengeId), { universityId });
  },
};
