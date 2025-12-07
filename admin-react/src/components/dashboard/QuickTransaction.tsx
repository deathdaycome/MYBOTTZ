import { useState, useEffect } from 'react'
import { Plus, CheckCircle, AlertCircle } from 'lucide-react'
import { apiService } from '../../services/api'

interface Category {
  id: number
  name: string
}

interface QuickTransactionProps {
  onSuccess?: () => void
}

export const QuickTransaction = ({ onSuccess }: QuickTransactionProps) => {
  const [type, setType] = useState<'income' | 'expense'>('income')
  const [amount, setAmount] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [account, setAccount] = useState('cash')
  const [description, setDescription] = useState('')
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(false)
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const loadCategories = async (transactionType: 'income' | 'expense') => {
    try {
      const response = await apiService.getFinanceCategories(transactionType)
      if (response.success) {
        setCategories(response.data)
        setCategoryId('') // Reset category when type changes
      }
    } catch (error) {
      console.error('Error loading categories:', error)
    }
  }

  useEffect(() => {
    loadCategories(type)
  }, [type])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!amount || !categoryId) {
      setAlert({ type: 'error', message: 'Заполните все обязательные поля' })
      return
    }

    setLoading(true)
    setAlert(null)

    try {
      const response = await apiService.createTransaction({
        type,
        amount: parseFloat(amount),
        category_id: parseInt(categoryId),
        account,
        description,
        date: new Date().toISOString(),
      })

      if (response.success) {
        setAlert({ type: 'success', message: 'Транзакция добавлена успешно!' })

        // Reset form
        setAmount('')
        setCategoryId('')
        setDescription('')
        setType('income')

        // Call onSuccess callback
        if (onSuccess) {
          onSuccess()
        }

        // Hide alert after 3 seconds
        setTimeout(() => {
          setAlert(null)
        }, 3000)
      } else {
        setAlert({ type: 'error', message: response.error || 'Ошибка добавления транзакции' })
      }
    } catch (error: any) {
      setAlert({ type: 'error', message: error.message || 'Ошибка при отправке данных' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Plus className="w-5 h-5 text-purple-600" />
        Быстрая транзакция
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Transaction Type */}
        <div className="flex gap-4">
          <label className="flex-1 cursor-pointer">
            <input
              type="radio"
              name="type"
              value="income"
              checked={type === 'income'}
              onChange={(e) => setType(e.target.value as 'income')}
              className="sr-only peer"
            />
            <div className="px-4 py-2 rounded-xl text-center font-semibold transition-all border-2 peer-checked:border-green-500 peer-checked:bg-green-50 peer-checked:text-green-700 border-gray-200 text-gray-600">
              Доход
            </div>
          </label>
          <label className="flex-1 cursor-pointer">
            <input
              type="radio"
              name="type"
              value="expense"
              checked={type === 'expense'}
              onChange={(e) => setType(e.target.value as 'expense')}
              className="sr-only peer"
            />
            <div className="px-4 py-2 rounded-xl text-center font-semibold transition-all border-2 peer-checked:border-red-500 peer-checked:bg-red-50 peer-checked:text-red-700 border-gray-200 text-gray-600">
              Расход
            </div>
          </label>
        </div>

        {/* Amount */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Сумма *
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            step="0.01"
            min="0"
            required
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="0.00"
          />
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Категория *
          </label>
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            required
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
          >
            <option value="">Выберите...</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        {/* Account */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Счет
          </label>
          <select
            value={account}
            onChange={(e) => setAccount(e.target.value)}
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
          >
            <option value="cash">Наличные</option>
            <option value="card">Карта</option>
            <option value="bank">Банк</option>
          </select>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Описание
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
            placeholder="Описание транзакции..."
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Добавление...
            </>
          ) : (
            <>
              <Plus className="w-5 h-5" />
              Добавить транзакцию
            </>
          )}
        </button>

        {/* Alert */}
        {alert && (
          <div
            className={`flex items-center gap-2 px-4 py-3 rounded-xl ${
              alert.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {alert.type === 'success' ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <AlertCircle className="w-5 h-5" />
            )}
            <span className="font-medium">{alert.message}</span>
          </div>
        )}
      </form>
    </div>
  )
}
