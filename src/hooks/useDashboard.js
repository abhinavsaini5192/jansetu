import { useState, useEffect, useCallback } from 'react';
import { dashboardService } from '../services/dashboardService';

export const useDashboard = () => {
  const [stats, setStats] = useState(null);
  const [domains, setDomains] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, domainsRes, districtsRes] = await Promise.allSettled([
        dashboardService.getStats(),
        dashboardService.getDomainBreakdown(),
        dashboardService.getDistrictTrends(),
      ]);

      if (statsRes.status === "fulfilled" && statsRes.value) {
        setStats(statsRes.value);
      } else {
        setStats(null);
      }

      if (domainsRes.status === "fulfilled" && Array.isArray(domainsRes.value)) {
        setDomains(domainsRes.value);
      } else {
        setDomains([]);
      }

      if (districtsRes.status === "fulfilled" && Array.isArray(districtsRes.value)) {
        setDistricts(districtsRes.value);
      } else {
        setDistricts([]);
      }

      // If all three failed
      if (statsRes.status === "rejected" && domainsRes.status === "rejected" && districtsRes.status === "rejected") {
        setError(statsRes.reason?.message || "Failed to load dashboard metrics.");
      }
    } catch (err) {
      setError(err.message || "An unexpected error occurred while loading dashboard metrics.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return { stats, domains, districts, loading, error, refetch: fetchDashboardData };
};
