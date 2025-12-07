import { useState, useEffect } from 'react'
import { X, Copy, AlertCircle } from 'lucide-react'

interface DuplicateProjectModalProps {
  isOpen: boolean
  onClose: () => void
  project: any | null
  onDuplicated: () => void
}

export const DuplicateProjectModal = ({
  isOpen,
  onClose,
  project,
  onDuplicated,
}: DuplicateProjectModalProps) => {
  const [options, setOptions] = useState({
    copyName: true,
    copyDescription: true,
    copyFinances: false,
    copyExecutor: false,
    copyDeadline: false,
    copyAttachments: false,
    namePrefix: 'Копия - ',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      setOptions({
        copyName: true,
        copyDescription: true,
        copyFinances: false,
        copyExecutor: false,
        copyDeadline: false,
        copyAttachments: false,
        namePrefix: 'Копия - ',
      })
      setError('')
    }
  }, [isOpen])

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

  const handleDuplicate = async () => {
    if (!project) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${project.id}/duplicate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify(options),
        }
      )

      if (response.ok) {
        onDuplicated()
        onClose()
      } else {
        const data = await response.json()
        setError(data.message || 'Ошибка дублирования проекта')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen || !project) return null

  const previewName = options.copyName
    ? `${options.namePrefix}${project.name}`
    : 'Новый проект'

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Copy className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Дублирование проекта</h3>
              <p className="text-violet-100 text-sm mt-1">Проект #{project.id}</p>
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
        <div className="p-6 space-y-6">
          {/* Name Prefix */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Префикс названия
            </label>
            <input
              type="text"
              value={options.namePrefix}
              onChange={(e) => setOptions({ ...options, namePrefix: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-violet-500 focus:ring-2 focus:ring-violet-200 outline-none transition-all"
              placeholder="Копия - "
            />
            <div className="mt-2 p-3 bg-violet-50 border-l-4 border-violet-500 rounded">
              <p className="text-sm text-violet-900">
                <span className="font-semibold">Предпросмотр:</span> {previewName}
              </p>
            </div>
          </div>

          {/* Options */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Что скопировать?
            </label>
            <div className="space-y-3">
              <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.copyName}
                  onChange={(e) => setOptions({ ...options, copyName: e.target.checked })}
                  className="w-5 h-5 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Название</div>
                  <div className="text-xs text-gray-600">
                    Скопировать название проекта (с префиксом)
                  </div>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.copyDescription}
                  onChange={(e) => setOptions({ ...options, copyDescription: e.target.checked })}
                  className="w-5 h-5 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Описание и ТЗ</div>
                  <div className="text-xs text-gray-600">
                    Скопировать полное описание проекта
                  </div>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.copyFinances}
                  onChange={(e) => setOptions({ ...options, copyFinances: e.target.checked })}
                  className="w-5 h-5 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Финансы</div>
                  <div className="text-xs text-gray-600">
                    Скопировать стоимость проекта и исполнителя
                  </div>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.copyExecutor}
                  onChange={(e) => setOptions({ ...options, copyExecutor: e.target.checked })}
                  className="w-5 h-5 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Исполнитель</div>
                  <div className="text-xs text-gray-600">
                    Назначить того же исполнителя
                  </div>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.copyDeadline}
                  onChange={(e) => setOptions({ ...options, copyDeadline: e.target.checked })}
                  className="w-5 h-5 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Дедлайн</div>
                  <div className="text-xs text-gray-600">Скопировать дату дедлайна</div>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.copyAttachments}
                  onChange={(e) => setOptions({ ...options, copyAttachments: e.target.checked })}
                  className="w-5 h-5 text-violet-600 rounded focus:ring-2 focus:ring-violet-500"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">Вложения</div>
                  <div className="text-xs text-gray-600">
                    Скопировать прикрепленные файлы
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-2 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
          <button
            type="button"
            onClick={handleDuplicate}
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Copy className="w-5 h-5" />
            {loading ? 'Дублирование...' : 'Создать копию'}
          </button>
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold disabled:opacity-50"
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  )
}
