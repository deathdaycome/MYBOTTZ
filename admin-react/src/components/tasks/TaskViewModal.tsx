import { useState, useEffect } from 'react'
import {
  X,
  Play,
  Pause,
  Clock,
  Calendar,
  User,
  MessageCircle,
  Send,
  Paperclip,
  CheckCircle,
  Archive,
  Edit,
  Trash2,
  AlertCircle,
  Download,
  ExternalLink,
  TrendingUp,
  Timer,
  Target,
  FileText,
  Tag,
} from 'lucide-react'
import tasksApi from '../../api/tasks'
import type { Task, TaskComment } from '../../api/tasks'
import { TaskTags } from './TaskTags'

interface TaskViewModalProps {
  isOpen: boolean
  onClose: () => void
  task: Task
  onEdit: () => void
  onDelete: () => void
  onRefresh: () => void
}

export const TaskViewModal = ({
  isOpen,
  onClose,
  task: initialTask,
  onEdit,
  onDelete,
  onRefresh,
}: TaskViewModalProps) => {
  const [task, setTask] = useState<Task>(initialTask)
  const [comments, setComments] = useState<TaskComment[]>([])
  const [newComment, setNewComment] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [isInternal, setIsInternal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [timerRunning, setTimerRunning] = useState(!!initialTask.timer_started_at)
  const [progress, setProgress] = useState(initialTask.progress || 0)
  const [previewUrls, setPreviewUrls] = useState<string[]>([])
  const [deployUrl, setDeployUrl] = useState(initialTask.deploy_url || '')
  const [isEditingDeployUrl, setIsEditingDeployUrl] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setTask(initialTask)
      setTimerRunning(!!initialTask.timer_started_at)
      setProgress(initialTask.progress || 0)
      setDeployUrl(initialTask.deploy_url || '')
      setIsEditingDeployUrl(false)
      loadComments()
    }
  }, [isOpen, initialTask])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'

      return () => {
        const scrollY = document.body.style.top
        document.body.style.position = ''
        document.body.style.top = ''
        document.body.style.width = ''
        document.body.style.overflow = ''
        window.scrollTo(0, parseInt(scrollY || '0') * -1)
      }
    }
  }, [isOpen])

  const loadComments = async () => {
    try {
      const response = await tasksApi.getComments(initialTask.id)
      if (response.success) {
        setComments(response.comments)
      }
    } catch (error) {
      console.error('Error loading comments:', error)
    }
  }

  const handleTimerToggle = async () => {
    try {
      if (timerRunning) {
        const response = await tasksApi.stopTimer(task.id)
        if (response.success) {
          setTask(response.data)
          setTimerRunning(false)
          onRefresh()
        }
      } else {
        const response = await tasksApi.startTimer(task.id)
        if (response.success) {
          setTask(response.data)
          setTimerRunning(true)
          onRefresh()
        }
      }
    } catch (error) {
      console.error('Error toggling timer:', error)
    }
  }

  const handleProgressChange = async (newProgress: number) => {
    try {
      const response = await tasksApi.updateProgress(task.id, newProgress)
      if (response.success) {
        setProgress(newProgress)
        onRefresh()
      }
    } catch (error) {
      console.error('Error updating progress:', error)
    }
  }

  const handleSaveDeployUrl = async () => {
    try {
      const response = await tasksApi.updateTask(task.id, { deploy_url: deployUrl })
      if (response.success) {
        setTask(response.task)
        setIsEditingDeployUrl(false)
        onRefresh()
      }
    } catch (error) {
      console.error('Error updating deploy URL:', error)
      alert('Ошибка сохранения ссылки на деплой')
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim() && selectedFiles.length === 0) return

    try {
      setLoading(true)
      const response = await tasksApi.addComment(task.id, newComment, isInternal, selectedFiles)

      if (response.success) {
        setNewComment('')
        setSelectedFiles([])
        previewUrls.forEach(url => URL.revokeObjectURL(url))
        setPreviewUrls([])
        setIsInternal(false)
        loadComments()
        onRefresh()
      } else {
        alert('Ошибка: ' + (response.error || 'Не удалось добавить комментарий'))
      }
    } catch (error: any) {
      let errorMessage = 'Ошибка добавления комментария'
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Превышено время ожидания. Попробуйте загрузить файлы меньшего размера.'
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      }
      alert(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const items = e.clipboardData?.items
    if (!items) return

    const files: File[] = []
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.type.indexOf('image') !== -1) {
        const file = item.getAsFile()
        if (file) {
          const timestamp = new Date().getTime()
          const newFile = new File([file], `screenshot-${timestamp}.png`, { type: file.type })
          files.push(newFile)
        }
      }
    }

    if (files.length > 0) {
      handleFilesAdded(files)
    }
  }

  const handleFilesAdded = (newFiles: File[]) => {
    const updatedFiles = [...selectedFiles, ...newFiles]
    setSelectedFiles(updatedFiles)

    const newPreviewUrls: string[] = []
    newFiles.forEach(file => {
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file)
        newPreviewUrls.push(url)
      }
    })
    setPreviewUrls([...previewUrls, ...newPreviewUrls])
  }

  const handleRemoveFile = (index: number) => {
    const updatedFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(updatedFiles)

    if (previewUrls[index]) {
      URL.revokeObjectURL(previewUrls[index])
    }
    const updatedPreviews = previewUrls.filter((_, i) => i !== index)
    setPreviewUrls(updatedPreviews)
  }

  useEffect(() => {
    return () => {
      previewUrls.forEach(url => URL.revokeObjectURL(url))
    }
  }, [previewUrls])

  const handleMarkCompleted = async () => {
    try {
      const response = await tasksApi.markCompleted(task.id)
      if (response.success) {
        onRefresh()
        onClose()
      }
    } catch (error) {
      console.error('Error marking completed:', error)
    }
  }

  const handleArchive = async () => {
    if (!confirm('Вы уверены, что хотите архивировать эту задачу?')) return

    try {
      const response = await tasksApi.archiveTask(task.id)
      if (response.success) {
        onRefresh()
        onClose()
      }
    } catch (error) {
      console.error('Error archiving task:', error)
    }
  }

  const formatTimeSpent = (seconds?: number) => {
    if (!seconds) return '0ч 0м'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}ч ${minutes}м`
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Не указано'
    const date = new Date(dateString)
    return date.toLocaleString('ru-RU')
  }

  const getPriorityColor = () => {
    switch (task.priority) {
      case 'urgent':
        return 'bg-red-100 text-red-700 border-red-300'
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-300'
      case 'normal':
        return 'bg-blue-100 text-blue-700 border-blue-300'
      case 'low':
        return 'bg-gray-100 text-gray-700 border-gray-300'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  const getStatusColor = () => {
    switch (task.status) {
      case 'pending':
        return 'bg-gradient-to-r from-blue-500 to-blue-600'
      case 'in_progress':
        return 'bg-gradient-to-r from-yellow-500 to-orange-500'
      case 'completed':
        return 'bg-gradient-to-r from-green-500 to-emerald-600'
      default:
        return 'bg-gradient-to-r from-gray-500 to-gray-600'
    }
  }

  const getStatusText = () => {
    switch (task.status) {
      case 'pending':
        return 'В ожидании'
      case 'in_progress':
        return 'В работе'
      case 'completed':
        return 'Выполнена'
      default:
        return task.status
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className={`${getStatusColor()} text-white px-8 py-6 flex-shrink-0`}>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <h3 className="text-2xl font-bold">{task.title}</h3>
                {task.is_overdue && (
                  <span className="flex items-center gap-1 bg-red-500 px-3 py-1 rounded-full text-sm font-semibold animate-pulse">
                    <AlertCircle className="w-4 h-4" />
                    Просрочено
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1.5 rounded-lg border text-sm font-semibold ${getPriorityColor()}`}>
                  {task.priority === 'urgent' && 'Срочно'}
                  {task.priority === 'high' && 'Высокий'}
                  {task.priority === 'normal' && 'Обычный'}
                  {task.priority === 'low' && 'Низкий'}
                </span>
                <span className="px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg text-sm font-semibold">
                  {getStatusText()}
                </span>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Body - Scrollable */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-4">
            {/* Description Card - Compact */}
            {task.description && (
              <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-xl p-4 border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <h4 className="text-lg font-bold text-gray-900">Описание</h4>
                </div>
                <p className="text-gray-800 text-sm whitespace-pre-wrap leading-relaxed">{task.description}</p>
              </div>
            )}

            {/* Compact 2-Column Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Progress Card */}
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-indigo-700" />
                  <h4 className="font-bold text-gray-900">Прогресс</h4>
                </div>
                <div className="text-center mb-3">
                  <span className={`text-3xl font-bold ${
                    progress < 25 ? 'text-red-600' :
                    progress < 50 ? 'text-orange-600' :
                    progress < 75 ? 'text-yellow-600' :
                    progress < 100 ? 'text-blue-600' :
                    'text-green-600'
                  }`}>{progress}%</span>
                </div>
                <div className="relative w-full">
                  <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full transition-all duration-500 ease-out"
                      style={{
                        width: `${progress}%`,
                        background: progress < 25
                          ? 'linear-gradient(90deg, #ef4444, #f87171)'
                          : progress < 50
                          ? 'linear-gradient(90deg, #f97316, #fb923c)'
                          : progress < 75
                          ? 'linear-gradient(90deg, #eab308, #fde047)'
                          : progress < 100
                          ? 'linear-gradient(90deg, #3b82f6, #60a5fa)'
                          : 'linear-gradient(90deg, #22c55e, #4ade80)',
                      }}
                    />
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={progress}
                    onChange={(e) => handleProgressChange(parseInt(e.target.value))}
                    className="absolute top-0 left-0 w-full h-3 appearance-none cursor-pointer bg-transparent opacity-0"
                    disabled={task.status === 'completed'}
                  />
                </div>
                <p className="text-xs text-gray-600 mt-1 text-center">Перетащите для изменения</p>
              </div>

              {/* Executor Card */}
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4 border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <User className="w-4 h-4 text-blue-700" />
                  <h4 className="font-bold text-gray-900">Исполнитель</h4>
                </div>
                <p className="text-lg font-semibold text-gray-900">
                  {task.assigned_to?.first_name || task.assigned_to?.username || 'Не назначен'}
                </p>
              </div>

              {/* Time Card */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-4 h-4 text-green-700" />
                  <h4 className="font-bold text-gray-900">Время</h4>
                </div>
                <p className="text-xl font-bold text-gray-900 mb-2">{formatTimeSpent(task.time_spent_seconds)}</p>
                {task.status !== 'completed' && (
                  <button
                    onClick={handleTimerToggle}
                    className={`w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg font-semibold transition-all text-sm ${
                      timerRunning
                        ? 'bg-red-500 text-white hover:bg-red-600'
                        : 'bg-green-500 text-white hover:bg-green-600'
                    }`}
                  >
                    {timerRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {timerRunning ? 'Остановить' : 'Запустить'}
                  </button>
                )}
              </div>

              {/* Creator Card */}
              <div className="bg-gradient-to-br from-slate-50 to-gray-100 rounded-xl p-4 border border-slate-200">
                <div className="flex items-center gap-2 mb-2">
                  <User className="w-4 h-4 text-slate-700" />
                  <h4 className="font-bold text-gray-900">Создатель</h4>
                </div>
                <p className="text-lg font-semibold text-gray-900">
                  {task.created_by?.first_name || task.created_by?.username || 'Неизвестно'}
                </p>
              </div>

              {/* Deadline Card */}
              <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-4 border border-orange-200">
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="w-4 h-4 text-orange-700" />
                  <h4 className="font-bold text-gray-900">Дедлайн</h4>
                </div>
                <p className={`text-base font-semibold ${task.is_overdue ? 'text-red-600' : 'text-gray-900'}`}>
                  {formatDate(task.deadline)}
                </p>
              </div>

              {/* Tags Card */}
              {task.tags && task.tags.length > 0 && (
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Tag className="w-4 h-4 text-purple-700" />
                    <h4 className="font-bold text-gray-900">Теги</h4>
                  </div>
                  <TaskTags tags={task.tags} size="sm" />
                </div>
              )}
            </div>

            {/* Deploy URL Card */}
            <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl p-4 border border-cyan-200">
              <div className="flex items-center gap-2 mb-3">
                <ExternalLink className="w-4 h-4 text-cyan-700" />
                <h4 className="font-bold text-gray-900">Ссылка на деплой</h4>
              </div>
              {isEditingDeployUrl ? (
                <div className="flex items-center gap-2">
                  <input
                    type="url"
                    value={deployUrl}
                    onChange={(e) => setDeployUrl(e.target.value)}
                    placeholder="https://example.com/app"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  />
                  <button
                    onClick={handleSaveDeployUrl}
                    className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Сохранить
                  </button>
                  <button
                    onClick={() => {
                      setDeployUrl(task.deploy_url || '')
                      setIsEditingDeployUrl(false)
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors text-sm"
                  >
                    Отмена
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  {task.deploy_url ? (
                    <>
                      <a
                        href={task.deploy_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 px-3 py-2 bg-white border border-blue-300 rounded-lg text-blue-600 font-semibold hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 text-sm"
                      >
                        Открыть приложение
                        <ExternalLink className="w-4 h-4" />
                      </a>
                      <button
                        onClick={() => setIsEditingDeployUrl(true)}
                        className="px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors text-sm"
                      >
                        Изменить
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => setIsEditingDeployUrl(true)}
                      className="w-full px-3 py-2 bg-blue-100 text-blue-700 font-semibold rounded-lg hover:bg-blue-200 transition-colors flex items-center justify-center gap-2 text-sm"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Добавить ссылку на деплой
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Comments Section */}
            <div className="bg-gradient-to-br from-slate-50 to-gray-100 rounded-xl p-4 border border-slate-200">
              <div className="flex items-center gap-2 mb-3">
                <MessageCircle className="w-4 h-4 text-slate-700" />
                <h4 className="font-bold text-gray-900">Комментарии ({comments.length})</h4>
              </div>

              {/* Comments List */}
              <div className="space-y-2 mb-4 max-h-80 overflow-y-auto">
                {comments.map((comment) => (
                  <div
                    key={comment.id}
                    className={`p-3 rounded-lg ${
                      comment.is_internal ? 'bg-yellow-50 border border-yellow-200' : 'bg-white border border-gray-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-xs text-gray-900">
                        {comment.author?.first_name || comment.author?.username}
                      </span>
                      <span className="text-xs text-gray-500">{formatDate(comment.created_at)}</span>
                      {comment.is_internal && (
                        <span className="text-xs bg-yellow-200 text-yellow-800 px-1.5 py-0.5 rounded font-semibold">
                          Внутренний
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap mb-2">{comment.comment}</p>
                    {comment.attachments && comment.attachments.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {comment.attachments.map((file, idx) => {
                          const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(file.original_filename)
                          const basePath = import.meta.env.MODE === 'production' ? '/admin' : ''
                          const fileUrl = `${basePath}/${file.path || file.filename}`

                          if (isImage) {
                            return (
                              <a
                                key={idx}
                                href={fileUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="group relative block"
                              >
                                <img
                                  src={fileUrl}
                                  alt={file.original_filename}
                                  className="h-32 w-auto rounded-lg border-2 border-gray-200 hover:border-blue-500 transition-all cursor-pointer object-cover shadow-sm hover:shadow-md"
                                  loading="lazy"
                                />
                                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity rounded-lg flex items-center justify-center">
                                  <ExternalLink className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                                <p className="text-xs text-gray-500 mt-1 max-w-[150px] truncate">
                                  {file.original_filename}
                                </p>
                              </a>
                            )
                          } else {
                            return (
                              <a
                                key={idx}
                                href={fileUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 bg-blue-50 px-3 py-2 rounded-lg hover:bg-blue-100 transition-colors"
                              >
                                <Download className="w-4 h-4" />
                                {file.original_filename}
                              </a>
                            )
                          }
                        })}
                      </div>
                    )}
                  </div>
                ))}
                {comments.length === 0 && (
                  <p className="text-center text-gray-400 py-4 text-sm">Комментариев пока нет</p>
                )}
              </div>

              {/* Add Comment */}
              <div className="space-y-3 bg-white p-3 rounded-lg border border-gray-200">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  onPaste={handlePaste}
                  placeholder="Написать комментарий... (Ctrl+V для вставки скриншотов)"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-sm"
                />

                {/* Preview изображений */}
                {previewUrls.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {previewUrls.map((url, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={url}
                          alt={`Preview ${index + 1}`}
                          className="w-24 h-24 object-cover rounded-lg border-2 border-gray-200"
                        />
                        <button
                          onClick={() => handleRemoveFile(index)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Список файлов */}
                {selectedFiles.filter(f => !f.type.startsWith('image/')).length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedFiles.map((file, index) =>
                      !file.type.startsWith('image/') && (
                        <div key={index} className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm">
                          <Paperclip className="w-4 h-4 text-gray-600" />
                          <span className="text-gray-700">{file.name}</span>
                          <button
                            onClick={() => handleRemoveFile(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      )
                    )}
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors">
                    <Paperclip className="w-3.5 h-3.5" />
                    <span className="text-xs font-medium">Прикрепить</span>
                    <input
                      type="file"
                      multiple
                      accept="image/*,application/pdf,.doc,.docx,.xls,.xlsx,.txt"
                      onChange={(e) => handleFilesAdded(Array.from(e.target.files || []))}
                      className="hidden"
                    />
                  </label>
                  {selectedFiles.length > 0 && (
                    <span className="text-xs text-gray-600">
                      {selectedFiles.length} {selectedFiles.length === 1 ? 'файл' : 'файлов'}
                    </span>
                  )}
                  <div className="flex-1" />
                  <label className="flex items-center gap-1.5 text-xs">
                    <input
                      type="checkbox"
                      checked={isInternal}
                      onChange={(e) => setIsInternal(e.target.checked)}
                      className="rounded"
                    />
                    Внутренний
                  </label>
                  <button
                    onClick={handleAddComment}
                    disabled={loading || (!newComment.trim() && selectedFiles.length === 0)}
                    className="flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    <Send className="w-3.5 h-3.5" />
                    Отправить
                  </button>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {task.status === 'in_progress' && (
              <div className="flex items-center justify-center">
                <button
                  onClick={handleMarkCompleted}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 font-bold transition-all shadow-md hover:shadow-lg"
                >
                  <CheckCircle className="w-5 h-5" />
                  Отметить выполненной
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Footer - Actions */}
        <div className="flex-shrink-0 bg-gray-50 px-6 py-3 border-t border-gray-200 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={onEdit}
              className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-semibold text-sm"
            >
              <Edit className="w-4 h-4" />
              Редактировать
            </button>
            <button
              onClick={handleArchive}
              className="flex items-center gap-1.5 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-all font-semibold text-sm"
            >
              <Archive className="w-4 h-4" />
              Архивировать
            </button>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold text-sm"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
