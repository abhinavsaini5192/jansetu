import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { appConfig } from "../config/appConfig";

export const authService = {
  async getCurrentUser() {
    try {
      const user = await apiClient.get(ENDPOINTS.AUTH.ME);
      return user;
    } catch (err) {
      // If unauthorized or offline, return null
      return null;
    }
  },

  async login(credentials) {
    const data = await apiClient.post(ENDPOINTS.AUTH.LOGIN, credentials);
    if (data?.token) {
      this.setSession(data.token, data.user);
    }
    return data;
  },

  async logout() {
    try {
      await apiClient.post(ENDPOINTS.AUTH.LOGOUT);
    } catch (e) {
      // Ignore network failures on logout
    } finally {
      this.clearSession();
    }
  },

  setSession(token, user) {
    if (token) localStorage.setItem(appConfig.tokenStorageKey, token);
    if (user) localStorage.setItem(appConfig.userStorageKey, JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem(appConfig.tokenStorageKey);
    localStorage.removeItem(appConfig.userStorageKey);
  },

  getStoredSession() {
    const token = localStorage.getItem(appConfig.tokenStorageKey);
    const userJson = localStorage.getItem(appConfig.userStorageKey);
    let user = null;
    if (userJson) {
      try {
        user = JSON.parse(userJson);
      } catch (e) {}
    }
    return { token, user };
  }
};
