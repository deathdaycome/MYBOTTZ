import { useState } from 'react'
import { Filter, X } from 'lucide-react'

interface AdvancedFiltersProps {
  onApply: (filters: FilterValues) => void
  executors: Array<{ id: number; username: string }>
  clients: Array<{ id: number; first_name: string; username: string }>
}

export interface FilterValues {
  executorId: number | null
  clientId: number | null
  colorFilter: string
  dateFrom: string
  dateTo: string
  hasPayment: string
}

export const AdvancedFilters = ({ onApply, executors, clients }: AdvancedFiltersProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [filters, setFilters] = useState<FilterValues>({
    executorId: null,
    clientId: null,
    colorFilter: '',
    dateFrom: '',
    dateTo: '',
    hasPayment: '',
  })

  const handleApply = () => {
    onApply(filters)
    setIsOpen(false)
  }

  const handleClear = () => {
    const clearedFilters: FilterValues = {
      executorId: null,
      clientId: null,
      colorFilter: '',
      dateFrom: '',
      dateTo: '',
      hasPayment: '',
    }
    setFilters(clearedFilters)
    onApply(clearedFilters)
  }

  const hasActiveFilters = filters.executorId || filters.clientId || filters.colorFilter || filters.dateFrom || filters.dateTo || filters.hasPayment

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`px-4 py-2 rounded-xl font-medium transition-all flex items-center gap-2 ${
          hasActiveFilters
            ? 'bg-purple-600 text-white hover:bg-purple-700'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        <Filter className="w-4 h-4" />
        Расширенные фильтры
        {hasActiveFilters && (
          <span className="bg-white text-purple-600 px-2 py-0.5 rounded-full text-xs font-bold">
            {[filters.executorId, filters.clientId, filters.colorFilter, filters.dateFrom, filters.hasPayment].filter(Boolean).length}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          {/* Overlay */}
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-gray-200 z-50">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-gray-900">Расширенные фильтры</h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-4 space-y-4 max-h-[500px] overflow-y-auto">
              {/* Исполнитель */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Исполнитель
                </label>
                <select
                  value={filters.executorId || ''}
                  onChange={(e) =>
                    setFilters({ ...filters, executorId: e.target.value ? Number(e.target.value) : null })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                >
                  <option value="">Все исполнители</option>
                  {executors.map((executor) => (
                    <option key={executor.id} value={executor.id}>
                      {executor.username}
                    </option>
                  ))}
                </select>
              </div>

              {/* Клиент */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Клиент
                </label>
                <select
                  value={filters.clientId || ''}
                  onChange={(e) =>
                    setFilters({ ...filters, clientId: e.target.value ? Number(e.target.value) : null })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                >
                  <option value="">Все клиенты</option>
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      {client.first_name} (@{client.username})
                    </option>
                  ))}
                </select>
              </div>

              {/* Цвет */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Цвет проекта
                </label>
                <select
                  value={filters.colorFilter}
                  onChange={(e) => setFilters({ ...filters, colorFilter: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                >
                  <option value="">Все цвета</option>
                  <option value="default">🔘 Серый</option>
                  <option value="green">🟢 Зеленый</option>
                  <option value="yellow">🟡 Желтый</option>
                  <option value="red">🔴 Красный</option>
                </select>
              </div>

              {/* Дата создания */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Дата создания
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="date"
                    value={filters.dateFrom}
                    onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                    placeholder="С"
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  />
                  <input
                    type="date"
                    value={filters.dateTo}
                    onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                    placeholder="По"
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>

              {/* Наличие оплаты */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Оплата
                </label>
                <select
                  value={filters.hasPayment}
                  onChange={(e) => setFilters({ ...filters, hasPayment: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                >
                  <option value="">Все проекты</option>
                  <option value="paid">С оплатой</option>
                  <option value="unpaid">Без оплаты</option>
                  <option value="partially">Частично оплачен</option>
                  <option value="fully">Полностью оплачен</option>
                </select>
              </div>
            </div>

            <div className="p-4 border-t border-gray-200 flex gap-2">
              <button
                onClick={handleApply}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold"
              >
                Применить
              </button>
              <button
                onClick={handleClear}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold"
              >
                Сбросить
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
