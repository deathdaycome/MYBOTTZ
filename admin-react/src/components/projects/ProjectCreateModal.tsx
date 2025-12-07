import { useState, useEffect, useRef } from 'react'
import { X, Plus, User } from 'lucide-react'
import { apiService } from '../../services/api'

interface ProjectCreateModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

interface Client {
  id: number
  first_name: string
  username?: string
  telegram_id?: number
}

interface Executor {
  id: number
  username: string
}

export const ProjectCreateModal = ({ isOpen, onClose, onSuccess }: ProjectCreateModalProps) => {
  // Form state
  const [title, setTitle] = useState('')
  const [projectType, setProjectType] = useState('website')
  const [description, setDescription] = useState('')
  const [clientId, setClientId] = useState('')
  const [complexity, setComplexity] = useState('medium')
  const [priority, setPriority] = useState('medium')
  const [estimatedCost, setEstimatedCost] = useState('')
  const [executorCost, setExecutorCost] = useState('')
  const [estimatedHours, setEstimatedHours] = useState('')
  const [prepaymentAmount, setPrepaymentAmount] = useState('')
  const [assignedExecutorId, setAssignedExecutorId] = useState('')
  const [deadline, setDeadline] = useState('')
  const [technicalRequirements, setTechnicalRequirements] = useState('')
  const [additionalRequirements, setAdditionalRequirements] = useState('')

  // New client fields
  const [showNewClientFields, setShowNewClientFields] = useState(false)
  const [newClientName, setNewClientName] = useState('')
  const [newClientPhone, setNewClientPhone] = useState('')
  const [newClientTelegramUsername, setNewClientTelegramUsername] = useState('')
  const [newClientTelegramId, setNewClientTelegramId] = useState('')

  // Data
  const [clients, setClients] = useState<Client[]>([])
  const [executors, setExecutors] = useState<Executor[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const modalContentRef = useRef<HTMLDivElement>(null)

  // Load clients and executors
  useEffect(() => {
    if (isOpen) {
      loadData()
    }
  }, [isOpen])

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
    try {
      setLoading(true)
      const [clientsData, executorsData] = await Promise.all([
        apiService.getClients(),
        apiService.getExecutors(),
      ])
      setClients(clientsData.clients || [])
      setExecutors(executorsData.executors || [])
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleClientSelectChange = (value: string) => {
    setClientId(value)
    setShowNewClientFields(value === 'new')
  }

  const resetForm = () => {
    setTitle('')
    setProjectType('website')
    setDescription('')
    setClientId('')
    setComplexity('medium')
    setPriority('medium')
    setEstimatedCost('')
    setExecutorCost('')
    setEstimatedHours('')
    setPrepaymentAmount('')
    setAssignedExecutorId('')
    setDeadline('')
    setTechnicalRequirements('')
    setAdditionalRequirements('')
    setShowNewClientFields(false)
    setNewClientName('')
    setNewClientPhone('')
    setNewClientTelegramUsername('')
    setNewClientTelegramId('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title || !description || (!clientId && !showNewClientFields)) {
      alert('Пожалуйста, заполните все обязательные поля')
      return
    }

    try {
      setSubmitting(true)

      const projectData: any = {
        title,
        project_type: projectType,
        description,
        complexity,
        priority,
        estimated_cost: estimatedCost ? Number(estimatedCost) : 0,
        executor_cost: executorCost ? Number(executorCost) : 0,
        estimated_hours: estimatedHours ? Number(estimatedHours) : 0,
        prepayment_amount: prepaymentAmount ? Number(prepaymentAmount) : 0,
        assigned_executor_id: assignedExecutorId ? Number(assignedExecutorId) : null,
        deadline: deadline || null,
        technical_requirements: technicalRequirements,
        additional_requirements: additionalRequirements,
      }

      // If creating new client
      if (showNewClientFields) {
        projectData.client_name = newClientName
        projectData.client_phone = newClientPhone
        projectData.client_telegram_id = newClientTelegramId || null
        // Don't send user_id when creating new client
      } else {
        projectData.user_id = Number(clientId)
      }

      await apiService.createProject(projectData)
      alert('Проект успешно создан!')
      resetForm()
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Error creating project:', error)
      alert('Ошибка при создании проекта')
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
        <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[95vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h3 className="text-xl font-bold">Создать новый проект</h3>
            <p className="text-purple-100 text-xs mt-0.5">Заполните информацию о проекте</p>
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
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Название проекта <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    placeholder="Например: Бот для автоматизации"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Тип проекта
                  </label>
                  <select
                    value={projectType}
                    onChange={(e) => setProjectType(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  >
                    <option value="website">Веб-сайт</option>
                    <option value="bot">Telegram-бот</option>
                    <option value="telegram_mini_app">Telegram Mini App</option>
                    <option value="app">Мобильное приложение</option>
                    <option value="other">Другое</option>
                  </select>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Описание проекта <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Опишите, что должен делать проект..."
                  required
                />
              </div>

              {/* Client Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Клиент <span className="text-red-500">*</span>
                </label>
                <select
                  value={clientId}
                  onChange={(e) => handleClientSelectChange(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required={!showNewClientFields}
                >
                  <option value="">Выберите клиента...</option>
                  <option value="new">+ Создать нового клиента</option>
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      {client.first_name} {client.username ? `(@${client.username})` : ''}
                    </option>
                  ))}
                </select>
              </div>

              {/* New Client Fields */}
              {showNewClientFields && (
                <div className="bg-blue-50 p-4 rounded-xl border-2 border-blue-200 space-y-4">
                  <div className="flex items-center gap-2 mb-4">
                    <User className="w-5 h-5 text-blue-600" />
                    <h4 className="font-semibold text-blue-900">Данные нового клиента</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Имя клиента <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={newClientName}
                        onChange={(e) => setNewClientName(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Имя клиента"
                        required={showNewClientFields}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Телефон клиента
                      </label>
                      <input
                        type="text"
                        value={newClientPhone}
                        onChange={(e) => setNewClientPhone(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="+7 900 000 00 00"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Telegram Username (для автопривязки)
                      </label>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500 font-semibold">@</span>
                        <input
                          type="text"
                          value={newClientTelegramUsername}
                          onChange={(e) => setNewClientTelegramUsername(e.target.value)}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="username"
                        />
                      </div>
                      <small className="text-gray-500 mt-1 block">
                        Клиент автоматически привяжется при /start
                      </small>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Telegram ID клиента (опционально)
                      </label>
                      <input
                        type="text"
                        value={newClientTelegramId}
                        onChange={(e) => setNewClientTelegramId(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="123456789"
                      />
                      <small className="text-gray-500 mt-1 block">
                        Или укажите username выше
                      </small>
                    </div>
                  </div>
                </div>
              )}

              {/* Complexity and Priority */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Сложность
                  </label>
                  <select
                    value={complexity}
                    onChange={(e) => setComplexity(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
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
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="low">Низкий</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                    <option value="urgent">Срочный</option>
                  </select>
                </div>
              </div>

              {/* Finance */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Стоимость (₽)
                  </label>
                  <input
                    type="number"
                    value={estimatedCost}
                    onChange={(e) => setEstimatedCost(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                    min="0"
                    step="1000"
                    placeholder="50000"
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
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                    min="0"
                    step="500"
                    placeholder="30000"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Часы (прогноз)
                  </label>
                  <input
                    type="number"
                    value={estimatedHours}
                    onChange={(e) => setEstimatedHours(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                    min="1"
                    step="1"
                    placeholder="40"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Предоплата (₽)
                  </label>
                  <input
                    type="number"
                    value={prepaymentAmount}
                    onChange={(e) => setPrepaymentAmount(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                    min="0"
                    step="1000"
                    placeholder="0"
                  />
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
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
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
                    type="date"
                    value={deadline}
                    onChange={(e) => setDeadline(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Technical Requirements */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Техническое задание
                </label>
                <textarea
                  value={technicalRequirements}
                  onChange={(e) => setTechnicalRequirements(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Детальное техническое задание..."
                />
              </div>

              {/* Additional Requirements */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Дополнительные требования
                </label>
                <textarea
                  value={additionalRequirements}
                  onChange={(e) => setAdditionalRequirements(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={2}
                  placeholder="Особые требования или пожелания..."
                />
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
              className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
              disabled={submitting}
            >
              {submitting ? (
                <>Создание...</>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Создать
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
