import { Clock, User, DollarSign, CheckCircle, AlertCircle, Palette, Calendar } from 'lucide-react'
import PixelCard from '../common/PixelCard'

interface EnhancedProjectCardProps {
  project: any
  colorClass: string
  onClick: () => void
  children?: React.ReactNode
}

export const EnhancedProjectCard = ({
  project,
  colorClass,
  onClick,
  children,
}: EnhancedProjectCardProps) => {
  const getPixelVariant = (): 'default' | 'blue' | 'yellow' | 'pink' | 'green' | 'purple' => {
    switch (colorClass) {
      case 'green':
        return 'green'
      case 'yellow':
        return 'yellow'
      case 'red':
        return 'pink'
      default:
        return 'default'
    }
  }

  const getColorBorderClass = () => {
    switch (colorClass) {
      case 'green':
        return 'border-l-8 border-green-500 bg-green-50/30'
      case 'yellow':
        return 'border-l-8 border-yellow-500 bg-yellow-50/30'
      case 'red':
        return 'border-l-8 border-red-500 bg-red-50/30'
      default:
        return 'border-l-4 border-gray-300'
    }
  }

  const getColorIndicator = () => {
    switch (colorClass) {
      case 'green':
        return (
          <div className="absolute top-3 right-3 flex items-center gap-1 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-semibold">
            <Palette className="w-3 h-3" />
            Зеленый
          </div>
        )
      case 'yellow':
        return (
          <div className="absolute top-3 right-3 flex items-center gap-1 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-semibold">
            <Palette className="w-3 h-3" />
            Желтый
          </div>
        )
      case 'red':
        return (
          <div className="absolute top-3 right-3 flex items-center gap-1 bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-semibold">
            <Palette className="w-3 h-3" />
            Красный
          </div>
        )
      default:
        return null
    }
  }

  const getPaymentStatusIndicator = () => {
    const paidTotal = project.paid_total || 0
    const projectCost = project.project_cost || 0

    if (projectCost === 0) return null

    const percentage = (paidTotal / projectCost) * 100

    if (percentage === 0) {
      return (
        <div className="flex items-center gap-1 text-red-600 text-xs font-semibold">
          <AlertCircle className="w-3 h-3" />
          Не оплачен
        </div>
      )
    } else if (percentage === 100) {
      return (
        <div className="flex items-center gap-1 text-green-600 text-xs font-semibold">
          <CheckCircle className="w-3 h-3" />
          Оплачен полностью
        </div>
      )
    } else {
      return (
        <div className="flex items-center gap-1 text-orange-600 text-xs font-semibold">
          <Clock className="w-3 h-3" />
          Оплачен {percentage.toFixed(0)}%
        </div>
      )
    }
  }

  const getDeadlineIndicator = () => {
    if (!project.deadline) return null

    const deadline = new Date(project.deadline)
    const now = new Date()
    const daysLeft = Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (daysLeft < 0) {
      return (
        <div className="flex items-center gap-1 text-red-600 text-xs font-semibold bg-red-50 px-2 py-1 rounded">
          <Calendar className="w-3 h-3" />
          Просрочено на {Math.abs(daysLeft)} дн.
        </div>
      )
    } else if (daysLeft === 0) {
      return (
        <div className="flex items-center gap-1 text-orange-600 text-xs font-semibold bg-orange-50 px-2 py-1 rounded">
          <Calendar className="w-3 h-3" />
          Сегодня
        </div>
      )
    } else if (daysLeft <= 3) {
      return (
        <div className="flex items-center gap-1 text-yellow-600 text-xs font-semibold bg-yellow-50 px-2 py-1 rounded">
          <Calendar className="w-3 h-3" />
          Осталось {daysLeft} дн.
        </div>
      )
    } else {
      return (
        <div className="flex items-center gap-1 text-blue-600 text-xs font-semibold bg-blue-50 px-2 py-1 rounded">
          <Calendar className="w-3 h-3" />
          Осталось {daysLeft} дн.
        </div>
      )
    }
  }

  return (
    <PixelCard
      variant={getPixelVariant()}
      className={`relative bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-6 cursor-pointer ${getColorBorderClass()}`}
      onClick={onClick}
    >
      {getColorIndicator()}

      {/* Main content */}
      <div className="space-y-4">
        {/* Project title and ID */}
        <div className="pr-24">
          <h3 className="text-lg font-bold text-gray-900 mb-1">{project.name || 'Без названия'}</h3>
          <p className="text-xs text-gray-500">ID: {project.id}</p>
        </div>

        {/* Status indicators row */}
        <div className="flex flex-wrap items-center gap-3">
          {getPaymentStatusIndicator()}
          {getDeadlineIndicator()}
        </div>

        {/* Financial info */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="w-4 h-4 text-blue-600" />
              <span className="text-xs text-blue-600 font-semibold">Стоимость</span>
            </div>
            <p className="text-lg font-bold text-blue-900">
              {(project.project_cost || 0).toLocaleString('ru-RU')} ₽
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-xs text-green-600 font-semibold">Оплачено</span>
            </div>
            <p className="text-lg font-bold text-green-900">
              {(project.paid_total || 0).toLocaleString('ru-RU')} ₽
            </p>
          </div>
        </div>

        {/* Executor info */}
        {project.assigned_to && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <User className="w-4 h-4" />
            <span className="font-medium">{project.assigned_to.username || project.assigned_to.first_name}</span>
          </div>
        )}

        {/* Custom children content */}
        {children}
      </div>
    </PixelCard>
  )
}
