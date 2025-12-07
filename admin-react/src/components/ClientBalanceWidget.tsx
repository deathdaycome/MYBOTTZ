import { useState, useEffect } from 'react'
import { Wallet, TrendingUp, AlertCircle, Plus } from 'lucide-react'
import hostingApi from '../api/hosting'

interface ClientBalanceWidgetProps {
  clientId: number | null
  clientName: string
  onBalanceUpdate?: () => void
}

export default function ClientBalanceWidget({
  clientId,
  clientName,
  onBalanceUpdate,
}: ClientBalanceWidgetProps) {
  const [balance, setBalance] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [addAmount, setAddAmount] = useState('')
  const [addDescription, setAddDescription] = useState('')

  useEffect(() => {
    if (clientId) {
      loadBalance()
    }
  }, [clientId])

  const loadBalance = async () => {
    if (!clientId) return

    try {
      setLoading(true)
      const response = await hostingApi.getClientBalance(clientId)
      setBalance(response.balance)
    } catch (error: any) {
      // Если клиента нет - создастся автоматически при первом пополнении
      console.log('Balance not found for client', clientId)
    } finally {
      setLoading(false)
    }
  }

  const handleAddBalance = async () => {
    if (!clientId || !addAmount) return

    try {
      await hostingApi.addClientBalance(clientId, parseFloat(addAmount), addDescription)
      setShowAddModal(false)
      setAddAmount('')
      setAddDescription('')
      loadBalance()
      onBalanceUpdate?.()
    } catch (error: any) {
      alert('Ошибка пополнения баланса: ' + error.message)
    }
  }

  if (!clientId) {
    return (
      <div className="text-sm text-gray-500">
        Укажите Client ID
      </div>
    )
  }

  if (loading) {
    return <div className="text-sm text-gray-500">Загрузка...</div>
  }

  const daysRemaining = balance?.days_remaining || 0
  const balanceAmount = balance?.balance || 0
  const monthlyCost = balance?.total_monthly_cost || 0

  const getDaysColor = () => {
    if (daysRemaining === 0) return 'text-red-600 bg-red-50'
    if (daysRemaining <= 3) return 'text-orange-600 bg-orange-50'
    if (daysRemaining <= 7) return 'text-yellow-600 bg-yellow-50'
    if (daysRemaining >= 999) return 'text-gray-500 bg-gray-50'
    return 'text-green-600 bg-green-50'
  }

  const getDaysIcon = () => {
    if (daysRemaining === 0) return <AlertCircle className="w-3.5 h-3.5" />
    if (daysRemaining <= 7) return <AlertCircle className="w-3.5 h-3.5" />
    return <TrendingUp className="w-3.5 h-3.5" />
  }

  const formatDays = () => {
    if (daysRemaining >= 999) return '∞'
    return `${daysRemaining} дн`
  }

  return (
    <>
      <div className="flex flex-col gap-2">
        {/* Баланс */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-sm bg-gray-50 px-2 py-1 rounded">
            <Wallet className="w-4 h-4 text-gray-500" />
            <span className="font-semibold text-gray-900">{balanceAmount.toFixed(0)}₽</span>
          </div>

          {/* Дни */}
          <div className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded ${getDaysColor()}`}>
            {getDaysIcon()}
            <span>{formatDays()}</span>
          </div>

          {/* Кнопка пополнения */}
          <button
            onClick={() => setShowAddModal(true)}
            className="p-1 hover:bg-blue-50 rounded transition-colors group"
            title="Пополнить баланс"
          >
            <Plus className="w-4 h-4 text-blue-600 group-hover:text-blue-700" />
          </button>
        </div>

        {/* Месячная стоимость */}
        {monthlyCost > 0 && (
          <div className="text-xs text-gray-500">
            {monthlyCost.toFixed(0)}₽/мес
          </div>
        )}
      </div>

      {/* Модальное окно пополнения */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">
              Пополнить баланс: {clientName}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Сумма пополнения (₽)
                </label>
                <input
                  type="number"
                  value={addAmount}
                  onChange={(e) => setAddAmount(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="4000"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Комментарий (опционально)
                </label>
                <input
                  type="text"
                  value={addDescription}
                  onChange={(e) => setAddDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Пополнение баланса"
                />
              </div>

              {balance && monthlyCost > 0 && addAmount && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm">
                  <div className="flex items-center gap-2 text-blue-700 font-medium mb-1">
                    <TrendingUp className="w-4 h-4" />
                    Прогноз
                  </div>
                  <div className="text-blue-600">
                    Новый баланс: {(balanceAmount + parseFloat(addAmount || '0')).toFixed(0)}₽
                  </div>
                  <div className="text-blue-600">
                    Хватит на: ~{Math.floor((balanceAmount + parseFloat(addAmount || '0')) / (monthlyCost / 30))} дней
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2 mt-6">
              <button
                onClick={handleAddBalance}
                disabled={!addAmount || parseFloat(addAmount) <= 0}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Пополнить
              </button>
              <button
                onClick={() => {
                  setShowAddModal(false)
                  setAddAmount('')
                  setAddDescription('')
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
