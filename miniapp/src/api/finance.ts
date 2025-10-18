import { apiClient } from './client';

export interface FinanceSummary {
  total_amount: number;
  paid_amount: number;
  balance: number;
  projects_count: number;
}

export interface Transaction {
  id: number;
  type: string;
  project_id: number;
  project_name: string;
  amount: number;
  currency: string;
  description: string;
  payment_method: string;
  status: string;
  date: string;
}

export interface Deal {
  id: number;
  title: string;
  status: string;
  description: string;
  amount: number;
  paid_amount: number;
  balance: number;
  start_date: string;
  end_date: string;
  prepayment_percent: number;
  prepayment_amount: number;
  project_name: string;
  project_id: number;
}

export const financeApi = {
  /**
   * Получить сводку по финансам
   */
  getSummary: async (): Promise<FinanceSummary> => {
    const response = await apiClient.get('/finance/summary');
    return response.data;
  },

  /**
   * Получить список транзакций
   */
  getTransactions: async (): Promise<Transaction[]> => {
    const response = await apiClient.get('/finance/transactions');
    return response.data.transactions || [];
  },

  /**
   * Получить список сделок
   */
  getDeals: async (): Promise<Deal[]> => {
    const response = await apiClient.get('/finance/deals');
    return response.data.deals || [];
  },
};
