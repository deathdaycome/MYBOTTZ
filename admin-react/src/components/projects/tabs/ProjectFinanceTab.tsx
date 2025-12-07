import { DollarSign, TrendingUp, TrendingDown, Plus, CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface Payment {
  id: number
  type: string
  amount: number
  status: string
  due_date: string | null
  paid_at: string | null
  description: string
}

interface ProjectFinanceTabProps {
  projectId: number
  estimatedCost: number
  executorCost: number
  finalCost: number
  clientPaidTotal: number
  executorPaidTotal: number
  payments: Payment[]
}

const getPaymentTypeName = (type: string) => {
  const names: Record<string, string> = {
    prepayment: 'Предоплата',
    milestone: 'Этап',
    final: 'Окончательный расчёт',
    additional: 'Дополнительные работы',
  }
  return names[type] || type
}

const getPaymentStatusBadge = (status: string) => {
  const badges: Record<string, { label: string; className: string; icon: any }> = {
    planned: { label: 'Запланировано', className: 'bg-gray-100 text-gray-700', icon: Clock },
    pending: { label: 'Ожидает оплаты', className: 'bg-yellow-100 text-yellow-700', icon: AlertCircle },
    paid: { label: 'Оплачено', className: 'bg-green-100 text-green-700', icon: CheckCircle },
    overdue: { label: 'Просрочено', className: 'bg-red-100 text-red-700', icon: AlertCircle },
  }
  return badges[status] || badges.planned
}

export const ProjectFinanceTab = ({
  projectId,
  estimatedCost,
  executorCost,
  finalCost,
  clientPaidTotal,
  executorPaidTotal,
  payments,
}: ProjectFinanceTabProps) => {
  const profit = estimatedCost - executorCost
  const profitMargin = estimatedCost > 0 ? ((profit / estimatedCost) * 100).toFixed(1) : 0
  const clientDebt = estimatedCost - clientPaidTotal
  const executorDebt = executorCost - executorPaidTotal

  return (
    <div className="p-6 space-y-6">
      {/* Финансовая сводка */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Стоимость клиента */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">Стоимость клиента</span>
          </div>
          <p className="text-2xl font-bold text-blue-900">{estimatedCost.toLocaleString('ru-RU')} ₽</p>
          {clientPaidTotal > 0 && (
            <p className="text-sm text-blue-700 mt-1">
              Оплачено: {clientPaidTotal.toLocaleString('ru-RU')} ₽
            </p>
          )}
        </div>

        {/* Стоимость исполнителя */}
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-5 h-5 text-orange-600" />
            <span className="text-sm font-medium text-orange-900">Стоимость исполнителя</span>
          </div>
          <p className="text-2xl font-bold text-orange-900">{executorCost.toLocaleString('ru-RU')} ₽</p>
          {executorPaidTotal > 0 && (
            <p className="text-sm text-orange-700 mt-1">
              Выплачено: {executorPaidTotal.toLocaleString('ru-RU')} ₽
            </p>
          )}
        </div>

        {/* Прибыль */}
        <div
          className={`bg-gradient-to-br ${
            profit >= 0 ? 'from-green-50 to-green-100 border-green-200' : 'from-red-50 to-red-100 border-red-200'
          } border rounded-lg p-4`}
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className={`w-5 h-5 ${profit >= 0 ? 'text-green-600' : 'text-red-600'}`} />
            <span className={`text-sm font-medium ${profit >= 0 ? 'text-green-900' : 'text-red-900'}`}>
              Прибыль
            </span>
          </div>
          <p className={`text-2xl font-bold ${profit >= 0 ? 'text-green-900' : 'text-red-900'}`}>
            {profit.toLocaleString('ru-RU')} ₽
          </p>
          <p className={`text-sm ${profit >= 0 ? 'text-green-700' : 'text-red-700'} mt-1`}>
            Маржа: {profitMargin}%
          </p>
        </div>

        {/* Задолженность */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-purple-600" />
            <span className="text-sm font-medium text-purple-900">Задолженность</span>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-purple-900">
              Клиент: <span className="font-bold">{clientDebt.toLocaleString('ru-RU')} ₽</span>
            </p>
            <p className="text-sm text-purple-900">
              Исполнитель: <span className="font-bold">{executorDebt.toLocaleString('ru-RU')} ₽</span>
            </p>
          </div>
        </div>
      </div>

      {/* График платежей */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-md">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h4 className="font-semibold text-gray-900 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-purple-600" />
            График платежей
          </h4>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all text-sm font-medium">
            <Plus className="w-4 h-4" />
            Добавить платёж
          </button>
        </div>

        {payments.length === 0 ? (
          <div className="p-8 text-center">
            <DollarSign className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">График платежей не создан</p>
            <p className="text-gray-400 text-sm mt-1">Добавьте платежи для отслеживания оплат</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {payments.map((payment) => {
              const statusBadge = getPaymentStatusBadge(payment.status)
              const StatusIcon = statusBadge.icon

              return (
                <div key={payment.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                        <DollarSign className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <h5 className="font-semibold text-gray-900">{getPaymentTypeName(payment.type)}</h5>
                        {payment.description && <p className="text-sm text-gray-500">{payment.description}</p>}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900">{payment.amount.toLocaleString('ru-RU')} ₽</p>
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${statusBadge.className}`}>
                        <StatusIcon className="w-3 h-3" />
                        {statusBadge.label}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-4 text-xs text-gray-500 ml-13">
                    {payment.due_date && (
                      <span>Срок: {new Date(payment.due_date).toLocaleDateString('ru-RU')}</span>
                    )}
                    {payment.paid_at && (
                      <span>Оплачено: {new Date(payment.paid_at).toLocaleDateString('ru-RU')}</span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
