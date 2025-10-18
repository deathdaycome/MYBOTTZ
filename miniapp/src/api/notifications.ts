import { apiClient } from './client';

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  status: string;
  sent_at: string;
  entity_type: string | null;
  entity_id: string | null;
}

export const notificationsApi = {
  /**
   * Получить список уведомлений
   */
  getNotifications: async (limit: number = 50): Promise<Notification[]> => {
    const response = await apiClient.get('/notifications', {
      params: { limit }
    });
    return response.data.notifications || [];
  },

  /**
   * Получить количество непрочитанных уведомлений
   */
  getUnreadCount: async (): Promise<number> => {
    const response = await apiClient.get('/notifications/unread-count');
    return response.data.unread_count || 0;
  },
};
