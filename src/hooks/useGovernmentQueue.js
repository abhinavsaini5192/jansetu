import { useState, useEffect, useCallback } from 'react';
import { governmentService } from '../services/governmentService';

export const useGovernmentQueue = (filters = {}) => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchQueue = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await governmentService.getValidationQueue(filters);
      setQueue(Array.isArray(data) ? data : (data?.items || []));
    } catch (err) {
      setError(err.message || "Failed to load government validation queue.");
      setQueue([]);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  const validate = async (challengeId, { remarks, department }) => {
    const res = await governmentService.validateChallenge(challengeId, { remarks, department });
    await fetchQueue();
    return res;
  };

  const reject = async (challengeId, { reason }) => {
    const res = await governmentService.rejectChallenge(challengeId, { reason });
    await fetchQueue();
    return res;
  };

  return { queue, loading, error, validate, reject, refetch: fetchQueue };
};
