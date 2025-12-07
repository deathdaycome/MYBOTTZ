import { useState, useEffect } from 'react'
import {
  X,
  FileText,
  Plus,
  Download,
  Eye,
  Trash2,
  Edit2,
  Check,
  Upload,
  Calendar,
  DollarSign,
  User,
  AlertCircle,
  CheckCircle,
  Clock,
} from 'lucide-react'

interface Contract {
  id: number
  title: string
  type: string
  description: string
  amount: number
  startDate: string
  endDate: string
  status: 'draft' | 'active' | 'expired' | 'terminated'
  file?: {
    name: string
    url: string
    size: number
    uploadedAt: string
  }
  signedBy?: string
  signedAt?: string
  createdAt: string
}

interface ContractManagementProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

const CONTRACT_TYPES = [
  'Договор на разработку',
  'Договор поддержки',
  'Договор консалтинга',
  'Лицензионное соглашение',
  'NDA',
  'SLA',
  'Прочее',
]

export const ContractManagement = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: ContractManagementProps) => {
  const [contracts, setContracts] = useState<Contract[]>([])
  const [isAdding, setIsAdding] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    title: '',
    type: CONTRACT_TYPES[0],
    description: '',
    amount: 0,
    startDate: '',
    endDate: '',
    status: 'draft' as const,
  })
  const [uploadingFile, setUploadingFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadContracts()
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

  const loadContracts = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/contracts`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setContracts(data.contracts || [])
      } else {
        // Mock data
        setContracts([
          {
            id: 1,
            title: 'Основной договор на разработку',
            type: 'Договор на разработку',
            description: 'Договор на разработку веб-приложения с полным циклом работ',
            amount: 500000,
            startDate: '2025-01-01',
            endDate: '2025-06-30',
            status: 'active',
            file: {
              name: 'contract_main.pdf',
              url: '/files/contract_main.pdf',
              size: 1024000,
              uploadedAt: new Date().toISOString(),
            },
            signedBy: 'Иван Иванов',
            signedAt: '2025-01-01',
            createdAt: new Date(Date.now() - 86400000 * 30).toISOString(),
          },
          {
            id: 2,
            title: 'Дополнительное соглашение №1',
            type: 'Договор на разработку',
            description: 'Дополнительные функции по требованию клиента',
            amount: 150000,
            startDate: '2025-02-01',
            endDate: '2025-04-30',
            status: 'active',
            file: {
              name: 'addendum_01.pdf',
              url: '/files/addendum_01.pdf',
              size: 512000,
              uploadedAt: new Date(Date.now() - 86400000 * 15).toISOString(),
            },
            signedBy: 'Мария Петрова',
            signedAt: '2025-02-01',
            createdAt: new Date(Date.now() - 86400000 * 15).toISOString(),
          },
          {
            id: 3,
            title: 'Соглашение о неразглашении',
            type: 'NDA',
            description: 'NDA с клиентом на весь срок сотрудничества',
            amount: 0,
            startDate: '2024-12-15',
            endDate: '2027-12-15',
            status: 'active',
            file: {
              name: 'nda.pdf',
              url: '/files/nda.pdf',
              size: 256000,
              uploadedAt: new Date(Date.now() - 86400000 * 45).toISOString(),
            },
            signedBy: 'Обе стороны',
            signedAt: '2024-12-15',
            createdAt: new Date(Date.now() - 86400000 * 45).toISOString(),
          },
          {
            id: 4,
            title: 'Черновик договора поддержки',
            type: 'Договор поддержки',
            description: 'Техническая поддержка после запуска проекта',
            amount: 50000,
            startDate: '2025-07-01',
            endDate: '2026-07-01',
            status: 'draft',
            createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
          },
        ])
      }
    } catch (err) {
      console.error('Error loading contracts:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddContract = async () => {
    if (!formData.title.trim()) return

    try {
      const formDataToSend = new FormData()
      Object.entries(formData).forEach(([key, value]) => {
        formDataToSend.append(key, String(value))
      })

      if (uploadingFile) {
        formDataToSend.append('file', uploadingFile)
      }

      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/contracts`,
        {
          method: 'POST',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: formDataToSend,
        }
      )

      if (response.ok) {
        setFormData({
          title: '',
          type: CONTRACT_TYPES[0],
          description: '',
          amount: 0,
          startDate: '',
          endDate: '',
          status: 'draft',
        })
        setUploadingFile(null)
        setIsAdding(false)
        await loadContracts()
      }
    } catch (err) {
      console.error('Error adding contract:', err)
    }
  }

  const handleDeleteContract = async (contractId: number) => {
    if (!confirm('Удалить этот договор?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/contracts/${contractId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadContracts()
      }
    } catch (err) {
      console.error('Error deleting contract:', err)
    }
  }

  const handleDownloadContract = (contract: Contract) => {
    if (contract.file) {
      window.open(contract.file.url, '_blank')
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploadingFile(file)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(date)
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-700 border-green-300'
      case 'draft':
        return 'bg-gray-100 text-gray-700 border-gray-300'
      case 'expired':
        return 'bg-red-100 text-red-700 border-red-300'
      case 'terminated':
        return 'bg-orange-100 text-orange-700 border-orange-300'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4" />
      case 'draft':
        return <Edit2 className="w-4 h-4" />
      case 'expired':
        return <AlertCircle className="w-4 h-4" />
      case 'terminated':
        return <X className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      draft: 'Черновик',
      active: 'Действует',
      expired: 'Истек',
      terminated: 'Расторгнут',
    }
    return labels[status] || status
  }

  if (!isOpen) return null

  const activeContracts = contracts.filter((c) => c.status === 'active').length
  const totalAmount = contracts
    .filter((c) => c.status === 'active')
    .reduce((sum, c) => sum + c.amount, 0)

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Управление контрактами</h3>
              <p className="text-emerald-100 text-sm mt-1">{projectName}</p>
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
          <div className="grid grid-cols-3 gap-4 mb-3">
            <div className="bg-white rounded-xl p-3 border-2 border-blue-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Всего контрактов</div>
              <div className="text-2xl font-bold text-blue-600">{contracts.length}</div>
            </div>
            <div className="bg-white rounded-xl p-3 border-2 border-green-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Активных</div>
              <div className="text-2xl font-bold text-green-600">{activeContracts}</div>
            </div>
            <div className="bg-white rounded-xl p-3 border-2 border-emerald-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Общая сумма</div>
              <div className="text-2xl font-bold text-emerald-600">
                {formatCurrency(totalAmount)}
              </div>
            </div>
          </div>

          {!isAdding && (
            <button
              onClick={() => setIsAdding(true)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-semibold text-sm"
            >
              <Plus className="w-4 h-4" />
              Добавить контракт
            </button>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Add Contract Form */}
          {isAdding && (
            <div className="mb-6 bg-emerald-50 border-2 border-emerald-200 rounded-xl p-4">
              <h4 className="font-bold text-gray-900 mb-4">Новый контракт</h4>

              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Название
                    </label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 outline-none"
                      placeholder="Название контракта"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Тип</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 outline-none"
                    >
                      {CONTRACT_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Описание
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 outline-none resize-none"
                    rows={2}
                    placeholder="Краткое описание контракта"
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Сумма (₽)
                    </label>
                    <input
                      type="number"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: Number(e.target.value) })}
                      className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 outline-none"
                      min="0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Дата начала
                    </label>
                    <input
                      type="date"
                      value={formData.startDate}
                      onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Дата окончания
                    </label>
                    <input
                      type="date"
                      value={formData.endDate}
                      onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Загрузить файл
                  </label>
                  <div className="flex items-center gap-3">
                    <label className="flex-1 px-4 py-2 border-2 border-dashed border-emerald-300 rounded-lg cursor-pointer hover:border-emerald-500 transition-colors">
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Upload className="w-4 h-4" />
                        {uploadingFile ? uploadingFile.name : 'Выберите файл PDF или DOCX'}
                      </div>
                      <input
                        type="file"
                        onChange={handleFileSelect}
                        className="hidden"
                        accept=".pdf,.doc,.docx"
                      />
                    </label>
                    {uploadingFile && (
                      <button
                        onClick={() => setUploadingFile(null)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleAddContract}
                    disabled={!formData.title.trim()}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                  >
                    <Check className="w-4 h-4" />
                    Создать
                  </button>
                  <button
                    onClick={() => {
                      setIsAdding(false)
                      setFormData({
                        title: '',
                        type: CONTRACT_TYPES[0],
                        description: '',
                        amount: 0,
                        startDate: '',
                        endDate: '',
                        status: 'draft',
                      })
                      setUploadingFile(null)
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Contracts List */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка контрактов...</div>
          ) : contracts.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">Нет контрактов</p>
              <p className="text-sm mt-2">Добавьте первый контракт проекта</p>
            </div>
          ) : (
            <div className="space-y-3">
              {contracts.map((contract) => (
                <div
                  key={contract.id}
                  className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-emerald-400 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h5 className="font-bold text-gray-900 text-lg">{contract.title}</h5>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold border-2 flex items-center gap-1 ${getStatusColor(
                            contract.status
                          )}`}
                        >
                          {getStatusIcon(contract.status)}
                          {getStatusLabel(contract.status)}
                        </span>
                      </div>

                      <p className="text-sm text-gray-700 mb-3">{contract.description}</p>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                        <div className="flex items-center gap-2 text-sm">
                          <FileText className="w-4 h-4 text-gray-500" />
                          <span className="text-gray-600">{contract.type}</span>
                        </div>

                        <div className="flex items-center gap-2 text-sm">
                          <DollarSign className="w-4 h-4 text-gray-500" />
                          <span className="font-bold text-gray-900">
                            {formatCurrency(contract.amount)}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 text-sm">
                          <Calendar className="w-4 h-4 text-gray-500" />
                          <span className="text-gray-600">{formatDate(contract.startDate)}</span>
                        </div>

                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span className="text-gray-600">{formatDate(contract.endDate)}</span>
                        </div>
                      </div>

                      {contract.file && (
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <FileText className="w-8 h-8 text-emerald-600" />
                              <div>
                                <div className="text-sm font-semibold text-gray-900">
                                  {contract.file.name}
                                </div>
                                <div className="text-xs text-gray-500">
                                  {formatFileSize(contract.file.size)} •{' '}
                                  {formatDate(contract.file.uploadedAt)}
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleDownloadContract(contract)}
                                className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                                title="Скачать"
                              >
                                <Download className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDownloadContract(contract)}
                                className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors"
                                title="Просмотреть"
                              >
                                <Eye className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {contract.signedBy && contract.signedAt && (
                        <div className="mt-3 flex items-center gap-2 text-xs text-gray-600">
                          <User className="w-3.5 h-3.5" />
                          <span>
                            Подписано: {contract.signedBy} • {formatDate(contract.signedAt)}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => handleDeleteContract(contract.id)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            Контрактов: <span className="font-bold text-emerald-600">{contracts.length}</span>
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
