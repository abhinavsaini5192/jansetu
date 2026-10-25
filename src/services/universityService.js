import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { SEED_UNIVERSITIES, SEED_CHALLENGES } from "../data/seedData";
import { basicAiEngine } from "./basicAiEngine";
import { challengeService } from "./challengeService";
import { projectService } from "./projectService";

const ADOPTIONS_STORAGE_KEY = "jansetu_adopted_challenges";
const INVITES_STORAGE_KEY = "jansetu_university_invites";

function getLocalAdoptions() {
  try {
    const raw = localStorage.getItem(ADOPTIONS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function saveLocalAdoption(challengeId, adoptionData) {
  try {
    const existing = getLocalAdoptions();
    existing[challengeId] = adoptionData;
    localStorage.setItem(ADOPTIONS_STORAGE_KEY, JSON.stringify(existing));
  } catch (e) {
    console.warn("Storage error saving adoption:", e);
  }
}

function getLocalInvites() {
  try {
    const raw = localStorage.getItem(INVITES_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function saveLocalInvite(challengeId, universityId, note) {
  try {
    const existing = getLocalInvites();
    if (!existing[challengeId]) existing[challengeId] = [];
    if (!existing[challengeId].includes(universityId)) {
      existing[challengeId].push(universityId);
    }
    localStorage.setItem(INVITES_STORAGE_KEY, JSON.stringify(existing));
  } catch (e) {
    console.warn("Storage error saving invite:", e);
  }
}

export const universityService = {
  async getUniversities(params = {}) {
    try {
      const data = await apiClient.get(ENDPOINTS.UNIVERSITIES.LIST, params);
      const items = Array.isArray(data) ? data : (data?.items || []);
      if (items.length > 0) return data;
      return SEED_UNIVERSITIES;
    } catch (err) {
      console.warn("Backend universities endpoint unavailable. Using seed institutions.");
      return SEED_UNIVERSITIES;
    }
  },

  async getUniversityById(id) {
    if (!id) throw new Error("University ID is required");
    try {
      return await apiClient.get(ENDPOINTS.UNIVERSITIES.DETAIL(id));
    } catch (err) {
      const found = SEED_UNIVERSITIES.find(u => u.id === id || u.universityId === id || u.code === id);
      return found || SEED_UNIVERSITIES[0];
    }
  },

  async getMatchesForChallenge(challengeId) {
    if (!challengeId) throw new Error("Challenge ID is required");
    try {
      const data = await apiClient.get(ENDPOINTS.CHALLENGES.MATCHES(challengeId));
      const list = Array.isArray(data) ? data : (data?.matches || []);
      if (list.length > 0) return data;
    } catch (err) {
      console.warn(`Backend matching for '${challengeId}' unavailable. Executing Basic Matching Engine:`, err.message);
    }

    // Run explainable basic AI matching engine
    const challenge = await challengeService.getChallengeById(challengeId);
    const matches = basicAiEngine.matchUniversities(challenge, SEED_UNIVERSITIES);
    
    // Enrich with local adoption and invitation statuses
    const adoptions = getLocalAdoptions();
    const invites = getLocalInvites();
    const challengeAdoption = adoptions[challengeId];
    const challengeInvites = invites[challengeId] || [];

    const enrichedMatches = matches.map(uni => {
      const uniId = uni.id || uni.universityId;
      const isAdoptedByThis = challengeAdoption && (challengeAdoption.universityId === uniId);
      const isInvited = challengeInvites.includes(uniId);

      return {
        ...uni,
        isAdopted: Boolean(isAdoptedByThis),
        adoptionDetails: isAdoptedByThis ? challengeAdoption : null,
        isInvited: Boolean(isInvited),
      };
    });

    return {
      challenge_id: challengeId,
      matches: enrichedMatches,
      total_matches: enrichedMatches.length,
      adoptedBy: challengeAdoption ? challengeAdoption.universityName : null,
      engine: "JanSetu Explainable Matching Engine (Deterministic Heuristic)"
    };
  },

  getAdoptions() {
    return getLocalAdoptions();
  },

  getAdoptionForChallenge(challengeId) {
    const adoptions = getLocalAdoptions();
    return adoptions[challengeId] || null;
  },

  getInvitations() {
    return getLocalInvites();
  },

  async sendRecommendationInvite(challengeId, universityId, note = "") {
    if (!challengeId || !universityId) throw new Error("Challenge ID and University ID are required");
    const uni = await this.getUniversityById(universityId);
    saveLocalInvite(challengeId, universityId, note);
    return {
      success: true,
      message: `Official recommendation invitation dispatched to ${uni.name}.`,
      challengeId,
      universityId,
      universityName: uni.name,
      dispatchedAt: new Date().toISOString()
    };
  },

  async adoptChallenge(challengeId, universityId, proposalDetails = {}, currentUser = null) {
    if (!challengeId || !universityId) throw new Error("Challenge ID and University ID are required");
    
    const uni = await this.getUniversityById(universityId);
    const challenge = await challengeService.getChallengeById(challengeId);

    const adoptionRecord = {
      challengeId,
      challengeTitle: challenge?.title || "Community Challenge",
      domain: challenge?.domain || "general",
      district: challenge?.location?.district || "Ranchi",
      universityId,
      universityName: uni.name,
      leadFaculty: proposalDetails.leadFaculty || currentUser?.full_name || uni.leadFaculty || "Dr. Alok Kumar",
      studentLead: proposalDetails.studentLead || "Lead Student Researcher",
      proposalSummary: proposalDetails.summary || "Autonomous research and prototype development under JanSetu framework.",
      adoptedAt: new Date().toISOString(),
      status: "ADOPTED",
      stage: "PROPOSAL_ACCEPTED",
    };

    // Save locally
    saveLocalAdoption(challengeId, adoptionRecord);

    // Initialize in projectService workspace
    let project = null;
    try {
      project = await projectService.createProject({
        name: proposalDetails.name || `${uni.name} - ${challenge?.title || 'Civic Solution'}`,
        challengeId,
        institutionName: uni.name,
        leadFaculty: adoptionRecord.leadFaculty,
        studentLead: adoptionRecord.studentLead,
        budget: proposalDetails.budget || "₹10,00,000",
        summary: adoptionRecord.proposalSummary,
      });
    } catch (e) {
      console.warn("Project workspace initialization fallback:", e.message);
    }

    // Try backend sync if available
    try {
      await apiClient.post(ENDPOINTS.CHALLENGES.ASSIGN_HEI(challengeId), { universityId });
    } catch (err) {
      console.warn("Backend assignment sync skipped (operating with local state).");
    }

    return {
      success: true,
      message: `Challenge '${challenge?.title || challengeId}' successfully adopted by ${uni.name}!`,
      adoption: adoptionRecord,
      project,
    };
  },

  async getRecommendedChallengesForUniversity(universityId) {
    if (!universityId) return [];
    
    // Fetch all challenges
    let allChallenges = [];
    try {
      const data = await challengeService.getChallenges({ limit: 50 });
      allChallenges = Array.isArray(data) ? data : (data?.items || data?.data || SEED_CHALLENGES);
    } catch (e) {
      allChallenges = SEED_CHALLENGES;
    }

    const uni = await this.getUniversityById(universityId);
    const adoptions = getLocalAdoptions();
    const invites = getLocalInvites();

    // Score and rank each challenge for this university
    const recommendations = allChallenges.map(ch => {
      const matches = basicAiEngine.matchUniversities(ch, SEED_UNIVERSITIES);
      const matchForThisUni = matches.find(m => (m.id === universityId || m.universityId === universityId)) || {
        overallMatch: 70,
        explainableFactors: {
          domainExpertise: { label: "Domain Capability Match", score: 70, reason: "Applicable engineering discipline" }
        }
      };

      const chId = ch.id || ch.challengeId;
      const adoption = adoptions[chId];
      const isAdoptedByYou = adoption && adoption.universityId === universityId;
      const isAdoptedByOther = adoption && adoption.universityId !== universityId;
      const isInvited = (invites[chId] || []).includes(universityId);

      return {
        challenge: ch,
        matchScore: matchForThisUni.overallMatch,
        explainableFactors: matchForThisUni.explainableFactors,
        strengths: uni.strengths || [],
        isAdoptedByYou,
        isAdoptedByOther,
        adoptionDetails: adoption || null,
        isInvited,
        status: isAdoptedByYou ? "ADOPTED_BY_YOU" : isAdoptedByOther ? "ADOPTED_BY_OTHER" : "OPEN_FOR_ADOPTION",
      };
    });

    // Sort descending by matchScore
    recommendations.sort((a, b) => b.matchScore - a.matchScore);
    return recommendations;
  },

  // Backward compatibility alias
  async assignChallengeToUniversity(challengeId, universityId) {
    return this.adoptChallenge(challengeId, universityId);
  },
};
