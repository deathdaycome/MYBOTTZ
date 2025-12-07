import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  RotateCcw,
  Plus,
  Filter,
  Play,
  Pause,
  Send,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileText,
  MessageCircle,
  X,
  Image as ImageIcon,
  Download,
  Loader2,
} from 'lucide-react'
// API imports
import revisionsApi from '../api/revisions'
import type { Revision, RevisionMessage, RevisionFile } from '../api/revisions'
import { apiService } from '../services/api'

export const Revisions = () => {
  const [revisions, setRevisions] = useState<Revision[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total_revisions: 0,
    pending_revisions: 0,
    completed_revisions: 0,
    my_revisions: 0,
  })

  // Filters
  const [projectFilter, setProjectFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')
  const [myRevisionsOnly, setMyRevisionsOnly] = useState(false)

  // Modal states
  const [selectedRevision, setSelectedRevision] = useState<Revision | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)

  // Create form
  const [projects, setProjects] = useState<any[]>([])
  const [createForm, setCreateForm] = useState({
    project_id: '',
    title: '',
    description: '',
    priority: 'normal',
  })

  // Message form
  const [messageText, setMessageText] = useState('')
  const [messageInternal, setMessageInternal] = useState(false)
  const [messageFiles, setMessageFiles] = useState<File[]>([])
  const [messages, setMessages] = useState<RevisionMessage[]>([])
  const [files, setFiles] = useState<RevisionFile[]>([])

  // Toast notifications
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null)

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }, [])

  // Load data
  const loadRevisions = useCallback(async () => {
    try {
      setLoading(true)
      const response = await revisionsApi.getRevisions({
        project_id: projectFilter ? parseInt(projectFilter) : undefined,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        assigned_to_me: myRevisionsOnly || undefined,
      })
      if (response.success) {
        setRevisions(response.data)
      }
    } catch (error) {
      showToast('Ошибка загрузки правок', 'error')
    } finally {
      setLoading(false)
    }
  }, [projectFilter, statusFilter, priorityFilter, myRevisionsOnly, showToast])

  const loadStats = useCallback(async () => {
    try {
      const response = await revisionsApi.getStats()
      if (response.success) {
        setStats(response.data)
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }, [])

  const loadProjects = useCallback(async () => {
    try {
      const response = await apiService.getProjects()
      if (response.success) {
        setProjects(response.projects)
      }
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }, [])

  useEffect(() => {
    loadRevisions()
    loadStats()
    loadProjects()
  }, [loadRevisions, loadStats, loadProjects])

  // Create revision
  const handleCreateRevision = async () => {
    if (!createForm.project_id || !createForm.title || !createForm.description) {
      showToast('Заполните все обязательные поля', 'error')
      return
    }

    try {
      const response = await revisionsApi.createRevision({
        project_id: parseInt(createForm.project_id),
        title: createForm.title,
        description: createForm.description,
        priority: createForm.priority,
      })

      if (response.success) {
        showToast('Правка создана успешно', 'success')
        setShowCreateModal(false)
        setCreateForm({ project_id: '', title: '', description: '', priority: 'normal' })
        loadRevisions()
        loadStats()
      }
    } catch (error) {
      showToast('Ошибка при создании правки', 'error')
    }
  }

  // View revision details
  const viewRevision = async (revision: Revision) => {
    try {
      const response = await revisionsApi.getRevision(revision.id)
      if (response.success) {
        setSelectedRevision(response.data)

        // Load messages and files
        const [messagesRes, filesRes] = await Promise.all([
          revisionsApi.getMessages(revision.id),
          revisionsApi.getFiles(revision.id),
        ])

        if (messagesRes.success) setMessages(messagesRes.data)
        if (filesRes.success) setFiles(filesRes.data)

        setShowDetailModal(true)
      }
    } catch (error) {
      showToast('Ошибка загрузки деталей правки', 'error')
    }
  }

  // Add message
  const handleAddMessage = async () => {
    if (!selectedRevision || !messageText.trim()) {
      showToast('Введите текст сообщения', 'error')
      return
    }

    try {
      const response = await revisionsApi.addMessage(
        selectedRevision.id,
        messageText,
        messageInternal,
        messageFiles
      )

      if (response.success) {
        showToast('Сообщение добавлено', 'success')
        setMessageText('')
        setMessageInternal(false)
        setMessageFiles([])

        // Reload messages
        const messagesRes = await revisionsApi.getMessages(selectedRevision.id)
        if (messagesRes.success) setMessages(messagesRes.data)
      }
    } catch (error) {
      showToast('Ошибка при добавлении сообщения', 'error')
    }
  }

  // Update status
  const handleUpdateStatus = async (status: string) => {
    if (!selectedRevision) return

    try {
      const response = await revisionsApi.updateRevision(selectedRevision.id, { status })
      if (response.success) {
        showToast('Статус обновлен', 'success')
        loadRevisions()
        loadStats()
        setShowDetailModal(false)
      }
    } catch (error) {
      showToast('Ошибка обновления статуса', 'error')
    }
  }

  // Send for review
  const handleSendForReview = async () => {
    if (!selectedRevision) return

    try {
      const response = await revisionsApi.sendForReview(selectedRevision.id)
      if (response.success) {
        showToast('Правка отправлена на проверку', 'success')
        loadRevisions()
        loadStats()
        setShowDetailModal(false)
      }
    } catch (error) {
      showToast('Ошибка отправки на проверку', 'error')
    }
  }

  // Timer controls
  const handleStartTimer = async (revisionId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await revisionsApi.startTimer(revisionId)
      loadRevisions()
    } catch (error) {
      showToast('Ошибка запуска таймера', 'error')
    }
  }

  const handleStopTimer = async (revisionId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await revisionsApi.stopTimer(revisionId)
      loadRevisions()
    } catch (error) {
      showToast('Ошибка остановки таймера', 'error')
    }
  }

  // Progress update
  const handleUpdateProgress = async (revisionId: number, progress: number) => {
    try {
      await revisionsApi.updateProgress(revisionId, progress)
      showToast('Прогресс обновлен', 'success')
      loadRevisions()
    } catch (error) {
      showToast('Ошибка обновления прогресса', 'error')
    }
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: 'В ожидании',
      in_progress: 'В работе',
      review: 'На проверке',
      completed: 'Выполнено',
      approved: 'Принято клиентом',
      needs_rework: 'Требует доработки',
      rejected: 'Отклонено',
    }
    return labels[status] || status
  }

  const getPriorityLabel = (priority: string) => {
    const labels: Record<string, string> = {
      low: 'Низкий',
      normal: 'Обычный',
      high: 'Высокий',
      urgent: 'Срочный',
    }
    return labels[priority] || priority
  }

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return hours > 0 ? `${hours}ч ${minutes}м` : `${minutes}м`
  }

  const filteredRevisions = useMemo(() => revisions, [revisions])

  return (
    <div className="p-8 max-w-[1920px] mx-auto">
      {/* Toast notification */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${
            toast.type === 'success'
              ? 'bg-green-500'
              : toast.type === 'error'
              ? 'bg-red-500'
              : 'bg-blue-500'
          } text-white flex items-center gap-2`}
        >
          <span>{toast.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <RotateCcw className="w-6 h-6 text-white" />
            </div>
            Правки проектов
          </h1>
          <p className="text-gray-500 mt-1">Управление правками и ревизиями</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Создать правку
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
              <FileText className="w-6 h-6 text-violet-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.total_revisions}</div>
              <div className="text-sm text-gray-500">Всего правок</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-yellow-100 flex items-center justify-center">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.pending_revisions}</div>
              <div className="text-sm text-gray-500">В ожидании</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.completed_revisions}</div>
              <div className="text-sm text-gray-500">Выполнено</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.my_revisions}</div>
              <div className="text-sm text-gray-500">Мои правки</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <h3 className="font-semibold text-gray-900">Фильтры</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <select
            value={projectFilter}
            onChange={(e) => setProjectFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
          >
            <option value="">Все проекты</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.title}
              </option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
          >
            <option value="">Все статусы</option>
            <option value="pending">В ожидании</option>
            <option value="in_progress">В работе</option>
            <option value="review">На проверке</option>
            <option value="completed">Выполнено</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
          >
            <option value="">Все приоритеты</option>
            <option value="low">Низкий</option>
            <option value="normal">Обычный</option>
            <option value="high">Высокий</option>
            <option value="urgent">Срочный</option>
          </select>

          <label className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg">
            <input
              type="checkbox"
              checked={myRevisionsOnly}
              onChange={(e) => setMyRevisionsOnly(e.target.checked)}
              className="w-4 h-4 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
            />
            <span className="text-sm text-gray-700">Только мои</span>
          </label>

          <button
            onClick={() => {
              setProjectFilter('')
              setStatusFilter('')
              setPriorityFilter('')
              setMyRevisionsOnly(false)
            }}
            className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-700"
          >
            Сбросить
          </button>
        </div>
      </div>

      {/* Revisions Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">№</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Проект</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Заголовок</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Статус</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">
                  Приоритет
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Прогресс</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Время</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto text-violet-500" />
                  </td>
                </tr>
              ) : filteredRevisions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                    Правки не найдены
                  </td>
                </tr>
              ) : (
                filteredRevisions.map((revision) => (
                  <tr
                    key={revision.id}
                    onClick={() => viewRevision(revision)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4">
                      <span className="text-sm font-medium text-gray-900">
                        #{revision.revision_number}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {revision.project?.title || 'Неизвестно'}
                      </div>
                      <div className="text-xs text-gray-500">{revision.project?.status}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{revision.title}</div>
                      <div className="text-xs text-gray-500 line-clamp-1">
                        {revision.description}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-violet-100 text-violet-700">
                        {getStatusLabel(revision.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`text-sm font-medium ${
                          revision.priority === 'urgent'
                            ? 'text-red-600'
                            : revision.priority === 'high'
                            ? 'text-orange-600'
                            : revision.priority === 'normal'
                            ? 'text-blue-600'
                            : 'text-green-600'
                        }`}
                      >
                        {getPriorityLabel(revision.priority)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                          <div
                            className="bg-violet-600 h-2 rounded-full transition-all"
                            style={{ width: `${revision.progress || 0}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {revision.progress || 0}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {formatTime(revision.time_spent_seconds || 0)}
                        </span>
                        {revision.timer_started_at ? (
                          <button
                            onClick={(e) => handleStopTimer(revision.id, e)}
                            className="p-1 hover:bg-red-100 rounded transition-colors"
                          >
                            <Pause className="w-4 h-4 text-red-600" />
                          </button>
                        ) : (
                          <button
                            onClick={(e) => handleStartTimer(revision.id, e)}
                            className="p-1 hover:bg-green-100 rounded transition-colors"
                          >
                            <Play className="w-4 h-4 text-green-600" />
                          </button>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => viewRevision(revision)}
                        className="text-violet-600 hover:text-violet-700 font-medium text-sm"
                      >
                        Открыть
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Создать правку</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Проект *
                </label>
                <select
                  value={createForm.project_id}
                  onChange={(e) => setCreateForm({ ...createForm, project_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                >
                  <option value="">Выберите проект</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Заголовок *
                </label>
                <input
                  type="text"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  placeholder="Краткое описание проблемы"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание *
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  placeholder="Подробное описание проблемы и что нужно исправить"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Приоритет</label>
                <select
                  value={createForm.priority}
                  onChange={(e) => setCreateForm({ ...createForm, priority: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                >
                  <option value="low">Низкий</option>
                  <option value="normal">Обычный</option>
                  <option value="high">Высокий</option>
                  <option value="urgent">Срочный</option>
                </select>
              </div>
            </div>

            <div className="p-6 border-t border-gray-100 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-700"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateRevision}
                className="px-6 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
              >
                Создать
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedRevision && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  Правка #{selectedRevision.revision_number} - {selectedRevision.title}
                </h2>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Info */}
              <div className="space-y-4">
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Проект</div>
                    <div className="font-medium">{selectedRevision.project?.title}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Статус</div>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-violet-100 text-violet-700">
                      {getStatusLabel(selectedRevision.status)}
                    </span>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Приоритет</div>
                    <div className="font-medium">{getPriorityLabel(selectedRevision.priority)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Описание</div>
                    <div className="text-sm">{selectedRevision.description}</div>
                  </div>
                </div>

                {files.length > 0 && (
                  <div className="bg-gray-50 rounded-xl p-4">
                    <div className="text-sm font-medium mb-3">Файлы</div>
                    <div className="space-y-2">
                      {files.map((file) => (
                        <div
                          key={file.id}
                          className="flex items-center gap-2 p-2 bg-white rounded-lg"
                        >
                          {file.file_type === 'image' ? (
                            <ImageIcon className="w-4 h-4 text-gray-400" />
                          ) : (
                            <FileText className="w-4 h-4 text-gray-400" />
                          )}
                          <span className="text-sm flex-1 truncate">{file.original_filename}</span>
                          <a
                            href={file.download_url}
                            download
                            className="p-1 hover:bg-gray-100 rounded"
                          >
                            <Download className="w-4 h-4 text-gray-600" />
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Messages */}
              <div className="lg:col-span-2">
                <div className="bg-gray-50 rounded-xl p-4 h-[400px] overflow-y-auto mb-4">
                  {messages.length === 0 ? (
                    <div className="text-center text-gray-500 py-8">Сообщений пока нет</div>
                  ) : (
                    <div className="space-y-3">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className={`p-4 rounded-lg ${
                            message.is_internal ? 'bg-yellow-50 border-l-4 border-yellow-400' : 'bg-white'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="font-medium text-sm">{message.sender_name}</div>
                            <div className="text-xs text-gray-500">
                              {new Date(message.created_at).toLocaleString('ru-RU')}
                            </div>
                          </div>
                          <div className="text-sm text-gray-700 whitespace-pre-wrap">
                            {message.message || message.content}
                          </div>
                          {message.is_internal && (
                            <div className="mt-2 text-xs text-yellow-700">Внутреннее сообщение</div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Message Form */}
                <div className="space-y-3">
                  <textarea
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    rows={3}
                    placeholder="Введите сообщение..."
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                  />
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={messageInternal}
                        onChange={(e) => setMessageInternal(e.target.checked)}
                        className="w-4 h-4 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
                      />
                      <span className="text-sm text-gray-700">Внутреннее сообщение</span>
                    </label>
                    <button
                      onClick={handleAddMessage}
                      className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 flex items-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Отправить
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-100 flex justify-between">
              <div className="flex gap-2">
                {selectedRevision.status === 'in_progress' && (
                  <button
                    onClick={handleSendForReview}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Отправить на проверку
                  </button>
                )}
                {selectedRevision.status === 'pending' && (
                  <button
                    onClick={() => handleUpdateStatus('in_progress')}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Взять в работу
                  </button>
                )}
                {selectedRevision.status !== 'completed' && (
                  <button
                    onClick={() => handleUpdateStatus('completed')}
                    className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 flex items-center gap-2"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    Завершить
                  </button>
                )}
              </div>
              <button
                onClick={() => setShowDetailModal(false)}
                className="px-6 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
