import { useState, useEffect, useCallback } from 'react';
import { industryService } from '../services/industryService';

export const useIndustryPartners = (params = {}) => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPartners = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await industryService.getPartners(params);
      setPartners(Array.isArray(data) ? data : (data?.items || []));
    } catch (err) {
      setError(err.message || "Failed to load industry partners.");
      setPartners([]);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchPartners();
  }, [fetchPartners]);

  const attach = async (projectId, partnerId, supportType) => {
    return industryService.attachPartner(projectId, partnerId, supportType);
  };

  return { partners, loading, error, attachPartner: attach, refetch: fetchPartners };
};
