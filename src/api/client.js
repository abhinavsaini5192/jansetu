import { appConfig } from "../config/appConfig";

/**
 * Standardized API Error structure
 */
export class ApiError extends Error {
  constructor(message, status = 0, data = null, meta = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
    this.isNetworkError = meta.isNetworkError || false;
    this.isTimeout = meta.isTimeout || false;
    this.isUnauthorized = status === 401;
    this.isForbidden = status === 403;
    this.isNotFound = status === 404;
  }
}

/**
 * Centralized API Client
 */
class ApiClient {
  constructor() {
    this.baseUrl = appConfig.apiBaseUrl;
    this.timeoutMs = appConfig.apiTimeoutMs;
  }

  getHeaders(customHeaders = {}) {
    const headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      ...customHeaders,
    };

    const token = localStorage.getItem(appConfig.tokenStorageKey);
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("http") 
      ? endpoint 
      : `${this.baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options.timeoutMs || this.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        headers: this.getHeaders(options.headers),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle 204 No Content
      if (response.status === 204) {
        return null;
      }

      let data;
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        const errorMessage = data?.message || data?.error || `Request failed with status ${response.status}`;
        throw new ApiError(errorMessage, response.status, data);
      }

      return data;
    } catch (err) {
      clearTimeout(timeoutId);

      if (err instanceof ApiError) {
        throw err;
      }

      if (err.name === "AbortError") {
        throw new ApiError("Request timed out. Please check your network connection.", 0, null, { isTimeout: true });
      }

      // Network or offline error
      throw new ApiError(
        err.message || "Network error. Unable to connect to backend server.",
        0,
        null,
        { isNetworkError: true }
      );
    }
  }

  get(endpoint, queryParams = null, options = {}) {
    let url = endpoint;
    if (queryParams && typeof queryParams === "object") {
      const filteredParams = Object.entries(queryParams)
        .filter(([_, v]) => v !== undefined && v !== null && v !== "")
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join("&");
      if (filteredParams) {
        url += (url.includes("?") ? "&" : "?") + filteredParams;
      }
    }
    return this.request(url, { ...options, method: "GET" });
  }

  post(endpoint, body = null, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  put(endpoint, body = null, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  patch(endpoint, body = null, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new ApiClient();
