import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send, Paperclip, X, Loader2, User } from 'lucide-react'
// API imports
import chatsApi from '../api/chats'
import type { ChatMessage } from '../api/chats'

export const ChatDetail = () => {
  const { chatId } = useParams<{ chatId: string }>()
  const navigate = useNavigate()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [messageText, setMessageText] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  const loadMessages = useCallback(async () => {
    if (!chatId) return

    try {
      const data = await chatsApi.getChatMessages(parseInt(chatId))
      const wasAtBottom =
        messagesEndRef.current &&
        messagesEndRef.current.getBoundingClientRect().bottom <= window.innerHeight + 100

      setMessages(data.messages)

      // Прокручиваем вниз только если были внизу или при первой загрузке
      if (wasAtBottom || loading) {
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
        }, 100)
      }
    } catch (error) {
      console.error('Error loading messages:', error)
      showToast('Ошибка загрузки сообщений', 'error')
    } finally {
      setLoading(false)
    }
  }, [chatId, loading, showToast])

  useEffect(() => {
    loadMessages()
    // Автообновление каждые 3 секунды
    const interval = setInterval(loadMessages, 3000)
    return () => clearInterval(interval)
  }, [loadMessages])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files))
    }
  }

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!chatId || (!messageText.trim() && selectedFiles.length === 0)) {
      showToast('Введите сообщение или прикрепите файл', 'error')
      return
    }

    try {
      setSending(true)
      const formData = new FormData()

      if (messageText.trim()) {
        formData.append('message_text', messageText.trim())
      }

      selectedFiles.forEach((file) => {
        formData.append('attachments', file)
      })

      await chatsApi.sendMessage(parseInt(chatId), formData)

      setMessageText('')
      setSelectedFiles([])
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      showToast('Сообщение отправлено', 'success')
      await loadMessages()
    } catch (error) {
      console.error('Error sending message:', error)
      showToast('Ошибка отправки сообщения', 'error')
    } finally {
      setSending(false)
    }
  }

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
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

      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/chats')}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-800">Чат проекта</h1>
            <p className="text-sm text-gray-500">ID: {chatId}</p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="bg-white rounded-full p-6 mb-4 shadow-md">
              <User className="w-12 h-12 text-gray-400" />
            </div>
            <p className="text-gray-500 text-lg font-medium">Нет сообщений</p>
            <p className="text-gray-400 text-sm mt-2">Начните диалог с клиентом!</p>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender_type === 'executor' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                    msg.sender_type === 'executor'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                      : 'bg-white shadow-md text-gray-800'
                  }`}
                >
                  {/* Sender Label */}
                  <div className="text-xs font-semibold mb-1 opacity-80">
                    {msg.sender_type === 'client' ? 'Клиент' : 'Вы'}
                  </div>

                  {/* Message Text */}
                  {msg.message_text && (
                    <div className="whitespace-pre-wrap break-words mb-1">{msg.message_text}</div>
                  )}

                  {/* Attachments */}
                  {msg.attachments && msg.attachments.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {msg.attachments.map((att, idx) => (
                        <a
                          key={idx}
                          href={att.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`flex items-center gap-2 p-2 rounded-lg ${
                            msg.sender_type === 'executor'
                              ? 'bg-white/20 hover:bg-white/30'
                              : 'bg-gray-100 hover:bg-gray-200'
                          } transition-colors`}
                        >
                          <Paperclip className="w-4 h-4" />
                          <span className="text-sm truncate flex-1">{att.filename}</span>
                          <span className="text-xs opacity-75">{formatFileSize(att.size)}</span>
                        </a>
                      ))}
                    </div>
                  )}

                  {/* Timestamp */}
                  <div
                    className={`text-xs mt-2 ${
                      msg.sender_type === 'executor' ? 'text-white/70' : 'text-gray-500'
                    }`}
                  >
                    {formatDateTime(msg.created_at)}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <form onSubmit={handleSendMessage} className="space-y-3">
          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {selectedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-2 rounded-lg text-sm"
                >
                  <Paperclip className="w-4 h-4" />
                  <span className="truncate max-w-[200px]">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveFile(idx)}
                    className="hover:bg-blue-200 rounded p-1 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Input Row */}
          <div className="flex items-end gap-3">
            {/* File Input */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              id="file-input"
            />
            <label
              htmlFor="file-input"
              className="p-3 bg-gray-100 hover:bg-gray-200 rounded-lg cursor-pointer transition-colors"
              title="Прикрепить файлы"
            >
              <Paperclip className="w-5 h-5 text-gray-600" />
            </label>

            {/* Text Input */}
            <textarea
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage(e)
                }
              }}
              placeholder="Введите сообщение... (Enter - отправить, Shift+Enter - новая строка)"
              className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
              rows={3}
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={sending || (!messageText.trim() && selectedFiles.length === 0)}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {sending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Отправить
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
