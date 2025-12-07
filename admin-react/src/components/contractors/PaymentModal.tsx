import { useState, useEffect } from 'react'
import { X, DollarSign } from 'lucide-react'
import contractorsApi from '../../api/contractors'
import type { CreatePaymentData } from '../../api/contractors'

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  contractorId: number
  contractorName: string
}

export const PaymentModal = ({
  isOpen,
  onClose,
  onSuccess,
  contractorId,
  contractorName,
}: PaymentModalProps) => {
  const [loading, setLoading] = useState(false)

  const [formData, setFormData] = useState<CreatePaymentData>({
    amount: 0,
    description: '',
  })

  useEffect(() => {
    if (isOpen) {
      // Reset form on open
      setFormData({
        amount: 0,
        description: '',
      })
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.amount || formData.amount <= 0) {
      alert('Введите корректную сумму')
      return
    }

    if (!formData.description.trim()) {
      alert('Введите описание выплаты')
      return
    }

    try {
      setLoading(true)
      const response = await contractorsApi.createPayment(contractorId, formData)

      if (response.success) {
        onSuccess()
      }
    } catch (error) {
      console.error('Error creating payment:', error)
      alert('Ошибка создания выплаты')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof CreatePaymentData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <DollarSign className="w-6 h-6" />
            <h3 className="text-xl font-bold">Создать выплату</h3>
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
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Contractor Name */}
          <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <span className="font-semibold">Исполнитель:</span> {contractorName}
            </p>
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Сумма (₽) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={formData.amount || ''}
              onChange={(e) => handleChange('amount', e.target.value ? parseFloat(e.target.value) : 0)}
              min="0"
              step="0.01"
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
              placeholder="Введите сумму"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Описание <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all resize-none"
              placeholder="Введите описание выплаты (например: Оплата за разработку сайта)"
              required
            />
          </div>

          {/* Info */}
          <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4">
            <p className="text-sm text-green-900">
              <span className="font-semibold">Информация:</span> Выплата будет создана со статусом "В ожидании". После создания вы сможете подтвердить или отменить её.
            </p>
          </div>

          {/* Footer */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                <>
                  <DollarSign className="w-5 h-5" />
                  Создать выплату
                </>
              )}
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
        </form>
      </div>
    </div>
  )
}
