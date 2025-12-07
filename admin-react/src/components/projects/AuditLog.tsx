import React, { useState, useEffect } from 'react'
import { Shield, X, Filter, Search, User, Calendar, Activity, FileText, Download, RefreshCw } from 'lucide-react'

interface AuditLogProps {
  projectId: number
  onClose: () => void
}

interface AuditEntry {
  id: number
  userId: number
  userName: string
  userRole: string
  action: 'create' | 'update' | 'delete' | 'view' | 'export' | 'login' | 'logout' | 'permission'
  entityType: 'project' | 'task' | 'file' | 'user' | 'setting' | 'report' | 'comment'
  entityId: number
  entityName: string
  changes?: {
    field: string
    oldValue: string
    newValue: string
  }[]
  ipAddress: string
  userAgent: string
  timestamp: string
  severity: 'info' | 'warning' | 'critical'
}

const AuditLog: React.FC<AuditLogProps> = ({ projectId, onClose }) => {
  const [entries, setEntries] = useState<AuditEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterAction, setFilterAction] = useState<string>('all')
  const [filterEntity, setFilterEntity] = useState<string>('all')
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState(new Date().toISOString().slice(0, 10))
  const [selectedEntry, setSelectedEntry] = useState<AuditEntry | null>(null)

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = 'unset' }
  }, [])

  useEffect(() => {
    fetchAuditLog()
  }, [projectId])

  const fetchAuditLog = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://147.45.215.199:8001/api/projects/${projectId}/audit-log`,
        {
          headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setEntries(data)
      } else {
        setEntries([
          {
            id: 1,
            userId: 1,
            userName: 'Иван Петров',
            userRole: 'Администратор',
            action: 'update',
            entityType: 'project',
            entityId: projectId,
            entityName: 'Основной проект',
            changes: [
              { field: 'Статус', oldValue: 'В процессе', newValue: 'Завершен' },
              { field: 'Бюджет', oldValue: '100000', newValue: '120000' },
            ],
            ipAddress: '192.168.1.100',
            userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            severity: 'info',
          },
          {
            id: 2,
            userId: 2,
            userName: 'Мария Смирнова',
            userRole: 'Менеджер',
            action: 'create',
            entityType: 'task',
            entityId: 101,
            entityName: 'Новая задача',
            ipAddress: '192.168.1.101',
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            severity: 'info',
          },
          {
            id: 3,
            userId: 3,
            userName: 'Алексей Коваленко',
            userRole: 'Разработчик',
            action: 'delete',
            entityType: 'file',
            entityId: 50,
            entityName: 'old_document.pdf',
            ipAddress: '192.168.1.102',
            userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
            timestamp: new Date(Date.now() - 14400000).toISOString(),
            severity: 'warning',
          },
          {
            id: 4,
            userId: 1,
            userName: 'Иван Петров',
            userRole: 'Администратор',
            action: 'permission',
            entityType: 'user',
            entityId: 5,
            entityName: 'Новый пользователь',
            changes: [
              { field: 'Роль', oldValue: 'Пользователь', newValue: 'Менеджер' },
              { field: 'Доступ', oldValue: 'Чтение', newValue: 'Полный' },
            ],
            ipAddress: '192.168.1.100',
            userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            timestamp: new Date(Date.now() - 21600000).toISOString(),
            severity: 'critical',
          },
          {
            id: 5,
            userId: 2,
            userName: 'Мария Смирнова',
            userRole: 'Менеджер',
            action: 'export',
            entityType: 'report',
            entityId: 20,
            entityName: 'Финансовый отчет',
            ipAddress: '192.168.1.101',
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            timestamp: new Date(Date.now() - 28800000).toISOString(),
            severity: 'info',
          },
          {
            id: 6,
            userId: 4,
            userName: 'Ольга Новикова',
            userRole: 'QA',
            action: 'update',
            entityType: 'task',
            entityId: 102,
            entityName: 'Тестирование функционала',
            changes: [
              { field: 'Статус', oldValue: 'Новая', newValue: 'В работе' },
            ],
            ipAddress: '192.168.1.103',
            userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1)',
            timestamp: new Date(Date.now() - 36000000).toISOString(),
            severity: 'info',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching audit log:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActionIcon = (action: string) => {
    const icons = {
      create: '➕',
      update: '✏️',
      delete: '🗑️',
      view: '👁️',
      export: '📤',
      login: '🔓',
      logout: '🔒',
      permission: '🔐',
    }
    return icons[action as keyof typeof icons] || '📝'
  }

  const getActionColor = (action: string) => {
    const colors = {
      create: 'text-green-600 bg-green-100',
      update: 'text-blue-600 bg-blue-100',
      delete: 'text-red-600 bg-red-100',
      view: 'text-gray-600 bg-gray-100',
      export: 'text-purple-600 bg-purple-100',
      login: 'text-teal-600 bg-teal-100',
      logout: 'text-orange-600 bg-orange-100',
      permission: 'text-pink-600 bg-pink-100',
    }
    return colors[action as keyof typeof colors] || 'text-gray-600 bg-gray-100'
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      info: 'bg-blue-100 text-blue-800',
      warning: 'bg-yellow-100 text-yellow-800',
      critical: 'bg-red-100 text-red-800',
    }
    return colors[severity as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getSeverityLabel = (severity: string) => {
    const labels = {
      info: 'Информация',
      warning: 'Предупреждение',
      critical: 'Критично',
    }
    return labels[severity as keyof typeof labels] || 'Неизвестно'
  }

  const getActionLabel = (action: string) => {
    const labels = {
      create: 'Создание',
      update: 'Обновление',
      delete: 'Удаление',
      view: 'Просмотр',
      export: 'Экспорт',
      login: 'Вход',
      logout: 'Выход',
      permission: 'Права доступа',
    }
    return labels[action as keyof typeof labels] || action
  }

  const getEntityLabel = (entityType: string) => {
    const labels = {
      project: 'Проект',
      task: 'Задача',
      file: 'Файл',
      user: 'Пользователь',
      setting: 'Настройка',
      report: 'Отчет',
      comment: 'Комментарий',
    }
    return labels[entityType as keyof typeof labels] || entityType
  }

  const filteredEntries = entries.filter((entry) => {
    const matchesSearch =
      entry.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.entityName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.action.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesAction = filterAction === 'all' || entry.action === filterAction
    const matchesEntity = filterEntity === 'all' || entry.entityType === filterEntity
    const matchesSeverity = filterSeverity === 'all' || entry.severity === filterSeverity

    const entryDate = new Date(entry.timestamp).toISOString().slice(0, 10)
    const matchesDate =
      (!dateFrom || entryDate >= dateFrom) && (!dateTo || entryDate <= dateTo)

    return matchesSearch && matchesAction && matchesEntity && matchesSeverity && matchesDate
  })

  const handleExport = () => {
    const csvContent = [
      ['ID', 'Пользователь', 'Действие', 'Тип', 'Объект', 'Время', 'IP', 'Уровень'].join(','),
      ...filteredEntries.map((entry) =>
        [
          entry.id,
          entry.userName,
          getActionLabel(entry.action),
          getEntityLabel(entry.entityType),
          entry.entityName,
          new Date(entry.timestamp).toLocaleString('ru-RU'),
          entry.ipAddress,
          getSeverityLabel(entry.severity),
        ].join(',')
      ),
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `audit-log-project-${projectId}-${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка журнала аудита...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Журнал аудита</h2>
              <p className="text-indigo-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 border-b bg-gray-50">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Поиск..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Все действия</option>
              <option value="create">Создание</option>
              <option value="update">Обновление</option>
              <option value="delete">Удаление</option>
              <option value="view">Просмотр</option>
              <option value="export">Экспорт</option>
              <option value="permission">Права</option>
            </select>

            <select
              value={filterEntity}
              onChange={(e) => setFilterEntity(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Все типы</option>
              <option value="project">Проекты</option>
              <option value="task">Задачи</option>
              <option value="file">Файлы</option>
              <option value="user">Пользователи</option>
              <option value="report">Отчеты</option>
            </select>

            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Все уровни</option>
              <option value="info">Информация</option>
              <option value="warning">Предупреждение</option>
              <option value="critical">Критично</option>
            </select>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Дата от</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Дата до</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-end gap-2">
              <button
                onClick={fetchAuditLog}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-5 h-5" />
                Обновить
              </button>
              <button
                onClick={handleExport}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Экспорт
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Найдено записей: <span className="font-bold text-gray-900">{filteredEntries.length}</span> из {entries.length}
            </p>
          </div>

          <div className="space-y-3">
            {filteredEntries.map((entry) => (
              <div
                key={entry.id}
                onClick={() => setSelectedEntry(entry)}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
              >
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-full ${getActionColor(entry.action)} flex items-center justify-center flex-shrink-0 text-xl`}>
                    {getActionIcon(entry.action)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className="font-bold text-gray-900 mb-1">
                          {getActionLabel(entry.action)} • {getEntityLabel(entry.entityType)}
                        </h3>
                        <p className="text-sm text-gray-600">{entry.entityName}</p>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(entry.severity)}`}>
                        {getSeverityLabel(entry.severity)}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-900">{entry.userName}</p>
                          <p className="text-xs text-gray-500">{entry.userRole}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <div>
                          <p className="text-gray-900">{new Date(entry.timestamp).toLocaleDateString('ru-RU')}</p>
                          <p className="text-xs text-gray-500">{new Date(entry.timestamp).toLocaleTimeString('ru-RU')}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-gray-400" />
                        <div>
                          <p className="text-gray-900">{entry.ipAddress}</p>
                          <p className="text-xs text-gray-500">IP адрес</p>
                        </div>
                      </div>

                      {entry.changes && entry.changes.length > 0 && (
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="text-gray-900">{entry.changes.length} изменений</p>
                            <p className="text-xs text-gray-500">Подробности</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredEntries.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Записи не найдены</p>
            </div>
          )}
        </div>
      </div>

      {selectedEntry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[80vh] overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8" />
                <div>
                  <h2 className="text-2xl font-bold">Детали записи</h2>
                  <p className="text-indigo-100 text-sm">ID: {selectedEntry.id}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedEntry(null)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[calc(80vh-80px)]">
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Пользователь</label>
                    <p className="text-lg font-semibold text-gray-900">{selectedEntry.userName}</p>
                    <p className="text-sm text-gray-500">{selectedEntry.userRole}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Действие</label>
                    <div className="flex items-center gap-2">
                      <span className={`text-2xl`}>{getActionIcon(selectedEntry.action)}</span>
                      <span className="text-lg font-semibold text-gray-900">
                        {getActionLabel(selectedEntry.action)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Тип объекта</label>
                    <p className="text-gray-900">{getEntityLabel(selectedEntry.entityType)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Объект</label>
                    <p className="text-gray-900">{selectedEntry.entityName}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Дата и время</label>
                    <p className="text-gray-900">
                      {new Date(selectedEntry.timestamp).toLocaleString('ru-RU')}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Уровень</label>
                    <span className={`inline-block text-xs px-3 py-1 rounded-full ${getSeverityColor(selectedEntry.severity)}`}>
                      {getSeverityLabel(selectedEntry.severity)}
                    </span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">IP адрес</label>
                  <p className="text-gray-900 font-mono">{selectedEntry.ipAddress}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">User Agent</label>
                  <p className="text-sm text-gray-600 font-mono break-all">{selectedEntry.userAgent}</p>
                </div>

                {selectedEntry.changes && selectedEntry.changes.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">Изменения</label>
                    <div className="space-y-3">
                      {selectedEntry.changes.map((change, idx) => (
                        <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                          <p className="font-medium text-gray-900 mb-2">{change.field}</p>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-xs text-gray-500 mb-1">Было</p>
                              <p className="text-sm text-red-600 font-mono bg-red-50 px-2 py-1 rounded">
                                {change.oldValue || '—'}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500 mb-1">Стало</p>
                              <p className="text-sm text-green-600 font-mono bg-green-50 px-2 py-1 rounded">
                                {change.newValue || '—'}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t flex justify-end">
              <button
                onClick={() => setSelectedEntry(null)}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AuditLog
