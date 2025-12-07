import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageCircle, User, Clock, Pin, EyeOff, Eye, Paperclip, Loader2 } from 'lucide-react'
// API imports
import chatsApi from '../api/chats'
import type { Chat } from '../api/chats'

export const Chats = () => {
  const navigate = useNavigate()
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(true)
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  const loadChats = useCallback(async () => {
    try {
      const data = await chatsApi.getChats()
      setChats(data)
    } catch (error) {
      console.error('Error loading chats:', error)
      showToast('Ошибка загрузки чатов', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    loadChats()
    // Автообновление каждые 10 секунд
    const interval = setInterval(loadChats, 10000)
    return () => clearInterval(interval)
  }, [loadChats])

  const handlePinChat = async (chatId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      const result = await chatsApi.togglePinChat(chatId)
      showToast(result.message, 'success')
      await loadChats()
    } catch (error: any) {
      console.error('Error pinning chat:', error)
      if (error.response?.status === 403) {
        showToast('Только владелец и админ могут закреплять чаты', 'error')
      } else {
        showToast('Ошибка закрепления чата', 'error')
      }
    }
  }

  const handleHideChat = async (chatId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      const result = await chatsApi.toggleHideChat(chatId)
      showToast(result.message, 'success')
      await loadChats()
    } catch (error: any) {
      console.error('Error hiding chat:', error)
      if (error.response?.status === 403) {
        showToast('Только владелец и админ могут скрывать чаты', 'error')
      } else {
        showToast('Ошибка скрытия чата', 'error')
      }
    }
  }

  const formatTime = (dateString: string | null) => {
    if (!dateString) return ''

    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'только что'
    if (diffMins < 60) return `${diffMins} мин назад`

    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} ч назад`

    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays} дн назад`

    return date.toLocaleDateString('ru-RU')
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      completed: 'Завершен',
      in_progress: 'В работе',
      pending: 'Ожидает',
      cancelled: 'Отменен',
    }
    return labels[status] || status
  }

  // Сортируем чаты: закрепленные сверху, затем по последнему сообщению
  const sortedChats = [...chats].sort((a, b) => {
    // Сначала закрепленные
    if (a.is_pinned_by_owner !== b.is_pinned_by_owner) {
      return a.is_pinned_by_owner ? -1 : 1
    }
    // Затем по времени последнего сообщения
    const aTime = a.last_message_at ? new Date(a.last_message_at).getTime() : 0
    const bTime = b.last_message_at ? new Date(b.last_message_at).getTime() : 0
    return bTime - aTime
  })

  // Фильтруем скрытые чаты
  const visibleChats = sortedChats.filter((chat) => !chat.is_hidden_by_owner)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Чаты проектов
        </h1>
        <p className="text-gray-600 mt-2">Переписка с клиентами по их проектам</p>
      </div>

      {/* Toasts */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-3 rounded-lg shadow-lg text-white ${
              toast.type === 'success'
                ? 'bg-green-500'
                : toast.type === 'error'
                ? 'bg-red-500'
                : 'bg-blue-500'
            } animate-slide-in`}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Chats Grid */}
      {visibleChats.length === 0 ? (
        <div className="text-center py-12">
          <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">Нет активных чатов</p>
          <p className="text-gray-400 text-sm mt-2">Чаты появятся, когда клиенты создадут проекты</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {visibleChats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => navigate(`/chats/${chat.id}`)}
              className={`bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1 relative ${
                chat.unread_by_executor > 0 ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              {/* Pin/Hide Icons */}
              <div className="absolute top-3 right-3 flex gap-2">
                {chat.is_pinned_by_owner && (
                  <button
                    onClick={(e) => handlePinChat(chat.id, e)}
                    className="p-2 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
                    title="Открепить чат"
                  >
                    <Pin className="w-4 h-4 fill-current" />
                  </button>
                )}
                {!chat.is_pinned_by_owner && (
                  <button
                    onClick={(e) => handlePinChat(chat.id, e)}
                    className="p-2 rounded-full bg-gray-100 text-gray-400 hover:bg-gray-200 transition-colors"
                    title="Закрепить чат"
                  >
                    <Pin className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={(e) => handleHideChat(chat.id, e)}
                  className="p-2 rounded-full bg-gray-100 text-gray-400 hover:bg-gray-200 transition-colors"
                  title="Скрыть чат"
                >
                  <EyeOff className="w-4 h-4" />
                </button>
              </div>

              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4 pr-16">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-gray-800 mb-1">{chat.project.title}</h3>
                    <span
                      className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        chat.project.status
                      )}`}
                    >
                      {getStatusLabel(chat.project.status)}
                    </span>
                  </div>
                  {chat.unread_by_executor > 0 && (
                    <span className="bg-blue-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                      {chat.unread_by_executor}
                    </span>
                  )}
                </div>

                {/* Client Info */}
                {chat.project.client_name && (
                  <div className="flex items-center gap-2 text-gray-600 text-sm mb-3">
                    <User className="w-4 h-4" />
                    <span>{chat.project.client_name}</span>
                  </div>
                )}

                {/* Last Message */}
                {chat.last_message ? (
                  <div className="mb-3">
                    <p className="text-sm text-gray-600 mb-1">
                      <span className="font-semibold">
                        {chat.last_message.sender_type === 'client' ? 'Клиент' : 'Вы'}:
                      </span>{' '}
                      {chat.last_message.message_text || (
                        <span className="italic flex items-center gap-1">
                          <Paperclip className="w-3 h-3" />
                          Вложение
                        </span>
                      )}
                    </p>
                    <div className="flex items-center gap-1 text-gray-400 text-xs">
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(chat.last_message_at)}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 italic mb-3">Нет сообщений</p>
                )}

                {/* Action Button */}
                <button
                  className={`w-full py-2 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                    chat.unread_by_executor > 0
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <MessageCircle className="w-4 h-4" />
                  Открыть чат
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
