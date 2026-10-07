import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const industryService = {
  async getPartners(params = {}) {
    return apiClient.get(ENDPOINTS.INDUSTRY.PARTNERS, params);
  },

  async getPartnerById(id) {
    if (!id) throw new Error("Partner ID is required");
    return apiClient.get(ENDPOINTS.INDUSTRY.DETAIL(id));
  },

  async attachPartner(projectId, partnerId, supportType) {
    if (!projectId || !partnerId) throw new Error("Project ID and Partner ID are required");
    return apiClient.post(ENDPOINTS.INDUSTRY.ATTACH(projectId), { partnerId, supportType });
  },
};
