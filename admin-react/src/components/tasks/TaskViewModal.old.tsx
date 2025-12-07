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
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      if (scrollY) {
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
          console.log('Таймер остановлен')
          onRefresh()
        }
      } else {
        const response = await tasksApi.startTimer(task.id)
        if (response.success) {
          setTask(response.data)
          setTimerRunning(true)
          console.log('Таймер запущен')
          onRefresh()
        }
      }
    } catch (error) {
      console.error('Error toggling timer:', error)
      console.log('Ошибка работы с таймером')
    }
  }

  const handleProgressChange = async (newProgress: number) => {
    try {
      const response = await tasksApi.updateProgress(task.id, newProgress)
      if (response.success) {
        setProgress(newProgress)
        console.log('Прогресс обновлен')
        onRefresh()
      }
    } catch (error) {
      console.error('Error updating progress:', error)
      console.log('Ошибка обновления прогресса')
    }
  }

  const handleSaveDeployUrl = async () => {
    try {
      const response = await tasksApi.updateTask(task.id, { deploy_url: deployUrl })
      if (response.success) {
        setTask(response.task)
        setIsEditingDeployUrl(false)
        console.log('Ссылка на деплой обновлена')
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
      console.log('📤 Отправка комментария...', {
        taskId: task.id,
        commentLength: newComment.length,
        filesCount: selectedFiles.length,
        filesSize: selectedFiles.reduce((sum, f) => sum + f.size, 0)
      })

      const response = await tasksApi.addComment(task.id, newComment, isInternal, selectedFiles)

      console.log('✅ Ответ сервера:', response)

      if (response.success) {
        console.log('✅ Комментарий успешно добавлен')
        setNewComment('')
        setSelectedFiles([])
        // Очистка preview URLs
        previewUrls.forEach(url => URL.revokeObjectURL(url))
        setPreviewUrls([])
        setIsInternal(false)
        loadComments()
        onRefresh()
      } else {
        console.error('❌ Сервер вернул ошибку:', response)
        alert('Ошибка: ' + (response.error || 'Не удалось добавить комментарий'))
      }
    } catch (error: any) {
      console.error('❌ Ошибка при отправке комментария:', error)
      console.error('Детали ошибки:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })

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

  // Обработчик вставки изображений через Ctrl+V
  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const items = e.clipboardData?.items
    if (!items) return

    const files: File[] = []

    for (let i = 0; i < items.length; i++) {
      const item = items[i]

      // Проверяем, является ли это изображением
      if (item.type.indexOf('image') !== -1) {
        const file = item.getAsFile()
        if (file) {
          // Генерируем имя файла для скриншота
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

  // Обработчик добавления файлов
  const handleFilesAdded = (newFiles: File[]) => {
    const updatedFiles = [...selectedFiles, ...newFiles]
    setSelectedFiles(updatedFiles)

    // Создаем preview для изображений
    const newPreviewUrls: string[] = []
    newFiles.forEach(file => {
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file)
        newPreviewUrls.push(url)
      }
    })
    setPreviewUrls([...previewUrls, ...newPreviewUrls])
  }

  // Удаление файла из списка
  const handleRemoveFile = (index: number) => {
    const updatedFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(updatedFiles)

    // Освобождаем URL и удаляем preview
    if (previewUrls[index]) {
      URL.revokeObjectURL(previewUrls[index])
    }
    const updatedPreviews = previewUrls.filter((_, i) => i !== index)
    setPreviewUrls(updatedPreviews)
  }

  // Cleanup preview URLs при размонтировании
  useEffect(() => {
    return () => {
      previewUrls.forEach(url => URL.revokeObjectURL(url))
    }
  }, [previewUrls])

  const handleMarkCompleted = async () => {
    try {
      const response = await tasksApi.markCompleted(task.id)
      if (response.success) {
        console.log('Задача отмечена как выполненная')
        onRefresh()
        onClose()
      }
    } catch (error) {
      console.error('Error marking completed:', error)
      console.log('Ошибка завершения задачи')
    }
  }

  const handleArchive = async () => {
    if (!confirm('Вы уверены, что хотите архивировать эту задачу?')) return

    try {
      const response = await tasksApi.archiveTask(task.id)
      if (response.success) {
        console.log('Задача архивирована')
        onRefresh()
        onClose()
      }
    } catch (error) {
      console.error('Error archiving task:', error)
      console.log('Ошибка архивации задачи')
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
        return 'bg-blue-500'
      case 'in_progress':
        return 'bg-yellow-500'
      case 'completed':
        return 'bg-green-500'
      default:
        return 'bg-gray-500'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div
          className={`${getStatusColor()} text-white px-6 py-4 flex items-center justify-between sticky top-0 z-10`}
        >
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-1">{task.title}</h3>
            <div className="flex items-center gap-3 text-sm">
              <span className={`px-2 py-1 rounded border ${getPriorityColor()}`}>
                {task.priority}
              </span>
              {task.is_overdue && (
                <span className="flex items-center gap-1 bg-red-500 px-2 py-1 rounded text-white">
                  <AlertCircle className="w-4 h-4" />
                  Просрочено
                </span>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors ml-4"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Task Details */}
          <div className="space-y-4">
            {/* Description */}
            {task.description && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Описание</h4>
                <p className="text-gray-600 whitespace-pre-wrap">{task.description}</p>
              </div>
            )}

            {/* Tags */}
            {task.tags && task.tags.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Теги</h4>
                <TaskTags tags={task.tags} size="md" />
              </div>
            )}

            {/* Info Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2 text-sm">
                <User className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Исполнитель:</span>
                <span className="font-semibold">
                  {task.assigned_to?.first_name || task.assigned_to?.username}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Дедлайн:</span>
                <span className={`font-semibold ${task.is_overdue ? 'text-red-600' : ''}`}>
                  {formatDate(task.deadline)}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Время:</span>
                <span className="font-semibold">{formatTimeSpent(task.time_spent_seconds)}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <User className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">Создатель:</span>
                <span className="font-semibold">
                  {task.created_by?.first_name || task.created_by?.username}
                </span>
              </div>
              {/* Deploy URL - всегда показываем для редактирования */}
              <div className="col-span-2">
                <div className="flex items-center gap-2 mb-2">
                  <ExternalLink className="w-4 h-4 text-blue-500" />
                  <span className="text-sm font-semibold text-gray-700">Ссылка на деплой</span>
                </div>
                {isEditingDeployUrl ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="url"
                      value={deployUrl}
                      onChange={(e) => setDeployUrl(e.target.value)}
                      placeholder="https://example.com/app"
                      className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={handleSaveDeployUrl}
                      className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Сохранить
                    </button>
                    <button
                      onClick={() => {
                        setDeployUrl(task.deploy_url || '')
                        setIsEditingDeployUrl(false)
                      }}
                      className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors"
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
                          className="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                        >
                          Открыть приложение
                          <ExternalLink className="w-3 h-3" />
                        </a>
                        <button
                          onClick={() => setIsEditingDeployUrl(true)}
                          className="ml-2 text-sm text-gray-600 hover:text-gray-800"
                        >
                          ✏️ Изменить
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => setIsEditingDeployUrl(true)}
                        className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Добавить ссылку на деплой
                      </button>
                    )}
                  </div>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Прикрепите ссылку на задеплоенное приложение для отслеживания прогресса
                </p>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-gray-700">Прогресс выполнения</h4>
              <span className={`text-lg font-bold transition-all duration-300 ${
                progress < 25 ? 'text-red-600' :
                progress < 50 ? 'text-orange-600' :
                progress < 75 ? 'text-yellow-600' :
                progress < 100 ? 'text-blue-600' :
                'text-green-600'
              }`}>{progress}%</span>
            </div>
            <div className="relative w-full">
              {/* Фон прогресс-бара */}
              <div className="w-full h-3 bg-gray-200 rounded-lg overflow-hidden">
                {/* Градиентная заливка прогресса */}
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
                    boxShadow: progress > 0
                      ? `0 0 15px ${
                          progress < 25 ? 'rgba(239, 68, 68, 0.5)' :
                          progress < 50 ? 'rgba(249, 115, 22, 0.5)' :
                          progress < 75 ? 'rgba(234, 179, 8, 0.5)' :
                          progress < 100 ? 'rgba(59, 130, 246, 0.5)' :
                          'rgba(34, 197, 94, 0.5)'
                        }`
                      : 'none'
                  }}
                />
              </div>
              {/* Невидимый слайдер для управления */}
              <input
                type="range"
                min="0"
                max="100"
                value={progress}
                onChange={(e) => handleProgressChange(parseInt(e.target.value))}
                className="absolute top-0 left-0 w-full h-3 appearance-none cursor-pointer bg-transparent"
                style={{
                  WebkitAppearance: 'none',
                  background: 'transparent'
                }}
                disabled={task.status === 'completed'}
              />
            </div>
          </div>

          {/* Timer Control */}
          {task.status !== 'completed' && (
            <div className="flex items-center gap-3">
              <button
                onClick={handleTimerToggle}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                  timerRunning
                    ? 'bg-red-100 text-red-700 hover:bg-red-200'
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                {timerRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                {timerRunning ? 'Остановить таймер' : 'Запустить таймер'}
              </button>
              {task.status === 'in_progress' && (
                <button
                  onClick={handleMarkCompleted}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold transition-all"
                >
                  <CheckCircle className="w-5 h-5" />
                  Отметить выполненной
                </button>
              )}
            </div>
          )}

          {/* Comments Section */}
          <div className="border-t pt-6">
            <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              Комментарии ({comments.length})
            </h4>

            {/* Comments List */}
            <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
              {comments.map((comment) => (
                <div
                  key={comment.id}
                  className={`p-3 rounded-lg ${
                    comment.is_internal ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold text-sm">
                      {comment.author?.first_name || comment.author?.username}
                    </span>
                    <span className="text-xs text-gray-500">{formatDate(comment.created_at)}</span>
                    {comment.is_internal && (
                      <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-0.5 rounded">
                        Внутренний
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{comment.comment}</p>
                  {comment.attachments && comment.attachments.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {comment.attachments.map((file, idx) => {
                        const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(file.original_filename)
                        // Формируем правильный путь с учетом базового пути в production
                        const basePath = import.meta.env.MODE === 'production' ? '/admin' : ''
                        // Используем поле path, которое содержит полный путь к файлу
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
                                className="h-24 w-auto rounded-lg border-2 border-gray-200 hover:border-blue-500 transition-all cursor-pointer object-cover shadow-sm hover:shadow-md"
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
                              className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 bg-blue-50 px-2 py-1 rounded"
                            >
                              <Download className="w-3 h-3" />
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
                <p className="text-center text-gray-400 py-4">Комментариев пока нет</p>
              )}
            </div>

            {/* Add Comment */}
            <div className="space-y-3">
              <div className="relative">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  onPaste={handlePaste}
                  placeholder="Написать комментарий... (Вставьте скриншот через Ctrl+V)"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
                <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                  💡 Ctrl+V для вставки скриншотов
                </div>
              </div>

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
                        title="Удалить"
                      >
                        <X className="w-3 h-3" />
                      </button>
                      <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs px-1 py-0.5 rounded-b-lg truncate">
                        {selectedFiles[index]?.name}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Список обычных файлов (не изображений) */}
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
                          title="Удалить"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    )
                  )}
                </div>
              )}

              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors">
                  <Paperclip className="w-4 h-4" />
                  <span className="text-sm">Прикрепить файлы</span>
                  <input
                    type="file"
                    multiple
                    accept="image/*,application/pdf,.doc,.docx,.xls,.xlsx,.txt"
                    onChange={(e) => handleFilesAdded(Array.from(e.target.files || []))}
                    className="hidden"
                  />
                </label>
                {selectedFiles.length > 0 && (
                  <span className="text-sm text-gray-600">
                    {selectedFiles.length} {selectedFiles.length === 1 ? 'файл' : 'файлов'}
                  </span>
                )}
                <div className="flex-1" />
                <label className="flex items-center gap-2 text-sm">
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
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-4 h-4" />
                  Отправить
                </button>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              onClick={onEdit}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-semibold"
            >
              <Edit className="w-4 h-4" />
              Редактировать
            </button>
            <button
              onClick={onDelete}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-all font-semibold"
            >
              <Archive className="w-4 h-4" />
              В архив
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
