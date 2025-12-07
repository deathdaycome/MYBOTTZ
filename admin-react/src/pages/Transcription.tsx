import { useState, useEffect, useRef } from 'react'
import {
  Mic,
  StopCircle,
  Upload,
  FileVideo,
  Download,
  FileAudio,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Clock,
  Trash2,
  PlayCircle,
  Copy,
  Save
} from 'lucide-react'
import { API_URL } from '../config'

// Helper function to get auth header
const getAuthHeader = () => {
  let auth = localStorage.getItem('auth')
  if (!auth) {
    // Use default credentials
    const defaultAuth = { username: 'admin', password: 'qwerty123' }
    localStorage.setItem('auth', JSON.stringify(defaultAuth))
    auth = JSON.stringify(defaultAuth)
  }
  const { username, password } = JSON.parse(auth)
  return `Basic ${btoa(`${username}:${password}`)}`
}

interface TranscriptionTask {
  task_id: string
  status: 'processing' | 'completed' | 'error'
  progress: number
  result?: {
    docx_url: string
    audio_url: string
    transcript: string
  }
  error?: string
}

interface SavedTranscription {
  task_id: string
  docx_url: string
  audio_url: string
  created_at: string
  docx_size: number
  audio_size: number
}

export const Transcription = () => {
  const [activeTab, setActiveTab] = useState<'record' | 'upload' | 'history'>('record')
  const [savedTranscriptions, setSavedTranscriptions] = useState<SavedTranscription[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)

  // Recording state - теперь с браузерным распознаванием речи
  const [isRecording, setIsRecording] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const recognitionRef = useRef<any>(null)

  // Upload state
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  // Processing state
  const [currentTask, setCurrentTask] = useState<TranscriptionTask | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0) // 0-100
  const [processingStage, setProcessingStage] = useState<string>('') // текущий этап

  // Инициализация Web Speech API для записи с микрофона
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
        const text = event.results[i][0].transcript

        if (event.results[i].isFinal) {
          final += text + ' '
          console.log('✅ Final transcript:', text)
        } else {
          interim += text
          console.log('⏳ Interim transcript:', text)
        }
      }

      setInterimTranscript(interim)

      if (final) {
        setTranscript((prev) => prev + final)
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
      // Если запись активна, перезапускаем распознавание
      if (isRecording) {
        try {
          recognition.start()
        } catch (e) {
          console.log('Recognition restart failed:', e)
        }
      }
      setIsListening(false)
    }

    recognitionRef.current = recognition

    return () => {
      if (recognition) {
        recognition.stop()
      }
    }
  }, [isRecording])

  // Timer effect for recording
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isRecording])

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const startRecording = async () => {
    try {
      // Сбрасываем все предыдущие состояния
      setError(null)
      setTranscript('')
      setInterimTranscript('')
      setRecordingTime(0)

      // Запрашиваем доступ к микрофону (нужно для индикации)
      await navigator.mediaDevices.getUserMedia({ audio: true })

      // Запускаем распознавание
      if (recognitionRef.current) {
        recognitionRef.current.start()
        setIsRecording(true)
        setIsListening(true)
      }
    } catch (err) {
      setError('Не удалось получить доступ к микрофону. Проверьте разрешения.')
      console.error('Error starting recording:', err)
    }
  }

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
      setIsListening(false)
    }
  }

  const clearRecording = () => {
    setTranscript('')
    setInterimTranscript('')
    setRecordingTime(0)
  }

  const downloadTranscript = () => {
    if (!transcript) return

    const blob = new Blob([transcript], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transcript_${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const copyToClipboard = () => {
    if (!transcript) return

    navigator.clipboard.writeText(transcript).then(() => {
      // Можно показать toast уведомление
      console.log('Текст скопирован в буфер обмена')
    }).catch(err => {
      console.error('Ошибка при копировании:', err)
      setError('Не удалось скопировать текст')
    })
  }

  // Helper function to upload with progress tracking
  const uploadWithProgress = (url: string, formData: FormData): Promise<any> => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = Math.round((e.loaded / e.total) * 100)
          const loadedMB = (e.loaded / (1024 * 1024)).toFixed(1)
          const totalMB = (e.total / (1024 * 1024)).toFixed(1)
          setUploadProgress(percentComplete)
          setProcessingStage(`Загрузка файла: ${loadedMB} MB из ${totalMB} MB (${percentComplete}%)`)
        }
      })

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            setUploadProgress(100)
            setProcessingStage('Файл загружен, начинаем обработку...')
            resolve(response)
          } catch (e) {
            reject(new Error('Ошибка при разборе ответа: ' + e))
          }
        } else {
          // Пробуем получить детали ошибки из ответа
          try {
            const errorResponse = JSON.parse(xhr.responseText)
            reject(new Error(`HTTP ${xhr.status}: ${errorResponse.detail || xhr.statusText}`))
          } catch {
            reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`))
          }
        }
      })

      // Handle errors
      xhr.addEventListener('error', () => {
        reject(new Error('Ошибка сети'))
      })

      xhr.addEventListener('abort', () => {
        reject(new Error('Загрузка отменена'))
      })

      // Open and send request
      xhr.open('POST', url)
      xhr.setRequestHeader('Authorization', getAuthHeader())
      xhr.send(formData)
    })
  }

  const handleFileUpload = async (file: File) => {
    if (!file) return

    // Check file size (max 10GB)
    if (file.size > 10 * 1024 * 1024 * 1024) {
      setError('Файл слишком большой. Максимальный размер: 10GB')
      return
    }

    // Сбрасываем предыдущие результаты
    setCurrentTask(null)
    setUploadedFile(file)
    setIsProcessing(true)
    setError(null)
    setUploadProgress(0)
    setProcessingStage('Подготовка файла...')

    try {
      // Simple single-file upload (much faster than chunked upload)
      const formData = new FormData()
      formData.append('video', file)

      const data = await uploadWithProgress(
        `${API_URL}/api/v1/transcription/upload-video`,
        formData
      )

      setCurrentTask({
        task_id: data.task_id,
        status: 'processing',
        progress: 0
      })

      setUploadProgress(100)
      setProcessingStage('Транскрипция видео...')

      // Start polling for status
      pollTaskStatus(data.task_id)
    } catch (err: any) {
      const errorMessage = err?.message || 'Ошибка при загрузке файла'
      setError(errorMessage)
      setIsProcessing(false)
      setProcessingStage('')
      console.error('Error uploading file:', err)
    }
  }

  const pollTaskStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/transcription/status/${taskId}`, {
          headers: {
            'Authorization': getAuthHeader()
          }
        })

        if (!response.ok) throw new Error('Ошибка при проверке статуса')

        const data = await response.json()
        setCurrentTask(data)

        // Update processing stage from backend or use fallback
        if (data.status === 'processing') {
          // Use stage from backend if available, otherwise use progress-based fallback
          if (data.stage) {
            setProcessingStage(data.stage)
          } else if (data.progress < 20) {
            setProcessingStage('Извлечение аудио из видео...')
          } else if (data.progress < 40) {
            setProcessingStage('Конвертация аудио формата...')
          } else if (data.progress < 70) {
            setProcessingStage('Распознавание речи...')
          } else if (data.progress < 90) {
            setProcessingStage('Формирование текста...')
          } else {
            setProcessingStage('Финальная обработка...')
          }
        } else if (data.status === 'completed') {
          setProcessingStage(data.stage || 'Готово!')
          setUploadProgress(100)
        } else if (data.status === 'error') {
          setProcessingStage('Ошибка обработки')
        }

        if (data.status === 'completed' || data.status === 'error') {
          clearInterval(pollInterval)
          setIsProcessing(false)

          if (data.status === 'error') {
            setError(data.error || 'Произошла ошибка при обработке')
            setProcessingStage('')
          }
        }
      } catch (err) {
        console.error('Error polling status:', err)
        clearInterval(pollInterval)
        setIsProcessing(false)
        setProcessingStage('')
        setError('Ошибка при проверке статуса обработки')
      }
    }, 2000)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.type.startsWith('video/') || file.type.startsWith('audio/')) {
        handleFileUpload(file)
      } else {
        setError('Пожалуйста, загрузите видео или аудио файл')
      }
    }
  }

  const clearUpload = () => {
    setUploadedFile(null)
  }

  const downloadFile = async (url: string, filename: string) => {
    try {
      const response = await fetch(`${API_URL}${url}`, {
        headers: {
          'Authorization': getAuthHeader()
        }
      })
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(downloadUrl)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Error downloading file:', err)
      setError('Ошибка при скачивании файла')
    }
  }

  // Load saved transcriptions history
  const loadHistory = async () => {
    try {
      setLoadingHistory(true)
      const response = await fetch(`${API_URL}/api/v1/transcription/list`, {
        headers: {
          'Authorization': getAuthHeader()
        }
      })

      if (!response.ok) throw new Error('Failed to load history')

      const data = await response.json()
      setSavedTranscriptions(data.transcriptions || [])
    } catch (err) {
      console.error('Error loading history:', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  // Load history when history tab is selected
  useEffect(() => {
    if (activeTab === 'history') {
      loadHistory()
    }
  }, [activeTab])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-normal text-gray-900 mb-2">Транскрибация видео/аудио</h1>
        <p className="text-gray-600">Запись с микрофона или загрузка файла для транскрибации</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-lg mb-6">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('record')}
            className={`flex-1 px-6 py-4 text-center font-medium transition-all ${
              activeTab === 'record'
                ? 'text-purple-600 border-b-2 border-purple-600 bg-purple-50'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Mic className="w-5 h-5" />
              <span>Запись с микрофона</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 px-6 py-4 text-center font-medium transition-all ${
              activeTab === 'upload'
                ? 'text-purple-600 border-b-2 border-purple-600 bg-purple-50'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Upload className="w-5 h-5" />
              <span>Загрузка видео</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 px-6 py-4 text-center font-medium transition-all ${
              activeTab === 'history'
                ? 'text-purple-600 border-b-2 border-purple-600 bg-purple-50'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Clock className="w-5 h-5" />
              <span>История расшифровок</span>
            </div>
          </button>
        </div>

        <div className="p-8">
          {/* Record Tab */}
          {activeTab === 'record' && (
            <div className="space-y-6">
              {/* Recording Controls */}
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-8 border border-purple-200">
                <div className="flex flex-col items-center space-y-6">
                  {/* Timer */}
                  <div className="flex items-center gap-3 text-4xl font-light text-gray-900">
                    <Clock className="w-8 h-8 text-purple-600" />
                    {formatTime(recordingTime)}
                  </div>

                  {/* Status indicator */}
                  {isListening && (
                    <div className="flex items-center gap-2 px-4 py-2 bg-green-100 rounded-full">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-sm font-medium text-green-800">Слушаю...</span>
                    </div>
                  )}

                  {/* Recording Button */}
                  <div className="flex items-center gap-4">
                    {!isRecording ? (
                      <button
                        onClick={startRecording}
                        className="flex items-center gap-3 px-8 py-4 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-all shadow-lg hover:shadow-xl"
                      >
                        <PlayCircle className="w-6 h-6" />
                        <span className="text-lg font-medium">Начать запись</span>
                      </button>
                    ) : (
                      <button
                        onClick={stopRecording}
                        className="flex items-center gap-3 px-8 py-4 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-all shadow-lg hover:shadow-xl animate-pulse"
                      >
                        <StopCircle className="w-6 h-6" />
                        <span className="text-lg font-medium">Остановить</span>
                      </button>
                    )}

                    {transcript && !isRecording && (
                      <button
                        onClick={clearRecording}
                        className="flex items-center gap-2 px-6 py-4 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-all"
                      >
                        <Trash2 className="w-5 h-5" />
                        <span>Очистить</span>
                      </button>
                    )}
                  </div>

                  {/* Transcript Display */}
                  {(transcript || interimTranscript) && (
                    <div className="w-full max-w-4xl">
                      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-lg">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-medium text-gray-900">Распознанный текст</h3>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={copyToClipboard}
                              className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
                              title="Копировать в буфер обмена"
                            >
                              <Copy className="w-4 h-4" />
                              <span className="text-sm">Копировать</span>
                            </button>
                            <button
                              onClick={downloadTranscript}
                              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
                              title="Скачать как TXT"
                            >
                              <Download className="w-4 h-4" />
                              <span className="text-sm">Скачать TXT</span>
                            </button>
                          </div>
                        </div>
                        <div className="max-h-96 overflow-y-auto bg-gray-50 rounded-lg p-4">
                          <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">
                            {transcript}
                            {interimTranscript && (
                              <span className="text-gray-500 italic">{interimTranscript}</span>
                            )}
                          </p>
                        </div>
                        <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                          <span>Символов: {transcript.length}</span>
                          <span>Слов: ~{transcript.split(/\s+/).filter(Boolean).length}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Recording Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-blue-900">
                    <p className="font-medium mb-1">Как это работает</p>
                    <ul className="list-disc list-inside text-blue-700 space-y-1">
                      <li>Распознавание речи происходит прямо в браузере (без отправки на сервер)</li>
                      <li>Поддерживается только в Chrome и Edge браузерах</li>
                      <li>Текст распознаётся в реальном времени</li>
                      <li>Вы можете скачать результат как TXT файл</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <div className="space-y-6">
              {/* Drag & Drop Area */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                  isDragging
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-300 hover:border-gray-400 bg-gray-50'
                }`}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept="video/*,audio/*,.m4a,.mp4,.mp3,.wav,.webm,.flac,.ogg"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) handleFileUpload(file)
                  }}
                  disabled={isProcessing}
                />

                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center gap-4"
                >
                  <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center">
                    <FileVideo className="w-10 h-10 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-lg font-medium text-gray-900 mb-1">
                      Перетащите файл сюда или нажмите для выбора
                    </p>
                    <p className="text-sm text-gray-600">
                      Поддерживаются: MP4, M4A, MP3, WAV, WebM, FLAC, OGG (до 10GB)
                    </p>
                  </div>
                </label>
              </div>

              {/* Uploaded File Info */}
              {uploadedFile && (
                <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileVideo className="w-6 h-6 text-green-600" />
                      <div>
                        <p className="font-medium text-green-900">{uploadedFile.name}</p>
                        <p className="text-sm text-green-700">
                          {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={clearUpload}
                      disabled={isProcessing}
                      className="p-2 hover:bg-green-100 rounded-lg transition-all disabled:opacity-50"
                    >
                      <Trash2 className="w-5 h-5 text-green-700" />
                    </button>
                  </div>
                </div>
              )}

              {/* Upload Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-blue-900">
                    <p className="font-medium mb-1">Обработка файлов</p>
                    <ul className="list-disc list-inside text-blue-700 space-y-1">
                      <li>Поддерживаются форматы: MP4, AVI, MOV, MP3, WAV и др.</li>
                      <li>Максимальный размер файла: 10GB</li>
                      <li>Время обработки зависит от длительности файла</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-900">Ошибка</p>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Upload Progress */}
          {isProcessing && processingStage && !currentTask && (
            <div className="mt-6 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-6 shadow-lg">
              <div className="space-y-4">
                {/* Stage Text */}
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />
                  <span className="text-lg font-medium text-gray-900">{processingStage}</span>
                </div>

                {/* Upload Progress Bar */}
                {uploadProgress > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-700">Прогресс загрузки</span>
                      <span className="font-medium text-purple-600">{uploadProgress}%</span>
                    </div>
                    <div className="h-3 bg-white rounded-full overflow-hidden shadow-inner">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-300 ease-out"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Processing Status */}
          {currentTask && (
            <div className="mt-6 bg-white border border-gray-200 rounded-xl p-6 shadow-lg">
              <div className="space-y-4">
                {/* Status Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {currentTask.status === 'processing' && (
                      <>
                        <Loader2 className="w-6 h-6 text-purple-600 animate-spin" />
                        <div className="flex flex-col">
                          <span className="text-lg font-medium text-gray-900">Обработка...</span>
                          {processingStage && uploadProgress === 100 && (
                            <span className="text-sm text-gray-600">{processingStage}</span>
                          )}
                        </div>
                      </>
                    )}
                    {currentTask.status === 'completed' && (
                      <>
                        <CheckCircle2 className="w-6 h-6 text-green-600" />
                        <span className="text-lg font-medium text-green-900">Готово!</span>
                      </>
                    )}
                    {currentTask.status === 'error' && (
                      <>
                        <AlertCircle className="w-6 h-6 text-red-600" />
                        <span className="text-lg font-medium text-red-900">Ошибка</span>
                      </>
                    )}
                  </div>
                  <span className="text-sm text-gray-600">{currentTask.progress}%</span>
                </div>

                {/* Progress Bar */}
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      currentTask.status === 'completed'
                        ? 'bg-gradient-to-r from-green-500 to-green-600'
                        : currentTask.status === 'error'
                        ? 'bg-gradient-to-r from-red-500 to-red-600'
                        : 'bg-gradient-to-r from-purple-500 to-purple-600'
                    }`}
                    style={{ width: `${currentTask.progress}%` }}
                  />
                </div>

                {/* Download Buttons */}
                {currentTask.status === 'completed' && currentTask.result && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                    <button
                      onClick={() => downloadFile(currentTask.result!.docx_url, 'transcription.docx')}
                      className="flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-all shadow-md hover:shadow-lg"
                    >
                      <Download className="w-5 h-5" />
                      <span>Скачать DOCX</span>
                    </button>
                    <button
                      onClick={() => downloadFile(currentTask.result!.audio_url, 'audio.mp3')}
                      className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg"
                    >
                      <FileAudio className="w-5 h-5" />
                      <span>Скачать аудио</span>
                    </button>
                  </div>
                )}

                {/* Transcript Preview */}
                {currentTask.status === 'completed' && currentTask.result && (
                  <div className="pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-900 mb-2">Предпросмотр транскрипции:</p>
                    <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {currentTask.result.transcript.slice(0, 500)}
                        {currentTask.result.transcript.length > 500 && '...'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <div className="space-y-6">
              {loadingHistory ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                </div>
              ) : savedTranscriptions.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">Нет сохраненных транскрипций</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {savedTranscriptions.map((item) => (
                    <div
                      key={item.task_id}
                      className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-all"
                    >
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <FileVideo className="w-5 h-5 text-purple-600" />
                          <span className="font-medium text-gray-900">Транскрипция</span>
                        </div>
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                      </div>

                      {/* Date */}
                      <p className="text-sm text-gray-600 mb-4">
                        {new Date(item.created_at).toLocaleDateString('ru-RU', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>

                      {/* File Sizes */}
                      <div className="flex gap-4 text-sm text-gray-600 mb-4">
                        <span>Текст: {(item.docx_size / 1024).toFixed(1)} KB</span>
                        <span>Аудио: {(item.audio_size / 1024 / 1024).toFixed(1)} MB</span>
                      </div>

                      {/* Download Buttons */}
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={() => downloadFile(item.docx_url, `transcript_${item.task_id.slice(0, 8)}.docx`)}
                          className="flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                        >
                          <Download className="w-4 h-4" />
                          <span>Текст</span>
                        </button>
                        <button
                          onClick={() => downloadFile(item.audio_url, `audio_${item.task_id.slice(0, 8)}.mp3`)}
                          className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                        >
                          <FileAudio className="w-4 h-4" />
                          <span>Аудио</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
