import React, { useState, useEffect } from 'react'
import {
  Clock,
  Play,
  Pause,
  Square,
  Calendar,
  BarChart2,
  Download,
  Filter,
  Search,
  Edit2,
  Trash2,
  X,
  TrendingUp,
  Users,
  DollarSign,
} from 'lucide-react'

interface TimeTrackingProps {
  projectId: number
  onClose: () => void
}

interface TimeEntry {
  id: number
  userId: number
  userName: string
  taskId?: number
  taskName?: string
  description: string
  startTime: string
  endTime: string | null
  duration: number // в минутах
  billable: boolean
  hourlyRate: number
  status: 'running' | 'stopped'
  createdAt: string
}

interface Timer {
  userId: number
  userName: string
  taskId?: number
  taskName?: string
  description: string
  startTime: string
  billable: boolean
  hourlyRate: number
}

interface TimeStats {
  totalHours: number
  billableHours: number
  nonBillableHours: number
  totalAmount: number
  entriesCount: number
  avgHourlyRate: number
  byUser: { [key: string]: number }
  byTask: { [key: string]: number }
  byDay: { [key: string]: number }
}

const TimeTracking: React.FC<TimeTrackingProps> = ({ projectId, onClose }) => {
  const [entries, setEntries] = useState<TimeEntry[]>([])
  const [timer, setTimer] = useState<Timer | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterUser, setFilterUser] = useState<string>('all')
  const [filterBillable, setFilterBillable] = useState<string>('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [editingEntry, setEditingEntry] = useState<TimeEntry | null>(null)
  const [activeTab, setActiveTab] = useState<'entries' | 'timer' | 'reports'>('entries')
  const [currentTime, setCurrentTime] = useState(new Date())

  // Новая запись времени
  const [newEntry, setNewEntry] = useState({
    description: '',
    taskId: 0,
    startTime: new Date().toISOString().slice(0, 16),
    endTime: new Date().toISOString().slice(0, 16),
    billable: true,
    hourlyRate: 50,
  })

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchEntries()
    const interval = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(interval)
  }, [projectId])

  const fetchEntries = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/time-entries`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setEntries(data.entries || [])
        setTimer(data.activeTimer || null)
      } else {
        // Mock data
        setEntries([
          {
            id: 1,
            userId: 1,
            userName: 'Алексей Иванов',
            taskId: 101,
            taskName: 'Разработка главной страницы',
            description: 'Верстка и интеграция с API',
            startTime: '2024-03-01T09:00:00',
            endTime: '2024-03-01T12:30:00',
            duration: 210,
            billable: true,
            hourlyRate: 60,
            status: 'stopped',
            createdAt: '2024-03-01T09:00:00',
          },
          {
            id: 2,
            userId: 2,
            userName: 'Мария Петрова',
            taskId: 102,
            taskName: 'Дизайн UI компонентов',
            description: 'Создание библиотеки компонентов',
            startTime: '2024-03-01T10:00:00',
            endTime: '2024-03-01T13:00:00',
            duration: 180,
            billable: true,
            hourlyRate: 55,
            status: 'stopped',
            createdAt: '2024-03-01T10:00:00',
          },
          {
            id: 3,
            userId: 1,
            userName: 'Алексей Иванов',
            taskId: 103,
            taskName: 'Code Review',
            description: 'Ревью pull requests',
            startTime: '2024-03-01T14:00:00',
            endTime: '2024-03-01T15:30:00',
            duration: 90,
            billable: false,
            hourlyRate: 60,
            status: 'stopped',
            createdAt: '2024-03-01T14:00:00',
          },
          {
            id: 4,
            userId: 3,
            userName: 'Дмитрий Смирнов',
            taskId: 104,
            taskName: 'Настройка CI/CD',
            description: 'Конфигурация GitHub Actions',
            startTime: '2024-03-02T09:00:00',
            endTime: '2024-03-02T11:45:00',
            duration: 165,
            billable: true,
            hourlyRate: 70,
            status: 'stopped',
            createdAt: '2024-03-02T09:00:00',
          },
          {
            id: 5,
            userId: 2,
            userName: 'Мария Петрова',
            description: 'Встреча с клиентом',
            startTime: '2024-03-02T14:00:00',
            endTime: '2024-03-02T15:00:00',
            duration: 60,
            billable: false,
            hourlyRate: 55,
            status: 'stopped',
            createdAt: '2024-03-02T14:00:00',
          },
        ])
        setTimer(null)
      }
    } catch (error) {
      console.error('Error fetching time entries:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStartTimer = async () => {
    if (!newEntry.description) {
      alert('Введите описание задачи')
      return
    }

    const timerData: Timer = {
      userId: 1, // Current user
      userName: 'Текущий пользователь',
      taskId: newEntry.taskId || undefined,
      description: newEntry.description,
      startTime: new Date().toISOString(),
      billable: newEntry.billable,
      hourlyRate: newEntry.hourlyRate,
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/timer/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(timerData),
      })

      if (response.ok) {
        const data = await response.json()
        setTimer(data)
      } else {
        setTimer(timerData)
      }

      setNewEntry({ ...newEntry, description: '' })
    } catch (error) {
      console.error('Error starting timer:', error)
    }
  }

  const handleStopTimer = async () => {
    if (!timer) return

    const duration = Math.floor((new Date().getTime() - new Date(timer.startTime).getTime()) / 1000 / 60)

    const entryData: TimeEntry = {
      id: Date.now(),
      userId: timer.userId,
      userName: timer.userName,
      taskId: timer.taskId,
      taskName: timer.taskName,
      description: timer.description,
      startTime: timer.startTime,
      endTime: new Date().toISOString(),
      duration,
      billable: timer.billable,
      hourlyRate: timer.hourlyRate,
      status: 'stopped',
      createdAt: timer.startTime,
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/timer/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(entryData),
      })

      if (response.ok) {
        const data = await response.json()
        setEntries([data, ...entries])
      } else {
        setEntries([entryData, ...entries])
      }

      setTimer(null)
    } catch (error) {
      console.error('Error stopping timer:', error)
    }
  }

  const handleAddManualEntry = async () => {
    if (!newEntry.description || !newEntry.startTime || !newEntry.endTime) {
      alert('Заполните все обязательные поля')
      return
    }

    const start = new Date(newEntry.startTime)
    const end = new Date(newEntry.endTime)
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000 / 60)

    if (duration <= 0) {
      alert('Время окончания должно быть позже времени начала')
      return
    }

    const entryData: TimeEntry = {
      id: Date.now(),
      userId: 1,
      userName: 'Текущий пользователь',
      taskId: newEntry.taskId || undefined,
      description: newEntry.description,
      startTime: newEntry.startTime,
      endTime: newEntry.endTime,
      duration,
      billable: newEntry.billable,
      hourlyRate: newEntry.hourlyRate,
      status: 'stopped',
      createdAt: new Date().toISOString(),
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/time-entries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(entryData),
      })

      if (response.ok) {
        const data = await response.json()
        setEntries([data, ...entries])
      } else {
        setEntries([entryData, ...entries])
      }

      setNewEntry({
        description: '',
        taskId: 0,
        startTime: new Date().toISOString().slice(0, 16),
        endTime: new Date().toISOString().slice(0, 16),
        billable: true,
        hourlyRate: 50,
      })
    } catch (error) {
      console.error('Error adding entry:', error)
    }
  }

  const handleDeleteEntry = async (entryId: number) => {
    if (!confirm('Удалить запись о времени?')) return

    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/time-entries/${entryId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      setEntries(entries.filter((e) => e.id !== entryId))
    } catch (error) {
      console.error('Error deleting entry:', error)
    }
  }

  const calculateStats = (): TimeStats => {
    let filtered = entries

    if (dateFrom) {
      filtered = filtered.filter((e) => new Date(e.startTime) >= new Date(dateFrom))
    }
    if (dateTo) {
      filtered = filtered.filter((e) => new Date(e.startTime) <= new Date(dateTo + 'T23:59:59'))
    }
    if (filterUser !== 'all') {
      filtered = filtered.filter((e) => e.userName === filterUser)
    }
    if (filterBillable !== 'all') {
      filtered = filtered.filter((e) => e.billable === (filterBillable === 'billable'))
    }

    const totalHours = filtered.reduce((sum, e) => sum + e.duration, 0) / 60
    const billableHours = filtered.filter((e) => e.billable).reduce((sum, e) => sum + e.duration, 0) / 60
    const nonBillableHours = totalHours - billableHours
    const totalAmount = filtered.reduce((sum, e) => {
      if (e.billable) {
        return sum + (e.duration / 60) * e.hourlyRate
      }
      return sum
    }, 0)

    const byUser: { [key: string]: number } = {}
    const byTask: { [key: string]: number } = {}
    const byDay: { [key: string]: number } = {}

    filtered.forEach((entry) => {
      // By user
      byUser[entry.userName] = (byUser[entry.userName] || 0) + entry.duration / 60

      // By task
      const taskKey = entry.taskName || 'Без задачи'
      byTask[taskKey] = (byTask[taskKey] || 0) + entry.duration / 60

      // By day
      const day = entry.startTime.slice(0, 10)
      byDay[day] = (byDay[day] || 0) + entry.duration / 60
    })

    return {
      totalHours,
      billableHours,
      nonBillableHours,
      totalAmount,
      entriesCount: filtered.length,
      avgHourlyRate: billableHours > 0 ? totalAmount / billableHours : 0,
      byUser,
      byTask,
      byDay,
    }
  }

  const formatDuration = (minutes: number): string => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}ч ${mins}м`
  }

  const formatTimerDuration = (): string => {
    if (!timer) return '00:00:00'
    const duration = Math.floor((currentTime.getTime() - new Date(timer.startTime).getTime()) / 1000)
    const hours = Math.floor(duration / 3600)
    const minutes = Math.floor((duration % 3600) / 60)
    const seconds = duration % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  const filteredEntries = entries.filter((entry) => {
    const matchesSearch =
      entry.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.userName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (entry.taskName && entry.taskName.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesUser = filterUser === 'all' || entry.userName === filterUser
    const matchesBillable = filterBillable === 'all' || entry.billable === (filterBillable === 'billable')

    const matchesDateFrom = !dateFrom || new Date(entry.startTime) >= new Date(dateFrom)
    const matchesDateTo = !dateTo || new Date(entry.startTime) <= new Date(dateTo + 'T23:59:59')

    return matchesSearch && matchesUser && matchesBillable && matchesDateFrom && matchesDateTo
  })

  const stats = calculateStats()
  const users = Array.from(new Set(entries.map((e) => e.userName)))

  const exportToCSV = () => {
    const headers = ['Дата', 'Пользователь', 'Задача', 'Описание', 'Начало', 'Конец', 'Длительность', 'Billable', 'Ставка', 'Сумма']
    const rows = filteredEntries.map((entry) => [
      entry.startTime.slice(0, 10),
      entry.userName,
      entry.taskName || '-',
      entry.description,
      new Date(entry.startTime).toLocaleTimeString('ru-RU'),
      entry.endTime ? new Date(entry.endTime).toLocaleTimeString('ru-RU') : '-',
      formatDuration(entry.duration),
      entry.billable ? 'Да' : 'Нет',
      `$${entry.hourlyRate}`,
      entry.billable ? `$${((entry.duration / 60) * entry.hourlyRate).toFixed(2)}` : '-',
    ])

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `time-tracking-project-${projectId}-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка данных...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Clock className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Учет времени</h2>
              <p className="text-blue-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            aria-label="Закрыть"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Timer */}
        {timer && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-200 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                  <Play className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Активный таймер</p>
                  <p className="font-semibold text-gray-900">{timer.description}</p>
                  {timer.taskName && <p className="text-sm text-gray-500">Задача: {timer.taskName}</p>}
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-4xl font-bold text-green-600 font-mono">{formatTimerDuration()}</p>
                  <p className="text-sm text-gray-600">
                    {timer.billable ? `$${timer.hourlyRate}/час` : 'Не оплачивается'}
                  </p>
                </div>
                <button
                  onClick={handleStopTimer}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2 font-medium"
                >
                  <Square className="w-5 h-5" />
                  Остановить
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Clock className="w-4 h-4" />
              <span>Всего</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalHours.toFixed(1)}ч</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <TrendingUp className="w-4 h-4" />
              <span>Billable</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.billableHours.toFixed(1)}ч</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <BarChart2 className="w-4 h-4" />
              <span>Non-billable</span>
            </div>
            <div className="text-2xl font-bold text-gray-600">{stats.nonBillableHours.toFixed(1)}ч</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <DollarSign className="w-4 h-4" />
              <span>Сумма</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">${stats.totalAmount.toFixed(0)}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Users className="w-4 h-4" />
              <span>Записей</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.entriesCount}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <DollarSign className="w-4 h-4" />
              <span>Ср. ставка</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">${stats.avgHourlyRate.toFixed(0)}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-4 bg-white border-b">
          <button
            onClick={() => setActiveTab('entries')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'entries' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Записи времени
          </button>
          <button
            onClick={() => setActiveTab('timer')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'timer' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Таймер
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'reports' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Отчеты
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'entries' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Поиск..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="От"
                />
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="До"
                />
                <select
                  value={filterUser}
                  onChange={(e) => setFilterUser(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">Все пользователи</option>
                  {users.map((user) => (
                    <option key={user} value={user}>
                      {user}
                    </option>
                  ))}
                </select>
                <select
                  value={filterBillable}
                  onChange={(e) => setFilterBillable(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">Все записи</option>
                  <option value="billable">Billable</option>
                  <option value="non-billable">Non-billable</option>
                </select>
                <button
                  onClick={exportToCSV}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                >
                  <Download className="w-5 h-5" />
                  Экспорт CSV
                </button>
              </div>

              {/* Entries Table */}
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Пользователь</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Задача</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Описание</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Время</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Длительность</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Billable</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Сумма</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredEntries.map((entry) => (
                        <tr key={entry.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {new Date(entry.startTime).toLocaleDateString('ru-RU')}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{entry.userName}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{entry.taskName || '-'}</td>
                          <td className="px-6 py-4 text-sm text-gray-900">{entry.description}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {new Date(entry.startTime).toLocaleTimeString('ru-RU', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}{' '}
                            -{' '}
                            {entry.endTime
                              ? new Date(entry.endTime).toLocaleTimeString('ru-RU', {
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })
                              : '...'}
                          </td>
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">{formatDuration(entry.duration)}</td>
                          <td className="px-6 py-4 text-center">
                            {entry.billable ? (
                              <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">Да</span>
                            ) : (
                              <span className="text-xs px-2 py-1 bg-gray-100 text-gray-800 rounded-full">Нет</span>
                            )}
                          </td>
                          <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                            {entry.billable ? `$${((entry.duration / 60) * entry.hourlyRate).toFixed(2)}` : '-'}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => handleDeleteEntry(entry.id)}
                              className="text-red-600 hover:text-red-800 p-1"
                              aria-label="Удалить"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {filteredEntries.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                      <Clock className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p>Нет записей времени</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'timer' && (
            <div className="max-w-2xl mx-auto space-y-6">
              {!timer ? (
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Запустить таймер</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Описание задачи *</label>
                      <input
                        type="text"
                        value={newEntry.description}
                        onChange={(e) => setNewEntry({ ...newEntry, description: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Над чем вы работаете?"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={newEntry.billable}
                            onChange={(e) => setNewEntry({ ...newEntry, billable: e.target.checked })}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700">Billable</span>
                        </label>
                      </div>
                      {newEntry.billable && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Ставка ($/час)</label>
                          <input
                            type="number"
                            min="0"
                            step="5"
                            value={newEntry.hourlyRate}
                            onChange={(e) => setNewEntry({ ...newEntry, hourlyRate: parseFloat(e.target.value) || 0 })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex justify-end mt-6">
                    <button
                      onClick={handleStartTimer}
                      className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 font-medium"
                    >
                      <Play className="w-5 h-5" />
                      Запустить таймер
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
                  <Clock className="w-16 h-16 mx-auto mb-4 text-green-600" />
                  <p className="text-gray-600 mb-2">Таймер уже запущен</p>
                  <p className="text-gray-900 font-medium">{timer.description}</p>
                </div>
              )}

              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Добавить запись вручную</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Описание *</label>
                    <input
                      type="text"
                      value={newEntry.description}
                      onChange={(e) => setNewEntry({ ...newEntry, description: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Описание работы"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Начало *</label>
                      <input
                        type="datetime-local"
                        value={newEntry.startTime}
                        onChange={(e) => setNewEntry({ ...newEntry, startTime: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Окончание *</label>
                      <input
                        type="datetime-local"
                        value={newEntry.endTime}
                        onChange={(e) => setNewEntry({ ...newEntry, endTime: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={newEntry.billable}
                          onChange={(e) => setNewEntry({ ...newEntry, billable: e.target.checked })}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">Billable</span>
                      </label>
                    </div>
                    {newEntry.billable && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Ставка ($/час)</label>
                        <input
                          type="number"
                          min="0"
                          step="5"
                          value={newEntry.hourlyRate}
                          onChange={(e) => setNewEntry({ ...newEntry, hourlyRate: parseFloat(e.target.value) || 0 })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex justify-end mt-6">
                  <button
                    onClick={handleAddManualEntry}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Добавить запись
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="space-y-6">
              {/* By User */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">По пользователям</h3>
                <div className="space-y-2">
                  {Object.entries(stats.byUser)
                    .sort(([, a], [, b]) => b - a)
                    .map(([user, hours]) => (
                      <div key={user} className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="flex justify-between mb-1">
                            <span className="text-sm font-medium text-gray-900">{user}</span>
                            <span className="text-sm text-gray-600">{hours.toFixed(1)}ч</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${(hours / stats.totalHours) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {/* By Task */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">По задачам</h3>
                <div className="space-y-2">
                  {Object.entries(stats.byTask)
                    .sort(([, a], [, b]) => b - a)
                    .map(([task, hours]) => (
                      <div key={task} className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="flex justify-between mb-1">
                            <span className="text-sm font-medium text-gray-900">{task}</span>
                            <span className="text-sm text-gray-600">{hours.toFixed(1)}ч</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${(hours / stats.totalHours) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {/* By Day */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">По дням</h3>
                <div className="space-y-2">
                  {Object.entries(stats.byDay)
                    .sort(([a], [b]) => b.localeCompare(a))
                    .map(([day, hours]) => (
                      <div key={day} className="flex items-center gap-4">
                        <div className="w-24 text-sm text-gray-600">{new Date(day).toLocaleDateString('ru-RU')}</div>
                        <div className="flex-1">
                          <div className="flex justify-between mb-1">
                            <div className="w-full bg-gray-200 rounded-full h-8 relative">
                              <div
                                className="bg-purple-600 h-8 rounded-full flex items-center justify-end pr-3"
                                style={{ width: `${(hours / Math.max(...Object.values(stats.byDay))) * 100}%` }}
                              >
                                <span className="text-xs font-medium text-white">{hours.toFixed(1)}ч</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TimeTracking
