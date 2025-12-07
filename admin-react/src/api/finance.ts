import axiosInstance from '../services/api'

// ============= TYPES =============

export interface FinanceCategory {
  id: number
  name: string
  type: 'income' | 'expense'
  description: string | null
  color: string
  icon: string
  is_active: boolean
  created_at: string
  created_by: {
    id: number
    username: string
    email: string
  } | null
}

export interface FinanceTransaction {
  id: number
  amount: number
  type: 'income' | 'expense'
  description: string
  date: string
  category: FinanceCategory
  project: {
    id: number
    title: string
  } | null
  contractor_name: string | null
  account: string
  receipt_url: string | null
  notes: string | null
  is_recurring: boolean
  recurring_period: string | null
  created_at: string
  created_by: {
    id: number
    username: string
    email: string
  } | null
}

export interface FinanceBudget {
  id: number
  name: string
  category: FinanceCategory
  planned_amount: number
  period_start: string
  period_end: string
  is_active: boolean
  created_at: string
  created_by: {
    id: number
    username: string
    email: string
  } | null
}

export interface FinanceSummary {
  period: {
    from: string
    to: string
  }
  income: {
    total: number
    count: number
  }
  expenses: {
    total: number
    count: number
  }
  profit: number
  top_income_categories: Array<{
    name: string
    total: number
  }>
  top_expense_categories: Array<{
    name: string
    total: number
  }>
}

export interface MonthlyData {
  month: number
  month_name: string
  income: number
  expenses: number
  profit: number
}

export interface MonthlyAnalytics {
  year: number
  monthly_data: MonthlyData[]
}

export interface CategoryCreateData {
  name: string
  type: 'income' | 'expense'
  description?: string
  color?: string
  icon?: string
}

export interface TransactionCreateData {
  amount: number
  type: 'income' | 'expense'
  description: string
  date: string
  category_id: number
  project_id?: number
  contractor_name?: string
  account?: string
  receipt_url?: string
  notes?: string
  is_recurring?: boolean
  recurring_period?: string
}

export interface TransactionFilters {
  type?: 'income' | 'expense'
  category_id?: number
  project_id?: number
  date_from?: string
  date_to?: string
  limit?: number
  offset?: number
}

// ============= API CLIENT =============

const financeApi = {
  // ========== CATEGORIES ==========

  /**
   * Получить все категории финансов
   */
  getCategories: async (type?: 'income' | 'expense') => {
    const params = type ? { type } : {}
    const response = await axiosInstance.get('/admin/api/finance/categories', { params })
    return response.data as {
      success: boolean
      data: FinanceCategory[]
    }
  },

  /**
   * Создать новую категорию финансов
   */
  createCategory: async (data: CategoryCreateData) => {
    const response = await axiosInstance.post('/admin/api/finance/categories', data)
    return response.data as {
      success: boolean
      data: FinanceCategory
      message: string
    }
  },

  /**
   * Обновить категорию финансов
   */
  updateCategory: async (categoryId: number, data: Partial<CategoryCreateData>) => {
    const response = await axiosInstance.put(`/admin/api/finance/categories/${categoryId}`, data)
    return response.data as {
      success: boolean
      data: FinanceCategory
      message: string
    }
  },

  /**
   * Удалить категорию финансов
   */
  deleteCategory: async (categoryId: number) => {
    const response = await axiosInstance.delete(`/admin/api/finance/categories/${categoryId}`)
    return response.data as {
      success: boolean
      message: string
    }
  },

  // ========== TRANSACTIONS ==========

  /**
   * Получить финансовые транзакции с фильтрами
   */
  getTransactions: async (filters?: TransactionFilters) => {
    const response = await axiosInstance.get('/admin/api/finance/transactions', {
      params: filters,
    })
    return response.data as {
      success: boolean
      data: FinanceTransaction[]
      total: number
      limit: number
      offset: number
    }
  },

  /**
   * Создать новую финансовую транзакцию
   */
  createTransaction: async (data: TransactionCreateData) => {
    const response = await axiosInstance.post('/admin/api/finance/transactions', data)
    return response.data as {
      success: boolean
      data: FinanceTransaction
      message: string
    }
  },

  /**
   * Обновить финансовую транзакцию
   */
  updateTransaction: async (transactionId: number, data: TransactionCreateData) => {
    const response = await axiosInstance.put(
      `/admin/api/finance/transactions/${transactionId}`,
      data
    )
    return response.data as {
      success: boolean
      data: FinanceTransaction
      message: string
    }
  },

  /**
   * Удалить финансовую транзакцию
   */
  deleteTransaction: async (transactionId: number) => {
    const response = await axiosInstance.delete(
      `/admin/api/finance/transactions/${transactionId}`
    )
    return response.data as {
      success: boolean
      message: string
    }
  },

  // ========== ANALYTICS ==========

  /**
   * Получить сводку по финансам
   */
  getSummary: async (date_from?: string, date_to?: string) => {
    const params: any = {}
    if (date_from) params.date_from = date_from
    if (date_to) params.date_to = date_to

    const response = await axiosInstance.get('/admin/api/finance/analytics/summary', { params })
    return response.data as {
      success: boolean
      data: FinanceSummary
    }
  },

  /**
   * Получить месячную аналитику по финансам
   */
  getMonthlyAnalytics: async (year?: number) => {
    const params = year ? { year } : {}
    const response = await axiosInstance.get('/admin/api/finance/analytics/monthly', { params })
    return response.data as {
      success: boolean
      data: MonthlyAnalytics
    }
  },

  // ========== BUDGETS ==========

  /**
   * Получить все бюджеты
   */
  getBudgets: async () => {
    const response = await axiosInstance.get('/admin/api/finance/budgets')
    return response.data as {
      success: boolean
      data: FinanceBudget[]
    }
  },

  /**
   * Создать новый бюджет
   */
  createBudget: async (data: {
    name: string
    category_id: number
    planned_amount: number
    period_start: string
    period_end: string
  }) => {
    const response = await axiosInstance.post('/admin/api/finance/budgets', data)
    return response.data as {
      success: boolean
      data: FinanceBudget
      message: string
    }
  },

  /**
   * Обновить бюджет
   */
  updateBudget: async (
    budgetId: number,
    data: {
      name?: string
      category_id?: number
      planned_amount?: number
      period_start?: string
      period_end?: string
    }
  ) => {
    const response = await axiosInstance.put(`/admin/api/finance/budgets/${budgetId}`, data)
    return response.data as {
      success: boolean
      data: FinanceBudget
      message: string
    }
  },

  /**
   * Удалить бюджет
   */
  deleteBudget: async (budgetId: number) => {
    const response = await axiosInstance.delete(`/admin/api/finance/budgets/${budgetId}`)
    return response.data as {
      success: boolean
      message: string
    }
  },
}

export default financeApi
