import axiosInstance from '../services/api'

// === Revision Interfaces ===
export interface Revision {
  id: number
  project_id: number
  revision_number: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'review' | 'completed' | 'approved' | 'needs_rework' | 'rejected'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  created_by_id: number
  assigned_to_id?: number
  estimated_time?: number
  actual_time?: number
  progress?: number
  timer_started_at?: string
  time_spent_seconds?: number
  test_link?: string
  created_at: string
  updated_at: string
  completed_at?: string
  project?: {
    id: number
    title: string
    status: string
  }
  created_by?: {
    id: number
    first_name: string
    username: string
  }
  assigned_to?: {
    id: number
    username: string
  }
  messages?: RevisionMessage[]
  files?: RevisionFile[]
}

export interface RevisionMessage {
  id: number
  revision_id: number
  sender_type: 'client' | 'admin' | 'executor'
  sender_name: string
  message: string
  content?: string
  is_internal: boolean
  created_at: string
  files?: RevisionFile[]
}

export interface RevisionFile {
  id: number
  filename: string
  original_filename: string
  file_type: 'image' | 'video' | 'document' | 'other'
  file_size: number
  download_url: string
  thumbnail_url?: string
  upload_date?: string
}

export interface RevisionStats {
  total_revisions: number
  pending_revisions: number
  completed_revisions: number
  my_revisions: number
}

const revisionsApi = {
  // Get all revisions with filters
  getRevisions: async (filters?: {
    project_id?: number
    status?: string
    priority?: string
    assigned_to_me?: boolean
  }) => {
    const params = new URLSearchParams()
    if (filters?.project_id) params.append('project_id', filters.project_id.toString())
    if (filters?.status) params.append('status', filters.status)
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.assigned_to_me) params.append('assigned_to_me', 'true')

    const response = await axiosInstance.get(`/admin/api/revisions?${params}`)
    return response.data as { success: boolean; data: Revision[]; total: number }
  },

  // Get single revision
  getRevision: async (revisionId: number) => {
    const response = await axiosInstance.get(`/admin/api/revisions/${revisionId}`)
    return response.data as { success: boolean; data: Revision }
  },

  // Get revision statistics
  getStats: async () => {
    const response = await axiosInstance.get('/admin/api/revisions/stats')
    return response.data as { success: boolean; data: RevisionStats }
  },

  // Create revision
  createRevision: async (data: {
    project_id: number
    title: string
    description: string
    priority?: string
  }) => {
    const response = await axiosInstance.post('/admin/api/revisions', data)
    return response.data as { success: boolean; message: string; data: Revision }
  },

  // Update revision
  updateRevision: async (
    revisionId: number,
    data: {
      title?: string
      description?: string
      status?: string
      priority?: string
      assigned_to_id?: number
      estimated_time?: number
      actual_time?: number
    }
  ) => {
    const response = await axiosInstance.put(`/admin/api/revisions/${revisionId}`, data)
    return response.data as { success: boolean; message: string; data: Revision }
  },

  // Get revision files
  getFiles: async (revisionId: number) => {
    const response = await axiosInstance.get(`/admin/api/revisions/${revisionId}/files`)
    return response.data as { success: boolean; data: RevisionFile[] }
  },

  // Get revision messages
  getMessages: async (revisionId: number) => {
    const response = await axiosInstance.get(`/admin/api/revisions/${revisionId}/messages`)
    return response.data as { success: boolean; data: RevisionMessage[] }
  },

  // Add message to revision
  addMessage: async (revisionId: number, message: string, isInternal: boolean, files?: File[]) => {
    const formData = new FormData()
    formData.append('revision_id', revisionId.toString())
    formData.append('message', message)
    formData.append('is_internal', isInternal.toString())

    if (files) {
      files.forEach((file) => {
        formData.append('files', file)
      })
    }

    const response = await axiosInstance.post('/admin/api/revisions/messages', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data as { success: boolean; message: string; message_id: number }
  },

  // Update progress
  updateProgress: async (revisionId: number, progress: number) => {
    const response = await axiosInstance.post(`/admin/api/revisions/${revisionId}/progress`, {
      progress,
    })
    return response.data as { success: boolean; progress: number; message: string }
  },

  // Start timer
  startTimer: async (revisionId: number) => {
    const response = await axiosInstance.post(`/admin/api/revisions/${revisionId}/timer/start`)
    return response.data as { success: boolean; message: string; started_at: string }
  },

  // Stop timer
  stopTimer: async (revisionId: number) => {
    const response = await axiosInstance.post(`/admin/api/revisions/${revisionId}/timer/stop`)
    return response.data as {
      success: boolean
      message: string
      time_spent_seconds: number
      elapsed_seconds: number
    }
  },

  // Send for review
  sendForReview: async (revisionId: number) => {
    const response = await axiosInstance.post(
      `/admin/api/revisions/${revisionId}/send-for-review`
    )
    return response.data as { success: boolean; message: string; data: Revision }
  },

  // Complete revision
  completeRevision: async (
    revisionId: number,
    actualTime?: number,
    completionMessage: string = 'Правки внесены'
  ) => {
    const formData = new FormData()
    if (actualTime) formData.append('actual_time', actualTime.toString())
    formData.append('completion_message', completionMessage)

    const response = await axiosInstance.post(
      `/admin/api/revisions/${revisionId}/complete`,
      formData
    )
    return response.data as { success: boolean; message: string; data: Revision }
  },
}

export default revisionsApi
