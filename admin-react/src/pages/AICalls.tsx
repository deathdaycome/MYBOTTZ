import { useState, useEffect, useRef } from 'react'
import {
  Mic,
  MicOff,
  Phone,
  PhoneOff,
  MessageSquare,
  Lightbulb,
  User,
  Bot,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Trash2,
  Save,
  Download,
} from 'lucide-react'
import { Document, Paragraph, TextRun, AlignmentType, HeadingLevel, Packer } from 'docx'
import { saveAs } from 'file-saver'
import { API_URL } from '../config'

// Типы для сообщений в диалоге
interface DialogMessage {
  id: string
  type: 'salesperson' | 'client'
  text: string
  timestamp: Date
  isQuestion?: boolean
}

// Типы для AI подсказок
interface AISuggestion {
  id: string
  question: string
  answer: string
  category: string
  confidence: number
  timestamp: Date
  used?: boolean
}

// Типы для статистики звонка
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

// Функция для форматирования ответов AI (удаление markdown)
const formatAnswer = (text: string): JSX.Element => {
  // Убираем markdown форматирование
  const cleanText = text
    .replace(/\*\*([^*]+)\*\*/g, '$1') // Убираем **текст**
    .replace(/\*([^*]+)\*/g, '$1') // Убираем *текст*
    .trim()

  // Разбиваем на строки и ищем паттерны типа "Скажи:", "Цель:", "Стадия:"
  const lines = cleanText.split('\n').filter(line => line.trim())

  return (
    <div className="space-y-2">
      {lines.map((line, index) => {
        const trimmedLine = line.trim()

        // Проверяем, начинается ли строка с эмодзи + ключевого слова и двоеточия
        // Паттерн: эмодзи (опционально) + пробелы (опционально) + слово + двоеточие
        const labelMatch = trimmedLine.match(/^(?:[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}])?\s*([А-Яа-яA-Za-z\s]+):\s*(.+)$/u)

        if (labelMatch) {
          const [, label, content] = labelMatch
          // Извлекаем эмодзи если есть
          const emojiMatch = trimmedLine.match(/^([\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}])/u)
          const emoji = emojiMatch ? emojiMatch[1] + ' ' : ''

          return (
            <div key={index} className="mb-2">
              <span className="text-gray-900">{emoji}</span>
              <span className="font-semibold text-gray-700">{label}:</span>{' '}
              <span className="text-gray-900">{content}</span>
            </div>
          )
        }

        // Обычная строка
        return (
          <div key={index} className="text-gray-900">
            {trimmedLine}
          </div>
        )
      })}
    </div>
  )
}

// Ключ для localStorage
const CALL_STATE_KEY = 'ai_call_persistent_state'

export const AICalls = () => {
  // Состояние звонка
  const [isCallActive, setIsCallActive] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentSpeaker, setCurrentSpeaker] = useState<'client' | 'salesperson'>('client')

  // Диалог
  const [messages, setMessages] = useState<DialogMessage[]>([])
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')

  // AI подсказки
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([])
  const [activeSuggestion, setActiveSuggestion] = useState<AISuggestion | null>(null)

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

  // Сохранение состояния в localStorage
  const saveState = () => {
    if (!isCallActive) {
      // Если звонок не активен, удаляем состояние
      localStorage.removeItem(CALL_STATE_KEY)
      return
    }

    const state = {
      isCallActive,
      currentSpeaker,
      messages: messages.map(m => ({
        ...m,
        timestamp: m.timestamp.toISOString()
      })),
      suggestions: suggestions.map(s => ({
        ...s,
        timestamp: s.timestamp.toISOString()
      })),
      callStats,
      startTime: Date.now() - callStats.duration * 1000
    }

    localStorage.setItem(CALL_STATE_KEY, JSON.stringify(state))
  }

  // Восстановление состояния из localStorage
  const restoreState = () => {
    const saved = localStorage.getItem(CALL_STATE_KEY)
    if (!saved) return false

    try {
      const state = JSON.parse(saved)

      // Восстанавливаем состояние
      setCurrentSpeaker(state.currentSpeaker)
      setMessages(state.messages.map((m: any) => ({
        ...m,
        timestamp: new Date(m.timestamp)
      })))
      setSuggestions(state.suggestions.map((s: any) => ({
        ...s,
        timestamp: new Date(s.timestamp)
      })))

      // Восстанавливаем статистику с корректным временем
      const elapsedSeconds = Math.floor((Date.now() - state.startTime) / 1000)
      setCallStats({
        ...state.callStats,
        duration: elapsedSeconds
      })

      return true
    } catch (e) {
      console.error('Error restoring state:', e)
      localStorage.removeItem(CALL_STATE_KEY)
      return false
    }
  }

  // Восстановление состояния при монтировании компонента
  useEffect(() => {
    const hasState = restoreState()
    if (hasState) {
      console.log('Восстановлено активное состояние звонка')
      setIsCallActive(true)
      isCallActiveRef.current = true
      // Переподключаемся к WebSocket
      connectWebSocket()
      // Перезапускаем слушание
      setTimeout(() => {
        startListening()
      }, 500)
    }
  }, [])

  // Сохранение состояния при каждом изменении
  useEffect(() => {
    saveState()
  }, [isCallActive, messages, suggestions, callStats, currentSpeaker])

  // Инициализация Web Speech API
  useEffect(() => {
    // Проверяем поддержку Web Speech API
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      setError('Web Speech API не поддерживается в вашем браузере. Используйте Chrome или Edge.')
      return
    }

    // Создаём экземпляр распознавания
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'ru-RU'
    recognition.maxAlternatives = 1

    // Обработчики событий
    recognition.onresult = (event: any) => {
      console.log('🎤 Recognition result received:', event)
      let interim = ''
      let final = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript

        if (event.results[i].isFinal) {
          final += transcript + ' '
          console.log('✅ Final transcript:', transcript)
        } else {
          interim += transcript
          console.log('⏳ Interim transcript:', transcript)
        }
      }

      setInterimTranscript(interim)

      if (final) {
        console.log('📝 Sending final text to AI:', final.trim())
        setCurrentTranscript((prev) => prev + final)
        // Отправляем финальный текст на анализ
        sendMessageToAI(final.trim())
      }
    }

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      if (event.error === 'no-speech') {
        // Игнорируем - это нормально
      } else if (event.error === 'aborted') {
        // Игнорируем - мы сами остановили
      } else {
        setError(`Ошибка распознавания: ${event.error}`)
      }
    }

    recognition.onend = () => {
      // Если звонок активен, перезапускаем распознавание
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

  // Автоскролл к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, activeSuggestion])

  // WebSocket подключение
  const connectWebSocket = () => {
    try {
      // Получаем auth данные
      const auth = localStorage.getItem('auth')
      if (!auth) {
        setError('Не найдены данные авторизации')
        return
      }

      const { username, password } = JSON.parse(auth)
      const authHeader = btoa(`${username}:${password}`)

      // Определяем WebSocket URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsHost = import.meta.env.MODE === 'production'
        ? window.location.host
        : 'localhost:8000'

      const wsUrl = `${wsProtocol}//${wsHost}/ws/voice-assistant?auth=${authHeader}`

      console.log('Connecting to WebSocket:', wsUrl)

      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket connected')
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

        // Переподключение через 3 секунды, если звонок активен (используем ref для избежания stale closure)
        if (isCallActiveRef.current) {
          console.log('Will reconnect in 3 seconds...')
          setTimeout(() => {
            connectWebSocket()
          }, 3000)
        } else {
          console.log('Call not active, will not reconnect')
        }
      }

      wsRef.current = ws
    } catch (e) {
      console.error('Error connecting to WebSocket:', e)
      setError('Не удалось подключиться к серверу AI')
    }
  }

  // Обработка сообщений от WebSocket
  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'suggestion') {
      // Новая подсказка от AI
      const suggestion: AISuggestion = {
        id: Date.now().toString(),
        question: data.question,
        answer: data.answer,
        category: data.category || 'general',
        confidence: data.confidence || 0.8,
        timestamp: new Date(),
      }

      setSuggestions((prev) => [suggestion, ...prev])
      setActiveSuggestion(suggestion)
      setCallStats((prev) => ({
        ...prev,
        suggestionsGenerated: prev.suggestionsGenerated + 1,
      }))

      // Автоскрытие подсказки через 30 секунд
      setTimeout(() => {
        setActiveSuggestion((current) => {
          if (current?.id === suggestion.id) return null
          return current
        })
      }, 30000)
    } else if (data.type === 'question_detected') {
      // Обнаружен вопрос от клиента
      setCallStats((prev) => ({
        ...prev,
        questionsDetected: prev.questionsDetected + 1,
      }))
    }
  }

  // Отправка сообщения на AI анализ
  const sendMessageToAI = (text: string) => {
    if (!text.trim()) {
      return
    }

    // Добавляем сообщение в историю ВСЕГДА (независимо от WebSocket)
    const message: DialogMessage = {
      id: Date.now().toString(),
      type: currentSpeaker, // Используем текущего говорящего
      text: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, message])
    setCallStats((prev) => ({
      ...prev,
      messagesCount: prev.messagesCount + 1,
    }))

    // Отправляем на AI анализ только если WebSocket подключён
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
      console.warn('WebSocket not connected, message not sent to AI')
    }

    setCurrentTranscript('')
  }

  // Начать звонок
  const startCall = () => {
    setIsCallActive(true)
    isCallActiveRef.current = true  // Обновляем ref
    setMessages([])
    setSuggestions([])
    setActiveSuggestion(null)
    setCallStats({
      duration: 0,
      messagesCount: 0,
      questionsDetected: 0,
      suggestionsGenerated: 0,
    })
    setError(null)

    // Подключаемся к WebSocket
    connectWebSocket()

    // Начинаем слушать
    startListening()
  }

  // Закончить звонок
  const endCall = () => {
    setIsCallActive(false)
    isCallActiveRef.current = false  // Обновляем ref
    stopListening()

    // Закрываем WebSocket
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setWsConnected(false)

    // Удаляем сохраненное состояние
    localStorage.removeItem(CALL_STATE_KEY)
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

  // Отметить подсказку как использованную
  const useSuggestion = (suggestion: AISuggestion) => {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === suggestion.id ? { ...s, used: true } : s))
    )
    setActiveSuggestion(null)
  }

  // Скрыть активную подсказку
  const dismissSuggestion = () => {
    setActiveSuggestion(null)
  }

  // Очистить историю
  const clearHistory = () => {
    setMessages([])
    setSuggestions([])
    setActiveSuggestion(null)
  }

  // Сохранить разговор
  const saveConversation = async () => {
    try {
      const now = new Date()
      const dateStr = now.toLocaleDateString('ru-RU')
      const timeStr = now.toLocaleTimeString('ru-RU')

      // Создаем документ Word
      const doc = new Document({
        sections: [{
          children: [
            // Заголовок
            new Paragraph({
              text: 'Запись AI Звонка',
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
            new Paragraph({ text: '' }), // Пустая строка

            // Статистика
            new Paragraph({
              text: 'Статистика звонка',
              heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
              children: [
                new TextRun({ text: 'Сообщений: ', bold: true }),
                new TextRun({ text: `${callStats.messagesCount}` }),
              ],
            }),
            new Paragraph({
              children: [
                new TextRun({ text: 'Обнаружено вопросов: ', bold: true }),
                new TextRun({ text: `${callStats.questionsDetected}` }),
              ],
            }),
            new Paragraph({
              children: [
                new TextRun({ text: 'Подсказок от AI: ', bold: true }),
                new TextRun({ text: `${callStats.suggestionsGenerated}` }),
              ],
            }),
            new Paragraph({ text: '' }),

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
                  new TextRun({
                    text: ` (${msg.timestamp.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })})`,
                    italics: true,
                    color: '6B7280',
                  }),
                ],
              })
            ),
            new Paragraph({ text: '' }),

            // Подсказки AI
            new Paragraph({
              text: 'Подсказки AI',
              heading: HeadingLevel.HEADING_2,
            }),
            ...suggestions.map((sugg) => [
              new Paragraph({
                children: [
                  new TextRun({ text: 'Вопрос: ', bold: true }),
                  new TextRun({ text: sugg.question, italics: true }),
                ],
              }),
              new Paragraph({
                children: [
                  new TextRun({ text: 'Ответ: ', bold: true }),
                  new TextRun({ text: sugg.answer }),
                ],
              }),
              new Paragraph({
                children: [
                  new TextRun({ text: 'Категория: ', bold: true }),
                  new TextRun({ text: sugg.category }),
                  new TextRun({ text: ' | ' }),
                  new TextRun({ text: sugg.used ? 'Использовано ✓' : 'Не использовано', color: sugg.used ? '10B981' : '6B7280' }),
                ],
              }),
              new Paragraph({ text: '' }),
            ]).flat(),
          ],
        }],
      })

      // Генерируем и сохраняем файл
      const blob = await Packer.toBlob(doc)
      saveAs(blob, `call_${now.toISOString().split('T')[0]}_${now.getHours()}-${now.getMinutes()}.docx`)
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
      {/* Active Call Banner */}
      {isCallActive && (
        <div className="mb-6 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              <div>
                <p className="font-semibold text-green-900">Звонок активен</p>
                <p className="text-sm text-green-700">
                  Можете переходить на другие страницы - запись продолжается
                </p>
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

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-normal text-gray-900 mb-2">AI Звонки</h1>
        <p className="text-gray-600">
          Голосовой помощник для продажников с AI подсказками в реальном времени
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

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Call Controls and Stats */}
        <div className="space-y-6">
          {/* Call Control */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
              <Phone className="w-5 h-5 text-purple-600" />
              Управление звонком
            </h2>

            {!isCallActive ? (
              <button
                onClick={startCall}
                className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl"
              >
                <Phone className="w-6 h-6" />
                <span className="text-lg font-medium">Начать звонок</span>
              </button>
            ) : (
              <div className="space-y-4">
                {/* Duration */}
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-4 border border-purple-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Длительность</span>
                    <div className="flex items-center gap-2 text-2xl font-light text-gray-900">
                      <Clock className="w-5 h-5 text-purple-600" />
                      {formatDuration(callStats.duration)}
                    </div>
                  </div>
                </div>

                {/* Connection Status */}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">AI сервер</span>
                  <div className="flex items-center gap-2">
                    {wsConnected ? (
                      <>
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-green-700 font-medium">Подключен</span>
                      </>
                    ) : (
                      <>
                        <div className="w-2 h-2 bg-red-500 rounded-full" />
                        <span className="text-red-700 font-medium">Отключен</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Microphone Status */}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">Микрофон</span>
                  <div className="flex items-center gap-2">
                    {isListening ? (
                      <>
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-green-700 font-medium">Слушает</span>
                      </>
                    ) : (
                      <>
                        <div className="w-2 h-2 bg-gray-500 rounded-full" />
                        <span className="text-gray-700 font-medium">Выключен</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Control Buttons */}
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
                    <span className="text-sm font-medium">{isMuted ? 'Включить' : 'Микрофон'}</span>
                  </button>

                  <button
                    onClick={endCall}
                    className="flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-all"
                  >
                    <PhoneOff className="w-5 h-5" />
                    <span className="text-sm font-medium">Завершить</span>
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
                      👤 Клиент
                    </button>
                    <button
                      onClick={() => setCurrentSpeaker('salesperson')}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        currentSpeaker === 'salesperson'
                          ? 'bg-green-600 text-white shadow-md'
                          : 'bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      💼 Менеджер
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Call Stats */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              Статистика
            </h2>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-sm text-gray-700">Сообщений</span>
                <span className="text-lg font-semibold text-blue-600">{callStats.messagesCount}</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <span className="text-sm text-gray-700">Вопросов</span>
                <span className="text-lg font-semibold text-purple-600">
                  {callStats.questionsDetected}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm text-gray-700">Подсказок</span>
                <span className="text-lg font-semibold text-green-600">
                  {callStats.suggestionsGenerated}
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          {messages.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Действия</h2>

              <div className="space-y-3">
                <button
                  onClick={saveConversation}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all"
                >
                  <Download className="w-5 h-5" />
                  <span className="text-sm font-medium">Сохранить разговор</span>
                </button>

                <button
                  onClick={clearHistory}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-all"
                >
                  <Trash2 className="w-5 h-5" />
                  <span className="text-sm font-medium">Очистить историю</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Middle Column - Conversation */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-lg flex flex-col h-[calc(100vh-200px)]">
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
                <p className="text-gray-500">Начните звонок, чтобы увидеть диалог</p>
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
                      : message.isQuestion
                      ? 'bg-yellow-50 text-gray-900 border-2 border-yellow-300'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.type === 'salesperson' ? 'text-purple-200' : 'text-gray-500'
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString('ru-RU', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                {message.type === 'salesperson' && (
                  <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-purple-600" />
                  </div>
                )}
              </div>
            ))}

            {/* Current transcript (interim) */}
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
                  <p className="text-xs text-gray-500 mt-1">Распознаётся...</p>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Right Column - AI Suggestions */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-lg flex flex-col h-[calc(100vh-200px)]">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-600" />
              AI Подсказки
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {/* Active Suggestion */}
            {activeSuggestion && (
              <div className="bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-400 rounded-xl p-4 shadow-lg animate-pulse-subtle">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-600" />
                    <span className="text-sm font-medium text-yellow-900">Новая подсказка</span>
                  </div>
                  <button
                    onClick={dismissSuggestion}
                    className="p-1 hover:bg-yellow-100 rounded transition-all"
                  >
                    <XCircle className="w-4 h-4 text-yellow-700" />
                  </button>
                </div>

                <div className="mb-3">
                  <p className="text-xs text-yellow-700 mb-1 font-medium">Вопрос клиента:</p>
                  <p className="text-sm text-yellow-900 italic">"{activeSuggestion.question}"</p>
                </div>

                <div className="mb-3">
                  <p className="text-xs text-green-700 mb-1 font-medium">Рекомендуемый ответ:</p>
                  <div className="text-sm text-gray-900 bg-white rounded-lg p-3">
                    {formatAnswer(activeSuggestion.answer)}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-yellow-700">
                    Категория: {activeSuggestion.category}
                  </span>
                  <button
                    onClick={() => useSuggestion(activeSuggestion)}
                    className="flex items-center gap-1 px-3 py-1 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 transition-all"
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    Использовал
                  </button>
                </div>
              </div>
            )}

            {/* Suggestions History */}
            {suggestions.length === 0 && !activeSuggestion && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <Bot className="w-16 h-16 text-gray-300 mb-4" />
                <p className="text-gray-500">Подсказки появятся при обнаружении вопросов</p>
              </div>
            )}

            {suggestions
              .filter((s) => s.id !== activeSuggestion?.id)
              .map((suggestion) => (
                <div
                  key={suggestion.id}
                  className={`border rounded-xl p-4 transition-all ${
                    suggestion.used
                      ? 'bg-green-50 border-green-200'
                      : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-xs text-gray-600">
                      {suggestion.timestamp.toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                    {suggestion.used && (
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                    )}
                  </div>

                  <div className="mb-2">
                    <p className="text-xs text-gray-700 mb-1">Вопрос:</p>
                    <p className="text-sm text-gray-900 italic">"{suggestion.question}"</p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-700 mb-1">Ответ:</p>
                    <div className="text-sm text-gray-900">{formatAnswer(suggestion.answer)}</div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900">
            <p className="font-medium mb-1">Как это работает</p>
            <ul className="list-disc list-inside text-blue-700 space-y-1">
              <li>Нажмите "Начать звонок" и разрешите доступ к микрофону</li>
              <li>Ведите разговор с клиентом - система автоматически распознаёт речь</li>
              <li>AI анализирует вопросы клиента и предлагает готовые ответы</li>
              <li>Используйте подсказки для более уверенных и точных ответов</li>
              <li>Все разговоры сохраняются для последующего анализа</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

// Add missing import
import { BarChart3 } from 'lucide-react'
