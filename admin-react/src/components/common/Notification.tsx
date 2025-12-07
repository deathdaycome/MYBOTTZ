import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from 'lucide-react'

interface NotificationProps {
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
  onClose?: () => void
}

export const Notification = ({
  type,
  message,
  duration = 5000,
  onClose,
}: NotificationProps) => {
  const [isVisible, setIsVisible] = useState(true)
  const [progress, setProgress] = useState(100)

  useEffect(() => {
    if (duration > 0) {
      const interval = setInterval(() => {
        setProgress((prev) => {
          const newProgress = prev - (100 / (duration / 100))
          if (newProgress <= 0) {
            clearInterval(interval)
            handleClose()
            return 0
          }
          return newProgress
        })
      }, 100)

      return () => clearInterval(interval)
    }
  }, [duration])

  const handleClose = () => {
    setIsVisible(false)
    setTimeout(() => {
      if (onClose) onClose()
    }, 300)
  }

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info,
    warning: AlertTriangle,
  }

  const colors = {
    success: 'bg-green-50 border-green-200 text-green-700',
    error: 'bg-red-50 border-red-200 text-red-700',
    info: 'bg-blue-50 border-blue-200 text-blue-700',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-700',
  }

  const progressColors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
    warning: 'bg-yellow-500',
  }

  const Icon = icons[type]

  return (
    <div
      className={`${
        isVisible ? 'animate-fadeIn' : 'animate-fadeOut'
      } ${colors[type]} border rounded-xl p-4 shadow-lg mb-3 relative overflow-hidden`}
    >
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <p className="flex-1 text-sm font-medium">{message}</p>
        <button
          onClick={handleClose}
          className="flex-shrink-0 hover:opacity-70 transition-opacity"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {duration > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200">
          <div
            className={`h-full ${progressColors[type]} transition-all duration-100 ease-linear`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}

// Notification Container Hook
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<
    Array<{
      id: string
      type: 'success' | 'error' | 'info' | 'warning'
      message: string
      duration?: number
    }>
  >([])

  const addNotification = (
    type: 'success' | 'error' | 'info' | 'warning',
    message: string,
    duration = 5000
  ) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    setNotifications((prev) => [...prev, { id, type, message, duration }])
  }

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    success: (message: string, duration?: number) =>
      addNotification('success', message, duration),
    error: (message: string, duration?: number) =>
      addNotification('error', message, duration),
    info: (message: string, duration?: number) =>
      addNotification('info', message, duration),
    warning: (message: string, duration?: number) =>
      addNotification('warning', message, duration),
  }
}

// Notification Container Component
interface NotificationContainerProps {
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'info' | 'warning'
    message: string
    duration?: number
  }>
  onRemove: (id: string) => void
}

export const NotificationContainer = ({
  notifications,
  onRemove,
}: NotificationContainerProps) => {
  return (
    <div className="fixed top-5 right-5 z-50 max-w-md w-full">
      {notifications.map((notification) => (
        <Notification
          key={notification.id}
          type={notification.type}
          message={notification.message}
          duration={notification.duration}
          onClose={() => onRemove(notification.id)}
        />
      ))}
    </div>
  )
}
