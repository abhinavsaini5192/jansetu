import { useState, useEffect, useCallback } from 'react';
import { projectService } from '../services/projectService';

export const useProject = (identifier = null, isChallengeId = false) => {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(Boolean(identifier));
  const [error, setError] = useState(null);

  const fetchProject = useCallback(async () => {
    if (!identifier) {
      setProject(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = isChallengeId
        ? await projectService.getProjectByChallengeId(identifier)
        : await projectService.getProjectById(identifier);
      setProject(data);
    } catch (err) {
      if (err.status === 404) {
        setProject(null);
      } else {
        setError(err.message || "Failed to load project details.");
      }
    } finally {
      setLoading(false);
    }
  }, [identifier, isChallengeId]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  const updateMilestone = async (milestoneId, updates) => {
    if (!project?.id) return;
    const res = await projectService.updateMilestone(project.id, milestoneId, updates);
    await fetchProject();
    return res;
  };

  const create = async (projectData) => {
    const res = await projectService.createProject(projectData);
    setProject(res);
    return res;
  };

  return { project, loading, error, updateMilestone, createProject: create, refetch: fetchProject };
};
