import { useState, useEffect } from 'react'
import { X, GitCompare, ArrowRight, Check, Minus, Plus, AlertCircle } from 'lucide-react'

interface Version {
  id: number
  version: string
  createdAt: string
  snapshot: Record<string, any>
}

interface VersionComparisonProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

interface Difference {
  field: string
  oldValue: any
  newValue: any
  type: 'added' | 'removed' | 'modified' | 'unchanged'
}

export const VersionComparison = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: VersionComparisonProps) => {
  const [versions, setVersions] = useState<Version[]>([])
  const [selectedVersion1, setSelectedVersion1] = useState<number | null>(null)
  const [selectedVersion2, setSelectedVersion2] = useState<number | null>(null)
  const [differences, setDifferences] = useState<Difference[]>([])
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

  useEffect(() => {
    if (selectedVersion1 && selectedVersion2) {
      compareVersions()
    } else {
      setDifferences([])
    }
  }, [selectedVersion1, selectedVersion2])

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
            version: 'v1.0.0',
            createdAt: '2025-01-01',
            snapshot: {
              name: 'Веб-приложение',
              status: 'planning',
              budget: 300000,
              deadline: '2025-05-01',
              team_size: 3,
            },
          },
          {
            id: 2,
            version: 'v2.0.0',
            createdAt: '2025-01-15',
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'in_progress',
              budget: 400000,
              deadline: '2025-04-01',
              team_size: 5,
              features: 'Базовый функционал',
            },
          },
          {
            id: 3,
            version: 'v2.5.0',
            createdAt: '2025-02-01',
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'in_progress',
              budget: 450000,
              deadline: '2025-03-01',
              team_size: 5,
              features: 'Расширенный функционал',
            },
          },
          {
            id: 4,
            version: 'v3.0.0',
            createdAt: '2025-02-15',
            snapshot: {
              name: 'Веб-приложение для клиента',
              status: 'in_progress',
              budget: 500000,
              deadline: '2025-03-01',
              team_size: 8,
              features: 'Полный функционал',
              integrations: 'API, Webhooks',
            },
          },
        ])

        // Auto-select last two versions
        if (versions.length >= 2) {
          setSelectedVersion1(versions[versions.length - 2].id)
          setSelectedVersion2(versions[versions.length - 1].id)
        }
      }
    } catch (err) {
      console.error('Error loading versions:', err)
    } finally {
      setLoading(false)
    }
  }

  const compareVersions = () => {
    const v1 = versions.find((v) => v.id === selectedVersion1)
    const v2 = versions.find((v) => v.id === selectedVersion2)

    if (!v1 || !v2) return

    const allKeys = new Set([...Object.keys(v1.snapshot), ...Object.keys(v2.snapshot)])
    const diffs: Difference[] = []

    allKeys.forEach((key) => {
      const oldValue = v1.snapshot[key]
      const newValue = v2.snapshot[key]

      if (oldValue === undefined && newValue !== undefined) {
        diffs.push({ field: key, oldValue: null, newValue, type: 'added' })
      } else if (oldValue !== undefined && newValue === undefined) {
        diffs.push({ field: key, oldValue, newValue: null, type: 'removed' })
      } else if (oldValue !== newValue) {
        diffs.push({ field: key, oldValue, newValue, type: 'modified' })
      } else {
        diffs.push({ field: key, oldValue, newValue, type: 'unchanged' })
      }
    })

    setDifferences(diffs)
  }

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '—'
    if (typeof value === 'boolean') return value ? 'Да' : 'Нет'
    if (typeof value === 'number') return value.toLocaleString()
    return String(value)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(date)
  }

  const getDiffIcon = (type: string) => {
    switch (type) {
      case 'added':
        return <Plus className="w-4 h-4 text-green-600" />
      case 'removed':
        return <Minus className="w-4 h-4 text-red-600" />
      case 'modified':
        return <AlertCircle className="w-4 h-4 text-orange-600" />
      case 'unchanged':
        return <Check className="w-4 h-4 text-gray-400" />
      default:
        return null
    }
  }

  const getDiffColor = (type: string): string => {
    switch (type) {
      case 'added':
        return 'bg-green-50 border-green-200'
      case 'removed':
        return 'bg-red-50 border-red-200'
      case 'modified':
        return 'bg-orange-50 border-orange-200'
      case 'unchanged':
        return 'bg-gray-50 border-gray-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getFieldLabel = (field: string): string => {
    const labels: Record<string, string> = {
      name: 'Название',
      status: 'Статус',
      budget: 'Бюджет',
      deadline: 'Дедлайн',
      team_size: 'Размер команды',
      features: 'Функционал',
      integrations: 'Интеграции',
    }
    return labels[field] || field
  }

  if (!isOpen) return null

  const changesCount = differences.filter((d) => d.type !== 'unchanged').length

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <GitCompare className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Сравнение версий</h3>
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

        {/* Version Selectors */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex-shrink-0">
          <div className="grid grid-cols-[1fr_auto_1fr] gap-4 items-center">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Версия 1 (старая)
              </label>
              <select
                value={selectedVersion1 || ''}
                onChange={(e) => setSelectedVersion1(Number(e.target.value))}
                className="w-full px-4 py-2 border-2 border-indigo-300 rounded-lg focus:border-indigo-500 outline-none"
              >
                <option value="">Выберите версию</option>
                {versions.map((version) => (
                  <option key={version.id} value={version.id}>
                    {version.version} - {formatDate(version.createdAt)}
                  </option>
                ))}
              </select>
            </div>

            <ArrowRight className="w-8 h-8 text-indigo-600 mt-6" />

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Версия 2 (новая)
              </label>
              <select
                value={selectedVersion2 || ''}
                onChange={(e) => setSelectedVersion2(Number(e.target.value))}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
              >
                <option value="">Выберите версию</option>
                {versions.map((version) => (
                  <option key={version.id} value={version.id}>
                    {version.version} - {formatDate(version.createdAt)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {selectedVersion1 && selectedVersion2 && (
            <div className="mt-4 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-indigo-800">
                <AlertCircle className="w-4 h-4" />
                <span>
                  Обнаружено изменений: <span className="font-bold">{changesCount}</span>
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Comparison Results */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка версий...</div>
          ) : !selectedVersion1 || !selectedVersion2 ? (
            <div className="text-center py-12 text-gray-500">
              <GitCompare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">Выберите две версии для сравнения</p>
              <p className="text-sm mt-2">Выберите версии из выпадающих списков выше</p>
            </div>
          ) : differences.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Check className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <p className="text-lg font-semibold">Версии идентичны</p>
              <p className="text-sm mt-2">Изменения не обнаружены</p>
            </div>
          ) : (
            <div className="space-y-3">
              {differences.map((diff, index) => (
                <div
                  key={index}
                  className={`border-2 rounded-xl p-4 ${getDiffColor(diff.type)}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">{getDiffIcon(diff.type)}</div>

                    <div className="flex-1">
                      <div className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                        <span>{getFieldLabel(diff.field)}</span>
                        {diff.type === 'added' && (
                          <span className="px-2 py-0.5 bg-green-500 text-white rounded-full text-xs font-bold">
                            Добавлено
                          </span>
                        )}
                        {diff.type === 'removed' && (
                          <span className="px-2 py-0.5 bg-red-500 text-white rounded-full text-xs font-bold">
                            Удалено
                          </span>
                        )}
                        {diff.type === 'modified' && (
                          <span className="px-2 py-0.5 bg-orange-500 text-white rounded-full text-xs font-bold">
                            Изменено
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs font-semibold text-gray-600 mb-1">
                            Было ({versions.find((v) => v.id === selectedVersion1)?.version})
                          </div>
                          <div
                            className={`px-3 py-2 rounded-lg text-sm font-mono ${
                              diff.type === 'added'
                                ? 'bg-gray-100 text-gray-400'
                                : diff.type === 'removed'
                                  ? 'bg-red-100 text-red-900 line-through'
                                  : 'bg-white'
                            }`}
                          >
                            {formatValue(diff.oldValue)}
                          </div>
                        </div>

                        <div>
                          <div className="text-xs font-semibold text-gray-600 mb-1">
                            Стало ({versions.find((v) => v.id === selectedVersion2)?.version})
                          </div>
                          <div
                            className={`px-3 py-2 rounded-lg text-sm font-mono ${
                              diff.type === 'removed'
                                ? 'bg-gray-100 text-gray-400'
                                : diff.type === 'added'
                                  ? 'bg-green-100 text-green-900 font-bold'
                                  : diff.type === 'modified'
                                    ? 'bg-orange-100 text-orange-900 font-bold'
                                    : 'bg-white'
                            }`}
                          >
                            {formatValue(diff.newValue)}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Plus className="w-4 h-4 text-green-600" />
              <span className="text-gray-600">
                Добавлено:{' '}
                <span className="font-bold text-green-600">
                  {differences.filter((d) => d.type === 'added').length}
                </span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-orange-600" />
              <span className="text-gray-600">
                Изменено:{' '}
                <span className="font-bold text-orange-600">
                  {differences.filter((d) => d.type === 'modified').length}
                </span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Minus className="w-4 h-4 text-red-600" />
              <span className="text-gray-600">
                Удалено:{' '}
                <span className="font-bold text-red-600">
                  {differences.filter((d) => d.type === 'removed').length}
                </span>
              </span>
            </div>
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
