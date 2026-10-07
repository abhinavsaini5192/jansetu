import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const governmentService = {
  async getValidationQueue(filters = {}) {
    return apiClient.get(ENDPOINTS.GOVERNMENT.QUEUE, filters);
  },

  async validateChallenge(challengeId, { remarks, department }) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.post(ENDPOINTS.GOVERNMENT.VALIDATE(challengeId), { remarks, department });
  },

  async rejectChallenge(challengeId, { reason }) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.post(ENDPOINTS.GOVERNMENT.REJECT(challengeId), { reason });
  },

  async assignDepartment(challengeId, department) {
    if (!challengeId) throw new Error("Challenge ID is required");
    return apiClient.post(ENDPOINTS.GOVERNMENT.ASSIGN_DEPARTMENT(challengeId), { department });
  },

  async getDepartments() {
    return apiClient.get(ENDPOINTS.GOVERNMENT.DEPARTMENTS);
  },
};
