import { useState, useEffect } from 'react'
import { Eye, EyeOff, Settings } from 'lucide-react'

// Column configuration interface
export interface ColumnConfig {
  id: string
  label: string
  visible: boolean
  required?: boolean
}

interface ColumnVisibilityControlProps {
  columns: ColumnConfig[]
  onChange: (columns: ColumnConfig[]) => void
  storageKey?: string
}

export const ColumnVisibilityControl = ({
  columns,
  onChange,
  storageKey = 'column-visibility',
}: ColumnVisibilityControlProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [localColumns, setLocalColumns] = useState(columns)

  useEffect(() => {
    // Load from localStorage on mount
    if (storageKey) {
      try {
        const stored = localStorage.getItem(storageKey)
        if (stored) {
          const storedVisibility = JSON.parse(stored) as Record<string, boolean>
          const updatedColumns = columns.map((col) => ({
            ...col,
            visible: storedVisibility[col.id] ?? col.visible,
          }))
          setLocalColumns(updatedColumns)
          onChange(updatedColumns)
        }
      } catch (err) {
        console.error('Error loading column visibility:', err)
      }
    }
  }, [])

  const toggleColumn = (columnId: string) => {
    const updated = localColumns.map((col) =>
      col.id === columnId && !col.required ? { ...col, visible: !col.visible } : col
    )
    setLocalColumns(updated)
    onChange(updated)

    // Save to localStorage
    if (storageKey) {
      try {
        const visibility = updated.reduce(
          (acc, col) => ({ ...acc, [col.id]: col.visible }),
          {}
        )
        localStorage.setItem(storageKey, JSON.stringify(visibility))
      } catch (err) {
        console.error('Error saving column visibility:', err)
      }
    }
  }

  const showAll = () => {
    const updated = localColumns.map((col) => ({ ...col, visible: true }))
    setLocalColumns(updated)
    onChange(updated)

    if (storageKey) {
      try {
        const visibility = updated.reduce(
          (acc, col) => ({ ...acc, [col.id]: col.visible }),
          {}
        )
        localStorage.setItem(storageKey, JSON.stringify(visibility))
      } catch (err) {
        console.error('Error saving column visibility:', err)
      }
    }
  }

  const hideAll = () => {
    const updated = localColumns.map((col) =>
      col.required ? col : { ...col, visible: false }
    )
    setLocalColumns(updated)
    onChange(updated)

    if (storageKey) {
      try {
        const visibility = updated.reduce(
          (acc, col) => ({ ...acc, [col.id]: col.visible }),
          {}
        )
        localStorage.setItem(storageKey, JSON.stringify(visibility))
      } catch (err) {
        console.error('Error saving column visibility:', err)
      }
    }
  }

  const visibleCount = localColumns.filter((col) => col.visible).length

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
        title="Настроить колонки"
      >
        <Settings className="w-4 h-4" />
        <span>Колонки ({visibleCount})</span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div className="absolute right-0 top-full mt-2 w-72 bg-white rounded-xl shadow-2xl border-2 border-gray-200 z-50 overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 bg-gradient-to-r from-gray-700 to-gray-800 text-white">
              <h3 className="font-semibold text-sm">Настройка колонок</h3>
              <p className="text-xs text-gray-300 mt-1">
                Видимых колонок: {visibleCount} из {localColumns.length}
              </p>
            </div>

            {/* Columns List */}
            <div className="max-h-96 overflow-y-auto p-2">
              {localColumns.map((column) => (
                <label
                  key={column.id}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                    column.required
                      ? 'opacity-50 cursor-not-allowed'
                      : 'hover:bg-gray-100 cursor-pointer'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={column.visible}
                    onChange={() => !column.required && toggleColumn(column.id)}
                    disabled={column.required}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">{column.label}</span>
                      {column.required && (
                        <span className="text-xs text-gray-500 font-medium">(обязательная)</span>
                      )}
                    </div>
                  </div>
                  {column.visible ? (
                    <Eye className="w-4 h-4 text-green-600" />
                  ) : (
                    <EyeOff className="w-4 h-4 text-gray-400" />
                  )}
                </label>
              ))}
            </div>

            {/* Footer Actions */}
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex gap-2">
              <button
                onClick={showAll}
                className="flex-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-xs font-semibold"
              >
                Показать все
              </button>
              <button
                onClick={hideAll}
                className="flex-1 px-3 py-1.5 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-xs font-semibold"
              >
                Скрыть все
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

// Hook for managing column visibility
export const useColumnVisibility = (
  defaultColumns: ColumnConfig[],
  storageKey: string = 'column-visibility'
) => {
  const [columns, setColumns] = useState<ColumnConfig[]>(defaultColumns)

  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const storedVisibility = JSON.parse(stored) as Record<string, boolean>
        const updatedColumns = defaultColumns.map((col) => ({
          ...col,
          visible: storedVisibility[col.id] ?? col.visible,
        }))
        setColumns(updatedColumns)
      }
    } catch (err) {
      console.error('Error loading column visibility:', err)
    }
  }, [storageKey])

  const updateColumns = (newColumns: ColumnConfig[]) => {
    setColumns(newColumns)
    try {
      const visibility = newColumns.reduce(
        (acc, col) => ({ ...acc, [col.id]: col.visible }),
        {}
      )
      localStorage.setItem(storageKey, JSON.stringify(visibility))
    } catch (err) {
      console.error('Error saving column visibility:', err)
    }
  }

  const isVisible = (columnId: string): boolean => {
    const column = columns.find((col) => col.id === columnId)
    return column?.visible ?? false
  }

  return {
    columns,
    updateColumns,
    isVisible,
  }
}
