import { Filter, X } from 'lucide-react'

interface AdvancedFiltersProps {
  filters: FilterValues
  onChange: (filters: FilterValues) => void
  onClear?: () => void
  executors?: Array<{ id: number; username: string }>
  clients?: Array<{ id: number; first_name: string; username: string }>
}

export interface FilterValues {
  executorId: number | null
  clientId: number | null
  colorFilter: string
  dateFrom: string
  dateTo: string
  hasPayment: string
  hasOverdue: boolean
  noExecutor: boolean
  priceFrom: string
  priceTo: string
}

export const AdvancedFilters = ({ filters, onChange, onClear, executors = [], clients = [] }: AdvancedFiltersProps) => {
  const handleClear = () => {
    const clearedFilters: FilterValues = {
      executorId: null,
      clientId: null,
      colorFilter: '',
      dateFrom: '',
      dateTo: '',
      hasPayment: '',
      hasOverdue: false,
      noExecutor: false,
      priceFrom: '',
      priceTo: '',
    }
    onChange(clearedFilters)
    onClear?.()
  }

  const hasActiveFilters = filters.executorId || filters.clientId || filters.colorFilter || filters.dateFrom || filters.dateTo || filters.hasPayment || filters.hasOverdue || filters.noExecutor || filters.priceFrom || filters.priceTo

  return (
    <div className="relative group">
      <button
        className={`px-4 py-2 rounded-xl font-medium transition-all flex items-center gap-2 ${
          hasActiveFilters
            ? 'bg-purple-600 text-white hover:bg-purple-700'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
        }`}
      >
        <Filter className="w-4 h-4" />
        Фильтры
        {hasActiveFilters && (
          <span className="bg-white text-purple-600 dark:bg-gray-700 dark:text-purple-400 px-2 py-0.5 rounded-full text-xs font-bold">
            {[filters.executorId, filters.clientId, filters.colorFilter, filters.dateFrom, filters.hasPayment, filters.hasOverdue, filters.noExecutor, filters.priceFrom].filter(Boolean).length}
          </span>
        )}
      </button>

      {/* Dropdown */}
      <div className="hidden group-hover:block absolute right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-gray-900 dark:text-white">Расширенные фильтры</h3>
            <button
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              title="Очистить фильтры"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-4 space-y-4 max-h-[500px] overflow-y-auto">
          {/* Исполнитель */}
          {executors.length > 0 && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Исполнитель
              </label>
              <select
                value={filters.executorId || ''}
                onChange={(e) =>
                  onChange({ ...filters, executorId: e.target.value ? Number(e.target.value) : null })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
              >
                <option value="">Все исполнители</option>
                {executors.map((executor) => (
                  <option key={executor.id} value={executor.id}>
                    {executor.username}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Клиент */}
          {clients.length > 0 && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Клиент
              </label>
              <select
                value={filters.clientId || ''}
                onChange={(e) =>
                  onChange({ ...filters, clientId: e.target.value ? Number(e.target.value) : null })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
              >
                <option value="">Все клиенты</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.first_name} (@{client.username})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Цвет */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Цвет проекта
            </label>
            <select
              value={filters.colorFilter}
              onChange={(e) => onChange({ ...filters, colorFilter: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
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
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Дата создания
            </label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => onChange({ ...filters, dateFrom: e.target.value })}
                placeholder="С"
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
              />
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => onChange({ ...filters, dateTo: e.target.value })}
                placeholder="По"
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
              />
            </div>
          </div>

          {/* Наличие оплаты */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Оплата
            </label>
            <select
              value={filters.hasPayment}
              onChange={(e) => onChange({ ...filters, hasPayment: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
            >
              <option value="">Все проекты</option>
              <option value="paid">С оплатой</option>
              <option value="unpaid">Без оплаты</option>
              <option value="partially">Частично оплачен</option>
              <option value="fully">Полностью оплачен</option>
            </select>
          </div>

          {/* Диапазон стоимости */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Диапазон стоимости (₽)
            </label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                value={filters.priceFrom}
                onChange={(e) => onChange({ ...filters, priceFrom: e.target.value })}
                placeholder="От"
                min="0"
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
              />
              <input
                type="number"
                value={filters.priceTo}
                onChange={(e) => onChange({ ...filters, priceTo: e.target.value })}
                placeholder="До"
                min="0"
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
              />
            </div>
          </div>

          {/* Дополнительные опции */}
          <div className="space-y-3">
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
              Дополнительные фильтры
            </label>

            {/* Есть просрочка */}
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.hasOverdue}
                onChange={(e) => onChange({ ...filters, hasOverdue: e.target.checked })}
                className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">Есть просрочка</span>
            </label>

            {/* Нет исполнителя */}
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.noExecutor}
                onChange={(e) => onChange({ ...filters, noExecutor: e.target.checked })}
                className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">Нет исполнителя</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdvancedFilters
