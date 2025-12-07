import { apiClient } from './client';

export const chatsApi = {
  // Получить все чаты проектов клиента
  async getChats() {
    const { data } = await apiClient.get('/chats');
    return data;
  },

  // Получить сообщения чата
  async getChatMessages(chatId: number) {
    const { data } = await apiClient.get(`/chats/${chatId}/messages`);
    return data;
  },

  // Отправить сообщение в чат
  async sendMessage(chatId: number, messageData: { message_text?: string; attachments?: File[] }) {
    console.log('🔧 chatsApi.sendMessage вызван', { chatId, messageData });

    const formData = new FormData();

    if (messageData.message_text) {
      console.log('📝 Добавляем текст в FormData:', messageData.message_text);
      formData.append('message_text', messageData.message_text);
    }

    if (messageData.attachments) {
      console.log('📎 Добавляем файлы в FormData:', messageData.attachments.length);
      messageData.attachments.forEach((file, index) => {
        console.log(`  Файл ${index + 1}:`, file.name, file.type, file.size);
        formData.append(`attachments`, file);
      });
    }

    console.log('🌐 Отправляем POST запрос на /chats/' + chatId + '/messages');

    try {
      // Axios автоматически установит правильный Content-Type с boundary для FormData
      const { data } = await apiClient.post(`/chats/${chatId}/messages`, formData);
      console.log('✅ Ответ от сервера:', data);
      return data;
    } catch (error: any) {
      console.error('❌ Ошибка при отправке:', error);
      console.error('❌ Детали ошибки:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw error;
    }
  },

  // Пометить сообщения как прочитанные
  async markAsRead(chatId: number) {
    const { data } = await apiClient.patch(`/chats/${chatId}/read`);
    return data;
  },
};
