import { useState, useEffect } from 'react'
import { X, Eye, Edit, Trash2, Calendar, DollarSign } from 'lucide-react'
import contractorsApi from '../../api/contractors'
import type { ContractorDetails, ContractorAssignment, ContractorPayment } from '../../api/contractors'

interface ContractorViewModalProps {
  isOpen: boolean
  onClose: () => void
  contractorId: number
  onEdit: () => void
  onDelete: () => void
}

export const ContractorViewModal = ({
  isOpen,
  onClose,
  contractorId,
  onEdit,
  onDelete,
}: ContractorViewModalProps) => {
  const [loading, setLoading] = useState(false)
  const [contractor, setContractor] = useState<ContractorDetails | null>(null)
  const [assignments, setAssignments] = useState<ContractorAssignment[]>([])
  const [payments, setPayments] = useState<ContractorPayment[]>([])

  useEffect(() => {
    if (isOpen) {
      loadContractorDetails()
    }
  }, [isOpen, contractorId])

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

  const loadContractorDetails = async () => {
    try {
      setLoading(true)
      const response = await contractorsApi.getContractor(contractorId)

      if (response.success) {
        setContractor(response.contractor)
        setAssignments(response.assignments || [])
        setPayments(response.payments || [])
      }
    } catch (error) {
      console.error('Error loading contractor details:', error)
      alert('Ошибка загрузки данных исполнителя')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Не указано'
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; color: string }> = {
      pending: { label: 'В ожидании', color: 'bg-yellow-100 text-yellow-800' },
      paid: { label: 'Оплачено', color: 'bg-green-100 text-green-800' },
      cancelled: { label: 'Отменено', color: 'bg-red-100 text-red-800' },
      active: { label: 'Активно', color: 'bg-blue-100 text-blue-800' },
      completed: { label: 'Завершено', color: 'bg-gray-100 text-gray-800' },
    }

    const statusInfo = statusMap[status] || { label: status, color: 'bg-gray-100 text-gray-800' }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusInfo.color}`}>
        {statusInfo.label}
      </span>
    )
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <Eye className="w-6 h-6" />
            <h3 className="text-xl font-bold">Просмотр исполнителя</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
          ) : contractor ? (
            <div className="space-y-6">
              {/* Contractor Info */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-lg font-bold text-gray-900 mb-4">Информация об исполнителе</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Имя пользователя</p>
                    <p className="text-gray-900">{contractor.username}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Email</p>
                    <p className="text-gray-900">{contractor.email}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Имя</p>
                    <p className="text-gray-900">{contractor.first_name || 'Не указано'}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Фамилия</p>
                    <p className="text-gray-900">{contractor.last_name || 'Не указано'}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Telegram ID</p>
                    <p className="text-gray-900">{contractor.telegram_id || 'Не указано'}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Статус</p>
                    <p className="text-gray-900">
                      {contractor.is_active ? (
                        <span className="text-green-600 font-semibold">Активен</span>
                      ) : (
                        <span className="text-red-600 font-semibold">Неактивен</span>
                      )}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Дата регистрации</p>
                    <p className="text-gray-900">{formatDate(contractor.created_at)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Последний вход</p>
                    <p className="text-gray-900">{formatDate(contractor.last_login)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-500">Всего выплат</p>
                    <p className="text-gray-900 font-bold text-lg">
                      {contractor.total_payments ? `${contractor.total_payments.toFixed(2)} ₽` : '0.00 ₽'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Assignments */}
              <div>
                <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Назначения на проекты ({assignments.length})
                </h4>
                {assignments.length > 0 ? (
                  <div className="space-y-3">
                    {assignments.map((assignment) => (
                      <div
                        key={assignment.id}
                        className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h5 className="font-semibold text-gray-900">{assignment.project_name}</h5>
                            <p className="text-sm text-gray-500">
                              {formatDate(assignment.start_date)} - {formatDate(assignment.end_date)}
                            </p>
                          </div>
                          {getStatusBadge(assignment.status)}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-8 text-center">
                    <p className="text-gray-500">Нет назначений на проекты</p>
                  </div>
                )}
              </div>

              {/* Payments */}
              <div>
                <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <DollarSign className="w-5 h-5" />
                  История выплат ({payments.length})
                </h4>
                {payments.length > 0 ? (
                  <div className="space-y-3">
                    {payments.map((payment) => (
                      <div
                        key={payment.id}
                        className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-green-300 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="font-bold text-lg text-gray-900">
                              {payment.amount.toFixed(2)} ₽
                            </p>
                            <p className="text-sm text-gray-500">{formatDate(payment.payment_date || payment.created_at)}</p>
                          </div>
                          {getStatusBadge(payment.status)}
                        </div>
                        <p className="text-gray-700">{payment.description}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-8 text-center">
                    <p className="text-gray-500">Нет истории выплат</p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={onEdit}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold"
                >
                  <Edit className="w-5 h-5" />
                  Редактировать
                </button>
                <button
                  type="button"
                  onClick={onDelete}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all font-semibold flex items-center gap-2"
                >
                  <Trash2 className="w-5 h-5" />
                  Удалить
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
                >
                  Закрыть
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
              <p className="text-red-900">Не удалось загрузить данные исполнителя</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
