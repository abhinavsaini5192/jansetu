import { useState, useEffect, useCallback } from 'react';
import { universityService } from '../services/universityService';

export const useUniversityMatches = (challengeId) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(Boolean(challengeId));
  const [error, setError] = useState(null);

  const fetchMatches = useCallback(async () => {
    if (!challengeId) {
      setMatches([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await universityService.getMatchesForChallenge(challengeId);
      setMatches(Array.isArray(data) ? data : (data?.matches || []));
    } catch (err) {
      setError(err.message || "Failed to load university recommendations.");
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }, [challengeId]);

  useEffect(() => {
    fetchMatches();
  }, [fetchMatches]);

  const assign = async (universityId) => {
    if (!challengeId || !universityId) return;
    const res = await universityService.assignChallengeToUniversity(challengeId, universityId);
    await fetchMatches();
    return res;
  };

  return { matches, loading, error, assignUniversity: assign, refetch: fetchMatches };
};
