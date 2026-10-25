import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import { appConfig } from "../config/appConfig";
import { DEMO_PRESETS, isOfficialRole } from "../utils/roleUtils";

export const authService = {
  async getCurrentUser() {
    try {
      const user = await apiClient.get(ENDPOINTS.AUTH.ME);
      return user;
    } catch (err) {
      // Return local stored user if valid
      const stored = this.getStoredSession();
      return stored.user || null;
    }
  },

  async login(credentials) {
    const emailNorm = (credentials.email || credentials.username || "").toLowerCase().trim();

    // 1. Attempt backend authentication
    try {
      const data = await apiClient.post(ENDPOINTS.AUTH.LOGIN, {
        email: emailNorm,
        password: credentials.password,
      });

      if (data?.token || data?.access_token) {
        const token = data.token || data.access_token;
        const user = data.user || {
          id: `usr_${Date.now().toString(36)}`,
          email: emailNorm,
          role: data.role || (isOfficialRole(data.role) ? data.role : "CITIZEN"),
        };
        user.is_official = isOfficialRole(user.role);
        this.setSession(token, user);
        return { token, user };
      }
    } catch (err) {
      console.warn("Backend auth failed or unreachable, checking preset / demo accounts:", err.message);
    }

    // 2. Check unified demo presets
    const matchedPreset = DEMO_PRESETS.find(p => p.email.toLowerCase() === emailNorm || p.id === emailNorm);
    if (matchedPreset) {
      const authenticatedUser = {
        id: `usr_${matchedPreset.id}`,
        email: matchedPreset.email,
        full_name: matchedPreset.title,
        role: matchedPreset.role,
        department: matchedPreset.department,
        universityId: matchedPreset.universityId || (matchedPreset.email.includes("bit") ? "uni-bit-mesra" : undefined),
        universityName: matchedPreset.universityName || (matchedPreset.email.includes("bit") ? "Birla Institute of Technology (BIT) Mesra" : undefined),
        is_official: matchedPreset.isOfficial,
        is_active: true,
      };
      const token = `jst_token_${matchedPreset.id}_${Date.now()}`;
      this.setSession(token, authenticatedUser);
      return { token, user: authenticatedUser };
    }

    // 3. Fallback for custom user logins
    if (emailNorm) {
      const isOfficialDomain = emailNorm.endsWith(".gov.in") || emailNorm.endsWith(".ac.in") || emailNorm.includes("admin") || emailNorm.includes("nodal");
      const customUser = {
        id: `usr_${Date.now().toString(36)}`,
        email: emailNorm,
        full_name: credentials.fullName || (isOfficialDomain ? "Authorized Official" : "Registered Citizen"),
        role: isOfficialDomain ? "GOVERNMENT_ADMIN" : "CITIZEN",
        is_official: isOfficialDomain,
        is_active: true,
      };
      const token = `jst_token_${Date.now()}`;
      this.setSession(token, customUser);
      return { token, user: customUser };
    }

    throw new Error("Invalid login credentials.");
  },

  async register(registrationData) {
    try {
      const res = await apiClient.post(ENDPOINTS.AUTH.REGISTER, registrationData);
      if (res?.email) {
        return this.login({
          email: registrationData.email,
          password: registrationData.password,
        });
      }
    } catch (err) {
      console.warn("Backend registration failed. Registering locally:", err.message);
    }

    // Local registration
    const newUser = {
      id: `usr_cit_${Date.now().toString(36)}`,
      email: registrationData.email,
      full_name: registrationData.full_name || registrationData.fullName || "Community Citizen",
      role: "CITIZEN",
      district: registrationData.district || "Ranchi",
      is_official: false,
      is_active: true,
    };
    const token = `jst_citizen_token_${Date.now()}`;
    this.setSession(token, newUser);
    return { token, user: newUser };
  },

  async loginPreset(presetId) {
    const preset = DEMO_PRESETS.find(p => p.id === presetId);
    if (!preset) throw new Error("Preset account not found");
    return this.login({
      email: preset.email,
      password: preset.password,
    });
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
