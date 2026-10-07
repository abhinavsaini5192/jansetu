/**
 * Application Configuration
 * Centralizes environment variables and application constants.
 */
export const appConfig = {
  appName: import.meta.env.VITE_APP_NAME || "JanSetu",
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  apiTimeoutMs: Number(import.meta.env.VITE_API_TIMEOUT_MS) || 15000,
  tokenStorageKey: "jansetu_auth_token",
  userStorageKey: "jansetu_user_session",
  defaultLanguage: "en",
};
