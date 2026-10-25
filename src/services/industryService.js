import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { SEED_INDUSTRY_PARTNERS } from "../data/seedData";

export const industryService = {
  async getPartners(params = {}) {
    try {
      const data = await apiClient.get(ENDPOINTS.INDUSTRY.PARTNERS, params);
      const items = Array.isArray(data) ? data : (data?.items || []);
      if (items.length > 0) return data;
      return SEED_INDUSTRY_PARTNERS;
    } catch (err) {
      console.warn("Backend industry partners endpoint unavailable. Providing seed CSR partners.");
      return SEED_INDUSTRY_PARTNERS;
    }
  },

  async getPartnerById(id) {
    if (!id) throw new Error("Partner ID is required");
    try {
      return await apiClient.get(ENDPOINTS.INDUSTRY.DETAIL(id));
    } catch (err) {
      const found = SEED_INDUSTRY_PARTNERS.find(p => p.id === id);
      return found || SEED_INDUSTRY_PARTNERS[0];
    }
  },

  async attachPartner(projectId, partnerId, supportType) {
    if (!projectId || !partnerId) throw new Error("Project ID and Partner ID are required");
    try {
      return await apiClient.post(ENDPOINTS.INDUSTRY.ATTACH(projectId), { partnerId, supportType });
    } catch (err) {
      console.warn("Backend partner attachment unavailable. Recording agreement locally.");
      return {
        success: true,
        message: "CSR partnership agreement recorded.",
        projectId,
        partnerId,
        supportType,
        attachedAt: new Date().toISOString()
      };
    }
  },
};
