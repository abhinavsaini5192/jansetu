import { useState, useEffect, useCallback } from 'react';
import { challengeService } from '../services/challengeService';

export const useChallenge = (challengeId) => {
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(Boolean(challengeId));
  const [error, setError] = useState(null);

  const fetchChallenge = useCallback(async () => {
    if (!challengeId) {
      setChallenge(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await challengeService.getChallengeById(challengeId);
      setChallenge(data);
    } catch (err) {
      setError(err.message || "Failed to load challenge details.");
      setChallenge(null);
    } finally {
      setLoading(false);
    }
  }, [challengeId]);

  useEffect(() => {
    fetchChallenge();
  }, [fetchChallenge]);

  const update = async (updates) => {
    if (!challengeId) return;
    const updated = await challengeService.updateChallenge(challengeId, updates);
    setChallenge(updated);
    return updated;
  };

  return { challenge, loading, error, refetch: fetchChallenge, update };
};
