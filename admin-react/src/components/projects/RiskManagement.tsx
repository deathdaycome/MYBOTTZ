import { useState, useEffect } from 'react'
import {
  X,
  AlertTriangle,
  Plus,
  Trash2,
  Edit2,
  Check,
  TrendingUp,
  Shield,
  Activity,
  Clock,
  CheckCircle,
} from 'lucide-react'

interface Risk {
  id: number
  title: string
  description: string
  probability: 'low' | 'medium' | 'high'
  impact: 'low' | 'medium' | 'high'
  category: string
  status: 'identified' | 'analyzing' | 'mitigated' | 'accepted' | 'resolved'
  mitigationPlan: string
  owner: string
  createdAt: string
  updatedAt?: string
}

interface RiskManagementProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

const RISK_CATEGORIES = [
  'Технический',
  'Финансовый',
  'Временной',
  'Ресурсный',
  'Правовой',
  'Коммерческий',
  'Операционный',
  'Репутационный',
]

const PROBABILITY_LABELS = {
  low: 'Низкая',
  medium: 'Средняя',
  high: 'Высокая',
}

const IMPACT_LABELS = {
  low: 'Низкое',
  medium: 'Среднее',
  high: 'Высокое',
}

const STATUS_LABELS = {
  identified: 'Выявлен',
  analyzing: 'Анализируется',
  mitigated: 'Снижен',
  accepted: 'Принят',
  resolved: 'Устранен',
}

export const RiskManagement = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: RiskManagementProps) => {
  const [risks, setRisks] = useState<Risk[]>([])
  const [isAdding, setIsAdding] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    probability: 'medium' as const,
    impact: 'medium' as const,
    category: RISK_CATEGORIES[0],
    status: 'identified' as const,
    mitigationPlan: '',
  })
  const [loading, setLoading] = useState(false)
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  useEffect(() => {
    if (isOpen && projectId) {
      loadRisks()
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

  const loadRisks = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/risks`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setRisks(data.risks || [])
      } else {
        // Mock data
        setRisks([
          {
            id: 1,
            title: 'Нехватка ресурсов разработки',
            description: 'Текущая команда может не справиться с объемом работ в срок',
            probability: 'high',
            impact: 'high',
            category: 'Ресурсный',
            status: 'analyzing',
            mitigationPlan: 'Нанять дополнительных разработчиков или распределить задачи',
            owner: 'admin',
            createdAt: new Date().toISOString(),
          },
          {
            id: 2,
            title: 'Изменение требований клиента',
            description: 'Клиент может изменить требования в процессе разработки',
            probability: 'medium',
            impact: 'high',
            category: 'Коммерческий',
            status: 'mitigated',
            mitigationPlan: 'Строгий контроль изменений, дополнительные согласования',
            owner: 'admin',
            createdAt: new Date(Date.now() - 86400000).toISOString(),
          },
          {
            id: 3,
            title: 'Проблемы с интеграцией API',
            description: 'Внешний API может работать нестабильно',
            probability: 'low',
            impact: 'medium',
            category: 'Технический',
            status: 'identified',
            mitigationPlan: 'Реализовать retry mechanism и fallback варианты',
            owner: 'admin',
            createdAt: new Date(Date.now() - 172800000).toISOString(),
          },
        ])
      }
    } catch (err) {
      console.error('Error loading risks:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddRisk = async () => {
    if (!formData.title.trim()) return

    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/risks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setFormData({
          title: '',
          description: '',
          probability: 'medium',
          impact: 'medium',
          category: RISK_CATEGORIES[0],
          status: 'identified',
          mitigationPlan: '',
        })
        setIsAdding(false)
        await loadRisks()
      }
    } catch (err) {
      console.error('Error adding risk:', err)
    }
  }

  const handleUpdateRisk = async (riskId: number, updates: Partial<Risk>) => {
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/risks/${riskId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify(updates),
        }
      )

      if (response.ok) {
        await loadRisks()
      }
    } catch (err) {
      console.error('Error updating risk:', err)
    }
  }

  const handleDeleteRisk = async (riskId: number) => {
    if (!confirm('Удалить этот риск?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/risks/${riskId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadRisks()
      }
    } catch (err) {
      console.error('Error deleting risk:', err)
    }
  }

  const calculateRiskScore = (probability: string, impact: string): number => {
    const probValue = probability === 'low' ? 1 : probability === 'medium' ? 2 : 3
    const impactValue = impact === 'low' ? 1 : impact === 'medium' ? 2 : 3
    return probValue * impactValue
  }

  const getRiskScoreColor = (score: number): string => {
    if (score >= 6) return 'bg-red-500'
    if (score >= 4) return 'bg-orange-500'
    return 'bg-yellow-500'
  }

  const getRiskScoreLabel = (score: number): string => {
    if (score >= 6) return 'Критический'
    if (score >= 4) return 'Высокий'
    return 'Умеренный'
  }

  const getProbabilityColor = (prob: string): string => {
    if (prob === 'high') return 'bg-red-100 text-red-700'
    if (prob === 'medium') return 'bg-orange-100 text-orange-700'
    return 'bg-yellow-100 text-yellow-700'
  }

  const getImpactColor = (impact: string): string => {
    if (impact === 'high') return 'bg-red-100 text-red-700'
    if (impact === 'medium') return 'bg-orange-100 text-orange-700'
    return 'bg-green-100 text-green-700'
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'identified':
        return 'bg-blue-100 text-blue-700'
      case 'analyzing':
        return 'bg-purple-100 text-purple-700'
      case 'mitigated':
        return 'bg-green-100 text-green-700'
      case 'accepted':
        return 'bg-yellow-100 text-yellow-700'
      case 'resolved':
        return 'bg-emerald-100 text-emerald-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    }).format(date)
  }

  if (!isOpen) return null

  const filteredRisks = risks.filter((risk) => {
    if (filterCategory !== 'all' && risk.category !== filterCategory) return false
    if (filterStatus !== 'all' && risk.status !== filterStatus) return false
    return true
  })

  const riskStats = {
    total: risks.length,
    critical: risks.filter((r) => calculateRiskScore(r.probability, r.impact) >= 6).length,
    active: risks.filter((r) => !['resolved', 'accepted'].includes(r.status)).length,
    resolved: risks.filter((r) => r.status === 'resolved').length,
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Управление рисками</h3>
              <p className="text-red-100 text-sm mt-1">{projectName}</p>
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
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex-shrink-0">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-3 border-2 border-blue-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Всего рисков</div>
              <div className="text-2xl font-bold text-blue-600">{riskStats.total}</div>
            </div>
            <div className="bg-white rounded-xl p-3 border-2 border-red-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Критических</div>
              <div className="text-2xl font-bold text-red-600">{riskStats.critical}</div>
            </div>
            <div className="bg-white rounded-xl p-3 border-2 border-orange-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Активных</div>
              <div className="text-2xl font-bold text-orange-600">{riskStats.active}</div>
            </div>
            <div className="bg-white rounded-xl p-3 border-2 border-green-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Устранено</div>
              <div className="text-2xl font-bold text-green-600">{riskStats.resolved}</div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex-shrink-0">
          <div className="flex gap-4">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-red-500 outline-none text-sm"
            >
              <option value="all">Все категории</option>
              {RISK_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border-2 border-gray-300 rounded-lg focus:border-red-500 outline-none text-sm"
            >
              <option value="all">Все статусы</option>
              {Object.entries(STATUS_LABELS).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Add Risk Button */}
          {!isAdding && (
            <button
              onClick={() => setIsAdding(true)}
              className="w-full mb-4 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-lg hover:from-red-700 hover:to-orange-700 transition-all font-semibold"
            >
              <Plus className="w-5 h-5" />
              Добавить риск
            </button>
          )}

          {/* Add Risk Form */}
          {isAdding && (
            <div className="mb-4 bg-red-50 border-2 border-red-200 rounded-xl p-4">
              <h4 className="font-bold text-gray-900 mb-3">Новый риск</h4>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Название риска
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-red-300 rounded-lg focus:border-red-500 outline-none"
                    placeholder="Краткое описание риска"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Описание
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-red-300 rounded-lg focus:border-red-500 outline-none resize-none"
                    rows={3}
                    placeholder="Подробное описание риска"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Вероятность
                    </label>
                    <select
                      value={formData.probability}
                      onChange={(e) =>
                        setFormData({ ...formData, probability: e.target.value as any })
                      }
                      className="w-full px-4 py-2 border-2 border-red-300 rounded-lg focus:border-red-500 outline-none"
                    >
                      <option value="low">Низкая</option>
                      <option value="medium">Средняя</option>
                      <option value="high">Высокая</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Влияние
                    </label>
                    <select
                      value={formData.impact}
                      onChange={(e) => setFormData({ ...formData, impact: e.target.value as any })}
                      className="w-full px-4 py-2 border-2 border-red-300 rounded-lg focus:border-red-500 outline-none"
                    >
                      <option value="low">Низкое</option>
                      <option value="medium">Среднее</option>
                      <option value="high">Высокое</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Категория
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-red-300 rounded-lg focus:border-red-500 outline-none"
                  >
                    {RISK_CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    План снижения
                  </label>
                  <textarea
                    value={formData.mitigationPlan}
                    onChange={(e) => setFormData({ ...formData, mitigationPlan: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-red-300 rounded-lg focus:border-red-500 outline-none resize-none"
                    rows={2}
                    placeholder="Как планируется снизить этот риск"
                  />
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleAddRisk}
                    disabled={!formData.title.trim()}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                  >
                    <Check className="w-4 h-4" />
                    Добавить
                  </button>
                  <button
                    onClick={() => {
                      setIsAdding(false)
                      setFormData({
                        title: '',
                        description: '',
                        probability: 'medium',
                        impact: 'medium',
                        category: RISK_CATEGORIES[0],
                        status: 'identified',
                        mitigationPlan: '',
                      })
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Risks List */}
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка...</div>
          ) : filteredRisks.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">
                {risks.length === 0 ? 'Нет выявленных рисков' : 'Нет рисков по выбранным фильтрам'}
              </p>
              <p className="text-sm mt-2">
                {risks.length === 0 ? 'Добавьте первый риск проекта' : 'Измените фильтры'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredRisks.map((risk) => {
                const riskScore = calculateRiskScore(risk.probability, risk.impact)

                return (
                  <div
                    key={risk.id}
                    className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-red-400 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h5 className="font-bold text-gray-900 text-lg">{risk.title}</h5>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold text-white ${getRiskScoreColor(
                              riskScore
                            )}`}
                          >
                            {getRiskScoreLabel(riskScore)}
                          </span>
                        </div>

                        <p className="text-sm text-gray-700 mb-3">{risk.description}</p>

                        <div className="flex flex-wrap gap-2 mb-3">
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-semibold ${getProbabilityColor(
                              risk.probability
                            )}`}
                          >
                            Вероятность: {PROBABILITY_LABELS[risk.probability]}
                          </span>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-semibold ${getImpactColor(
                              risk.impact
                            )}`}
                          >
                            Влияние: {IMPACT_LABELS[risk.impact]}
                          </span>
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold">
                            {risk.category}
                          </span>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                              risk.status
                            )}`}
                          >
                            {STATUS_LABELS[risk.status]}
                          </span>
                        </div>

                        {risk.mitigationPlan && (
                          <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded">
                            <div className="text-xs font-semibold text-green-700 mb-1">
                              План снижения:
                            </div>
                            <div className="text-sm text-green-900">{risk.mitigationPlan}</div>
                          </div>
                        )}

                        <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
                          <div className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            <span>Создан: {formatDate(risk.createdAt)}</span>
                          </div>
                          {risk.updatedAt && (
                            <div className="flex items-center gap-1">
                              <Activity className="w-3.5 h-3.5" />
                              <span>Обновлен: {formatDate(risk.updatedAt)}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <select
                          value={risk.status}
                          onChange={(e) =>
                            handleUpdateRisk(risk.id, { status: e.target.value as any })
                          }
                          className="px-3 py-1 border-2 border-gray-300 rounded-lg text-xs focus:border-red-500 outline-none"
                        >
                          {Object.entries(STATUS_LABELS).map(([key, label]) => (
                            <option key={key} value={key}>
                              {label}
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={() => handleDeleteRisk(risk.id)}
                          className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            Показано: <span className="font-bold text-red-600">{filteredRisks.length}</span> из{' '}
            {risks.length}
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
