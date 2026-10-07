import { useState, useEffect, useCallback } from 'react';
import { impactService } from '../services/impactService';

export const useImpact = (challengeId) => {
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(Boolean(challengeId));
  const [error, setError] = useState(null);

  const fetchImpact = useCallback(async () => {
    if (!challengeId) {
      setImpact(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await impactService.getImpactByChallengeId(challengeId);
      setImpact(data);
    } catch (err) {
      if (err.status === 404) {
        setImpact(null);
      } else {
        setError(err.message || "Failed to load impact metrics.");
      }
    } finally {
      setLoading(false);
    }
  }, [challengeId]);

  useEffect(() => {
    fetchImpact();
  }, [fetchImpact]);

  const submitEvidence = async (evidenceData) => {
    if (!challengeId) return;
    const res = await impactService.submitEvidence(challengeId, evidenceData);
    await fetchImpact();
    return res;
  };

  const verify = async (impactId, verificationData) => {
    const res = await impactService.verifyImpact(impactId, verificationData);
    await fetchImpact();
    return res;
  };

  return { impact, loading, error, submitEvidence, verifyImpact: verify, refetch: fetchImpact };
};
