import { X, Keyboard } from 'lucide-react'
import { useEffect } from 'react'

interface Shortcut {
  keys: string[]
  description: string
  category: string
}

interface ShortcutsHelpModalProps {
  isOpen: boolean
  onClose: () => void
}

const shortcuts: Shortcut[] = [
  // Navigation
  { keys: ['/'], description: 'Фокус на поиске', category: 'Навигация' },
  { keys: ['R'], description: 'Обновить список проектов', category: 'Навигация' },
  { keys: ['Esc'], description: 'Закрыть модальное окно', category: 'Навигация' },

  // Actions
  { keys: ['N'], description: 'Создать новый проект', category: 'Действия' },
  { keys: ['Ctrl', 'E'], description: 'Экспорт проектов', category: 'Действия' },
  { keys: ['Ctrl', 'A'], description: 'Выбрать все проекты', category: 'Действия' },
  { keys: ['Ctrl', 'P'], description: 'Печать выбранных проектов', category: 'Действия' },

  // Filters
  { keys: ['F'], description: 'Открыть расширенные фильтры', category: 'Фильтры' },
  { keys: ['Shift', 'C'], description: 'Сбросить все фильтры', category: 'Фильтры' },

  // View
  { keys: ['G'], description: 'Переключить группировку', category: 'Вид' },
  { keys: ['A'], description: 'Показать/скрыть аналитику', category: 'Вид' },

  // Help
  { keys: ['?'], description: 'Показать это окно', category: 'Помощь' },
]

export const ShortcutsHelpModal = ({ isOpen, onClose }: ShortcutsHelpModalProps) => {
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

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEsc)
    return () => document.removeEventListener('keydown', handleEsc)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const categories = [...new Set(shortcuts.map((s) => s.category))]

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-700 to-gray-800 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Keyboard className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Горячие клавиши</h3>
              <p className="text-slate-300 text-sm mt-1">Комбинации для быстрой работы</p>
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

        {/* Body */}
        <div className="p-6 max-h-[600px] overflow-y-auto">
          {categories.map((category) => (
            <div key={category} className="mb-6 last:mb-0">
              <h4 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">
                {category}
              </h4>
              <div className="space-y-2">
                {shortcuts
                  .filter((s) => s.category === category)
                  .map((shortcut, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <span className="text-sm text-gray-700">{shortcut.description}</span>
                      <div className="flex items-center gap-1">
                        {shortcut.keys.map((key, keyIndex) => (
                          <span key={keyIndex} className="flex items-center">
                            <kbd className="px-3 py-1.5 bg-white border-2 border-gray-300 rounded-lg shadow-sm text-xs font-semibold text-gray-800 min-w-[2rem] text-center">
                              {key}
                            </kbd>
                            {keyIndex < shortcut.keys.length - 1 && (
                              <span className="mx-1 text-gray-400 font-bold">+</span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <p className="text-xs text-gray-500">
            💡 Совет: Используйте <kbd className="px-2 py-0.5 bg-white border border-gray-300 rounded text-xs">?</kbd> чтобы снова открыть это окно
          </p>
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold text-sm"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
