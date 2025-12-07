/**
 * Вкладка "Чат" проекта
 * Общение с клиентом + создание задач/правок из сообщений
 */

import { useState, useEffect, useRef } from 'react'
import { useOutletContext } from 'react-router-dom'
import { MessageSquare, Send, Loader2, CheckSquare, RotateCcw, User, Clock } from 'lucide-react'
import axiosInstance from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'

interface Project {
  id: number
  title: string
  client_id?: number
}

interface ChatMessage {
  id: number
  text: string
  sender_id: number
  sender_name?: string
  is_client: boolean
  created_at: string
}

interface OutletContext {
  project: Project
}

export const ProjectChat = () => {
  const { project } = useOutletContext<OutletContext>()
  const { user } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newMessage, setNewMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [selectedMessage, setSelectedMessage] = useState<ChatMessage | null>(null)
  const [showCreateMenu, setShowCreateMenu] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Загрузка сообщений чата
  useEffect(() => {
    loadMessages()
  }, [project.id])

  // Автоскролл к последнему сообщению
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadMessages = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(`/admin/api/projects/${project.id}/chat`)

      if (response.data.success) {
        setMessages(response.data.messages || [])
      }
      setError(null)
    } catch (err: any) {
      console.error('Error loading chat:', err)
      setError('Ошибка загрузки чата')
    } finally {
      setLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Отправка сообщения
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim() || sending) return

    try {
      setSending(true)
      const response = await axiosInstance.post(`/admin/api/projects/${project.id}/chat`, {
        text: newMessage.trim(),
        sender_id: user?.id,
        is_client: false,
      })

      if (response.data.success) {
        setMessages([...messages, response.data.message])
        setNewMessage('')
      }
    } catch (err: any) {
      console.error('Error sending message:', err)
      alert('Ошибка отправки сообщения')
    } finally {
      setSending(false)
    }
  }

  // Создать задачу из сообщения
  const createTaskFromMessage = async (message: ChatMessage) => {
    try {
      const response = await axiosInstance.post(`/admin/api/tasks`, {
        project_id: project.id,
        title: `Задача из чата: ${message.text.substring(0, 50)}...`,
        description: message.text,
        type: 'TASK',
        status: 'new',
        priority: 'medium',
        created_from_chat: true,
      })

      if (response.data.success) {
        alert('Задача успешно создана!')
        setShowCreateMenu(false)
        setSelectedMessage(null)
      }
    } catch (err: any) {
      console.error('Error creating task:', err)
      alert('Ошибка создания задачи')
    }
  }

  // Создать правку из сообщения
  const createRevisionFromMessage = async (message: ChatMessage) => {
    try {
      const response = await axiosInstance.post(`/admin/api/tasks`, {
        project_id: project.id,
        title: `Правка из чата: ${message.text.substring(0, 50)}...`,
        description: message.text,
        type: 'REVISION',
        status: 'new',
        priority: 'high',
        created_from_chat: true,
      })

      if (response.data.success) {
        alert('Правка успешно создана!')
        setShowCreateMenu(false)
        setSelectedMessage(null)
      }
    } catch (err: any) {
      console.error('Error creating revision:', err)
      alert('Ошибка создания правки')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[600px]">
      {/* Заголовок */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Чат с клиентом</h2>
        {project.client_id && (
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-2">
              <User className="w-4 h-4" />
              Клиент ID: {project.client_id}
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Область сообщений */}
      <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col">
        {messages.length > 0 ? (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => {
              const isOwnMessage = !message.is_client

              return (
                <div
                  key={message.id}
                  className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[70%] ${isOwnMessage ? 'order-2' : 'order-1'}`}>
                    {/* Имя отправителя */}
                    <div className={`text-xs text-gray-500 dark:text-gray-400 mb-1 ${isOwnMessage ? 'text-right' : 'text-left'}`}>
                      {message.sender_name || (message.is_client ? 'Клиент' : 'Вы')}
                    </div>

                    {/* Сообщение */}
                    <div
                      className={`relative group rounded-lg px-4 py-3 ${
                        isOwnMessage
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap break-words">{message.text}</p>

                      {/* Кнопки создания задачи/правки (только для сообщений клиента) */}
                      {message.is_client && (
                        <div className="absolute top-0 right-0 -mt-8 opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="flex items-center gap-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-1">
                            <button
                              onClick={() => {
                                setSelectedMessage(message)
                                setShowCreateMenu(true)
                              }}
                              className="flex items-center gap-1 px-2 py-1 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
                              title="Создать задачу"
                            >
                              <CheckSquare className="w-3 h-3" />
                              <span>Задача</span>
                            </button>
                            <button
                              onClick={() => {
                                setSelectedMessage(message)
                                createRevisionFromMessage(message)
                              }}
                              className="flex items-center gap-1 px-2 py-1 text-xs text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded transition-colors"
                              title="Создать правку"
                            >
                              <RotateCcw className="w-3 h-3" />
                              <span>Правка</span>
                            </button>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Время */}
                    <div className={`flex items-center gap-1 text-xs text-gray-400 mt-1 ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
                      <Clock className="w-3 h-3" />
                      <span>{new Date(message.created_at).toLocaleString('ru-RU')}</span>
                    </div>
                  </div>
                </div>
              )
            })}
            <div ref={messagesEndRef} />
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <MessageSquare className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Чат пока пуст</h3>
            <p className="text-gray-500 dark:text-gray-400">Начните общение с клиентом</p>
          </div>
        )}

        {/* Форма отправки сообщения */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <form onSubmit={handleSendMessage} className="flex items-center gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Введите сообщение..."
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!newMessage.trim() || sending}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              <span>Отправить</span>
            </button>
          </form>
        </div>
      </div>

      {/* Модалка подтверждения создания задачи */}
      {showCreateMenu && selectedMessage && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Создать задачу из сообщения?
            </h3>
            <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 mb-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
                {selectedMessage.text}
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => createTaskFromMessage(selectedMessage)}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Создать задачу
              </button>
              <button
                onClick={() => {
                  setShowCreateMenu(false)
                  setSelectedMessage(null)
                }}
                className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectChat
