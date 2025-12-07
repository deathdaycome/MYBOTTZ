import { useState, useEffect } from 'react'
import { X, AlertCircle, CreditCard } from 'lucide-react'

interface AddPaymentModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectCost: number
  paidTotal: number
  onPaymentAdded: () => void
}

export const AddPaymentModal = ({
  isOpen,
  onClose,
  projectId,
  projectCost = 0,
  paidTotal = 0,
  onPaymentAdded,
}: AddPaymentModalProps) => {
  const [paymentType, setPaymentType] = useState('prepayment')
  const [amount, setAmount] = useState<number>(0)
  const [paymentDate, setPaymentDate] = useState('')
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      const today = new Date().toISOString().split('T')[0]
      setPaymentDate(today)
      setPaymentType('prepayment')
      setAmount(0)
      setComment('')
      setError('')
    }
  }, [isOpen])

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

  const handleSubmit = async () => {
    if (!amount || amount <= 0) {
      setError('Пожалуйста, укажите сумму оплаты')
      return
    }

    if (!projectId) {
      setError('Не указан ID проекта')
      return
    }

    setLoading(true)
    setError('')

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/admin'
      const response = await fetch(`${apiUrl}/api/projects/${projectId}/payments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          payment_type: paymentType,
          amount: amount,
          payment_date: paymentDate,
          comment: comment || undefined,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        onPaymentAdded()
        onClose()
      } else {
        setError(data.message || 'Ошибка добавления оплаты')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen || !projectId) return null

  const remaining = projectCost - paidTotal

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CreditCard className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Добавление оплаты</h3>
              <p className="text-emerald-100 text-sm mt-1">Проект #{projectId}</p>
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

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Payment Summary */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
              <p className="text-xs text-blue-600 font-semibold mb-1">Общая стоимость</p>
              <p className="text-2xl font-bold text-blue-900">
                {projectCost.toLocaleString('ru-RU')} ₽
              </p>
            </div>
            <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4">
              <p className="text-xs text-green-600 font-semibold mb-1">Уже оплачено</p>
              <p className="text-2xl font-bold text-green-900">
                {paidTotal.toLocaleString('ru-RU')} ₽
              </p>
            </div>
            <div className="bg-orange-50 border-l-4 border-orange-500 rounded-lg p-4">
              <p className="text-xs text-orange-600 font-semibold mb-1">Осталось</p>
              <p className="text-2xl font-bold text-orange-900">
                {remaining.toLocaleString('ru-RU')} ₽
              </p>
            </div>
          </div>

          {/* Payment Type */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Тип оплаты <span className="text-red-500">*</span>
            </label>
            <select
              value={paymentType}
              onChange={(e) => setPaymentType(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
            >
              <option value="prepayment">Предоплата</option>
              <option value="partial">Частичная оплата</option>
              <option value="full">Полная оплата</option>
              <option value="final">Окончательный расчет</option>
            </select>
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Сумма оплаты (₽) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={amount || ''}
              onChange={(e) => setAmount(Number(e.target.value) || 0)}
              min="0"
              step="100"
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
              placeholder="Введите сумму"
            />
          </div>

          {/* Payment Date */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Дата оплаты <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={paymentDate}
              onChange={(e) => setPaymentDate(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
            />
          </div>

          {/* Comment */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Комментарий
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all resize-none"
              rows={3}
              placeholder="Добавьте комментарий к оплате (необязательно)"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-2 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading || !amount || amount <= 0}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Добавление...' : 'Добавить оплату'}
          </button>
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold disabled:opacity-50"
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  )
}
