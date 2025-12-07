import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  MessageSquare,
  Send,
  Image as ImageIcon,
  RefreshCw,
  Settings,
  Search,
  User,
  Check,
  Ban,
  Info,
  Star,
  Briefcase,
  X,
  Loader,
  Download,
  Bot,
  Play,
  Pause
} from 'lucide-react'
import avitoApi from '../api/avito'

interface Chat {
  id: string
  users: Array<{
    id: number
    name: string
  }>
  context?: {
    type: string
    value: {
      title?: string
      price?: number
    }
  }
  last_message?: {
    content: {
      text: string
    }
    created: number
  }
  unread_count: number
}

interface Message {
  id: string
  chat_id: string
  author_id: number
  type: string
  direction: string
  content: {
    text?: string
    image?: {
      '640x480'?: string
      '1280x960'?: string
    }
  }
  created: number
}

export const Avito = () => {
  const [chats, setChats] = useState<Chat[]>([])
  const [selectedChat, setSelectedChat] = useState<Chat | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [messageInput, setMessageInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)
  const [loading, setLoading] = useState(true)
  const [messagesLoading, setMessagesLoading] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [showAiModal, setShowAiModal] = useState(false)
  const [aiIndustry, setAiIndustry] = useState('')
  const [aiResult, setAiResult] = useState<any>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiSuggestion, setAiSuggestion] = useState<string | null>(null)
  const [showAiAssistant, setShowAiAssistant] = useState(false)
  const [pollingActive, setPollingActive] = useState(false)
  const [autoResponseEnabled, setAutoResponseEnabled] = useState(false)

  // Toast notification
  const [toasts, setToasts] = useState<Array<{ id: number; message: string; type: 'success' | 'error' | 'info' }>>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 3000)
  }, [])

  // Load chats
  const loadChats = useCallback(async () => {
    try {
      setLoading(true)
      const data = await avitoApi.getChats(showUnreadOnly)
      setChats(data.chats)
      setCurrentUserId(data.current_user_id)
    } catch (error: any) {
      console.error('Error loading chats:', error)
      showToast(error.response?.data?.message || 'Ошибка загрузки чатов', 'error')
    } finally {
      setLoading(false)
    }
  }, [showUnreadOnly, showToast])

  // Load messages
  const loadMessages = useCallback(async (chatId: string) => {
    try {
      setMessagesLoading(true)
      const data = await avitoApi.getChatMessages(chatId)
      setMessages(data.messages)
      await avitoApi.markChatAsRead(chatId)
      loadChats() // Refresh chat list to update unread count
    } catch (error: any) {
      console.error('Error loading messages:', error)
      showToast('Ошибка загрузки сообщений', 'error')
    } finally {
      setMessagesLoading(false)
    }
  }, [loadChats, showToast])

  // Send message
  const sendMessage = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedChat || !messageInput.trim()) return

    try {
      const message = await avitoApi.sendMessage(selectedChat.id, messageInput.trim())
      setMessages(prev => [...prev, message])
      setMessageInput('')
    } catch (error: any) {
      console.error('Error sending message:', error)
      showToast('Ошибка отправки сообщения', 'error')
    }
  }, [selectedChat, messageInput, showToast])

  // Upload image
  const handleImageUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedChat || !e.target.files?.[0]) return

    try {
      const file = e.target.files[0]
      const message = await avitoApi.uploadImage(selectedChat.id, file)
      setMessages(prev => [...prev, message])
      showToast('Изображение отправлено', 'success')
    } catch (error: any) {
      console.error('Error uploading image:', error)
      showToast('Ошибка загрузки изображения', 'error')
    }
  }, [selectedChat, showToast])

  // Select chat
  const selectChat = useCallback((chat: Chat) => {
    setSelectedChat(chat)
    loadMessages(chat.id)
  }, [loadMessages])

  // Generate AI suggestion
  const generateAiSuggestion = useCallback(async () => {
    if (!selectedChat) return

    try {
      setShowAiAssistant(true)
      setAiSuggestion(null)
      const data = await avitoApi.generateAiResponse(selectedChat.id)
      setAiSuggestion(data.suggestion)
    } catch (error: any) {
      console.error('Error generating AI suggestion:', error)
      showToast('Ошибка генерации AI ответа', 'error')
    }
  }, [selectedChat, showToast])

  // Use AI suggestion
  const useAiSuggestion = useCallback(() => {
    if (aiSuggestion) {
      setMessageInput(aiSuggestion)
      setShowAiAssistant(false)
    }
  }, [aiSuggestion])

  // Create lead from chat
  const createLead = useCallback(async () => {
    if (!selectedChat) return

    if (!confirm('Создать лид из этого чата?')) return

    try {
      const data = await avitoApi.createLead(selectedChat.id)
      if (data.status === 'success') {
        showToast(`Лид "${data.lead_data.name}" успешно создан`, 'success')
      } else {
        showToast('Лид уже существует', 'info')
      }
    } catch (error: any) {
      console.error('Error creating lead:', error)
      showToast('Ошибка создания лида', 'error')
    }
  }, [selectedChat, showToast])

  // Generate AI sales response
  const generateAiSales = useCallback(async (actionType: 'suggest_response' | 'startup_offer') => {
    if (!selectedChat || !aiIndustry.trim()) {
      showToast('Укажите сферу деятельности клиента', 'error')
      return
    }

    try {
      setAiLoading(true)
      const data = await avitoApi.getAiSalesSuggestions(selectedChat.id, aiIndustry, actionType)
      setAiResult(data)
    } catch (error: any) {
      console.error('Error generating AI sales:', error)
      showToast('Ошибка генерации AI предложения', 'error')
    } finally {
      setAiLoading(false)
    }
  }, [selectedChat, aiIndustry, showToast])

  // Use AI result
  const useAiResult = useCallback((text: string) => {
    setMessageInput(text)
    setShowAiModal(false)
    showToast('Текст добавлен в сообщение', 'success')
  }, [showToast])

  // Export chat
  const exportChat = useCallback(async () => {
    if (!selectedChat) return

    try {
      const blob = await avitoApi.exportChat(selectedChat.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `avito_chat_${selectedChat.id}_${new Date().toISOString().split('T')[0]}.txt`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      showToast('Чат экспортирован', 'success')
    } catch (error: any) {
      console.error('Error exporting chat:', error)
      showToast('Ошибка экспорта чата', 'error')
    }
  }, [selectedChat, showToast])

  // Load polling status
  const loadPollingStatus = useCallback(async () => {
    try {
      const data = await avitoApi.getPollingStatus()
      setPollingActive(data.polling_active)
      setAutoResponseEnabled(data.auto_response_enabled)
    } catch (error) {
      console.error('Error loading polling status:', error)
    }
  }, [])

  // Toggle auto response
  const toggleAutoResponse = useCallback(async () => {
    try {
      const data = await avitoApi.toggleAutoResponse(!autoResponseEnabled)
      setAutoResponseEnabled(data.enabled)
      showToast(data.message, 'success')
      loadPollingStatus()
    } catch (error: any) {
      console.error('Error toggling auto response:', error)
      showToast('Ошибка переключения автоответов', 'error')
    }
  }, [autoResponseEnabled, showToast, loadPollingStatus])

  // Filtered chats
  const filteredChats = useMemo(() => {
    return chats.filter(chat => {
      const otherUser = chat.users.find(u => u.id !== currentUserId)
      const userName = otherUser?.name || ''
      const lastMessage = chat.last_message?.content?.text || ''
      const searchLower = searchQuery.toLowerCase()

      return userName.toLowerCase().includes(searchLower) ||
             lastMessage.toLowerCase().includes(searchLower)
    })
  }, [chats, searchQuery, currentUserId])

  // Total unread
  const totalUnread = useMemo(() => {
    return chats.reduce((sum, chat) => sum + chat.unread_count, 0)
  }, [chats])

  // Get other user
  const getOtherUser = useCallback((chat: Chat) => {
    return chat.users.find(u => u.id !== currentUserId)
  }, [currentUserId])

  // Format time
  const formatTime = useCallback((timestamp: number) => {
    const date = new Date(timestamp * 1000)
    const now = new Date()

    if (date.toDateString() === now.toDateString()) {
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
    }

    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
  }, [])

  useEffect(() => {
    loadChats()
    loadPollingStatus()
    const interval = setInterval(loadChats, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [loadChats, loadPollingStatus])

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg">
            <MessageSquare className="w-6 h-6 text-gray-900" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Авито Мессенджер</h1>
            <p className="text-sm text-gray-600">Управление чатами с клиентами</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Auto Response Toggle */}
          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-gray-200">
            <Bot className="w-5 h-5 text-purple-400" />
            <span className="text-sm font-medium text-gray-700">AI Автоответы</span>
            <button
              onClick={toggleAutoResponse}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                autoResponseEnabled ? 'bg-green-500' : 'bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoResponseEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          <button
            onClick={loadChats}
            className="px-4 py-2 bg-white hover:bg-gray-50 rounded-xl border border-gray-200 text-gray-900 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Обновить
          </button>
          <button
            onClick={() => setShowSettingsModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-pink-500 to-rose-600 hover:from-pink-600 hover:to-rose-700 rounded-xl text-gray-900 transition-all flex items-center gap-2"
          >
            <Settings className="w-4 h-4" />
            Настройки
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-12 gap-6">
        {/* Chat List */}
        <div className="col-span-4 space-y-4">
          <div className="bg-white backdrop-blur-xl rounded-2xl border border-gray-200 overflow-hidden">
            {/* Search and Filters */}
            <div className="p-4 space-y-3 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-600" />
                <input
                  type="text"
                  placeholder="Поиск чатов..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-pink-500"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showUnreadOnly}
                    onChange={(e) => setShowUnreadOnly(e.target.checked)}
                    className="rounded border-gray-300 bg-white"
                  />
                  Только непрочитанные
                </label>
                <span className="px-3 py-1 bg-pink-500/20 text-pink-300 rounded-full text-sm font-medium">
                  {totalUnread} непрочитанных
                </span>
              </div>
            </div>

            {/* Chat List */}
            <div className="max-h-[600px] overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center p-8">
                  <Loader className="w-6 h-6 animate-spin text-pink-500" />
                </div>
              ) : filteredChats.length === 0 ? (
                <div className="text-center p-8 text-gray-600">
                  <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Нет чатов</p>
                </div>
              ) : (
                filteredChats.map((chat) => {
                  const otherUser = getOtherUser(chat)
                  const userName = otherUser?.name || 'Неизвестный'
                  const lastMessage = chat.last_message?.content?.text || 'Нет сообщений'
                  const lastTime = chat.last_message ? formatTime(chat.last_message.created) : ''

                  return (
                    <button
                      key={chat.id}
                      onClick={() => selectChat(chat)}
                      className={`w-full p-4 border-b border-gray-100 hover:bg-white transition-colors text-left ${
                        selectedChat?.id === chat.id ? 'bg-gray-50' : ''
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center text-gray-900 font-bold flex-shrink-0">
                          {userName.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-gray-900 truncate">{userName}</span>
                            {chat.unread_count > 0 && (
                              <span className="px-2 py-0.5 bg-pink-500 text-gray-900 text-xs rounded-full">
                                {chat.unread_count}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 truncate">{lastMessage}</p>
                        </div>
                        <span className="text-xs text-gray-600">{lastTime}</span>
                      </div>
                    </button>
                  )
                })
              )}
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="col-span-8">
          {!selectedChat ? (
            <div className="h-full bg-white backdrop-blur-xl rounded-2xl border border-gray-200 flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p className="text-xl text-gray-600">Выберите чат для начала общения</p>
              </div>
            </div>
          ) : (
            <div className="h-full bg-white backdrop-blur-xl rounded-2xl border border-gray-200 flex flex-col">
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center text-gray-900 font-bold">
                    {getOtherUser(selectedChat)?.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{getOtherUser(selectedChat)?.name}</h3>
                    {selectedChat.context?.value?.title && (
                      <p className="text-sm text-gray-600">
                        {selectedChat.context.value.title} - {selectedChat.context.value.price} руб.
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowAiModal(true)}
                    className="p-2 hover:bg-white rounded-lg text-purple-400 transition-colors"
                    title="AI Продажник"
                  >
                    <Briefcase className="w-5 h-5" />
                  </button>
                  <button
                    onClick={createLead}
                    className="p-2 hover:bg-white rounded-lg text-green-400 transition-colors"
                    title="Создать лид"
                  >
                    <Star className="w-5 h-5" />
                  </button>
                  <button
                    onClick={exportChat}
                    className="p-2 hover:bg-white rounded-lg text-blue-400 transition-colors"
                    title="Экспорт чата"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messagesLoading ? (
                  <div className="flex items-center justify-center h-full">
                    <Loader className="w-6 h-6 animate-spin text-pink-500" />
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.direction === 'out' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-2xl p-3 ${
                          msg.direction === 'out'
                            ? 'bg-gradient-to-r from-pink-500 to-rose-600 text-gray-900'
                            : 'bg-gray-50 text-gray-900'
                        }`}
                      >
                        {msg.type === 'text' && msg.content.text && (
                          <p className="text-sm">{msg.content.text}</p>
                        )}
                        {msg.type === 'image' && msg.content.image && (
                          <img
                            src={msg.content.image['640x480'] || msg.content.image['1280x960']}
                            alt="Attachment"
                            className="max-w-xs rounded-lg cursor-pointer"
                            onClick={() => window.open(msg.content.image?.['1280x960'], '_blank')}
                          />
                        )}
                        <p className="text-xs opacity-70 mt-1">{formatTime(msg.created)}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* AI Assistant */}
              {showAiAssistant && (
                <div className="p-4 bg-purple-500/10 border-t border-gray-200">
                  <div className="flex items-start gap-2 mb-2">
                    <Bot className="w-5 h-5 text-purple-400 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm text-gray-700 mb-2">AI Ассистент анализирует контекст</p>
                      {aiSuggestion ? (
                        <div className="p-3 bg-white rounded-lg border border-gray-200">
                          <p className="text-sm text-gray-900">{aiSuggestion}</p>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-gray-600">
                          <Loader className="w-4 h-4 animate-spin" />
                          <span className="text-sm">Генерирую ответ...</span>
                        </div>
                      )}
                    </div>
                    <button onClick={() => setShowAiAssistant(false)} className="text-gray-600 hover:text-gray-900">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  {aiSuggestion && (
                    <div className="flex gap-2">
                      <button
                        onClick={useAiSuggestion}
                        className="px-3 py-1.5 bg-green-500 hover:bg-green-600 text-gray-900 rounded-lg text-sm transition-colors"
                      >
                        <Check className="w-4 h-4 inline mr-1" />
                        Использовать
                      </button>
                      <button
                        onClick={generateAiSuggestion}
                        className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-gray-900 rounded-lg text-sm transition-colors"
                      >
                        <RefreshCw className="w-4 h-4 inline mr-1" />
                        Новый вариант
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200">
                <form onSubmit={sendMessage} className="flex items-center gap-2">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    id="image-upload"
                  />
                  <label
                    htmlFor="image-upload"
                    className="p-2 hover:bg-white rounded-lg text-gray-600 hover:text-gray-900 cursor-pointer transition-colors"
                  >
                    <ImageIcon className="w-5 h-5" />
                  </label>
                  <button
                    type="button"
                    onClick={generateAiSuggestion}
                    className="p-2 hover:bg-white rounded-lg text-purple-400 hover:text-purple-300 transition-colors"
                    title="AI Ассистент"
                  >
                    <Bot className="w-5 h-5" />
                  </button>
                  <input
                    type="text"
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    placeholder="Введите сообщение..."
                    className="flex-1 px-4 py-2 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-pink-500"
                  />
                  <button
                    type="submit"
                    disabled={!messageInput.trim()}
                    className="px-4 py-2 bg-gradient-to-r from-pink-500 to-rose-600 hover:from-pink-600 hover:to-rose-700 rounded-xl text-gray-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Отправить
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* AI Sales Modal */}
      {showAiModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#1a1d2e] rounded-2xl border border-gray-200 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Briefcase className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-bold text-gray-900">AI Продажник</h2>
              </div>
              <button onClick={() => setShowAiModal(false)} className="text-gray-600 hover:text-gray-900">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Сфера деятельности клиента
                </label>
                <input
                  type="text"
                  value={aiIndustry}
                  onChange={(e) => setAiIndustry(e.target.value)}
                  placeholder="ювелирка, красота, ресторан..."
                  className="w-full px-4 py-2 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => generateAiSales('startup_offer')}
                  disabled={aiLoading}
                  className="px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-xl text-gray-900 transition-all disabled:opacity-50"
                >
                  Стартовый оффер
                </button>
                <button
                  onClick={() => generateAiSales('suggest_response')}
                  disabled={aiLoading}
                  className="px-4 py-3 bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 rounded-xl text-gray-900 transition-all disabled:opacity-50"
                >
                  Варианты ответов
                </button>
              </div>

              {aiLoading && (
                <div className="flex items-center justify-center p-8">
                  <Loader className="w-6 h-6 animate-spin text-purple-500" />
                </div>
              )}

              {aiResult && !aiLoading && (
                <div className="space-y-3">
                  {aiResult.offer && (
                    <div className="p-4 bg-white rounded-xl border border-gray-200">
                      <p className="text-gray-900 whitespace-pre-wrap">{aiResult.offer}</p>
                      <button
                        onClick={() => useAiResult(aiResult.offer)}
                        className="mt-3 px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg text-gray-900 text-sm transition-colors"
                      >
                        Использовать
                      </button>
                    </div>
                  )}

                  {aiResult.variants && (
                    <div className="space-y-2">
                      {aiResult.variants.map((variant: any, index: number) => (
                        <div key={index} className="p-4 bg-white rounded-xl border border-gray-200">
                          <p className="text-sm text-gray-600 mb-2">{variant.title}</p>
                          <p className="text-gray-900">{variant.text}</p>
                          <button
                            onClick={() => useAiResult(variant.text)}
                            className="mt-2 px-3 py-1.5 bg-green-500 hover:bg-green-600 rounded-lg text-gray-900 text-sm transition-colors"
                          >
                            Выбрать
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Toasts */}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-3 rounded-xl shadow-lg backdrop-blur-sm border ${
              toast.type === 'success'
                ? 'bg-green-500/90 border-green-400'
                : toast.type === 'error'
                ? 'bg-red-500/90 border-red-400'
                : 'bg-blue-500/90 border-blue-400'
            } text-gray-900`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  )
}
