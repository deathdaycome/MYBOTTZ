import { useState, useEffect, useRef } from 'react'
import { X, Save } from 'lucide-react'
import { apiService } from '../../services/api'

interface Project {
  id: number
  title: string
  description: string
  project_type: string
  status: string
  complexity: string
  priority: string
  estimated_cost: number
  executor_cost: number
  final_cost: number
  estimated_hours: number
  prepayment_amount: number
  client_paid_total: number
  executor_paid_total: number
  assigned_executor_id: number | null
  deadline: string | null
  project_metadata: {
    test_link: string | null
  } | null
}

interface Executor {
  id: number
  username: string
}

interface ProjectEditModalProps {
  projectId: number | null
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export const ProjectEditModal = ({
  projectId,
  isOpen,
  onClose,
  onSuccess,
}: ProjectEditModalProps) => {
  // Form state
  const [title, setTitle] = useState('')
  const [projectType, setProjectType] = useState('website')
  const [description, setDescription] = useState('')
  const [status, setStatus] = useState('new')
  const [complexity, setComplexity] = useState('medium')
  const [priority, setPriority] = useState('medium')
  const [estimatedCost, setEstimatedCost] = useState('')
  const [executorCost, setExecutorCost] = useState('')
  const [finalCost, setFinalCost] = useState('')
  const [estimatedHours, setEstimatedHours] = useState('')
  const [prepaymentAmount, setPrepaymentAmount] = useState('')
  const [clientPaidTotal, setClientPaidTotal] = useState('')
  const [executorPaidTotal, setExecutorPaidTotal] = useState('')
  const [assignedExecutorId, setAssignedExecutorId] = useState('')
  const [deadline, setDeadline] = useState('')
  const [testLink, setTestLink] = useState('')

  // Data
  const [executors, setExecutors] = useState<Executor[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const modalContentRef = useRef<HTMLDivElement>(null)

  // Load project data and executors
  useEffect(() => {
    if (isOpen && projectId) {
      loadData()
    }
  }, [isOpen, projectId])

  // Block body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'

      // Reset modal content scroll to top
      if (modalContentRef.current) {
        modalContentRef.current.scrollTop = 0
      }
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
    return () => {
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
    }
  }, [isOpen])

  const loadData = async () => {
    if (!projectId) return

    try {
      setLoading(true)
      const [projectData, executorsData] = await Promise.all([
        apiService.getProject(projectId),
        apiService.getExecutors(),
      ])

      // Set form fields from project data
      const project: Project = projectData.project
      setTitle(project.title || '')
      setProjectType(project.project_type || 'website')
      setDescription(project.description || '')
      setStatus(project.status || 'new')
      setComplexity(project.complexity || 'medium')
      setPriority(project.priority || 'medium')
      setEstimatedCost(project.estimated_cost?.toString() || '')
      setExecutorCost(project.executor_cost?.toString() || '')
      setFinalCost(project.final_cost?.toString() || '')
      setEstimatedHours(project.estimated_hours?.toString() || '')
      setPrepaymentAmount(project.prepayment_amount?.toString() || '')
      setClientPaidTotal(project.client_paid_total?.toString() || '')
      setExecutorPaidTotal(project.executor_paid_total?.toString() || '')
      setAssignedExecutorId(project.assigned_executor_id?.toString() || '')
      setDeadline(project.deadline ? project.deadline.slice(0, 16) : '') // Format for datetime-local
      setTestLink(project.project_metadata?.test_link || '')

      setExecutors(executorsData.executors || [])
    } catch (error) {
      console.error('Error loading project data:', error)
      alert('Ошибка при загрузке данных проекта')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setTitle('')
    setProjectType('website')
    setDescription('')
    setStatus('new')
    setComplexity('medium')
    setPriority('medium')
    setEstimatedCost('')
    setExecutorCost('')
    setFinalCost('')
    setEstimatedHours('')
    setPrepaymentAmount('')
    setClientPaidTotal('')
    setExecutorPaidTotal('')
    setAssignedExecutorId('')
    setDeadline('')
    setTestLink('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title || !projectId) {
      alert('Пожалуйста, заполните все обязательные поля')
      return
    }

    try {
      setSubmitting(true)

      const projectData: any = {
        title,
        project_type: projectType,
        description,
        status,
        complexity,
        priority,
        estimated_cost: estimatedCost ? Number(estimatedCost) : 0,
        executor_cost: executorCost ? Number(executorCost) : 0,
        final_cost: finalCost ? Number(finalCost) : 0,
        estimated_hours: estimatedHours ? Number(estimatedHours) : 0,
        prepayment_amount: prepaymentAmount ? Number(prepaymentAmount) : 0,
        client_paid_total: clientPaidTotal ? Number(clientPaidTotal) : 0,
        executor_paid_total: executorPaidTotal ? Number(executorPaidTotal) : 0,
        assigned_executor_id: assignedExecutorId ? Number(assignedExecutorId) : null,
        deadline: deadline || null,
        project_metadata: {
          test_link: testLink || null,
        },
      }

      await apiService.updateProject(projectId, projectData)
      alert('Проект успешно обновлен!')
      resetForm()
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Error updating project:', error)
      alert('Ошибка при обновлении проекта')
    } finally {
      setSubmitting(false)
    }
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  if (!isOpen) return null

  return (
    <>
      <style>{`
        .modal-content-scrollable {
          scrollbar-width: none !important;
          -ms-overflow-style: none !important;
        }
        .modal-content-scrollable::-webkit-scrollbar {
          display: none !important;
          width: 0 !important;
          height: 0 !important;
        }
      `}</style>
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-2"
        style={{ overflow: 'hidden' }}
      >
        <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[95vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-600 to-blue-600 text-white px-4 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h3 className="text-xl font-bold">Редактировать проект #{projectId}</h3>
            <p className="text-cyan-100 text-xs mt-0.5">Изменить информацию о проекте</p>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 hover:bg-white/20 rounded-full transition-all flex-shrink-0"
            disabled={submitting}
            type="button"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body - Scrollable */}
        <form onSubmit={handleSubmit} className="flex-1 flex flex-col overflow-hidden">
          <div ref={modalContentRef} className="modal-content-scrollable px-4 py-3 overflow-y-auto flex-1">
          {loading ? (
            <div className="text-center py-12">
              <div className="text-gray-600">Загрузка...</div>
            </div>
          ) : (
            <div className="space-y-3">
              {/* Title and Type */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Название проекта <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Тип проекта
                  </label>
                  <select
                    value={projectType}
                    onChange={(e) => setProjectType(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  >
                    <option value="website">Веб-сайт</option>
                    <option value="bot">Telegram-бот</option>
                    <option value="app">Мобильное приложение</option>
                    <option value="other">Другое</option>
                  </select>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Описание проекта
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  rows={3}
                />
              </div>

              {/* Status, Complexity, Priority */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Статус
                  </label>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  >
                    <option value="new">🆕 Новый</option>
                    <option value="review">👀 На рассмотрении</option>
                    <option value="accepted">✅ Принят</option>
                    <option value="in_progress">🔄 В работе</option>
                    <option value="testing">🧪 Тестирование</option>
                    <option value="completed">🎉 Завершен</option>
                    <option value="cancelled">❌ Отменен</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Сложность
                  </label>
                  <select
                    value={complexity}
                    onChange={(e) => setComplexity(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  >
                    <option value="simple">🟢 Простой</option>
                    <option value="medium">🟡 Средний</option>
                    <option value="complex">🟠 Сложный</option>
                    <option value="premium">🔴 Премиум</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Приоритет
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  >
                    <option value="low">Низкий</option>
                    <option value="normal">Обычный</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                    <option value="urgent">Срочный</option>
                  </select>
                </div>
              </div>

              {/* Costs */}
              <div className="bg-orange-50 p-4 rounded-xl border-2 border-orange-200">
                <h4 className="font-semibold text-orange-900 mb-3">💰 Финансы</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Ориентировочная стоимость (₽)
                    </label>
                    <input
                      type="number"
                      value={estimatedCost}
                      onChange={(e) => setEstimatedCost(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="0"
                      step="100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Стоимость для исполнителя (₽)
                    </label>
                    <input
                      type="number"
                      value={executorCost}
                      onChange={(e) => setExecutorCost(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="0"
                      step="100"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Предоплата (₽)
                    </label>
                    <input
                      type="number"
                      value={prepaymentAmount}
                      onChange={(e) => setPrepaymentAmount(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="0"
                      step="100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Оплачено клиентом (₽)
                    </label>
                    <input
                      type="number"
                      value={clientPaidTotal}
                      onChange={(e) => setClientPaidTotal(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="0"
                      step="100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Выплачено исполнителю (₽)
                    </label>
                    <input
                      type="number"
                      value={executorPaidTotal}
                      onChange={(e) => setExecutorPaidTotal(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="0"
                      step="100"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Финальная стоимость (₽)
                    </label>
                    <input
                      type="number"
                      value={finalCost}
                      onChange={(e) => setFinalCost(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="0"
                      step="100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Оценочное время (часы)
                    </label>
                    <input
                      type="number"
                      value={estimatedHours}
                      onChange={(e) => setEstimatedHours(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      min="1"
                    />
                  </div>
                </div>
              </div>

              {/* Executor and Deadline */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Назначить исполнителя
                  </label>
                  <select
                    value={assignedExecutorId}
                    onChange={(e) => setAssignedExecutorId(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  >
                    <option value="">Выберите исполнителя</option>
                    {executors.map((executor) => (
                      <option key={executor.id} value={executor.id}>
                        {executor.username}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Дедлайн
                  </label>
                  <input
                    type="datetime-local"
                    value={deadline}
                    onChange={(e) => setDeadline(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
              </div>

              {/* Test Link */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  🧪 Ссылка на тестовую версию{' '}
                  <small className="text-gray-500">(опционально)</small>
                </label>
                <input
                  type="text"
                  value={testLink}
                  onChange={(e) => setTestLink(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  placeholder="https://t.me/your_bot или @your_bot"
                />
                <small className="text-gray-500 mt-1 block">
                  Укажите ссылку или username бота (например: https://t.me/test_bot или
                  @test_bot)
                </small>
              </div>
            </div>
          )}

          </div>

          {/* Footer */}
          <div className="flex gap-2 px-4 py-2.5 border-t border-gray-200 bg-white flex-shrink-0">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-all text-sm"
              disabled={submitting}
            >
              Отмена
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg font-semibold hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
              disabled={submitting}
            >
              {submitting ? (
                <>Сохранение...</>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Сохранить
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
    </>
  )
}
