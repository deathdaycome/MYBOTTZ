/**
 * Вкладка "Финансы" проекта
 * Платежи, бюджет, отчет по прибыли
 */

import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { DollarSign, Plus, TrendingUp, TrendingDown, Calendar, Loader2, CheckCircle, Clock } from 'lucide-react'
import axiosInstance from '../../services/api'

interface Project {
  id: number
  title: string
  budget?: number
}

interface Payment {
  id: number
  type: string
  amount: number
  status: string
  due_date?: string
  paid_at?: string
  description?: string
  created_at: string
}

interface PaymentSummary {
  total_amount: number
  paid_amount: number
  pending_amount: number
}

interface OutletContext {
  project: Project
}

export const ProjectFinance = () => {
  const { project } = useOutletContext<OutletContext>()
  const [payments, setPayments] = useState<Payment[]>([])
  const [summary, setSummary] = useState<PaymentSummary>({
    total_amount: 0,
    paid_amount: 0,
    pending_amount: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Загрузка платежей
  useEffect(() => {
    loadPayments()
  }, [project.id])

  const loadPayments = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(`/admin/api/projects/${project.id}/payments`)

      if (response.data.success) {
        setPayments(response.data.payments || [])
        setSummary(response.data.summary || { total_amount: 0, paid_amount: 0, pending_amount: 0 })
      }
      setError(null)
    } catch (err: any) {
      console.error('Error loading payments:', err)
      setError('Ошибка загрузки платежей')
    } finally {
      setLoading(false)
    }
  }

  // Типы платежей
  const paymentTypes: Record<string, string> = {
    PREPAYMENT: 'Предоплата',
    MILESTONE: 'Этап',
    FINAL: 'Финальный',
    ADDITIONAL: 'Дополнительный',
  }

  // Статусы платежей с цветами
  const paymentStatuses: Record<string, { label: string; color: string; icon: any }> = {
    PLANNED: { label: 'Запланирован', color: 'gray', icon: Clock },
    PENDING: { label: 'Ожидает', color: 'yellow', icon: Clock },
    PAID: { label: 'Оплачен', color: 'green', icon: CheckCircle },
    OVERDUE: { label: 'Просрочен', color: 'red', icon: TrendingDown },
  }

  const getPaymentStatusInfo = (status: string) => {
    return paymentStatuses[status] || paymentStatuses.PLANNED
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Финансы проекта</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors">
          <Plus className="w-4 h-4" />
          <span>Добавить платеж</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Карточки финансов */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 bg-blue-500 rounded-lg">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-blue-600 dark:text-blue-400">Общий бюджет</p>
              <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                {summary.total_amount.toLocaleString('ru-RU')} ₽
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-6 border border-green-200 dark:border-green-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 bg-green-500 rounded-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-green-600 dark:text-green-400">Оплачено</p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                {summary.paid_amount.toLocaleString('ru-RU')} ₽
              </p>
            </div>
          </div>
          <div className="w-full bg-green-200 dark:bg-green-900/50 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{
                width: `${summary.total_amount > 0 ? (summary.paid_amount / summary.total_amount) * 100 : 0}%`,
              }}
            ></div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-lg p-6 border border-red-200 dark:border-red-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 bg-red-500 rounded-lg">
              <TrendingDown className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-red-600 dark:text-red-400">Ожидается</p>
              <p className="text-2xl font-bold text-red-900 dark:text-red-100">
                {summary.pending_amount.toLocaleString('ru-RU')} ₽
              </p>
            </div>
          </div>
          <div className="w-full bg-red-200 dark:bg-red-900/50 rounded-full h-2">
            <div
              className="bg-red-500 h-2 rounded-full transition-all"
              style={{
                width: `${summary.total_amount > 0 ? (summary.pending_amount / summary.total_amount) * 100 : 0}%`,
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* История платежей */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">История платежей</h3>
        </div>

        {payments.length > 0 ? (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {payments.map((payment) => {
              const statusInfo = getPaymentStatusInfo(payment.status)
              const StatusIcon = statusInfo.icon

              return (
                <div key={payment.id} className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className={`p-2 bg-${statusInfo.color}-100 dark:bg-${statusInfo.color}-900/20 rounded-lg`}>
                        <StatusIcon className={`w-5 h-5 text-${statusInfo.color}-600 dark:text-${statusInfo.color}-400`} />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                            {paymentTypes[payment.type] || payment.type}
                          </h4>
                          <span
                            className={`px-2 py-0.5 rounded-full text-xs font-medium bg-${statusInfo.color}-100 text-${statusInfo.color}-700 dark:bg-${statusInfo.color}-900/30 dark:text-${statusInfo.color}-400`}
                          >
                            {statusInfo.label}
                          </span>
                        </div>

                        {payment.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{payment.description}</p>
                        )}

                        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                          {payment.due_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              <span>Срок: {new Date(payment.due_date).toLocaleDateString('ru-RU')}</span>
                            </div>
                          )}
                          {payment.paid_at && (
                            <div className="flex items-center gap-1">
                              <CheckCircle className="w-3 h-3" />
                              <span>Оплачено: {new Date(payment.paid_at).toLocaleDateString('ru-RU')}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {payment.amount.toLocaleString('ru-RU')} ₽
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="px-6 py-12 text-center">
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              Платежи для этого проекта еще не созданы
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProjectFinance
