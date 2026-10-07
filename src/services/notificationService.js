import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export const notificationService = {
  async getNotifications(params = {}) {
    return apiClient.get(ENDPOINTS.NOTIFICATIONS.LIST, params);
  },

  async markAsRead(notificationId) {
    if (!notificationId) throw new Error("Notification ID is required");
    return apiClient.patch(ENDPOINTS.NOTIFICATIONS.MARK_READ(notificationId));
  },

  async markAllAsRead() {
    return apiClient.post(ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ);
  },
};
