import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight, Calendar, X } from 'lucide-react'

interface Project {
  id: number
  title: string
  deadline: string | null
  status: string
  color?: string
}

interface ProjectCalendarProps {
  isOpen: boolean
  onClose: () => void
  projects: Project[]
  onProjectClick: (projectId: number) => void
}

export const ProjectCalendar = ({
  isOpen,
  onClose,
  projects,
  onProjectClick,
}: ProjectCalendarProps) => {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<'month' | 'week'>('month')

  const daysInMonth = useMemo(() => {
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysCount = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()

    const days: (Date | null)[] = []

    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null)
    }

    // Add days of month
    for (let i = 1; i <= daysCount; i++) {
      days.push(new Date(year, month, i))
    }

    return days
  }, [currentDate])

  const projectsByDate = useMemo(() => {
    const map = new Map<string, Project[]>()

    projects.forEach((project) => {
      if (project.deadline) {
        const dateKey = project.deadline.slice(0, 10)
        if (!map.has(dateKey)) {
          map.set(dateKey, [])
        }
        map.get(dateKey)!.push(project)
      }
    })

    return map
  }, [projects])

  const formatDateKey = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))
  }

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))
  }

  const goToToday = () => {
    setCurrentDate(new Date())
  }

  const isToday = (date: Date) => {
    const today = new Date()
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-blue-500',
      review: 'bg-orange-500',
      accepted: 'bg-purple-500',
      in_progress: 'bg-yellow-500',
      testing: 'bg-green-500',
      completed: 'bg-green-600',
      cancelled: 'bg-red-500',
      on_hold: 'bg-gray-500',
    }
    return colors[status] || 'bg-gray-500'
  }

  if (!isOpen) return null

  const monthNames = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
  ]

  const weekDays = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Календарь проектов</h3>
              <p className="text-indigo-100 text-sm mt-1">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Controls */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
          <div className="flex items-center gap-2">
            <button
              onClick={goToPreviousMonth}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              title="Предыдущий месяц"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={goToToday}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold text-sm"
            >
              Сегодня
            </button>
            <button
              onClick={goToNextMonth}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              title="Следующий месяц"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('month')}
              className={`px-4 py-2 rounded-lg font-semibold text-sm transition-colors ${
                viewMode === 'month'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Месяц
            </button>
            <button
              onClick={() => setViewMode('week')}
              className={`px-4 py-2 rounded-lg font-semibold text-sm transition-colors ${
                viewMode === 'week'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Неделя
            </button>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="flex-1 overflow-auto p-6">
          {/* Week day headers */}
          <div className="grid grid-cols-7 gap-2 mb-2">
            {weekDays.map((day) => (
              <div
                key={day}
                className="text-center font-bold text-gray-600 text-sm py-2"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Calendar days */}
          <div className="grid grid-cols-7 gap-2">
            {daysInMonth.map((date, index) => {
              if (!date) {
                return <div key={`empty-${index}`} className="aspect-square" />
              }

              const dateKey = formatDateKey(date)
              const dayProjects = projectsByDate.get(dateKey) || []
              const isTodayDate = isToday(date)

              return (
                <div
                  key={index}
                  className={`aspect-square border-2 rounded-lg p-2 flex flex-col ${
                    isTodayDate
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 bg-white hover:bg-gray-50'
                  } transition-colors`}
                >
                  <div
                    className={`text-sm font-semibold mb-1 ${
                      isTodayDate ? 'text-indigo-600' : 'text-gray-900'
                    }`}
                  >
                    {date.getDate()}
                  </div>

                  {dayProjects.length > 0 && (
                    <div className="flex-1 overflow-hidden">
                      {dayProjects.slice(0, 3).map((project) => (
                        <button
                          key={project.id}
                          onClick={() => onProjectClick(project.id)}
                          className={`w-full text-left px-2 py-1 mb-1 rounded text-xs font-medium truncate ${getStatusColor(
                            project.status
                          )} text-white hover:opacity-80 transition-opacity`}
                          title={project.title}
                        >
                          {project.title}
                        </button>
                      ))}
                      {dayProjects.length > 3 && (
                        <div className="text-xs text-gray-500 text-center mt-1">
                          +{dayProjects.length - 3} еще
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex flex-wrap items-center gap-4">
          <span className="text-sm font-semibold text-gray-700">Статусы:</span>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-blue-500" />
            <span className="text-xs text-gray-600">Новый</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-yellow-500" />
            <span className="text-xs text-gray-600">В работе</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-500" />
            <span className="text-xs text-gray-600">Тестирование</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-green-600" />
            <span className="text-xs text-gray-600">Завершен</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-red-500" />
            <span className="text-xs text-gray-600">Отменен</span>
          </div>
        </div>
      </div>
    </div>
  )
}
