import { useState, useEffect } from 'react'
import {
  X,
  GitBranch,
  Clock,
  User,
  RotateCcw,
  Plus,
  Tag,
  Check,
  FileText,
  AlertCircle,
  ChevronRight,
  ChevronDown,
} from 'lucide-react'

interface ProjectVersion {
  id: number
  version: string
  description: string
  changes: string[]
  createdBy: string
  createdAt: string
  isCurrent: boolean
  snapshot: Record<string, any>
  tags: string[]
}

interface ProjectVersioningProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
  onRestore?: (versionId: number) => void
}

export const ProjectVersioning = ({
  isOpen,
  onClose,
  projectId,
  projectName,
  onRestore,
}: ProjectVersioningProps) => {
  const [versions, setVersions] = useState<ProjectVersion[]>([])
  const [expandedVersions, setExpandedVersions] = useState<Set<number>>(new Set())
  const [isCreatingVersion, setIsCreatingVersion] = useState(false)
  const [newVersion, setNewVersion] = useState({
    version: '',
    description: '',
    tags: [] as string[],
  })
  const [newTag, setNewTag] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadVersions()
    }
  }, [isOpen, projectId])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  const loadVersions = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/versions`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setVersions(data.versions || [])
      } else {
        // Mock data
        setVersions([
          {
            id: 1,
            version: 'v3.0.0',
            description: 'Мажорное обновление с новыми функциями',
            changes: [
              'Добавлена система уведомлений',
              'Реализована интеграция с внешними сервисами',
              'Улучшен интерфейс управления проектами',
              'Исправлены критические баги с производительностью',
            ],
            createdBy: 'admin',
            createdAt: new Date().toISOString(),
            isCurrent: true,
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'in_progress',
              deadline: '2025-03-01',
              budget: 500000,
            },
            tags: ['release', 'major'],
          },
          {
            id: 2,
            version: 'v2.5.1',
            description: 'Патч для исправления багов',
            changes: [
              'Исправлена ошибка в модуле аутентификации',
              'Улучшена производительность запросов к БД',
              'Обновлены зависимости',
            ],
            createdBy: 'admin',
            createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
            isCurrent: false,
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'in_progress',
              deadline: '2025-03-01',
              budget: 480000,
            },
            tags: ['bugfix', 'patch'],
          },
          {
            id: 3,
            version: 'v2.5.0',
            description: 'Добавлены новые функции',
            changes: [
              'Реализована система комментариев',
              'Добавлена возможность загрузки файлов',
              'Улучшена навигация',
            ],
            createdBy: 'admin',
            createdAt: new Date(Date.now() - 86400000 * 7).toISOString(),
            isCurrent: false,
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'planning',
              deadline: '2025-03-01',
              budget: 450000,
            },
            tags: ['feature', 'minor'],
          },
          {
            id: 4,
            version: 'v2.0.0',
            description: 'Полный редизайн проекта',
            changes: [
              'Переработан дизайн всех страниц',
              'Обновлена архитектура приложения',
              'Миграция на новый стек технологий',
              'Оптимизация для мобильных устройств',
            ],
            createdBy: 'admin',
            createdAt: new Date(Date.now() - 86400000 * 14).toISOString(),
            isCurrent: false,
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'planning',
              deadline: '2025-04-01',
              budget: 400000,
            },
            tags: ['release', 'major', 'redesign'],
          },
          {
            id: 5,
            version: 'v1.0.0',
            description: 'Первый релиз проекта',
            changes: [
              'Базовая функциональность',
              'Система авторизации',
              'Управление задачами',
            ],
            createdBy: 'admin',
            createdAt: new Date(Date.now() - 86400000 * 30).toISOString(),
            isCurrent: false,
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'planning',
              deadline: '2025-05-01',
              budget: 300000,
            },
            tags: ['release', 'initial'],
          },
        ])
      }
    } catch (err) {
      console.error('Error loading versions:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateVersion = async () => {
    if (!newVersion.version.trim() || !newVersion.description.trim()) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/versions`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify(newVersion),
        }
      )

      if (response.ok) {
        setNewVersion({ version: '', description: '', tags: [] })
        setIsCreatingVersion(false)
        await loadVersions()
      }
    } catch (err) {
      console.error('Error creating version:', err)
    }
  }

  const handleRestoreVersion = async (versionId: number) => {
    if (!confirm('Восстановить проект к этой версии? Текущее состояние будет сохранено.'))
      return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/versions/${versionId}/restore`,
        {
          method: 'POST',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadVersions()
        if (onRestore) {
          onRestore(versionId)
        }
        alert('Проект успешно восстановлен!')
      }
    } catch (err) {
      console.error('Error restoring version:', err)
    }
  }

  const toggleVersionExpanded = (versionId: number) => {
    const newExpanded = new Set(expandedVersions)
    if (newExpanded.has(versionId)) {
      newExpanded.delete(versionId)
    } else {
      newExpanded.add(versionId)
    }
    setExpandedVersions(newExpanded)
  }

  const handleAddTag = () => {
    if (newTag.trim() && !newVersion.tags.includes(newTag.trim())) {
      setNewVersion({
        ...newVersion,
        tags: [...newVersion.tags, newTag.trim()],
      })
      setNewTag('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    setNewVersion({
      ...newVersion,
      tags: newVersion.tags.filter((t) => t !== tag),
    })
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const getTagColor = (tag: string): string => {
    const colors: Record<string, string> = {
      release: 'bg-blue-100 text-blue-700',
      major: 'bg-red-100 text-red-700',
      minor: 'bg-yellow-100 text-yellow-700',
      patch: 'bg-green-100 text-green-700',
      bugfix: 'bg-orange-100 text-orange-700',
      feature: 'bg-purple-100 text-purple-700',
      redesign: 'bg-pink-100 text-pink-700',
      initial: 'bg-emerald-100 text-emerald-700',
    }
    return colors[tag] || 'bg-gray-100 text-gray-700'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <GitBranch className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">История версий</h3>
              <p className="text-indigo-100 text-sm mt-1">{projectName}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Stats */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-gray-600" />
              <span className="text-gray-600">Всего версий:</span>
              <span className="font-bold text-indigo-600">{versions.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-600" />
              <span className="text-gray-600">Текущая:</span>
              <span className="font-bold text-green-600">
                {versions.find((v) => v.isCurrent)?.version || '-'}
              </span>
            </div>
          </div>

          {!isCreatingVersion && (
            <button
              onClick={() => setIsCreatingVersion(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold text-sm"
            >
              <Plus className="w-4 h-4" />
              Создать версию
            </button>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Create Version Form */}
          {isCreatingVersion && (
            <div className="mb-6 bg-indigo-50 border-2 border-indigo-200 rounded-xl p-4">
              <h4 className="font-bold text-gray-900 mb-3">Создать новую версию</h4>

              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Номер версии
                    </label>
                    <input
                      type="text"
                      value={newVersion.version}
                      onChange={(e) => setNewVersion({ ...newVersion, version: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-indigo-300 rounded-lg focus:border-indigo-500 outline-none"
                      placeholder="v1.0.0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Теги
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                        className="flex-1 px-4 py-2 border-2 border-indigo-300 rounded-lg focus:border-indigo-500 outline-none"
                        placeholder="release, major, etc."
                      />
                      <button
                        onClick={handleAddTag}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                    {newVersion.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {newVersion.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-semibold flex items-center gap-1"
                          >
                            {tag}
                            <button
                              onClick={() => handleRemoveTag(tag)}
                              className="hover:text-indigo-900"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Описание изменений
                  </label>
                  <textarea
                    value={newVersion.description}
                    onChange={(e) =>
                      setNewVersion({ ...newVersion, description: e.target.value })
                    }
                    className="w-full px-4 py-2 border-2 border-indigo-300 rounded-lg focus:border-indigo-500 outline-none resize-none"
                    rows={3}
                    placeholder="Опишите основные изменения в этой версии"
                  />
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleCreateVersion}
                    disabled={!newVersion.version.trim() || !newVersion.description.trim()}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                  >
                    <Check className="w-4 h-4" />
                    Создать
                  </button>
                  <button
                    onClick={() => {
                      setIsCreatingVersion(false)
                      setNewVersion({ version: '', description: '', tags: [] })
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Versions List */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка истории версий...</div>
          ) : versions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">Нет версий проекта</p>
              <p className="text-sm mt-2">Создайте первую версию</p>
            </div>
          ) : (
            <div className="space-y-3">
              {versions.map((version) => (
                <div
                  key={version.id}
                  className={`bg-white border-2 rounded-xl overflow-hidden transition-all ${
                    version.isCurrent
                      ? 'border-green-400 shadow-lg'
                      : 'border-gray-200 hover:border-indigo-400'
                  }`}
                >
                  {/* Version Header */}
                  <div
                    className={`p-4 cursor-pointer ${
                      version.isCurrent ? 'bg-green-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => toggleVersionExpanded(version.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {expandedVersions.has(version.id) ? (
                            <ChevronDown className="w-5 h-5 text-gray-500" />
                          ) : (
                            <ChevronRight className="w-5 h-5 text-gray-500" />
                          )}

                          <h5 className="font-bold text-gray-900 text-lg">{version.version}</h5>

                          {version.isCurrent && (
                            <span className="px-2 py-1 bg-green-500 text-white rounded-full text-xs font-bold flex items-center gap-1">
                              <Check className="w-3 h-3" />
                              Текущая
                            </span>
                          )}

                          {version.tags.map((tag) => (
                            <span
                              key={tag}
                              className={`px-2 py-1 rounded-full text-xs font-semibold ${getTagColor(
                                tag
                              )}`}
                            >
                              {tag}
                            </span>
                          ))}
                        </div>

                        <p className="text-sm text-gray-700 mb-2">{version.description}</p>

                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <div className="flex items-center gap-1">
                            <User className="w-3.5 h-3.5" />
                            <span>{version.createdBy}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            <span>{formatDate(version.createdAt)}</span>
                          </div>
                        </div>
                      </div>

                      {!version.isCurrent && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRestoreVersion(version.id)
                          }}
                          className="ml-4 flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold text-sm"
                        >
                          <RotateCcw className="w-4 h-4" />
                          Восстановить
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Version Details (Expanded) */}
                  {expandedVersions.has(version.id) && (
                    <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-4">
                      {/* Changes List */}
                      {version.changes.length > 0 && (
                        <div>
                          <h6 className="text-sm font-semibold text-gray-700 mb-2">Изменения:</h6>
                          <ul className="space-y-1">
                            {version.changes.map((change, index) => (
                              <li
                                key={index}
                                className="flex items-start gap-2 text-sm text-gray-700"
                              >
                                <span className="text-indigo-600 mt-1">•</span>
                                <span>{change}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Snapshot Data */}
                      <div>
                        <h6 className="text-sm font-semibold text-gray-700 mb-2">
                          Состояние проекта:
                        </h6>
                        <div className="grid grid-cols-2 gap-3">
                          {Object.entries(version.snapshot).map(([key, value]) => (
                            <div key={key} className="bg-white rounded-lg p-2 border border-gray-200">
                              <div className="text-xs text-gray-600 mb-1">{key}</div>
                              <div className="text-sm font-semibold text-gray-900">
                                {String(value)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <AlertCircle className="w-4 h-4" />
            <span>Восстановление версии сохранит текущее состояние</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
