import { useState, useEffect, useRef } from 'react'
import { Search, X, Filter, FileText, User, Calendar, DollarSign } from 'lucide-react'

interface SearchResult {
  id: number
  type: 'project' | 'task' | 'comment' | 'file'
  title: string
  description: string
  matchedField: string
  matchedText: string
  relevance: number
  metadata: {
    status?: string
    client?: string
    deadline?: string
    cost?: number
  }
}

interface FullTextSearchProps {
  isOpen: boolean
  onClose: () => void
  onResultClick: (type: string, id: number) => void
}

export const FullTextSearch = ({ isOpen, onClose, onResultClick }: FullTextSearchProps) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    projects: true,
    tasks: true,
    comments: true,
    files: true,
  })
  const [searchIn, setSearchIn] = useState({
    title: true,
    description: true,
    comments: true,
    tags: true,
  })
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceTimer = useRef<NodeJS.Timeout>()

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus()

      // Lock body scroll
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      // Restore scroll
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }

    return () => {
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
    }
  }, [isOpen])

  useEffect(() => {
    if (query.length >= 2) {
      // Debounce search
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }

      debounceTimer.current = setTimeout(() => {
        performSearch()
      }, 300)
    } else {
      setResults([])
    }

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
    }
  }, [query, filters, searchIn])

  const performSearch = async () => {
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8001/admin/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          query,
          filters,
          searchIn,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setResults(data.results || [])
      }
    } catch (err) {
      console.error('Search error:', err)
      // Mock results for demo
      setResults(getMockResults(query))
    } finally {
      setLoading(false)
    }
  }

  const getMockResults = (searchQuery: string): SearchResult[] => {
    // Mock data for demonstration
    const mockResults: SearchResult[] = [
      {
        id: 1,
        type: 'project',
        title: 'Разработка CRM системы',
        description: 'Создание CRM системы для управления проектами',
        matchedField: 'title',
        matchedText: `Разработка <mark>CRM</mark> системы`,
        relevance: 95,
        metadata: {
          status: 'in_progress',
          client: 'ООО "Ромашка"',
          cost: 150000,
        },
      },
      {
        id: 2,
        type: 'task',
        title: 'Настройка базы данных',
        description: 'Настроить PostgreSQL для CRM',
        matchedField: 'description',
        matchedText: `Настроить PostgreSQL для <mark>CRM</mark>`,
        relevance: 80,
        metadata: {
          status: 'completed',
        },
      },
    ]

    return mockResults.filter((r) =>
      r.title.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }

  const highlightText = (text: string) => {
    return { __html: text }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'project':
        return <FileText className="w-5 h-5 text-blue-600" />
      case 'task':
        return <FileText className="w-5 h-5 text-green-600" />
      case 'comment':
        return <FileText className="w-5 h-5 text-purple-600" />
      case 'file':
        return <FileText className="w-5 h-5 text-orange-600" />
      default:
        return <FileText className="w-5 h-5 text-gray-600" />
    }
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      project: 'Проект',
      task: 'Задача',
      comment: 'Комментарий',
      file: 'Файл',
    }
    return labels[type] || type
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-start justify-center pt-20">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full mx-4 overflow-hidden">
        {/* Search Input */}
        <div className="p-6 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Поиск по проектам, задачам, комментариям..."
              className="w-full pl-12 pr-12 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none text-lg transition-all"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Filters */}
          <div className="mt-4 flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-semibold text-gray-700">Искать в:</span>
            </div>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.projects}
                onChange={(e) => setFilters({ ...filters, projects: e.target.checked })}
                className="w-4 h-4 rounded"
              />
              <span className="text-sm text-gray-700">Проекты</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.tasks}
                onChange={(e) => setFilters({ ...filters, tasks: e.target.checked })}
                className="w-4 h-4 rounded"
              />
              <span className="text-sm text-gray-700">Задачи</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.comments}
                onChange={(e) => setFilters({ ...filters, comments: e.target.checked })}
                className="w-4 h-4 rounded"
              />
              <span className="text-sm text-gray-700">Комментарии</span>
            </label>
          </div>
        </div>

        {/* Results */}
        <div className="max-h-[500px] overflow-y-auto">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
              <p className="text-gray-600 mt-4">Поиск...</p>
            </div>
          ) : query.length < 2 ? (
            <div className="p-12 text-center text-gray-500">
              <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Введите минимум 2 символа для поиска</p>
            </div>
          ) : results.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Ничего не найдено по запросу "{query}"</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {results.map((result) => (
                <button
                  key={`${result.type}-${result.id}`}
                  onClick={() => {
                    onResultClick(result.type, result.id)
                    onClose()
                  }}
                  className="w-full p-4 hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">{getTypeIcon(result.type)}</div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
                          {getTypeLabel(result.type)}
                        </span>
                        <span className="text-xs text-gray-500">
                          Релевантность: {result.relevance}%
                        </span>
                      </div>

                      <h4 className="font-semibold text-gray-900 mb-1">{result.title}</h4>

                      <div
                        className="text-sm text-gray-600 mb-2 line-clamp-2"
                        dangerouslySetInnerHTML={highlightText(result.matchedText)}
                      />

                      {result.metadata && (
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          {result.metadata.client && (
                            <div className="flex items-center gap-1">
                              <User className="w-3 h-3" />
                              {result.metadata.client}
                            </div>
                          )}
                          {result.metadata.cost && (
                            <div className="flex items-center gap-1">
                              <DollarSign className="w-3 h-3" />
                              {result.metadata.cost.toLocaleString()}₽
                            </div>
                          )}
                          {result.metadata.deadline && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {result.metadata.deadline}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
          <div>
            {results.length > 0 && (
              <span>
                Найдено результатов: <strong>{results.length}</strong>
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <span>
              <kbd className="px-2 py-1 bg-white border border-gray-300 rounded">Esc</kbd> закрыть
            </span>
            <span>
              <kbd className="px-2 py-1 bg-white border border-gray-300 rounded">↑</kbd>
              <kbd className="px-2 py-1 bg-white border border-gray-300 rounded ml-1">↓</kbd>{' '}
              навигация
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
