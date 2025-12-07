import { useState, useEffect, useRef } from 'react'
import {
  Mic,
  MicOff,
  Phone,
  PhoneOff,
  MessageSquare,
  Lightbulb,
  User,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Download,
  Target,
  ListTodo,
  HelpCircle,
  TrendingUp,
  Flag,
  DollarSign,
} from 'lucide-react'
import { Document, Paragraph, TextRun, AlignmentType, HeadingLevel, Packer } from 'docx'
import { saveAs } from 'file-saver'
import { API_URL } from '../config'

// ====================================
// Types
// ====================================

interface DialogMessage {
  id: string
  type: 'salesperson' | 'client'
  text: string
  timestamp: Date
}

interface ThreeLevelSuggestion {
  reply_now: string  // Что сказать сейчас
  next_steps: string[]  // План на 2-3 минуты
  explanation: string  // Объяснение для новичка
  context?: CallContext
  timestamp: Date
}

interface CallContext {
  summary: string
  requirements: string[]
  stage: ConversationStage
  client_type: ClientType
  budget_signals: string[]
  red_flags: string[]
  message_count: number
  questions_count: number
}

type ConversationStage = 'greeting' | 'discovery' | 'presentation' | 'pricing' | 'objection' | 'closing'
type ClientType = 'unknown' | 'newbie' | 'technical' | 'business' | 'toxic'

interface CallStats {
  duration: number
  messagesCount: number
  questionsDetected: number
  suggestionsGenerated: number
}

// Helper для получения auth header
const getAuthHeader = () => {
  let auth = localStorage.getItem('auth')
  if (!auth) {
    const defaultAuth = { username: 'admin', password: 'qwerty123' }
    localStorage.setItem('auth', JSON.stringify(defaultAuth))
    auth = JSON.stringify(defaultAuth)
  }
  const { username, password } = JSON.parse(auth)
  return `Basic ${btoa(`${username}:${password}`)}`
}

// Маппинг этапов на русский
const STAGE_LABELS: Record<ConversationStage, { label: string; color: string; emoji: string }> = {
  greeting: { label: 'Знакомство', color: 'bg-blue-100 text-blue-700 border-blue-300', emoji: '👋' },
  discovery: { label: 'Сбор требований', color: 'bg-purple-100 text-purple-700 border-purple-300', emoji: '🔍' },
  presentation: { label: 'Презентация', color: 'bg-indigo-100 text-indigo-700 border-indigo-300', emoji: '📊' },
  pricing: { label: 'Обсуждение цены', color: 'bg-yellow-100 text-yellow-700 border-yellow-300', emoji: '💰' },
  objection: { label: 'Возражения', color: 'bg-orange-100 text-orange-700 border-orange-300', emoji: '⚠️' },
  closing: { label: 'Закрытие сделки', color: 'bg-green-100 text-green-700 border-green-300', emoji: '🎉' },
}

// Маппинг типов клиентов
const CLIENT_TYPE_LABELS: Record<ClientType, { label: string; color: string }> = {
  unknown: { label: 'Неизвестен', color: 'bg-gray-100 text-gray-700' },
  newbie: { label: 'Новичок', color: 'bg-blue-100 text-blue-700' },
  technical: { label: 'Технарь', color: 'bg-purple-100 text-purple-700' },
  business: { label: 'Бизнесмен', color: 'bg-green-100 text-green-700' },
  toxic: { label: 'Токсик', color: 'bg-red-100 text-red-700' },
}

// Ключ для localStorage
const CALL_STATE_KEY = 'ai_call_v2_persistent_state'

export const AICallsV2 = () => {
  // Состояние звонка
  const [isCallActive, setIsCallActive] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentSpeaker, setCurrentSpeaker] = useState<'client' | 'salesperson'>('client')

  // Диалог
  const [messages, setMessages] = useState<DialogMessage[]>([])
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')

  // AI подсказки V2
  const [currentSuggestion, setCurrentSuggestion] = useState<ThreeLevelSuggestion | null>(null)
  const [suggestionHistory, setSuggestionHistory] = useState<ThreeLevelSuggestion[]>([])
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set())

  // Контекст звонка
  const [callContext, setCallContext] = useState<CallContext | null>(null)

  // Статистика
  const [callStats, setCallStats] = useState<CallStats>({
    duration: 0,
    messagesCount: 0,
    questionsDetected: 0,
    suggestionsGenerated: 0,
  })

  // WebSocket и Speech Recognition
  const wsRef = useRef<WebSocket | null>(null)
  const recognitionRef = useRef<any>(null)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isCallActiveRef = useRef(false)

  // Состояние подключения
  const [wsConnected, setWsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Автоскролл к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentSuggestion])

  // Инициализация Web Speech API
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      setError('Web Speech API не поддерживается в вашем браузере. Используйте Chrome или Edge.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'ru-RU'
    recognition.maxAlternatives = 1

    recognition.onresult = (event: any) => {
      let interim = ''
      let final = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript

        if (event.results[i].isFinal) {
          final += transcript + ' '
        } else {
          interim += transcript
        }
      }

      setInterimTranscript(interim)

      if (final) {
        setCurrentTranscript((prev) => prev + final)
        sendMessageToAI(final.trim())
      }
    }

    recognition.onerror = (event: any) => {
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        setError(`Ошибка распознавания: ${event.error}`)
      }
    }

    recognition.onend = () => {
      if (isCallActive && !isMuted) {
        try {
          recognition.start()
        } catch (e) {
          console.log('Recognition restart failed:', e)
        }
      }
    }

    recognitionRef.current = recognition

    return () => {
      if (recognition) {
        recognition.stop()
      }
    }
  }, [isCallActive, isMuted])

  // Таймер звонка
  useEffect(() => {
    if (isCallActive) {
      timerRef.current = setInterval(() => {
        setCallStats((prev) => ({
          ...prev,
          duration: prev.duration + 1,
        }))
      }, 1000)
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isCallActive])

  // WebSocket подключение к V2 API
  const connectWebSocket = () => {
    try {
      const auth = localStorage.getItem('auth')
      if (!auth) {
        setError('Не найдены данные авторизации')
        return
      }

      const { username, password } = JSON.parse(auth)
      const authHeader = btoa(`${username}:${password}`)

      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsHost = import.meta.env.MODE === 'production'
        ? window.location.host
        : 'localhost:8000'

      const wsUrl = `${wsProtocol}//${wsHost}/ws/voice-assistant-v2?auth=${authHeader}`

      console.log('Connecting to V2 WebSocket:', wsUrl)

      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('V2 WebSocket connected')
        setWsConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        } catch (e) {
          console.error('Error parsing WebSocket message:', e)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError('Ошибка подключения к серверу AI')
        setWsConnected(false)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setWsConnected(false)

        if (isCallActiveRef.current) {
          setTimeout(() => {
            connectWebSocket()
          }, 3000)
        }
      }

      wsRef.current = ws
    } catch (e) {
      console.error('Error connecting to WebSocket:', e)
      setError('Не удалось подключиться к серверу AI')
    }
  }

  // Обработка сообщений от WebSocket V2
  const handleWebSocketMessage = (data: any) => {
    console.log('[V2] Received:', data.type)

    if (data.type === 'connected') {
      console.log('[V2] Connected:', data.message)
    } else if (data.type === 'suggestion_v2') {
      // Трехуровневая подсказка
      const suggestion: ThreeLevelSuggestion = {
        reply_now: data.reply_now || '',
        next_steps: data.next_steps || [],
        explanation: data.explanation || '',
        context: data.context,
        timestamp: new Date(),
      }

      setCurrentSuggestion(suggestion)
      setSuggestionHistory((prev) => [suggestion, ...prev])
      setCompletedSteps(new Set()) // Сбрасываем чекбоксы для новых шагов

      // Обновляем контекст
      if (data.context) {
        setCallContext(data.context)
      }

      setCallStats((prev) => ({
        ...prev,
        suggestionsGenerated: prev.suggestionsGenerated + 1,
      }))
    } else if (data.type === 'context_data') {
      setCallContext(data.context)
    }
  }

  // Отправка сообщения на AI анализ
  const sendMessageToAI = (text: string) => {
    if (!text.trim()) {
      return
    }

    const message: DialogMessage = {
      id: Date.now().toString(),
      type: currentSpeaker,
      text: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, message])
    setCallStats((prev) => ({
      ...prev,
      messagesCount: prev.messagesCount + 1,
    }))

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'speech',
          text: text,
          timestamp: new Date().toISOString(),
          speaker: currentSpeaker,
        })
      )
    } else {
      console.warn('WebSocket not connected')
    }

    setCurrentTranscript('')
  }

  // Начать звонок
  const startCall = () => {
    setIsCallActive(true)
    isCallActiveRef.current = true
    setMessages([])
    setSuggestionHistory([])
    setCurrentSuggestion(null)
    setCallContext(null)
    setCallStats({
      duration: 0,
      messagesCount: 0,
      questionsDetected: 0,
      suggestionsGenerated: 0,
    })
    setError(null)

    connectWebSocket()
    startListening()
  }

  // Закончить звонок
  const endCall = () => {
    setIsCallActive(false)
    isCallActiveRef.current = false
    stopListening()

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setWsConnected(false)
  }

  // Начать слушать
  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start()
        setIsListening(true)
        setIsMuted(false)
      } catch (e) {
        console.error('Error starting recognition:', e)
      }
    }
  }

  // Остановить слушать
  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    }
  }

  // Переключить микрофон
  const toggleMute = () => {
    if (isMuted) {
      startListening()
    } else {
      stopListening()
      setIsMuted(true)
    }
  }

  // Отметить шаг как выполненный
  const toggleStep = (index: number) => {
    setCompletedSteps((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      return newSet
    })
  }

  // Сохранить разговор
  const saveConversation = async () => {
    try {
      const now = new Date()
      const dateStr = now.toLocaleDateString('ru-RU')
      const timeStr = now.toLocaleTimeString('ru-RU')

      const doc = new Document({
        sections: [{
          children: [
            // Заголовок
            new Paragraph({
              text: 'Запись AI Звонка V2',
              heading: HeadingLevel.HEADING_1,
              alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
              text: `Дата: ${dateStr} ${timeStr}`,
              alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
              text: `Длительность: ${formatDuration(callStats.duration)}`,
              alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: '' }),

            // Контекст звонка
            new Paragraph({
              text: 'Контекст звонка',
              heading: HeadingLevel.HEADING_2,
            }),
            ...(callContext ? [
              new Paragraph({
                children: [
                  new TextRun({ text: 'Этап: ', bold: true }),
                  new TextRun({ text: STAGE_LABELS[callContext.stage].label }),
                ],
              }),
              new Paragraph({
                children: [
                  new TextRun({ text: 'Тип клиента: ', bold: true }),
                  new TextRun({ text: CLIENT_TYPE_LABELS[callContext.client_type].label }),
                ],
              }),
              new Paragraph({
                children: [
                  new TextRun({ text: 'Требования: ', bold: true }),
                  new TextRun({ text: callContext.requirements.join(', ') || 'Нет' }),
                ],
              }),
              new Paragraph({ text: '' }),
            ] : []),

            // Диалог
            new Paragraph({
              text: 'Диалог',
              heading: HeadingLevel.HEADING_2,
            }),
            ...messages.map((msg) =>
              new Paragraph({
                children: [
                  new TextRun({
                    text: msg.type === 'client' ? 'Клиент: ' : 'Менеджер: ',
                    bold: true,
                    color: msg.type === 'client' ? '2563EB' : '9333EA',
                  }),
                  new TextRun({ text: msg.text }),
                ],
              })
            ),
            new Paragraph({ text: '' }),

            // Подсказки AI
            new Paragraph({
              text: 'Подсказки AI',
              heading: HeadingLevel.HEADING_2,
            }),
            ...suggestionHistory.map((sugg) => [
              new Paragraph({
                children: [
                  new TextRun({ text: 'Что сказать: ', bold: true }),
                  new TextRun({ text: sugg.reply_now }),
                ],
              }),
              new Paragraph({
                children: [
                  new TextRun({ text: 'План: ', bold: true }),
                ],
              }),
              ...sugg.next_steps.map(step =>
                new Paragraph({
                  text: `  • ${step}`,
                })
              ),
              new Paragraph({ text: '' }),
            ]).flat(),
          ],
        }],
      })

      const blob = await Packer.toBlob(doc)
      saveAs(blob, `ai_call_v2_${now.toISOString().split('T')[0]}_${now.getHours()}-${now.getMinutes()}.docx`)
    } catch (e) {
      console.error('Error saving conversation:', e)
      setError('Ошибка при сохранении разговора')
    }
  }

  // Форматирование времени
  const formatDuration = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hrs > 0 ? hrs.toString().padStart(2, '0') + ':' : ''}${mins
      .toString()
      .padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-normal text-gray-900 mb-2">AI Звонки V2 (Продвинутый помощник)</h1>
        <p className="text-gray-600">
          Умный AI-тимлид с контекстным анализом и трехуровневыми подсказками
        </p>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900">Ошибка</p>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Active Call Banner with Stage */}
      {isCallActive && callContext && (
        <div className="mb-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              <div>
                <p className="font-semibold text-green-900">Звонок активен</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${STAGE_LABELS[callContext.stage].color}`}>
                    {STAGE_LABELS[callContext.stage].emoji} {STAGE_LABELS[callContext.stage].label}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${CLIENT_TYPE_LABELS[callContext.client_type].color}`}>
                    {CLIENT_TYPE_LABELS[callContext.client_type].label}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-green-800">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span className="font-mono">{formatDuration(callStats.duration)}</span>
              </div>
              {isListening && (
                <div className="flex items-center gap-2">
                  <Mic className="w-4 h-4 text-green-600" />
                  <span>Запись</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left Column - Controls */}
        <div className="col-span-3 space-y-6">
          {/* Call Control */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
              <Phone className="w-5 h-5 text-purple-600" />
              Управление
            </h2>

            {!isCallActive ? (
              <button
                onClick={startCall}
                className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg"
              >
                <Phone className="w-6 h-6" />
                <span className="text-lg font-medium">Начать звонок</span>
              </button>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={toggleMute}
                    className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-all ${
                      isMuted
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                  </button>

                  <button
                    onClick={endCall}
                    className="flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-all"
                  >
                    <PhoneOff className="w-5 h-5" />
                  </button>
                </div>

                {/* Speaker Toggle */}
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200">
                  <div className="text-xs text-gray-600 mb-2 text-center">Сейчас говорит:</div>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setCurrentSpeaker('client')}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        currentSpeaker === 'client'
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      Клиент
                    </button>
                    <button
                      onClick={() => setCurrentSpeaker('salesperson')}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        currentSpeaker === 'salesperson'
                          ? 'bg-green-600 text-white shadow-md'
                          : 'bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      Менеджер
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Context Panel */}
          {callContext && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Контекст звонка</h2>

              <div className="space-y-4">
                {/* Requirements */}
                {callContext.requirements.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <ListTodo className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-gray-700">Требования:</span>
                    </div>
                    <div className="space-y-1">
                      {callContext.requirements.map((req, i) => (
                        <div key={i} className="text-sm text-gray-600 pl-6">• {req}</div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Budget Signals */}
                {callContext.budget_signals.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-gray-700">Бюджет:</span>
                    </div>
                    <div className="space-y-1">
                      {callContext.budget_signals.map((signal, i) => (
                        <div key={i} className="text-sm text-gray-600 pl-6">• {signal}</div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Red Flags */}
                {callContext.red_flags.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Flag className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-medium text-red-700">Красные флаги:</span>
                    </div>
                    <div className="space-y-1">
                      {callContext.red_flags.map((flag, i) => (
                        <div key={i} className="text-sm text-red-600 pl-6">• {flag}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          {messages.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
              <button
                onClick={saveConversation}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all"
              >
                <Download className="w-5 h-5" />
                <span className="text-sm font-medium">Сохранить</span>
              </button>
            </div>
          )}
        </div>

        {/* Middle Column - Conversation */}
        <div className="col-span-5 bg-white rounded-2xl border border-gray-200 shadow-lg flex flex-col h-[calc(100vh-200px)]">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-purple-600" />
              Диалог
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && !isCallActive && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <Phone className="w-16 h-16 text-gray-300 mb-4" />
                <p className="text-gray-500">Начните звонок</p>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.type === 'salesperson' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.type === 'client' && (
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-blue-600" />
                  </div>
                )}

                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                    message.type === 'salesperson'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                </div>

                {message.type === 'salesperson' && (
                  <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-purple-600" />
                  </div>
                )}
              </div>
            ))}

            {(currentTranscript || interimTranscript) && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-blue-600" />
                </div>
                <div className="max-w-[75%] rounded-2xl px-4 py-3 bg-gray-100 text-gray-900 border-2 border-purple-300">
                  <p className="text-sm">
                    {currentTranscript}
                    <span className="text-gray-500 italic">{interimTranscript}</span>
                  </p>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Right Column - AI Suggestions V2 */}
        <div className="col-span-4 space-y-6">
          {/* Current Suggestion - Reply Now */}
          {currentSuggestion && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-400 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-6 h-6 text-green-600" />
                <h3 className="text-lg font-bold text-green-900">Что сказать сейчас</h3>
              </div>
              <p className="text-gray-900 text-base leading-relaxed">
                {currentSuggestion.reply_now}
              </p>
            </div>
          )}

          {/* Next Steps */}
          {currentSuggestion && currentSuggestion.next_steps.length > 0 && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-6 h-6 text-blue-600" />
                <h3 className="text-lg font-bold text-blue-900">План на 2-3 минуты</h3>
              </div>
              <div className="space-y-3">
                {currentSuggestion.next_steps.map((step, index) => (
                  <label key={index} className="flex items-start gap-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={completedSteps.has(index)}
                      onChange={() => toggleStep(index)}
                      className="mt-1 rounded border-blue-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className={`text-sm ${completedSteps.has(index) ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                      {step}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Explanation */}
          {currentSuggestion && currentSuggestion.explanation && (
            <div className="bg-gradient-to-br from-yellow-50 to-amber-50 border-2 border-yellow-300 rounded-xl p-6 shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <HelpCircle className="w-6 h-6 text-yellow-600" />
                <h3 className="text-lg font-bold text-yellow-900">Подсказка для новичка</h3>
              </div>
              <p className="text-gray-900 text-sm leading-relaxed">
                {currentSuggestion.explanation}
              </p>
            </div>
          )}

          {/* Empty State */}
          {!currentSuggestion && isCallActive && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-8">
              <div className="flex flex-col items-center justify-center text-center">
                <Lightbulb className="w-16 h-16 text-gray-300 mb-4" />
                <p className="text-gray-500">Подсказки появятся после речи клиента</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
