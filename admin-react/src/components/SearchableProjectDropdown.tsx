import { useState, useEffect, useRef } from 'react'
import { Search, X, ChevronDown } from 'lucide-react'
import type { HostingProject } from '../api/hosting'

interface SearchableProjectDropdownProps {
  projects: HostingProject[]
  value: number | null
  onChange: (projectId: number | null) => void
  placeholder?: string
  disabled?: boolean
}

export const SearchableProjectDropdown = ({
  projects,
  value,
  onChange,
  placeholder = 'Выберите проект',
  disabled = false,
}: SearchableProjectDropdownProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Найти выбранный проект
  const selectedProject = projects.find((p) => p.id === value)

  // Фильтрация проектов по поисковому запросу
  const filteredProjects = projects.filter((project) =>
    project.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Debug logging
  console.log('SearchableProjectDropdown:', {
    totalProjects: projects.length,
    filteredProjects: filteredProjects.length,
    searchQuery,
    isOpen,
  })

  // Закрытие dropdown при клике вне компонента
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Фокус на поле поиска при открытии dropdown
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [isOpen])

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen)
      setSearchQuery('')
    }
  }

  const handleSelect = (projectId: number) => {
    onChange(projectId)
    setIsOpen(false)
    setSearchQuery('')
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChange(null)
    setSearchQuery('')
  }

  return (
    <div ref={dropdownRef} className="relative w-full">
      {/* Main Button */}
      <button
        type="button"
        onClick={handleToggle}
        disabled={disabled}
        className={`w-full px-4 py-3 border-2 rounded-lg text-left flex items-center justify-between transition-all ${
          disabled
            ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
            : isOpen
            ? 'border-sky-500 ring-2 ring-sky-200'
            : 'border-gray-200 hover:border-gray-300'
        }`}
      >
        <span className={selectedProject ? 'text-gray-800' : 'text-gray-400'}>
          {selectedProject ? (
            <span>
              <span className="font-semibold">{selectedProject.title}</span>
              <span className="text-sm text-gray-500 ml-2">(#{selectedProject.id})</span>
            </span>
          ) : (
            placeholder
          )}
        </span>

        <div className="flex items-center gap-2">
          {selectedProject && !disabled && (
            <X
              className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-pointer"
              onClick={handleClear}
            />
          )}
          <ChevronDown
            className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          />
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border-2 border-sky-500 rounded-lg shadow-xl max-h-[400px] overflow-hidden">
          {/* Search Input */}
          <div className="p-3 border-b border-gray-200 sticky top-0 bg-white">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Поиск проектов..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-200 focus:border-sky-500"
              />
            </div>
          </div>

          {/* Options List */}
          <div className="max-h-[300px] overflow-y-auto">
            {/* Option "Без привязки" */}
            <button
              type="button"
              onClick={() => {
                onChange(null)
                setIsOpen(false)
              }}
              className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                !value ? 'bg-sky-50 text-sky-700' : 'text-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                <span className="font-medium">Без привязки к проекту</span>
              </div>
            </button>

            {/* Project Options */}
            {filteredProjects.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <p>Проекты не найдены</p>
                {searchQuery && (
                  <p className="text-sm mt-1">Попробуйте изменить запрос поиска</p>
                )}
              </div>
            ) : (
              filteredProjects.map((project) => (
                <button
                  key={project.id}
                  type="button"
                  onClick={() => handleSelect(project.id)}
                  className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0 ${
                    value === project.id ? 'bg-sky-50' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        value === project.id ? 'bg-sky-500' : 'bg-gray-300'
                      }`}
                    ></div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span
                          className={`font-semibold truncate ${
                            value === project.id ? 'text-sky-700' : 'text-gray-800'
                          }`}
                        >
                          {project.title}
                        </span>
                        <span className="text-xs text-gray-500">#{project.id}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                        <span className="px-2 py-0.5 bg-gray-100 rounded">
                          {project.status === 'in_progress'
                            ? 'В работе'
                            : project.status === 'new'
                            ? 'Новый'
                            : project.status === 'review'
                            ? 'На проверке'
                            : project.status === 'accepted'
                            ? 'Принят'
                            : project.status === 'testing'
                            ? 'Тестирование'
                            : project.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
