import {
  Clock,
  Calendar,
  AlertCircle,
  Play,
  Pause,
  MessageCircle,
  Edit,
  Trash2,
  Eye,
  CheckCircle,
  Archive,
} from 'lucide-react'
import React, { useState, useRef } from 'react'
import type { Task } from '../../api/tasks'
import tasksApi from '../../api/tasks'
import { TaskTags } from './TaskTags'

interface TaskCardProps {
  task: Task
  onView: () => void
  onEdit: () => void
  onDelete: () => void
  onStatusChange: (newStatus: string) => void
  onDragStart?: (e: React.DragEvent<HTMLDivElement>) => void
}

export const TaskCard = ({ task, onView, onEdit, onDelete, onStatusChange, onDragStart }: TaskCardProps) =>{
  const [timerRunning, setTimerRunning] = useState(!!task.timer_started_at)
  const [unreadCount, setUnreadCount] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  const dragStartTime = useRef<number>(0)

  // Для простоты считаем что пользователь - owner (права проверяются на бэкенде)
  const isOwner = true

  // Get card background gradient based on priority and color
  const getCardStyle = () => {
    // Custom color overrides priority
    if (task.color && task.color !== 'normal') {
      const colorStyles = {
        red: 'bg-gradient-to-br from-red-100 to-red-200 border-red-600',
        yellow: 'bg-gradient-to-br from-yellow-100 to-yellow-200 border-yellow-600',
        green: 'bg-gradient-to-br from-green-100 to-green-200 border-green-600',
      }
      return colorStyles[task.color] || ''
    }

    // Priority colors
    const priorityStyles = {
      urgent: 'bg-gradient-to-br from-red-100 to-red-200 border-red-600',
      high: 'bg-gradient-to-br from-orange-100 to-orange-200 border-orange-500',
      normal: 'bg-gradient-to-br from-blue-100 to-blue-200 border-blue-500',
      low: 'bg-gradient-to-br from-gray-100 to-gray-200 border-gray-400',
    }
    return priorityStyles[task.priority] || priorityStyles.normal
  }

  // Get priority badge color
  const getPriorityBadgeColor = () => {
    switch (task.priority) {
      case 'urgent':
        return 'bg-red-200 text-red-900'
      case 'high':
        return 'bg-orange-200 text-orange-900'
      case 'normal':
        return 'bg-blue-200 text-blue-900'
      case 'low':
        return 'bg-gray-200 text-gray-900'
      default:
        return 'bg-gray-200 text-gray-900'
    }
  }

  // Get priority label
  const getPriorityLabel = () => {
    switch (task.priority) {
      case 'urgent':
        return 'СРОЧНО'
      case 'high':
        return 'ВЫСОКИЙ'
      case 'normal':
        return 'ОБЫЧНЫЙ'
      case 'low':
        return 'НИЗКИЙ'
      default:
        return task.priority.toUpperCase()
    }
  }

  // Get status badge color
  const getStatusBadgeColor = () => {
    switch (task.status) {
      case 'pending':
        return 'bg-blue-200 text-blue-900'
      case 'in_progress':
        return 'bg-yellow-200 text-yellow-900'
      case 'completed':
        return 'bg-green-200 text-green-900'
      default:
        return 'bg-gray-200 text-gray-900'
    }
  }

  // Get status label
  const getStatusLabel = () => {
    switch (task.status) {
      case 'pending':
        return 'ОЖИДАЕТ'
      case 'in_progress':
        return 'В РАБОТЕ'
      case 'completed':
        return 'ВЫПОЛНЕНО'
      default:
        return task.status.toUpperCase()
    }
  }

  // Format time spent
  const formatTimeSpent = (seconds?: number) => {
    if (!seconds) return '0ч 0м'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}ч ${minutes}м`
  }

  // Format deadline
  const formatDeadline = (deadline?: string) => {
    if (!deadline) return null
    const date = new Date(deadline)
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  // Handle timer toggle
  const handleTimerToggle = async (e: React.MouseEvent) => {
    e.stopPropagation()

    try {
      if (timerRunning) {
        await tasksApi.stopTimer(task.id)
      } else {
        await tasksApi.startTimer(task.id)
      }
      setTimerRunning(!timerRunning)
    } catch (error) {
      console.error('Error toggling timer:', error)
    }
  }

  // Handle status change
  const handleStatusChangeLocal = (e: React.MouseEvent, newStatus: string) => {
    e.stopPropagation()
    onStatusChange(newStatus)
  }

  // Handle drag start
  const handleDragStartLocal = (e: React.DragEvent<HTMLDivElement>) => {
    dragStartTime.current = Date.now()
    setIsDragging(true)
    if (onDragStart) {
      onDragStart(e)
    }
  }

  // Handle drag end
  const handleDragEnd = () => {
    setTimeout(() => {
      setIsDragging(false)
    }, 100) // Небольшая задержка чтобы предотвратить клик
  }

  // Handle click - только если не было перетаскивания
  const handleClick = (e: React.MouseEvent) => {
    // Если прошло меньше 200ms с начала drag, или isDragging - игнорируем клик
    const timeSinceDragStart = Date.now() - dragStartTime.current
    if (timeSinceDragStart > 200 && !isDragging) {
      onView()
    }
  }

  return (
    <div
      draggable
      onDragStart={handleDragStartLocal}
      onDragEnd={handleDragEnd}
      className={`group rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-4 cursor-move relative border-l-4 hover:-translate-y-0.5 ${isDragging ? 'opacity-50' : ''} ${getCardStyle()}`}
      onClick={handleClick}
    >
      {/* Action buttons - top right corner (appear on hover) */}
      <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onView()
          }}
          className="p-1.5 bg-white/90 hover:bg-blue-50 rounded-md transition-all shadow-sm"
          title="Просмотр"
        >
          <Eye className="w-3.5 h-3.5 text-blue-600" />
        </button>
        {isOwner && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            className="p-1.5 bg-white/90 hover:bg-orange-50 rounded-md transition-all shadow-sm"
            title="В архив"
          >
            <Archive className="w-3.5 h-3.5 text-orange-600" />
          </button>
        )}
      </div>

      {/* Task title */}
      <h4 className="font-semibold text-gray-900 mb-2 pr-16 text-[0.95rem] leading-tight">
        {task.priority === 'urgent' && (
          <AlertCircle className="w-4 h-4 inline-block mr-1.5 text-red-600 animate-pulse" />
        )}
        {task.title}
      </h4>

      {/* Description */}
      {task.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2 leading-relaxed">{task.description}</p>
      )}

      {/* Tags */}
      {task.tags && task.tags.length > 0 && (
        <div className="mb-3">
          <TaskTags tags={task.tags} size="sm" />
        </div>
      )}

      {/* Badges */}
      <div className="flex gap-2 mb-3 flex-wrap">
        <span className={`text-[0.7rem] font-bold px-2 py-1 rounded-md uppercase ${getPriorityBadgeColor()}`}>
          {getPriorityLabel()}
        </span>
        <span className={`text-[0.7rem] font-bold px-2 py-1 rounded-md uppercase ${getStatusBadgeColor()}`}>
          {getStatusLabel()}
        </span>
        {task.is_overdue && (
          <span className="text-[0.7rem] font-bold px-2 py-1 rounded-md uppercase bg-red-200 text-red-900">
            ПРОСРОЧЕНО
          </span>
        )}
      </div>

      {/* Deadline */}
      {task.deadline && (
        <div className="flex items-center gap-1.5 text-xs text-gray-600 mb-3">
          <Calendar className="w-3.5 h-3.5" />
          <span>{formatDeadline(task.deadline)}</span>
        </div>
      )}

      {/* Footer with progress and timer */}
      {task.status !== 'completed' && (
        <div className="flex items-center gap-3 mt-4">
          {/* Progress bar */}
          <div className="flex-1 flex items-center gap-2 cursor-pointer hover:scale-105 transition-transform">
            <div className="flex-1 h-2 bg-indigo-100 rounded-full overflow-hidden relative">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-full transition-all duration-500"
                style={{ width: `${task.progress || 0}%` }}
              />
            </div>
            <span className="text-xs font-bold text-indigo-600 min-w-[40px] text-right">
              {task.progress || 0}%
            </span>
          </div>

          {/* Timer */}
          {task.time_spent_seconds !== undefined && task.time_spent_seconds > 0 && (
            <div className="flex items-center gap-1.5">
              <div
                onClick={handleTimerToggle}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold cursor-pointer transition-all ${
                  timerRunning
                    ? 'bg-green-100 text-green-700 animate-pulse'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {timerRunning ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                <span>{formatTimeSpent(task.time_spent_seconds)}</span>
              </div>
            </div>
          )}

          {/* Quick status change button */}
          {task.status === 'pending' && (
            <button
              onClick={(e) => handleStatusChangeLocal(e, 'in_progress')}
              className="px-3 py-1 bg-yellow-100 text-yellow-700 hover:bg-yellow-200 rounded-md text-xs font-bold transition-all flex items-center gap-1"
              title="Взять в работу"
            >
              <Play className="w-3 h-3" />
              <span>Старт</span>
            </button>
          )}

          {task.status === 'in_progress' && (
            <button
              onClick={(e) => handleStatusChangeLocal(e, 'completed')}
              className="px-3 py-1 bg-green-100 text-green-700 hover:bg-green-200 rounded-md text-xs font-bold transition-all flex items-center gap-1"
              title="Завершить"
            >
              <CheckCircle className="w-3 h-3" />
              <span>Готово</span>
            </button>
          )}
        </div>
      )}
    </div>
  )
}
