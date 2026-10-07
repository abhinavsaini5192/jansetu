import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const dashboardService = {
  async getStats() {
    return apiClient.get(ENDPOINTS.DASHBOARD.STATS);
  },

  async getDomainBreakdown() {
    return apiClient.get(ENDPOINTS.DASHBOARD.DOMAINS);
  },

  async getDistrictTrends() {
    return apiClient.get(ENDPOINTS.DASHBOARD.DISTRICTS);
  },

  async getRecentActivity() {
    return apiClient.get(ENDPOINTS.DASHBOARD.RECENT_ACTIVITY);
  },
};
