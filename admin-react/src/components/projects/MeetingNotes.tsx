import React, { useState, useEffect } from 'react'
import { Video, Calendar, Users, FileText, Clock, Plus, X, Edit2, Trash2, CheckCircle, Circle, Link as LinkIcon } from 'lucide-react'

interface MeetingNotesProps {
  projectId: number
  onClose: () => void
}

interface Meeting {
  id: number
  title: string
  date: string
  duration: number
  type: 'internal' | 'client' | 'planning' | 'review' | 'standup'
  participants: string[]
  agenda: string[]
  notes: string
  actionItems: ActionItem[]
  recordingUrl?: string
  status: 'scheduled' | 'completed' | 'cancelled'
  createdBy: string
}

interface ActionItem {
  id: number
  description: string
  assignee: string
  dueDate: string
  completed: boolean
}

const MeetingNotes: React.FC<MeetingNotesProps> = ({ projectId, onClose }) => {
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null)

  const [newMeeting, setNewMeeting] = useState({
    title: '',
    date: new Date().toISOString().slice(0, 16),
    duration: 60,
    type: 'internal' as Meeting['type'],
    participants: [] as string[],
    agenda: [] as string[],
    notes: '',
  })

  const [newParticipant, setNewParticipant] = useState('')
  const [newAgendaItem, setNewAgendaItem] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchMeetings()
  }, [projectId])

  const fetchMeetings = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/meetings`, {
        headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
      })
      if (response.ok) {
        const data = await response.json()
        setMeetings(data)
      } else {
        setMeetings([
          {
            id: 1,
            title: 'Планирование спринта',
            date: '2024-03-18T10:00:00',
            duration: 120,
            type: 'planning',
            participants: ['Алексей Иванов', 'Мария Петрова', 'Дмитрий Смирнов'],
            agenda: ['Обзор бэклога', 'Оценка задач', 'Распределение задач', 'Q&A'],
            notes: 'Обсудили приоритеты на следующий спринт. Решили сфокусироваться на новом функционале API.',
            actionItems: [
              {
                id: 1,
                description: 'Создать спецификацию API endpoints',
                assignee: 'Дмитрий Смирнов',
                dueDate: '2024-03-20',
                completed: false,
              },
              {
                id: 2,
                description: 'Подготовить макеты новых экранов',
                assignee: 'Мария Петрова',
                dueDate: '2024-03-22',
                completed: true,
              },
            ],
            status: 'completed',
            createdBy: 'Алексей Иванов',
          },
          {
            id: 2,
            title: 'Демонстрация для клиента',
            date: '2024-03-20T14:00:00',
            duration: 60,
            type: 'client',
            participants: ['Алексей Иванов', 'Иван Петров (клиент)', 'Ольга Сидорова (клиент)'],
            agenda: ['Демо новых функций', 'Обратная связь', 'Обсуждение следующих этапов'],
            notes: 'Клиент доволен прогрессом. Запросили несколько дополнительных функций.',
            actionItems: [
              {
                id: 3,
                description: 'Уточнить требования к экспорту данных',
                assignee: 'Алексей Иванов',
                dueDate: '2024-03-22',
                completed: false,
              },
            ],
            recordingUrl: 'https://example.com/recording/123',
            status: 'completed',
            createdBy: 'Алексей Иванов',
          },
          {
            id: 3,
            title: 'Daily Standup',
            date: '2024-03-21T09:00:00',
            duration: 15,
            type: 'standup',
            participants: ['Алексей Иванов', 'Мария Петрова', 'Дмитрий Смирнов', 'Елена Козлова'],
            agenda: ['Что сделано вчера', 'Что планируется сегодня', 'Есть ли блокеры'],
            notes: 'Все работают по плану. Елена сообщила о проблеме с тестовой средой.',
            actionItems: [
              {
                id: 4,
                description: 'Исправить конфигурацию тестовой среды',
                assignee: 'Дмитрий Смирнов',
                dueDate: '2024-03-21',
                completed: false,
              },
            ],
            status: 'completed',
            createdBy: 'Алексей Иванов',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching meetings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddMeeting = async () => {
    if (!newMeeting.title) {
      alert('Введите название встречи')
      return
    }

    const meetingData: Meeting = {
      ...newMeeting,
      id: Date.now(),
      actionItems: [],
      status: 'scheduled',
      createdBy: 'Текущий пользователь',
    }

    setMeetings([...meetings, meetingData])
    setShowAddModal(false)
    setNewMeeting({
      title: '',
      date: new Date().toISOString().slice(0, 16),
      duration: 60,
      type: 'internal',
      participants: [],
      agenda: [],
      notes: '',
    })
  }

  const handleDeleteMeeting = (meetingId: number) => {
    if (!confirm('Удалить встречу?')) return
    setMeetings(meetings.filter((m) => m.id !== meetingId))
  }

  const handleToggleActionItem = (meetingId: number, actionItemId: number) => {
    setMeetings(
      meetings.map((m) => {
        if (m.id === meetingId) {
          return {
            ...m,
            actionItems: m.actionItems.map((ai) => (ai.id === actionItemId ? { ...ai, completed: !ai.completed } : ai)),
          }
        }
        return m
      })
    )
  }

  const getMeetingTypeBadge = (type: string) => {
    const badges = {
      internal: { label: 'Внутренняя', color: 'bg-blue-100 text-blue-800' },
      client: { label: 'С клиентом', color: 'bg-purple-100 text-purple-800' },
      planning: { label: 'Планирование', color: 'bg-green-100 text-green-800' },
      review: { label: 'Ревью', color: 'bg-yellow-100 text-yellow-800' },
      standup: { label: 'Standup', color: 'bg-cyan-100 text-cyan-800' },
    }
    return badges[type as keyof typeof badges] || badges.internal
  }

  const stats = {
    total: meetings.length,
    completed: meetings.filter((m) => m.status === 'completed').length,
    upcoming: meetings.filter((m) => m.status === 'scheduled').length,
    totalActionItems: meetings.reduce((sum, m) => sum + m.actionItems.length, 0),
    completedActionItems: meetings.reduce((sum, m) => sum + m.actionItems.filter((ai) => ai.completed).length, 0),
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка встреч...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Video className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Протоколы встреч</h2>
              <p className="text-purple-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-5 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Video className="w-4 h-4" />
              <span>Всего</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <CheckCircle className="w-4 h-4" />
              <span>Проведено</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Calendar className="w-4 h-4" />
              <span>Запланировано</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.upcoming}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <FileText className="w-4 h-4" />
              <span>Action Items</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalActionItems}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <CheckCircle className="w-4 h-4" />
              <span>Выполнено</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">{stats.completedActionItems}</div>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex justify-between items-center p-6 bg-white border-b">
          <h3 className="text-lg font-semibold text-gray-900">Список встреч</h3>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить встречу
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {meetings.map((meeting) => {
              const typeBadge = getMeetingTypeBadge(meeting.type)
              return (
                <div key={meeting.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-4 flex-1">
                      <Video className="w-8 h-8 text-purple-600 flex-shrink-0 mt-1" />
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-bold text-xl text-gray-900">{meeting.title}</h3>
                          <span className={`text-xs px-2 py-1 rounded-full ${typeBadge.color}`}>{typeBadge.label}</span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>{new Date(meeting.date).toLocaleString('ru-RU')}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            <span>{meeting.duration} мин</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            <span>{meeting.participants.length} участников</span>
                          </div>
                        </div>
                        {meeting.recordingUrl && (
                          <a
                            href={meeting.recordingUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-sm text-purple-600 hover:text-purple-700"
                          >
                            <LinkIcon className="w-4 h-4" />
                            Ссылка на запись
                          </a>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setSelectedMeeting(meeting)}
                        className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                      >
                        <Edit2 className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDeleteMeeting(meeting.id)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {meeting.agenda.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Повестка:</p>
                      <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                        {meeting.agenda.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {meeting.notes && (
                    <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-700 mb-2">Заметки:</p>
                      <p className="text-sm text-gray-600 whitespace-pre-wrap">{meeting.notes}</p>
                    </div>
                  )}

                  {meeting.actionItems.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Action Items:</p>
                      <div className="space-y-2">
                        {meeting.actionItems.map((item) => (
                          <div key={item.id} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                            <button
                              onClick={() => handleToggleActionItem(meeting.id, item.id)}
                              className="mt-0.5"
                            >
                              {item.completed ? (
                                <CheckCircle className="w-5 h-5 text-green-600" />
                              ) : (
                                <Circle className="w-5 h-5 text-gray-400" />
                              )}
                            </button>
                            <div className="flex-1">
                              <p className={`text-sm ${item.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                {item.description}
                              </p>
                              <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                                <span>Исполнитель: {item.assignee}</span>
                                <span>•</span>
                                <span>Срок: {new Date(item.dueDate).toLocaleDateString('ru-RU')}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="mt-4 pt-4 border-t text-xs text-gray-500">
                    Создано: {meeting.createdBy} • {new Date(meeting.date).toLocaleDateString('ru-RU')}
                  </div>
                </div>
              )
            })}
          </div>

          {meetings.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Video className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Нет встреч</p>
            </div>
          )}
        </div>

        {/* Add Modal */}
        {showAddModal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[80vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">Создать встречу</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название *</label>
                  <input
                    type="text"
                    value={newMeeting.title}
                    onChange={(e) => setNewMeeting({ ...newMeeting, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Дата и время</label>
                    <input
                      type="datetime-local"
                      value={newMeeting.date}
                      onChange={(e) => setNewMeeting({ ...newMeeting, date: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Длительность (мин)</label>
                    <input
                      type="number"
                      value={newMeeting.duration}
                      onChange={(e) => setNewMeeting({ ...newMeeting, duration: parseInt(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Тип</label>
                  <select
                    value={newMeeting.type}
                    onChange={(e) => setNewMeeting({ ...newMeeting, type: e.target.value as Meeting['type'] })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="internal">Внутренняя</option>
                    <option value="client">С клиентом</option>
                    <option value="planning">Планирование</option>
                    <option value="review">Ревью</option>
                    <option value="standup">Standup</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Участники</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newParticipant}
                      onChange={(e) => setNewParticipant(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newParticipant) {
                          setNewMeeting({ ...newMeeting, participants: [...newMeeting.participants, newParticipant] })
                          setNewParticipant('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Добавить участника (Enter)"
                    />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {newMeeting.participants.map((p, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 text-sm px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                        {p}
                        <button
                          onClick={() =>
                            setNewMeeting({
                              ...newMeeting,
                              participants: newMeeting.participants.filter((_, i) => i !== idx),
                            })
                          }
                          className="hover:text-purple-900"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Повестка</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newAgendaItem}
                      onChange={(e) => setNewAgendaItem(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newAgendaItem) {
                          setNewMeeting({ ...newMeeting, agenda: [...newMeeting.agenda, newAgendaItem] })
                          setNewAgendaItem('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Добавить пункт повестки (Enter)"
                    />
                  </div>
                  <ol className="list-decimal list-inside space-y-1">
                    {newMeeting.agenda.map((item, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-center justify-between bg-gray-50 p-2 rounded">
                        <span>{item}</span>
                        <button
                          onClick={() => setNewMeeting({ ...newMeeting, agenda: newMeeting.agenda.filter((_, i) => i !== idx) })}
                          className="text-red-600 hover:text-red-800"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Заметки</label>
                  <textarea
                    value={newMeeting.notes}
                    onChange={(e) => setNewMeeting({ ...newMeeting, notes: e.target.value })}
                    rows={5}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Заметки о встрече..."
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddMeeting}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Создать
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MeetingNotes
