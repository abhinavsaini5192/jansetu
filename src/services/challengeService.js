import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { SEED_CHALLENGES } from "../data/seedData";

const STORAGE_KEY = "jansetu_offline_challenges";
const DELETED_KEY = "jansetu_deleted_challenge_ids";

function getDeletedIds() {
  try {
    const raw = localStorage.getItem(DELETED_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function getLocalChallenges() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveLocalChallenge(challenge) {
  try {
    const existing = getLocalChallenges();
    const updated = [challenge, ...existing.filter(c => c.id !== challenge.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (e) {
    console.warn("Could not save to localStorage", e);
  }
}

export const challengeService = {
  async getChallenges(filters = {}) {
    const deleted = getDeletedIds();

    try {
      const data = await apiClient.get(ENDPOINTS.CHALLENGES.LIST, filters);
      const items = Array.isArray(data) ? data : (data?.items || []);
      if (items.length > 0) {
        // Filter out deleted
        const activeItems = items.filter(c => !deleted.includes(c.id) && !deleted.includes(c.reference_code));
        const local = getLocalChallenges().filter(c => !deleted.includes(c.id));
        // Merge any local ones not already present
        const merged = [...local, ...activeItems.filter(ai => !local.some(l => l.id === ai.id))];
        return Array.isArray(data) ? merged : { ...data, items: merged, total: merged.length };
      }
    } catch (err) {
      console.warn("Backend challenges endpoint unavailable. Using seed catalog:", err.message);
    }

    const local = getLocalChallenges();
    const merged = [...local, ...SEED_CHALLENGES.filter(s => !local.some(l => l.id === s.id))]
      .filter(c => !deleted.includes(c.id) && !deleted.includes(c.reference_code));
    return merged;
  },

  async getRecentChallenges(limit = 3) {
    try {
      const res = await apiClient.get(ENDPOINTS.CHALLENGES.LIST, { limit, sortBy: "submittedAt", order: "desc" });
      const items = Array.isArray(res) ? res : (res?.items || []);
      if (items.length > 0) return items;
    } catch (err) {}

    const all = await this.getChallenges();
    const items = Array.isArray(all) ? all : (all?.items || []);
    return items.slice(0, limit);
  },

  async getChallengeById(id) {
    if (!id) throw new Error("Challenge ID is required");
    try {
      return await apiClient.get(ENDPOINTS.CHALLENGES.DETAIL(id));
    } catch (err) {
      console.warn(`Backend detail for challenge '${id}' unavailable. Checking local seed catalog.`);
      const local = getLocalChallenges();
      const found = local.find(c => c.id === id || c.reference_code === id || c.referenceCode === id) ||
                    SEED_CHALLENGES.find(c => c.id === id || c.reference_code === id || c.referenceCode === id);
      if (found) return found;
      return SEED_CHALLENGES[0];
    }
  },

  async createChallenge(challengeData) {
    const id = `c-${Date.now().toString(36)}`;
    const refCode = `JS-2026-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;

    const newChallenge = {
      id,
      reference_code: refCode,
      referenceCode: refCode,
      title: challengeData.title,
      titleHi: challengeData.titleHi || "",
      description: challengeData.description,
      domain: challengeData.domain || "water_sanitation",
      district: challengeData.location?.district || "Ranchi",
      location: challengeData.location || { district: "Ranchi" },
      urgency: challengeData.urgency || "HIGH",
      priority: challengeData.urgency || "HIGH",
      status: "SUBMITTED",
      validation_status: "SUBMITTED",
      affected_population: challengeData.affectedPopulation || "Community residents",
      submitted_at: new Date().toISOString(),
      attachments: challengeData.attachments || [],
      submitted_by_user_id: challengeData.submitted_by_user_id || challengeData.userId || "usr_citizen",
      submitter_email: challengeData.submitter_email || challengeData.email || "citizen@jansetu.gov.in",
      submitter_name: challengeData.submitter_name || challengeData.fullName || "Community Citizen",
      is_user_submitted: true,
    };

    try {
      const res = await apiClient.post(ENDPOINTS.CHALLENGES.CREATE, challengeData);
      if (res?.id) {
        const mergedRes = { ...newChallenge, ...res, id: res.id, is_user_submitted: true };
        saveLocalChallenge(mergedRes);
        return mergedRes;
      }
    } catch (err) {
      console.warn("Backend challenge creation unavailable. Recording challenge locally:", err.message);
    }

    saveLocalChallenge(newChallenge);
    return newChallenge;
  },

  async updateChallenge(id, updates) {
    if (!id) throw new Error("Challenge ID is required");
    let current = null;
    try {
      current = await this.getChallengeById(id);
    } catch (e) {
      current = { id };
    }

    const updated = {
      ...current,
      ...updates,
      updated_at: new Date().toISOString(),
    };

    saveLocalChallenge(updated);

    try {
      await apiClient.patch(ENDPOINTS.CHALLENGES.UPDATE(id), updates);
    } catch (err) {
      console.warn("Backend challenge update unavailable. Updated locally.");
    }

    return updated;
  },

  async deleteChallenge(id) {
    if (!id) throw new Error("Challenge ID is required");

    // Add to deleted IDs registry
    try {
      const deleted = getDeletedIds();
      if (!deleted.includes(id)) {
        deleted.push(id);
        localStorage.setItem(DELETED_KEY, JSON.stringify(deleted));
      }
      const local = getLocalChallenges().filter(c => c.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(local));
    } catch (e) {
      console.warn("Error recording deletion in localStorage", e);
    }

    try {
      await apiClient.delete(ENDPOINTS.CHALLENGES.DELETE(id));
    } catch (err) {
      console.warn("Backend challenge deletion unavailable. Removed locally.");
    }

    return { success: true };
  },
};
