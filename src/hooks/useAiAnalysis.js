import { useState, useEffect, useCallback } from 'react';
import { aiService } from '../services/aiService';

export const useAiAnalysis = (challengeId) => {
  const [analysis, setAnalysis] = useState(null);
  const [status, setStatus] = useState("NOT_STARTED"); // NOT_STARTED | PROCESSING | COMPLETED | FAILED
  const [loading, setLoading] = useState(Boolean(challengeId));
  const [error, setError] = useState(null);

  const fetchAnalysis = useCallback(async () => {
    if (!challengeId) {
      setAnalysis(null);
      setStatus("NOT_STARTED");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await aiService.getAnalysis(challengeId);
      if (data) {
        setAnalysis(data);
        setStatus(data.status || "COMPLETED");
      } else {
        setAnalysis(null);
        setStatus("NOT_STARTED");
      }
    } catch (err) {
      if (err.status === 404) {
        setAnalysis(null);
        setStatus("NOT_STARTED");
      } else {
        setError(err.message || "Failed to load AI intelligence data.");
        setStatus("FAILED");
      }
    } finally {
      setLoading(false);
    }
  }, [challengeId]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  const trigger = async () => {
    if (!challengeId) return;
    setLoading(true);
    setStatus("PROCESSING");
    setError(null);
    try {
      const res = await aiService.triggerAnalysis(challengeId);
      setAnalysis(res);
      setStatus(res?.status || "COMPLETED");
      return res;
    } catch (err) {
      setError(err.message || "AI pipeline execution failed.");
      setStatus("FAILED");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { analysis, status, loading, error, triggerAnalysis: trigger, refetch: fetchAnalysis };
};
