import { useState, useEffect, useCallback } from 'react';
import { aiService } from '../services/aiService';
import { basicAiEngine } from '../services/basicAiEngine';

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
        // Fallback to basic AI engine
        const fallbackData = basicAiEngine.analyzeChallengeById(challengeId);
        setAnalysis(fallbackData);
        setStatus("COMPLETED");
      }
    } catch (err) {
      // Instead of failing and showing "AI Analysis Unavailable", run the basic AI engine
      console.warn("AI intelligence fetch failed. Activating Basic AI Engine:", err);
      const fallbackData = basicAiEngine.analyzeChallengeById(challengeId);
      setAnalysis(fallbackData);
      setStatus("COMPLETED");
      setError(null);
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
      console.warn("AI pipeline error. Applying Basic AI Engine fallback:", err);
      const fallbackRes = basicAiEngine.analyzeChallengeById(challengeId);
      setAnalysis(fallbackRes);
      setStatus("COMPLETED");
      return fallbackRes;
    } finally {
      setLoading(false);
    }
  };

  return { analysis, status, loading, error, triggerAnalysis: trigger, refetch: fetchAnalysis };
};
