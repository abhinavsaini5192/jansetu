import { useState, useEffect, useCallback } from 'react';
import { challengeService } from '../services/challengeService';

export const useChallenges = (filters = {}) => {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchChallenges = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await challengeService.getChallenges(filters);
      setChallenges(Array.isArray(data) ? data : (data?.items || []));
    } catch (err) {
      setError(err.message || "Failed to load challenges from platform.");
      setChallenges([]);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    fetchChallenges();
  }, [fetchChallenges]);

  return { challenges, loading, error, refetch: fetchChallenges };
};
