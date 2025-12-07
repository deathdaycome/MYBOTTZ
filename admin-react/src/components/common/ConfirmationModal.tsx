import { useEffect } from 'react'
import { X, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'

interface ConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info' | 'success'
  loading?: boolean
}

export const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  type = 'warning',
  loading = false,
}: ConfirmationModalProps) => {
  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !loading) {
        onClose()
      } else if (e.key === 'Enter' && !loading) {
        onConfirm()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, loading, onClose, onConfirm])

  if (!isOpen) return null

  const getTypeConfig = () => {
    switch (type) {
      case 'danger':
        return {
          icon: <XCircle className="w-12 h-12" />,
          iconColor: 'text-red-600',
          bgColor: 'from-red-600 to-red-700',
          buttonColor: 'from-red-600 to-red-700 hover:from-red-700 hover:to-red-800',
        }
      case 'warning':
        return {
          icon: <AlertTriangle className="w-12 h-12" />,
          iconColor: 'text-yellow-600',
          bgColor: 'from-yellow-600 to-orange-600',
          buttonColor:
            'from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700',
        }
      case 'info':
        return {
          icon: <Info className="w-12 h-12" />,
          iconColor: 'text-blue-600',
          bgColor: 'from-blue-600 to-indigo-600',
          buttonColor: 'from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700',
        }
      case 'success':
        return {
          icon: <CheckCircle className="w-12 h-12" />,
          iconColor: 'text-green-600',
          bgColor: 'from-green-600 to-emerald-600',
          buttonColor:
            'from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700',
        }
    }
  }

  const config = getTypeConfig()

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-scale-in">
        {/* Icon */}
        <div className={`bg-gradient-to-r ${config.bgColor} px-6 py-8 flex justify-center`}>
          <div className="text-white">{config.icon}</div>
        </div>

        {/* Content */}
        <div className="p-6 text-center">
          <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
          <p className="text-gray-600 leading-relaxed">{message}</p>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className={`flex-1 px-6 py-3 bg-gradient-to-r ${config.buttonColor} text-white rounded-lg transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {loading ? 'Обработка...' : confirmText}
          </button>
        </div>

        {/* Keyboard hint */}
        <div className="px-6 py-2 bg-gray-100 text-xs text-center text-gray-500">
          <kbd className="px-2 py-0.5 bg-white border border-gray-300 rounded">Enter</kbd>{' '}
          подтвердить ·{' '}
          <kbd className="px-2 py-0.5 bg-white border border-gray-300 rounded">Esc</kbd> отмена
        </div>
      </div>

      <style>{`
        @keyframes scale-in {
          from {
            transform: scale(0.9);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }
        .animate-scale-in {
          animation: scale-in 0.2s ease-out;
        }
      `}</style>
    </div>
  )
}

// Hook for easier usage
export const useConfirmation = () => {
  return {
    confirm: (options: Omit<ConfirmationModalProps, 'isOpen' | 'onClose' | 'onConfirm'>) => {
      return new Promise<boolean>((resolve) => {
        // This would need to be implemented with state management
        // For now, it's a placeholder for the pattern
        resolve(true)
      })
    },
  }
}
