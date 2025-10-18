import { apiClient } from './client';

export interface Document {
  id: number;
  type: string;
  name: string;
  number: string;
  project_id: number;
  project_name?: string;
  file_path: string;
  file_url: string | null;
  file_size: number;
  file_type: string;
  status: string;
  date: string;
  signed_at: string | null;
  description: string | null;
  created_at: string;
}

export const documentsApi = {
  /**
   * Получить список всех документов клиента
   */
  getDocuments: async (): Promise<Document[]> => {
    const response = await apiClient.get('/documents');
    return response.data.documents || [];
  },

  /**
   * Получить информацию о конкретном документе
   */
  getDocument: async (documentId: number): Promise<Document> => {
    const response = await apiClient.get(`/documents/${documentId}`);
    return response.data.document;
  },
};
