import { useState, useEffect, useCallback } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import projectFilesApi from '../api/projectFiles'
import type { ProjectWithFiles, ProjectFilesStats, ProjectFilesFilters } from '../api/projectFiles'

interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

export const ProjectFiles = () => {
  const { currentTheme } = useTheme()

  // ============= STATE =============
  const [projects, setProjects] = useState<ProjectWithFiles[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<ProjectFilesStats>({
    total_projects: 0,
    projects_with_files: 0,
    projects_without_files: 0,
    total_files: 0,
    total_size: 0
  })
  const [filters, setFilters] = useState<ProjectFilesFilters>({
    search: '',
    page: 1,
    limit: 20
  })
  const [expandedProjects, setExpandedProjects] = useState<Set<number>>(new Set())
  const [uploadingFor, setUploadingFor] = useState<number | null>(null)
  const [toasts, setToasts] = useState<Toast[]>([])

  // ============= TOAST NOTIFICATIONS =============
  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 3000)
  }, [])

  // ============= DATA LOADING =============
  const loadData = useCallback(async () => {
    try {
      setLoading(true)

      const [projectsResponse, statsResponse] = await Promise.all([
        projectFilesApi.getProjectsWithFiles(filters),
        projectFilesApi.getStats()
      ])

      if (projectsResponse.success) {
        setProjects(projectsResponse.projects)
      } else {
        showToast(projectsResponse.message || 'Ошибка загрузки проектов', 'error')
      }

      if (statsResponse.success) {
        setStats(statsResponse.stats)
      }
    } catch (error) {
      console.error('Error loading data:', error)
      showToast('Ошибка загрузки данных', 'error')
    } finally {
      setLoading(false)
    }
  }, [filters, showToast])

  useEffect(() => {
    loadData()
  }, [loadData])

  // ============= HANDLERS =============
  const toggleProject = (projectId: number) => {
    setExpandedProjects(prev => {
      const newSet = new Set(prev)
      if (newSet.has(projectId)) {
        newSet.delete(projectId)
      } else {
        newSet.add(projectId)
      }
      return newSet
    })
  }

  const handleFileUpload = async (projectId: number, file: File, description?: string) => {
    try {
      setUploadingFor(projectId)
      const response = await projectFilesApi.uploadFile(projectId, file, description)

      if (response.success) {
        showToast('Файл успешно загружен', 'success')
        // Обновляем данные
        await loadData()
      } else {
        showToast(response.message || 'Ошибка загрузки файла', 'error')
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      showToast('Ошибка загрузки файла', 'error')
    } finally {
      setUploadingFor(null)
    }
  }

  const handleFileDelete = async (fileId: number, projectId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот файл?')) {
      return
    }

    try {
      const response = await projectFilesApi.deleteFile(fileId)

      if (response.success) {
        showToast('Файл успешно удален', 'success')
        // Обновляем данные
        await loadData()
      } else {
        showToast(response.message || 'Ошибка удаления файла', 'error')
      }
    } catch (error) {
      console.error('Error deleting file:', error)
      showToast('Ошибка удаления файла', 'error')
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  // ============= RENDER =============
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className={`text-3xl font-bold ${currentTheme.text}`}>База проектов</h1>
          <p className="text-gray-500 mt-1">Управление файлами проектов</p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-4`}>
          <div className="text-sm text-gray-500">Всего проектов</div>
          <div className={`text-2xl font-bold ${currentTheme.text}`}>{stats.total_projects}</div>
        </div>

        <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-4`}>
          <div className="text-sm text-gray-500">С файлами</div>
          <div className={`text-2xl font-bold text-green-600`}>{stats.projects_with_files}</div>
        </div>

        <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-4`}>
          <div className="text-sm text-gray-500">Без файлов</div>
          <div className={`text-2xl font-bold text-orange-600`}>{stats.projects_without_files}</div>
        </div>

        <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-4`}>
          <div className="text-sm text-gray-500">Всего файлов</div>
          <div className={`text-2xl font-bold ${currentTheme.primary}`}>{stats.total_files}</div>
          <div className="text-xs text-gray-400 mt-1">{formatFileSize(stats.total_size)}</div>
        </div>
      </div>

      {/* Search */}
      <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-4`}>
        <input
          type="text"
          placeholder="Поиск по названию проекта..."
          value={filters.search || ''}
          onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
          className={`w-full px-4 py-2 border ${currentTheme.border} rounded-lg ${currentTheme.input} ${currentTheme.text}`}
        />
      </div>

      {/* Projects List */}
      {loading ? (
        <div className="text-center py-12">
          <div className={`inline-block animate-spin rounded-full h-12 w-12 border-b-2 ${currentTheme.primary}`}></div>
          <p className={`mt-4 ${currentTheme.text}`}>Загрузка проектов...</p>
        </div>
      ) : projects.length === 0 ? (
        <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-12 text-center`}>
          <div className="text-gray-400 text-6xl mb-4">📁</div>
          <h3 className={`text-xl font-semibold ${currentTheme.text} mb-2`}>Проекты не найдены</h3>
          <p className="text-gray-500">Попробуйте изменить параметры поиска</p>
        </div>
      ) : (
        <div className="space-y-4">
          {projects.map((project) => {
            const isExpanded = expandedProjects.has(project.id)
            const hasFiles = (project.files_count || 0) > 0

            return (
              <div
                key={project.id}
                className={`${currentTheme.card} ${currentTheme.border} border rounded-lg overflow-hidden`}
              >
                {/* Project Header */}
                <div
                  className={`p-4 cursor-pointer hover:bg-opacity-50 ${currentTheme.hover}`}
                  onClick={() => toggleProject(project.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`transform transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
                        ▶
                      </div>
                      <div>
                        <h3 className={`font-semibold ${currentTheme.text}`}>{project.title}</h3>
                        <div className="flex items-center space-x-3 text-sm text-gray-500 mt-1">
                          <span>ID: {project.id}</span>
                          {project.user && (
                            <span>
                              Клиент: {project.user.first_name} {project.user.last_name}
                            </span>
                          )}
                          <span className={hasFiles ? 'text-green-600' : 'text-orange-600'}>
                            {hasFiles ? `📎 ${project.files_count} файлов` : '📎 Нет файлов'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className={`px-3 py-1 rounded-full text-sm ${
                        project.status === 'completed' ? 'bg-green-100 text-green-800' :
                        project.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {project.status_name || project.status}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Project Files (Expanded) */}
                {isExpanded && (
                  <div className={`border-t ${currentTheme.border} p-4 space-y-4`}>
                    {/* Upload Section */}
                    <div className={`p-4 rounded-lg ${currentTheme.hover}`}>
                      <h4 className={`font-semibold ${currentTheme.text} mb-3`}>Загрузить файл</h4>
                      <input
                        type="file"
                        onChange={(e) => {
                          const file = e.target.files?.[0]
                          if (file) {
                            handleFileUpload(project.id, file)
                            e.target.value = ''
                          }
                        }}
                        disabled={uploadingFor === project.id}
                        className={`w-full px-4 py-2 border ${currentTheme.border} rounded-lg ${currentTheme.input}`}
                      />
                      {uploadingFor === project.id && (
                        <p className="text-sm text-blue-600 mt-2">Загрузка файла...</p>
                      )}
                    </div>

                    {/* Files List */}
                    {project.files && project.files.length > 0 ? (
                      <div className="space-y-2">
                        <h4 className={`font-semibold ${currentTheme.text}`}>Файлы проекта:</h4>
                        {project.files.map((file) => (
                          <div
                            key={file.id}
                            className={`flex items-center justify-between p-3 rounded-lg ${currentTheme.hover} border ${currentTheme.border}`}
                          >
                            <div className="flex items-center space-x-3">
                              <div className="text-2xl">
                                {file.file_type === 'archive' ? '📦' :
                                 file.file_type === 'image' ? '🖼️' :
                                 file.file_type === 'document' ? '📄' : '📎'}
                              </div>
                              <div>
                                <div className={`font-medium ${currentTheme.text}`}>
                                  {file.original_filename}
                                </div>
                                <div className="text-sm text-gray-500">
                                  {formatFileSize(file.file_size)} • {new Date(file.uploaded_at).toLocaleDateString()}
                                  {file.description && ` • ${file.description}`}
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center space-x-2">
                              <a
                                href={projectFilesApi.getDownloadUrl(file.id)}
                                download
                                className={`px-3 py-1 rounded ${currentTheme.primary} text-white hover:opacity-80`}
                              >
                                Скачать
                              </a>
                              <button
                                onClick={() => handleFileDelete(file.id, project.id)}
                                className="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700"
                              >
                                Удалить
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-400">
                        <p>Файлы не найдены</p>
                        <p className="text-sm mt-2">Загрузите первый файл для этого проекта</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Toast Notifications */}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-3 rounded-lg shadow-lg text-white ${
              toast.type === 'success' ? 'bg-green-600' :
              toast.type === 'error' ? 'bg-red-600' :
              'bg-blue-600'
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  )
}
