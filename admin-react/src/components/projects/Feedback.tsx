import React, { useState, useEffect } from 'react'
import { MessageSquare, X, Plus, Star, ThumbsUp, ThumbsDown, Send, Calendar, User, Tag } from 'lucide-react'

interface FeedbackProps {
  projectId: number
  onClose: () => void
}

interface FeedbackItem {
  id: number
  clientName: string
  clientEmail: string
  date: string
  rating: number
  category: 'quality' | 'communication' | 'timeline' | 'budget' | 'support' | 'overall'
  title: string
  message: string
  sentiment: 'positive' | 'neutral' | 'negative'
  status: 'new' | 'reviewed' | 'responded' | 'archived'
  response?: string
  respondedBy?: string
  respondedAt?: string
  tags: string[]
}

const Feedback: React.FC<FeedbackProps> = ({ projectId, onClose }) => {
  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null)
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterSentiment, setFilterSentiment] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [responseText, setResponseText] = useState('')

  const [newFeedback, setNewFeedback] = useState({
    clientName: '',
    clientEmail: '',
    date: new Date().toISOString().slice(0, 10),
    rating: 5,
    category: 'overall' as FeedbackItem['category'],
    title: '',
    message: '',
    tags: [] as string[],
  })

  const [newTag, setNewTag] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = 'unset' }
  }, [])

  useEffect(() => {
    fetchFeedbacks()
  }, [projectId])

  const fetchFeedbacks = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://147.45.215.199:8001/api/projects/${projectId}/feedback`,
        {
          headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setFeedbacks(data)
      } else {
        setFeedbacks([
          {
            id: 1,
            clientName: 'Иван Сергеев',
            clientEmail: 'ivan@example.com',
            date: '2024-03-15',
            rating: 5,
            category: 'overall',
            title: 'Отличная работа команды!',
            message: 'Проект выполнен в срок и даже раньше. Качество работы на высоком уровне. Особенно хочу отметить профессионализм команды и оперативность в решении возникающих вопросов.',
            sentiment: 'positive',
            status: 'responded',
            response: 'Спасибо за теплые слова! Было приятно работать с вами над этим проектом.',
            respondedBy: 'Мария Смирнова',
            respondedAt: '2024-03-16',
            tags: ['профессионализм', 'сроки'],
          },
          {
            id: 2,
            clientName: 'Ольга Петрова',
            clientEmail: 'olga@example.com',
            date: '2024-03-10',
            rating: 4,
            category: 'communication',
            title: 'Хорошая коммуникация',
            message: 'Команда всегда на связи, оперативно отвечает на вопросы. Единственное замечание — хотелось бы более частых обновлений по ходу работы.',
            sentiment: 'positive',
            status: 'reviewed',
            tags: ['коммуникация'],
          },
          {
            id: 3,
            clientName: 'Дмитрий Козлов',
            clientEmail: 'dmitry@example.com',
            date: '2024-03-05',
            rating: 3,
            category: 'timeline',
            title: 'Были задержки',
            message: 'Проект затянулся на 2 недели. Хотя в итоге все сделано качественно, хотелось бы более точного соблюдения сроков.',
            sentiment: 'neutral',
            status: 'responded',
            response: 'Приносим извинения за задержку. Она была вызвана необходимостью дополнительного тестирования. В будущем будем более точно планировать сроки.',
            respondedBy: 'Иван Петров',
            respondedAt: '2024-03-06',
            tags: ['сроки', 'качество'],
          },
          {
            id: 4,
            clientName: 'Анна Волкова',
            clientEmail: 'anna@example.com',
            date: '2024-03-01',
            rating: 5,
            category: 'quality',
            title: 'Превосходное качество',
            message: 'Работа выполнена безупречно! Все требования учтены, дизайн превзошел ожидания. Буду рекомендовать вас своим партнерам.',
            sentiment: 'positive',
            status: 'responded',
            response: 'Огромное спасибо! Рады, что вы остались довольны результатом.',
            respondedBy: 'Мария Смирнова',
            respondedAt: '2024-03-02',
            tags: ['качество', 'дизайн'],
          },
          {
            id: 5,
            clientName: 'Сергей Михайлов',
            clientEmail: 'sergey@example.com',
            date: '2024-02-28',
            rating: 2,
            category: 'budget',
            title: 'Превышение бюджета',
            message: 'Итоговая стоимость оказалась выше первоначальной оценки на 30%. Хотелось бы более точной оценки на старте проекта.',
            sentiment: 'negative',
            status: 'new',
            tags: ['бюджет'],
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching feedbacks:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateSentiment = (rating: number): FeedbackItem['sentiment'] => {
    if (rating >= 4) return 'positive'
    if (rating >= 3) return 'neutral'
    return 'negative'
  }

  const handleAddFeedback = () => {
    if (!newFeedback.clientName || !newFeedback.title || !newFeedback.message) {
      alert('Заполните обязательные поля')
      return
    }

    const feedback: FeedbackItem = {
      id: Date.now(),
      clientName: newFeedback.clientName,
      clientEmail: newFeedback.clientEmail,
      date: newFeedback.date,
      rating: newFeedback.rating,
      category: newFeedback.category,
      title: newFeedback.title,
      message: newFeedback.message,
      sentiment: calculateSentiment(newFeedback.rating),
      status: 'new',
      tags: newFeedback.tags,
    }

    setFeedbacks([feedback, ...feedbacks])
    setShowAddModal(false)
    setNewFeedback({
      clientName: '',
      clientEmail: '',
      date: new Date().toISOString().slice(0, 10),
      rating: 5,
      category: 'overall',
      title: '',
      message: '',
      tags: [],
    })
  }

  const handleAddTag = () => {
    if (newTag && !newFeedback.tags.includes(newTag)) {
      setNewFeedback({ ...newFeedback, tags: [...newFeedback.tags, newTag] })
      setNewTag('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    setNewFeedback({ ...newFeedback, tags: newFeedback.tags.filter((t) => t !== tag) })
  }

  const handleRespond = () => {
    if (!selectedFeedback || !responseText) return

    setFeedbacks(
      feedbacks.map((fb) =>
        fb.id === selectedFeedback.id
          ? {
              ...fb,
              status: 'responded',
              response: responseText,
              respondedBy: 'Текущий пользователь',
              respondedAt: new Date().toISOString().slice(0, 10),
            }
          : fb
      )
    )

    setResponseText('')
    setSelectedFeedback(null)
  }

  const handleMarkAsReviewed = (feedbackId: number) => {
    setFeedbacks(
      feedbacks.map((fb) =>
        fb.id === feedbackId ? { ...fb, status: 'reviewed' as const } : fb
      )
    )
  }

  const getCategoryIcon = (category: string) => {
    const icons = {
      quality: '⭐',
      communication: '💬',
      timeline: '⏰',
      budget: '💰',
      support: '🤝',
      overall: '📊',
    }
    return icons[category as keyof typeof icons] || '📋'
  }

  const getCategoryLabel = (category: string) => {
    const labels = {
      quality: 'Качество',
      communication: 'Коммуникация',
      timeline: 'Сроки',
      budget: 'Бюджет',
      support: 'Поддержка',
      overall: 'Общее впечатление',
    }
    return labels[category as keyof typeof labels] || category
  }

  const getSentimentColor = (sentiment: string) => {
    const colors = {
      positive: 'text-green-600 bg-green-100',
      neutral: 'text-yellow-600 bg-yellow-100',
      negative: 'text-red-600 bg-red-100',
    }
    return colors[sentiment as keyof typeof colors] || 'text-gray-600 bg-gray-100'
  }

  const getSentimentIcon = (sentiment: string) => {
    const icons = {
      positive: <ThumbsUp className="w-5 h-5" />,
      neutral: <MessageSquare className="w-5 h-5" />,
      negative: <ThumbsDown className="w-5 h-5" />,
    }
    return icons[sentiment as keyof typeof icons] || <MessageSquare className="w-5 h-5" />
  }

  const getStatusColor = (status: string) => {
    const colors = {
      new: 'bg-blue-100 text-blue-700',
      reviewed: 'bg-purple-100 text-purple-700',
      responded: 'bg-green-100 text-green-700',
      archived: 'bg-gray-100 text-gray-700',
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  const getStatusLabel = (status: string) => {
    const labels = {
      new: 'Новый',
      reviewed: 'Просмотрен',
      responded: 'Отвечен',
      archived: 'Архив',
    }
    return labels[status as keyof typeof labels] || status
  }

  const filteredFeedbacks = feedbacks.filter((feedback) => {
    const matchesCategory = filterCategory === 'all' || feedback.category === filterCategory
    const matchesSentiment = filterSentiment === 'all' || feedback.sentiment === filterSentiment
    const matchesStatus = filterStatus === 'all' || feedback.status === filterStatus
    return matchesCategory && matchesSentiment && matchesStatus
  })

  const averageRating = feedbacks.length > 0
    ? feedbacks.reduce((sum, fb) => sum + fb.rating, 0) / feedbacks.length
    : 0

  const sentimentStats = {
    positive: feedbacks.filter((fb) => fb.sentiment === 'positive').length,
    neutral: feedbacks.filter((fb) => fb.sentiment === 'neutral').length,
    negative: feedbacks.filter((fb) => fb.sentiment === 'negative').length,
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка отзывов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Отзывы клиентов</h2>
              <p className="text-purple-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 border-b bg-gray-50">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <Star className="w-8 h-8 text-yellow-500" />
                <div>
                  <p className="text-sm text-gray-500">Средняя оценка</p>
                  <p className="text-2xl font-bold text-gray-900">{averageRating.toFixed(1)} / 5</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <ThumbsUp className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-sm text-gray-500">Положительные</p>
                  <p className="text-2xl font-bold text-green-700">{sentimentStats.positive}</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <MessageSquare className="w-8 h-8 text-yellow-600" />
                <div>
                  <p className="text-sm text-gray-500">Нейтральные</p>
                  <p className="text-2xl font-bold text-yellow-700">{sentimentStats.neutral}</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <ThumbsDown className="w-8 h-8 text-red-600" />
                <div>
                  <p className="text-sm text-gray-500">Отрицательные</p>
                  <p className="text-2xl font-bold text-red-700">{sentimentStats.negative}</p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setShowAddModal(true)}
              className="bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2 font-medium"
            >
              <Plus className="w-5 h-5" />
              Добавить отзыв
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">Все категории</option>
              <option value="quality">Качество</option>
              <option value="communication">Коммуникация</option>
              <option value="timeline">Сроки</option>
              <option value="budget">Бюджет</option>
              <option value="support">Поддержка</option>
              <option value="overall">Общее впечатление</option>
            </select>

            <select
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">Все настроения</option>
              <option value="positive">Положительные</option>
              <option value="neutral">Нейтральные</option>
              <option value="negative">Отрицательные</option>
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">Все статусы</option>
              <option value="new">Новые</option>
              <option value="reviewed">Просмотренные</option>
              <option value="responded">Отвеченные</option>
              <option value="archived">Архивные</option>
            </select>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {filteredFeedbacks.map((feedback) => (
              <div
                key={feedback.id}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg ${getSentimentColor(feedback.sentiment)}`}>
                    {getSentimentIcon(feedback.sentiment)}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-1">{feedback.title}</h3>
                        <div className="flex items-center gap-3 text-sm">
                          <div className="flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <Star
                                key={star}
                                className={`w-4 h-4 ${
                                  star <= feedback.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                                }`}
                              />
                            ))}
                          </div>
                          <span className="text-2xl">{getCategoryIcon(feedback.category)}</span>
                          <span className="text-gray-600">{getCategoryLabel(feedback.category)}</span>
                        </div>
                      </div>
                      <span className={`text-xs px-3 py-1 rounded-full ${getStatusColor(feedback.status)}`}>
                        {getStatusLabel(feedback.status)}
                      </span>
                    </div>

                    <p className="text-gray-700 mb-3">{feedback.message}</p>

                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4" />
                        <span>{feedback.clientName}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(feedback.date).toLocaleDateString('ru-RU')}</span>
                      </div>
                    </div>

                    {feedback.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {feedback.tags.map((tag, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {feedback.response && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-3">
                        <p className="text-sm font-medium text-green-800 mb-2">Ответ:</p>
                        <p className="text-sm text-green-700 mb-2">{feedback.response}</p>
                        <p className="text-xs text-green-600">
                          {feedback.respondedBy} • {new Date(feedback.respondedAt!).toLocaleDateString('ru-RU')}
                        </p>
                      </div>
                    )}

                    <div className="flex gap-2 mt-4">
                      {feedback.status === 'new' && (
                        <>
                          <button
                            onClick={() => setSelectedFeedback(feedback)}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                          >
                            <Send className="w-4 h-4" />
                            Ответить
                          </button>
                          <button
                            onClick={() => handleMarkAsReviewed(feedback.id)}
                            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                          >
                            Отметить прочитанным
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredFeedbacks.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Отзывы не найдены</p>
            </div>
          )}
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 flex justify-between items-center">
              <h3 className="text-2xl font-bold">Добавить отзыв</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Клиент *</label>
                    <input
                      type="text"
                      value={newFeedback.clientName}
                      onChange={(e) => setNewFeedback({ ...newFeedback, clientName: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input
                      type="email"
                      value={newFeedback.clientEmail}
                      onChange={(e) => setNewFeedback({ ...newFeedback, clientEmail: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Дата</label>
                    <input
                      type="date"
                      value={newFeedback.date}
                      onChange={(e) => setNewFeedback({ ...newFeedback, date: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Категория</label>
                    <select
                      value={newFeedback.category}
                      onChange={(e) => setNewFeedback({ ...newFeedback, category: e.target.value as FeedbackItem['category'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="overall">Общее впечатление</option>
                      <option value="quality">Качество</option>
                      <option value="communication">Коммуникация</option>
                      <option value="timeline">Сроки</option>
                      <option value="budget">Бюджет</option>
                      <option value="support">Поддержка</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Оценка *</label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setNewFeedback({ ...newFeedback, rating: star })}
                        className="transition-transform hover:scale-110"
                      >
                        <Star
                          className={`w-10 h-10 ${
                            star <= newFeedback.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Заголовок *</label>
                  <input
                    type="text"
                    value={newFeedback.title}
                    onChange={(e) => setNewFeedback({ ...newFeedback, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Отзыв *</label>
                  <textarea
                    value={newFeedback.message}
                    onChange={(e) => setNewFeedback({ ...newFeedback, message: e.target.value })}
                    rows={5}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Теги</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                      placeholder="Добавить тег (Enter)"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {newFeedback.tags.map((tag, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 text-sm px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                        {tag}
                        <button onClick={() => handleRemoveTag(tag)} className="hover:text-purple-900">
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t flex gap-3 justify-end">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleAddFeedback}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Добавить
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 flex justify-between items-center">
              <h3 className="text-2xl font-bold">Ответить на отзыв</h3>
              <button
                onClick={() => setSelectedFeedback(null)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                <h4 className="font-bold text-gray-900 mb-2">{selectedFeedback.title}</h4>
                <p className="text-gray-700 mb-2">{selectedFeedback.message}</p>
                <p className="text-sm text-gray-500">— {selectedFeedback.clientName}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ваш ответ</label>
                <textarea
                  value={responseText}
                  onChange={(e) => setResponseText(e.target.value)}
                  rows={5}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Введите ответ клиенту..."
                />
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t flex gap-3 justify-end">
              <button
                onClick={() => setSelectedFeedback(null)}
                className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleRespond}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                <Send className="w-5 h-5" />
                Отправить ответ
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Feedback
