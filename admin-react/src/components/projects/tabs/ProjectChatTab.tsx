import { useState, useEffect, useRef } from 'react'
import { Send, MessageCircle, Paperclip } from 'lucide-react'

interface Message {
  id: number
  author_id: number
  author_name: string
  text: string
  created_at: string
  is_client: boolean
}

interface ProjectChatTabProps {
  projectId: number
  chatId?: number
  onUnreadChange?: (count: number) => void
}

export const ProjectChatTab = ({ projectId, chatId, onUnreadChange }: ProjectChatTabProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (chatId) {
      loadMessages()
    } else {
      setLoading(false)
    }
  }, [chatId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadMessages = async () => {
    try {
      setLoading(true)
      // TODO: Загрузить сообщения через API
      const response = await fetch(`http://localhost:8001/admin/api/chats/${chatId}/messages`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
      }
    } catch (err) {
      console.error('Ошибка загрузки сообщений:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || sending) return

    try {
      setSending(true)
      // TODO: Отправить сообщение через API
      const response = await fetch(`http://localhost:8001/admin/api/chats/${chatId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          text: newMessage,
          project_id: projectId,
        }),
      })

      if (response.ok) {
        setNewMessage('')
        await loadMessages()
      }
    } catch (err) {
      console.error('Ошибка отправки сообщения:', err)
    } finally {
      setSending(false)
    }
  }

  if (!chatId) {
    return (
      <div className="p-6">
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Чат не создан</p>
          <p className="text-gray-400 text-sm mt-1">Чат будет создан автоматически при первом сообщении</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[600px]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-12">
            <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">Сообщений пока нет</p>
            <p className="text-gray-400 text-sm mt-1">Начните обсуждение проекта</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.is_client ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-md px-4 py-3 rounded-2xl ${
                  message.is_client
                    ? 'bg-gray-100 text-gray-900'
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                }`}
              >
                <p className="text-xs opacity-75 mb-1">{message.author_name}</p>
                <p className="whitespace-pre-wrap">{message.text}</p>
                <p className="text-xs opacity-60 mt-1">
                  {new Date(message.created_at).toLocaleTimeString('ru-RU', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <div className="flex items-center gap-2">
          <button className="p-2 text-gray-500 hover:text-gray-700 transition-colors">
            <Paperclip className="w-5 h-5" />
          </button>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Напишите сообщение..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={sending}
          />
          <button
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || sending}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-medium shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Отправить
          </button>
        </div>
      </div>
    </div>
  )
}
