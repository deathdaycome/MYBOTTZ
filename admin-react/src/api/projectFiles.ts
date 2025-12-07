import axiosInstance from '../services/api'

// ============= TYPES =============
// Force Vite to recompile this module

export interface ProjectFile {
  id: number
  filename: string
  original_filename: string
  file_path: string
  file_size: number
  file_type: string
  description?: string
  uploaded_at: string
  project_id: number
  uploaded_by_id: number
  uploaded_by_name?: string
  project_name?: string
}

export interface ProjectWithFiles {
  id: number
  title: string
  description?: string
  status: string
  status_name?: string
  user_id: number
  user?: {
    id: number
    first_name?: string
    last_name?: string
    telegram_id?: string
  }
  created_at: string
  files_count?: number
  files?: ProjectFile[]
}

export interface ProjectFilesStats {
  total_projects: number
  projects_with_files: number
  projects_without_files: number
  total_files: number
  total_size: number
}

export interface ProjectFilesFilters {
  search?: string
  has_files?: boolean
  status?: string
  page?: number
  limit?: number
}

// ============= API FUNCTIONS =============

class ProjectFilesAPI {
  /**
   * Получить все проекты с информацией о файлах
   * ОПТИМИЗИРОВАНО: загружаем все файлы одним запросом вместо множества параллельных
   */
  async getProjectsWithFiles(filters?: ProjectFilesFilters) {
    try {
      const params = new URLSearchParams()

      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.page) params.append('page', filters.page.toString())
      if (filters?.limit) params.append('per_page', filters.limit.toString())

      // Загружаем проекты и все файлы параллельно (2 запроса вместо N+1)
      const [projectsResponse, filesResponse] = await Promise.all([
        axiosInstance.get(`/admin/projects/?${params.toString()}`),
        this.getAllFiles()
      ])

      const projects = projectsResponse.data.projects as ProjectWithFiles[]
      const allFiles = filesResponse.files || []

      // Группируем файлы по project_id
      const filesByProject = new Map<number, ProjectFile[]>()
      allFiles.forEach((file: ProjectFile) => {
        if (!filesByProject.has(file.project_id)) {
          filesByProject.set(file.project_id, [])
        }
        filesByProject.get(file.project_id)!.push(file)
      })

      // Добавляем файлы к каждому проекту
      const projectsWithFiles = projects.map((project) => ({
        ...project,
        files: filesByProject.get(project.id) || [],
        files_count: filesByProject.get(project.id)?.length || 0
      }))

      // Фильтруем по наличию файлов если нужно
      let filteredProjects = projectsWithFiles
      if (filters?.has_files !== undefined) {
        filteredProjects = projectsWithFiles.filter(p =>
          filters.has_files ? (p.files_count || 0) > 0 : (p.files_count || 0) === 0
        )
      }

      return {
        success: true,
        projects: filteredProjects,
        pagination: projectsResponse.data.pagination || {
          total: filteredProjects.length,
          page: filters?.page || 1,
          limit: filters?.limit || 20,
          pages: Math.ceil(filteredProjects.length / (filters?.limit || 20))
        }
      }
    } catch (error: any) {
      console.error('Error fetching projects with files:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки проектов',
        projects: [],
        pagination: { total: 0, page: 1, limit: 20, pages: 0 }
      }
    }
  }

  /**
   * Получить все файлы (для статистики)
   */
  async getAllFiles() {
    try {
      const response = await axiosInstance.get('/admin/files/all')

      return {
        success: true,
        files: response.data.files as ProjectFile[]
      }
    } catch (error: any) {
      console.error('Error fetching all files:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки файлов',
        files: []
      }
    }
  }

  /**
   * Получить файлы конкретного проекта
   */
  async getProjectFiles(projectId: number) {
    try {
      const response = await axiosInstance.get(`/admin/files/project/${projectId}`)

      return {
        success: true,
        files: response.data.files as ProjectFile[]
      }
    } catch (error: any) {
      console.error(`Error fetching files for project ${projectId}:`, error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки файлов',
        files: []
      }
    }
  }

  /**
   * Загрузить файл для проекта
   */
  async uploadFile(projectId: number, file: File, description?: string) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (description) {
        formData.append('description', description)
      }

      const response = await axiosInstance.post(`/admin/files/upload/${projectId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      return {
        success: true,
        file: response.data.file as ProjectFile,
        message: 'Файл успешно загружен'
      }
    } catch (error: any) {
      console.error('Error uploading file:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки файла'
      }
    }
  }

  /**
   * Удалить файл
   */
  async deleteFile(fileId: number) {
    try {
      const response = await axiosInstance.delete(`/admin/files/delete/${fileId}`)

      return {
        success: true,
        message: 'Файл успешно удален'
      }
    } catch (error: any) {
      console.error('Error deleting file:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка удаления файла'
      }
    }
  }

  /**
   * Получить URL для скачивания файла
   */
  getDownloadUrl(fileId: number): string {
    return `/admin/files/download/${fileId}`
  }

  /**
   * Получить статистику по файлам
   */
  async getStats() {
    try {
      const [projectsResponse, filesResponse] = await Promise.all([
        axiosInstance.get('/admin/projects/?per_page=1000'),
        this.getAllFiles()
      ])

      const projects = projectsResponse.data.projects || []
      const allFiles = filesResponse.files || []

      // Подсчитываем статистику
      const projectsWithFiles = new Set(allFiles.map((f: ProjectFile) => f.project_id))
      const totalSize = allFiles.reduce((sum: number, f: ProjectFile) => sum + (f.file_size || 0), 0)

      return {
        success: true,
        stats: {
          total_projects: projects.length,
          projects_with_files: projectsWithFiles.size,
          projects_without_files: projects.length - projectsWithFiles.size,
          total_files: allFiles.length,
          total_size: totalSize
        } as ProjectFilesStats
      }
    } catch (error: any) {
      console.error('Error fetching stats:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки статистики',
        stats: {
          total_projects: 0,
          projects_with_files: 0,
          projects_without_files: 0,
          total_files: 0,
          total_size: 0
        }
      }
    }
  }
}

const projectFilesApi = new ProjectFilesAPI()
export default projectFilesApi

// Re-export types for clarity
export type { ProjectFile, ProjectWithFiles, ProjectFilesStats, ProjectFilesFilters }
