// Filter presets utility for saving and loading filter configurations

export interface FilterPreset {
  id: string
  name: string
  filters: {
    searchTerm?: string
    statusFilter?: string
    complexityFilter?: string
    executorId?: number | null
    clientId?: number | null
    colorFilter?: string
    dateFrom?: string
    dateTo?: string
    hasPayment?: string
    sortBy?: string
    groupBy?: string
  }
  createdAt: string
}

const STORAGE_KEY = 'projects_filter_presets'

// Load all filter presets from localStorage
export const loadFilterPresets = (): FilterPreset[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    return JSON.parse(stored)
  } catch (err) {
    console.error('Error loading filter presets:', err)
    return []
  }
}

// Save a new filter preset
export const saveFilterPreset = (name: string, filters: FilterPreset['filters']): FilterPreset => {
  const presets = loadFilterPresets()

  const newPreset: FilterPreset = {
    id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
    name,
    filters,
    createdAt: new Date().toISOString(),
  }

  presets.push(newPreset)

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(presets))
  } catch (err) {
    console.error('Error saving filter preset:', err)
  }

  return newPreset
}

// Delete a filter preset
export const deleteFilterPreset = (id: string): void => {
  const presets = loadFilterPresets()
  const filtered = presets.filter((p) => p.id !== id)

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
  } catch (err) {
    console.error('Error deleting filter preset:', err)
  }
}

// Update a filter preset
export const updateFilterPreset = (
  id: string,
  updates: Partial<Omit<FilterPreset, 'id' | 'createdAt'>>
): FilterPreset | null => {
  const presets = loadFilterPresets()
  const index = presets.findIndex((p) => p.id === id)

  if (index === -1) return null

  presets[index] = {
    ...presets[index],
    ...updates,
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(presets))
  } catch (err) {
    console.error('Error updating filter preset:', err)
  }

  return presets[index]
}

// Get a specific filter preset by ID
export const getFilterPreset = (id: string): FilterPreset | null => {
  const presets = loadFilterPresets()
  return presets.find((p) => p.id === id) || null
}

// Export presets to JSON file
export const exportFilterPresets = (): void => {
  const presets = loadFilterPresets()
  const dataStr = JSON.stringify(presets, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `filter-presets-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Import presets from JSON file
export const importFilterPresets = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target?.result as string) as FilterPreset[]
        const existing = loadFilterPresets()

        // Merge imported presets with existing ones (avoid duplicates by name)
        const existingNames = new Set(existing.map((p) => p.name))
        const newPresets = imported.filter((p) => !existingNames.has(p.name))

        const merged = [...existing, ...newPresets]
        localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))

        resolve(newPresets.length)
      } catch (err) {
        reject(new Error('Ошибка импорта: неверный формат файла'))
      }
    }

    reader.onerror = () => {
      reject(new Error('Ошибка чтения файла'))
    }

    reader.readAsText(file)
  })
}

// Get default/built-in presets
export const getBuiltInPresets = (): FilterPreset[] => {
  return [
    {
      id: 'builtin-unpaid',
      name: 'Неоплаченные проекты',
      filters: {
        hasPayment: 'unpaid',
        sortBy: 'deadline',
      },
      createdAt: new Date().toISOString(),
    },
    {
      id: 'builtin-overdue',
      name: 'Просроченные',
      filters: {
        dateTo: new Date().toISOString().split('T')[0],
        sortBy: 'deadline',
      },
      createdAt: new Date().toISOString(),
    },
    {
      id: 'builtin-high-cost',
      name: 'Дорогие проекты (>50к)',
      filters: {
        sortBy: 'cost-desc',
      },
      createdAt: new Date().toISOString(),
    },
    {
      id: 'builtin-this-month',
      name: 'Созданные в этом месяце',
      filters: {
        dateFrom: new Date(new Date().getFullYear(), new Date().getMonth(), 1)
          .toISOString()
          .split('T')[0],
        sortBy: 'date-desc',
      },
      createdAt: new Date().toISOString(),
    },
  ]
}

// Check if filters are currently applied
export const hasActiveFilters = (filters: FilterPreset['filters']): boolean => {
  return Object.values(filters).some((value) => {
    if (value === null || value === undefined || value === '') return false
    if (typeof value === 'string' && value.trim() === '') return false
    return true
  })
}

// Clear all filters (return empty filter object)
export const clearFilters = (): FilterPreset['filters'] => {
  return {
    searchTerm: '',
    statusFilter: '',
    complexityFilter: '',
    executorId: null,
    clientId: null,
    colorFilter: '',
    dateFrom: '',
    dateTo: '',
    hasPayment: '',
    sortBy: '',
    groupBy: '',
  }
}
