import { useState, useEffect, useCallback } from 'react';
import { universityService } from '../services/universityService';

export const useUniversityMatches = (challengeId) => {
  const [matches, setMatches] = useState([]);
  const [adoptedBy, setAdoptedBy] = useState(null);
  const [loading, setLoading] = useState(Boolean(challengeId));
  const [error, setError] = useState(null);

  const fetchMatches = useCallback(async () => {
    if (!challengeId) {
      setMatches([]);
      setAdoptedBy(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await universityService.getMatchesForChallenge(challengeId);
      setMatches(Array.isArray(data) ? data : (data?.matches || []));
      setAdoptedBy(data?.adoptedBy || null);
    } catch (err) {
      setError(err.message || "Failed to load university recommendations.");
      setMatches([]);
      setAdoptedBy(null);
    } finally {
      setLoading(false);
    }
  }, [challengeId]);

  useEffect(() => {
    fetchMatches();
  }, [fetchMatches]);

  const adopt = async (universityId, proposalDetails = {}, currentUser = null) => {
    if (!challengeId || !universityId) return;
    const res = await universityService.adoptChallenge(challengeId, universityId, proposalDetails, currentUser);
    await fetchMatches();
    return res;
  };

  const invite = async (universityId, note = "") => {
    if (!challengeId || !universityId) return;
    const res = await universityService.sendRecommendationInvite(challengeId, universityId, note);
    await fetchMatches();
    return res;
  };

  return { 
    matches, 
    adoptedBy,
    loading, 
    error, 
    adoptChallenge: adopt,
    sendRecommendationInvite: invite,
    assignUniversity: adopt, // backward compatibility
    refetch: fetchMatches 
  };
};
