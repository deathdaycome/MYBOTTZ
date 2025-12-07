import axiosInstance from '../services/api'

export interface AutomationSummary {
  total_projects: number
  overdue_count: number
  unpaid_projects_count: number
  unpaid_executors_count: number
  total_unpaid_clients: number
  total_unpaid_executors: number
}

export interface OverdueProject {
  id: number
  title: string
  old_status: string
  message: string
}

export interface UnpaidProject {
  id: number
  title: string
  remaining: number
  days_passed: number
  total_cost: number
  paid: number
}

export interface UnpaidExecutor {
  project_id: number
  project_title: string
  executor_id: number
  executor_name: string
  remaining: number
  days_passed: number
  total_cost: number
  paid: number
}

const automationApi = {
  // Get automation summary
  getSummary: async () => {
    const response = await axiosInstance.get('/admin/api/automation/summary')
    return response.data as {
      success: boolean
      summary: AutomationSummary
      scheduler_running: boolean
    }
  },

  // Check overdue projects
  checkOverdue: async () => {
    const response = await axiosInstance.post('/admin/api/automation/check-overdue')
    return response.data as {
      success: boolean
      message: string
      projects: OverdueProject[]
    }
  },

  // Check unpaid projects
  checkUnpaid: async () => {
    const response = await axiosInstance.post('/admin/api/automation/check-unpaid')
    return response.data as {
      success: boolean
      unpaid_projects: UnpaidProject[]
      unpaid_executors: UnpaidExecutor[]
    }
  },

  // Run daily checks
  runDailyChecks: async () => {
    const response = await axiosInstance.post('/admin/api/automation/run-daily')
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Send test notification
  sendNotification: async (message: string) => {
    const response = await axiosInstance.post('/admin/api/automation/send-notification', {
      message,
    })
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Start scheduler
  startScheduler: async () => {
    const response = await axiosInstance.post('/admin/api/automation/scheduler/start')
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Stop scheduler
  stopScheduler: async () => {
    const response = await axiosInstance.post('/admin/api/automation/scheduler/stop')
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Run scheduler task
  runTask: async (taskName: string) => {
    const response = await axiosInstance.post('/admin/api/automation/scheduler/run-task', {
      task_name: taskName,
    })
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Get scheduler status
  getSchedulerStatus: async () => {
    const response = await axiosInstance.get('/admin/api/automation/scheduler/status')
    return response.data as {
      success: boolean
      is_running: boolean
      available_tasks: string[]
    }
  },
}

export default automationApi
