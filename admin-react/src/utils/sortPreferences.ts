// Sort preferences utility for persisting sort state

export type SortOption =
  | 'date-desc'
  | 'date-asc'
  | 'cost-desc'
  | 'cost-asc'
  | 'deadline-asc'
  | 'deadline-desc'
  | 'name-asc'
  | 'name-desc'
  | 'status'
  | 'executor'

export interface SortPreferences {
  currentSort: SortOption
  lastUsed: string
}

const STORAGE_KEY = 'projects_sort_preferences'

// Load sort preferences
export const loadSortPreferences = (): SortPreferences | null => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return null
    return JSON.parse(stored)
  } catch (err) {
    console.error('Error loading sort preferences:', err)
    return null
  }
}

// Save sort preferences
export const saveSortPreferences = (sortOption: SortOption): void => {
  try {
    const prefs: SortPreferences = {
      currentSort: sortOption,
      lastUsed: new Date().toISOString(),
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs))
  } catch (err) {
    console.error('Error saving sort preferences:', err)
  }
}

// Get default sort option (from preferences or fallback)
export const getDefaultSort = (): SortOption => {
  const prefs = loadSortPreferences()
  return prefs?.currentSort || 'date-desc'
}

// Sort function for projects
export const sortProjects = <T extends Record<string, any>>(
  projects: T[],
  sortOption: SortOption
): T[] => {
  const sorted = [...projects]

  switch (sortOption) {
    case 'date-desc':
      return sorted.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0
        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0
        return dateB - dateA
      })

    case 'date-asc':
      return sorted.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0
        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0
        return dateA - dateB
      })

    case 'cost-desc':
      return sorted.sort((a, b) => (b.project_cost || 0) - (a.project_cost || 0))

    case 'cost-asc':
      return sorted.sort((a, b) => (a.project_cost || 0) - (b.project_cost || 0))

    case 'deadline-asc':
      return sorted.sort((a, b) => {
        if (!a.deadline) return 1
        if (!b.deadline) return -1
        const dateA = new Date(a.deadline).getTime()
        const dateB = new Date(b.deadline).getTime()
        return dateA - dateB
      })

    case 'deadline-desc':
      return sorted.sort((a, b) => {
        if (!a.deadline) return 1
        if (!b.deadline) return -1
        const dateA = new Date(a.deadline).getTime()
        const dateB = new Date(b.deadline).getTime()
        return dateB - dateA
      })

    case 'name-asc':
      return sorted.sort((a, b) => (a.name || '').localeCompare(b.name || ''))

    case 'name-desc':
      return sorted.sort((a, b) => (b.name || '').localeCompare(a.name || ''))

    case 'status':
      return sorted.sort((a, b) => (a.status || '').localeCompare(b.status || ''))

    case 'executor':
      return sorted.sort((a, b) => {
        const nameA = a.assigned_to?.username || a.assigned_to?.first_name || ''
        const nameB = b.assigned_to?.username || b.assigned_to?.first_name || ''
        return nameA.localeCompare(nameB)
      })

    default:
      return sorted
  }
}

// Get sort option label
export const getSortLabel = (sortOption: SortOption): string => {
  const labels: Record<SortOption, string> = {
    'date-desc': 'Дата создания (новые)',
    'date-asc': 'Дата создания (старые)',
    'cost-desc': 'Стоимость (по убыванию)',
    'cost-asc': 'Стоимость (по возрастанию)',
    'deadline-asc': 'Дедлайн (ближайшие)',
    'deadline-desc': 'Дедлайн (дальние)',
    'name-asc': 'Название (А-Я)',
    'name-desc': 'Название (Я-А)',
    status: 'По статусу',
    executor: 'По исполнителю',
  }
  return labels[sortOption] || sortOption
}

// Get all available sort options
export const getAllSortOptions = (): Array<{ value: SortOption; label: string }> => {
  return [
    { value: 'date-desc', label: 'Дата создания (новые)' },
    { value: 'date-asc', label: 'Дата создания (старые)' },
    { value: 'cost-desc', label: 'Стоимость (по убыванию)' },
    { value: 'cost-asc', label: 'Стоимость (по возрастанию)' },
    { value: 'deadline-asc', label: 'Дедлайн (ближайшие)' },
    { value: 'deadline-desc', label: 'Дедлайн (дальние)' },
    { value: 'name-asc', label: 'Название (А-Я)' },
    { value: 'name-desc', label: 'Название (Я-А)' },
    { value: 'status', label: 'По статусу' },
    { value: 'executor', label: 'По исполнителю' },
  ]
}
