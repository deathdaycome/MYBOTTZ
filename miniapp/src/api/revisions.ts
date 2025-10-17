import apiClient from './client';
import type { Revision, RevisionMessage, CreateRevisionData, RevisionStats } from '../types/revision';

export const revisionsApi = {
  // Получить все правки проекта
  getProjectRevisions: async (projectId: number): Promise<Revision[]> => {
    const response = await apiClient.get(`/miniapp/projects/${projectId}/revisions`);
    return response.data.revisions || response.data;
  },

  // Получить статистику по правкам проекта
  getProjectRevisionStats: async (projectId: number): Promise<RevisionStats> => {
    const response = await apiClient.get(`/miniapp/projects/${projectId}/revisions/stats`);
    return response.data.stats;
  },

  // Получить общую статистику по всем правкам пользователя
  getAllRevisionsStats: async (): Promise<RevisionStats> => {
    const response = await apiClient.get('/miniapp/revisions/stats');
    return response.data;
  },

  // Получить детали правки
  getRevisionDetails: async (revisionId: number): Promise<Revision> => {
    const response = await apiClient.get(`/miniapp/revisions/${revisionId}`);
    return response.data.revision || response.data;
  },

  // Получить сообщения правки (чат)
  getRevisionMessages: async (revisionId: number): Promise<RevisionMessage[]> => {
    const response = await apiClient.get(`/miniapp/revisions/${revisionId}/messages`);
    return response.data.messages;
  },

  // Отправить сообщение в чат правки
  sendRevisionMessage: async (revisionId: number, message: string, files?: File[]): Promise<RevisionMessage> => {
    const formData = new FormData();
    formData.append('message', message);
    
    if (files && files.length > 0) {
      files.forEach((file) => {
        formData.append('files', file);
      });
    }

    const response = await apiClient.post(`/miniapp/revisions/${revisionId}/messages`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.message;
  },

  // Создать новую правку
  createRevision: async (data: CreateRevisionData): Promise<Revision> => {
    const formData = new FormData();
    formData.append('project_id', data.project_id.toString());
    formData.append('title', data.title);
    formData.append('description', data.description);
    formData.append('priority', data.priority);
    
    if (data.files && data.files.length > 0) {
      data.files.forEach((file) => {
        formData.append('files', file);
      });
    }

    const response = await apiClient.post('/miniapp/revisions', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.revision || response.data;
  },

  // Обновить статус правки (только для админов/исполнителей)
  updateRevisionStatus: async (revisionId: number, status: string): Promise<Revision> => {
    const response = await apiClient.patch(`/miniapp/revisions/${revisionId}/status`, { status });
    return response.data.revision || response.data;
  },

  // Обновить прогресс правки (только для админов/исполнителей)
  updateRevisionProgress: async (revisionId: number, progress: number): Promise<Revision> => {
    const response = await apiClient.patch(`/miniapp/revisions/${revisionId}/progress`, { progress });
    return response.data.revision || response.data;
  },
};
