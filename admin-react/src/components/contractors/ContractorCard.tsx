import { Eye, Edit, Trash2, DollarSign, Star } from 'lucide-react'
import type { Contractor } from '../../api/contractors'

interface ContractorCardProps {
  contractor: Contractor
  onView: () => void
  onEdit: () => void
  onDelete: () => void
  onCreatePayment: () => void
}

export const ContractorCard = ({
  contractor,
  onView,
  onEdit,
  onDelete,
  onCreatePayment,
}: ContractorCardProps) => {
  const displayName =
    contractor.first_name && contractor.last_name
      ? `${contractor.first_name} ${contractor.last_name}`
      : contractor.username

  const formatCurrency = (amount?: number) => {
    if (!amount) return '0 ₽'
    return `${amount.toLocaleString('ru-RU')} ₽`
  }

  return (
    <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-200 overflow-hidden border border-gray-100">
      {/* Header with gradient */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-2">{displayName}</h3>
            <div className="flex flex-wrap gap-2">
              <span className="inline-block px-3 py-1 bg-green-500 text-white text-xs rounded-full font-medium">
                Исполнитель
              </span>
              <span className="inline-block px-3 py-1 bg-blue-500 text-white text-xs rounded-full font-medium">
                Фриланс
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-yellow-300">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-4 h-4 fill-current" />
              ))}
            </div>
            <span className="text-sm mt-1 block">5/5</span>
          </div>
        </div>
      </div>

      {/* Info section */}
      <div className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-gray-500 mb-1">Email</p>
            <p className="text-sm text-gray-900 truncate" title={contractor.email}>
              {contractor.email || 'Не указан'}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-500 mb-1">Username</p>
            <p className="text-sm text-gray-900 truncate" title={contractor.username}>
              {contractor.username || 'Не указан'}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-semibold text-gray-500 mb-1">Дата создания</p>
            <p className="text-sm text-gray-900">
              {contractor.created_at
                ? new Date(contractor.created_at).toLocaleDateString('ru-RU')
                : 'Не указана'}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-500 mb-1">Статус</p>
            <span
              className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                contractor.is_active
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {contractor.is_active ? 'Активен' : 'Неактивен'}
            </span>
          </div>
        </div>
      </div>

      {/* Stats section */}
      <div className="bg-gray-50 px-6 py-4 grid grid-cols-3 gap-4 border-t border-gray-100">
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">0</div>
          <div className="text-xs text-gray-500">Проектов</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">0</div>
          <div className="text-xs text-gray-500">Активных</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900 truncate" title={formatCurrency(contractor.total_payments)}>
            {contractor.total_payments
              ? formatCurrency(contractor.total_payments).slice(0, 10) + (formatCurrency(contractor.total_payments).length > 10 ? '...' : '')
              : '0 ₽'}
          </div>
          <div className="text-xs text-gray-500">Выплачено</div>
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 flex flex-wrap gap-2 border-t border-gray-100">
        <button
          onClick={onView}
          className="flex items-center gap-1 px-3 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
        >
          <Eye className="w-4 h-4" />
          <span className="hidden sm:inline">Детали</span>
        </button>
        <button
          onClick={onCreatePayment}
          className="flex items-center gap-1 px-3 py-2 text-sm bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
        >
          <DollarSign className="w-4 h-4" />
          <span className="hidden sm:inline">Выплата</span>
        </button>
        <button
          onClick={onEdit}
          className="flex items-center gap-1 px-3 py-2 text-sm bg-yellow-50 text-yellow-600 rounded-lg hover:bg-yellow-100 transition-colors"
        >
          <Edit className="w-4 h-4" />
          <span className="hidden sm:inline">Редактировать</span>
        </button>
        <button
          onClick={onDelete}
          className="flex items-center gap-1 px-3 py-2 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          <span className="hidden sm:inline">Удалить</span>
        </button>
      </div>
    </div>
  )
}
