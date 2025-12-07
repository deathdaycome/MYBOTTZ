import { useState, useEffect } from 'react'
import { X, Clock, User, DollarSign, Edit2, Tag, CheckCircle, AlertCircle } from 'lucide-react'

interface TimelineEvent {
  id: number
  type:
    | 'created'
    | 'status_changed'
    | 'executor_assigned'
    | 'payment_added'
    | 'executor_payment'
    | 'edited'
    | 'comment'
    | 'completed'
  description: string
  user?: { first_name: string; username?: string }
  created_at: string
  details?: any
}

interface ProjectTimelineModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

export const ProjectTimelineModal = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: ProjectTimelineModalProps) => {
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen && projectId) {
      loadTimeline()
    }
  }, [isOpen, projectId])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  const loadTimeline = async () => {
    if (!projectId) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/timeline`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setTimeline(data.timeline || [])
      } else {
        setError('Ошибка загрузки истории')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'created':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'status_changed':
        return <Tag className="w-5 h-5 text-blue-600" />
      case 'executor_assigned':
        return <User className="w-5 h-5 text-purple-600" />
      case 'payment_added':
        return <DollarSign className="w-5 h-5 text-emerald-600" />
      case 'executor_payment':
        return <DollarSign className="w-5 h-5 text-orange-600" />
      case 'edited':
        return <Edit2 className="w-5 h-5 text-amber-600" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  const getEventColor = (type: string) => {
    switch (type) {
      case 'created':
        return 'border-green-500 bg-green-50'
      case 'status_changed':
        return 'border-blue-500 bg-blue-50'
      case 'executor_assigned':
        return 'border-purple-500 bg-purple-50'
      case 'payment_added':
        return 'border-emerald-500 bg-emerald-50'
      case 'executor_payment':
        return 'border-orange-500 bg-orange-50'
      case 'edited':
        return 'border-amber-500 bg-amber-50'
      case 'completed':
        return 'border-green-500 bg-green-50'
      default:
        return 'border-gray-500 bg-gray-50'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">История проекта</h3>
              <p className="text-indigo-100 text-sm mt-1">{projectName}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="flex items-start gap-2 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg mb-4">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка истории...</div>
          ) : timeline.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              История событий пока пуста
            </div>
          ) : (
            <div className="relative">
              {/* Timeline Line */}
              <div className="absolute left-[29px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-indigo-200 to-blue-200" />

              {/* Events */}
              <div className="space-y-4">
                {timeline.map((event, index) => (
                  <div key={event.id} className="relative pl-16">
                    {/* Icon Circle */}
                    <div className="absolute left-0 top-0 w-14 h-14 bg-white border-4 border-indigo-200 rounded-full flex items-center justify-center">
                      {getEventIcon(event.type)}
                    </div>

                    {/* Event Card */}
                    <div
                      className={`border-l-4 rounded-lg p-4 ${getEventColor(
                        event.type
                      )}`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h4 className="font-semibold text-gray-900">{event.description}</h4>
                        <span className="text-xs text-gray-500 whitespace-nowrap">
                          {formatDate(event.created_at)}
                        </span>
                      </div>

                      {event.user && (
                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                          <User className="w-4 h-4" />
                          <span>
                            {event.user.first_name || event.user.username || 'Пользователь'}
                          </span>
                        </div>
                      )}

                      {event.details && (
                        <div className="mt-2 text-sm text-gray-700 bg-white/50 rounded p-2">
                          <pre className="whitespace-pre-wrap font-sans">
                            {JSON.stringify(event.details, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>

                    {/* Connector to next event */}
                    {index < timeline.length - 1 && (
                      <div className="absolute left-[29px] top-14 w-0.5 h-4 bg-indigo-200" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <span className="text-xs text-gray-500">
            Всего событий: {timeline.length}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
