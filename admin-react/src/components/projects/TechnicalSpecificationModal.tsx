import { useState } from 'react'
import { X, FileText, Copy, ChevronDown, ChevronUp } from 'lucide-react'
import { copyToClipboard } from '../../utils/clipboard'

interface TechnicalSpecificationModalProps {
  isOpen: boolean
  onClose: () => void
  project: any
  onShowToast: (message: string, type: 'success' | 'error') => void
}

export const TechnicalSpecificationModal = ({
  isOpen,
  onClose,
  project,
  onShowToast,
}: TechnicalSpecificationModalProps) => {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!isOpen || !project) return null

  const handleCopy = async () => {
    const tzText = formatTZ(project)
    const success = await copyToClipboard(tzText)
    if (success) {
      onShowToast('ТЗ скопировано в буфер обмена!', 'success')
    } else {
      onShowToast('Ошибка копирования', 'error')
    }
  }

  const formatTZ = (project: any) => {
    const sections = []

    sections.push('=' + '='.repeat(60))
    sections.push(`ТЕХНИЧЕСКОЕ ЗАДАНИЕ - ПРОЕКТ #${project.id}`)
    sections.push('=' + '='.repeat(60))
    sections.push('')

    sections.push(`📋 НАЗВАНИЕ: ${project.title}`)
    sections.push(`👤 КЛИЕНТ: ${project.user?.first_name || 'Не указан'} (@${project.user?.username || 'нет'})`)
    sections.push(`📁 ТИП: ${project.project_type || 'Не указан'}`)
    sections.push(`📊 СТАТУС: ${project.status}`)
    sections.push(`🎯 СЛОЖНОСТЬ: ${project.complexity}`)
    sections.push('')

    sections.push('-' + '-'.repeat(60))
    sections.push('💰 ФИНАНСЫ')
    sections.push('-' + '-'.repeat(60))
    sections.push(`Стоимость проекта: ${(project.estimated_cost || 0).toLocaleString('ru-RU')} ₽`)
    sections.push(`Оплачено клиентом: ${(project.client_paid_total || 0).toLocaleString('ru-RU')} ₽`)
    sections.push(`Остаток к оплате: ${((project.estimated_cost || 0) - (project.client_paid_total || 0)).toLocaleString('ru-RU')} ₽`)
    sections.push('')
    sections.push(`Стоимость исполнителю: ${(project.executor_cost || 0).toLocaleString('ru-RU')} ₽`)
    sections.push(`Выплачено исполнителю: ${(project.executor_paid_total || 0).toLocaleString('ru-RU')} ₽`)
    sections.push(`Прибыль: ${((project.client_paid_total || 0) - (project.executor_paid_total || 0)).toLocaleString('ru-RU')} ₽`)
    sections.push('')

    if (project.deadline) {
      sections.push('-' + '-'.repeat(60))
      sections.push('⏰ ДЕДЛАЙН')
      sections.push('-' + '-'.repeat(60))
      sections.push(project.deadline)
      sections.push('')
    }

    if (project.assigned_to) {
      sections.push('-' + '-'.repeat(60))
      sections.push('👨‍💻 ИСПОЛНИТЕЛЬ')
      sections.push('-' + '-'.repeat(60))
      sections.push(project.assigned_to.username)
      sections.push('')
    }

    sections.push('-' + '-'.repeat(60))
    sections.push('📝 ОПИСАНИЕ И ТРЕБОВАНИЯ')
    sections.push('-' + '-'.repeat(60))
    sections.push(project.description || 'Описание отсутствует')
    sections.push('')

    if (project.project_metadata?.test_link) {
      sections.push('-' + '-'.repeat(60))
      sections.push('🔗 ТЕСТОВАЯ ССЫЛКА')
      sections.push('-' + '-'.repeat(60))
      sections.push(project.project_metadata.test_link)
      sections.push('')
    }

    sections.push('-' + '-'.repeat(60))
    sections.push('📅 ДАТЫ')
    sections.push('-' + '-'.repeat(60))
    sections.push(`Создан: ${new Date(project.created_at).toLocaleString('ru-RU')}`)
    sections.push(`Обновлен: ${new Date(project.updated_at).toLocaleString('ru-RU')}`)
    sections.push('')

    sections.push('=' + '='.repeat(60))

    return sections.join('\n')
  }

  const descriptionLines = project.description?.split('\n') || []
  const showExpandButton = descriptionLines.length > 10
  const displayedDescription = isExpanded || !showExpandButton
    ? project.description
    : descriptionLines.slice(0, 10).join('\n') + '\n...'

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Техническое задание</h3>
              <p className="text-indigo-100 text-sm mt-1">Проект #{project.id} - {project.title}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors flex items-center gap-2"
            >
              <Copy className="w-4 h-4" />
              Копировать
            </button>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Основная информация */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
              <p className="text-xs text-blue-600 font-semibold mb-1">Клиент</p>
              <p className="text-sm font-bold text-blue-900">
                {project.user?.first_name || 'Не указан'}
              </p>
              <p className="text-xs text-blue-700">@{project.user?.username || 'нет'}</p>
            </div>
            <div className="bg-purple-50 border-l-4 border-purple-500 rounded-lg p-4">
              <p className="text-xs text-purple-600 font-semibold mb-1">Тип проекта</p>
              <p className="text-sm font-bold text-purple-900">{project.project_type || 'Не указан'}</p>
            </div>
          </div>

          {/* Финансы */}
          <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-200">
            <h4 className="font-bold text-emerald-900 mb-4 flex items-center gap-2">
              💰 Финансовая информация
            </h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-emerald-700 mb-1">Стоимость</p>
                <p className="text-xl font-bold text-emerald-900">
                  {(project.estimated_cost || 0).toLocaleString('ru-RU')} ₽
                </p>
              </div>
              <div>
                <p className="text-xs text-emerald-700 mb-1">Оплачено</p>
                <p className="text-xl font-bold text-emerald-900">
                  {(project.client_paid_total || 0).toLocaleString('ru-RU')} ₽
                </p>
              </div>
              <div>
                <p className="text-xs text-orange-700 mb-1">Остаток</p>
                <p className="text-xl font-bold text-orange-900">
                  {((project.estimated_cost || 0) - (project.client_paid_total || 0)).toLocaleString('ru-RU')} ₽
                </p>
              </div>
            </div>
          </div>

          {/* Описание */}
          <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
            <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              📝 Описание и требования
            </h4>
            <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 leading-relaxed">
              {displayedDescription || 'Описание отсутствует'}
            </pre>
            {showExpandButton && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="mt-4 text-indigo-600 hover:text-indigo-700 font-semibold text-sm flex items-center gap-1"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="w-4 h-4" />
                    Свернуть
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4" />
                    Развернуть полностью
                  </>
                )}
              </button>
            )}
          </div>

          {/* Дополнительная информация */}
          {(project.deadline || project.assigned_to || project.project_metadata?.test_link) && (
            <div className="grid gap-4">
              {project.deadline && (
                <div className="bg-orange-50 border-l-4 border-orange-500 rounded-lg p-4">
                  <p className="text-xs text-orange-600 font-semibold mb-1">⏰ Дедлайн</p>
                  <p className="text-sm font-bold text-orange-900">{project.deadline}</p>
                </div>
              )}
              {project.assigned_to && (
                <div className="bg-violet-50 border-l-4 border-violet-500 rounded-lg p-4">
                  <p className="text-xs text-violet-600 font-semibold mb-1">👨‍💻 Исполнитель</p>
                  <p className="text-sm font-bold text-violet-900">{project.assigned_to.username}</p>
                </div>
              )}
              {project.project_metadata?.test_link && (
                <div className="bg-cyan-50 border-l-4 border-cyan-500 rounded-lg p-4">
                  <p className="text-xs text-cyan-600 font-semibold mb-1">🔗 Тестовая ссылка</p>
                  <a
                    href={project.project_metadata.test_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-bold text-cyan-900 hover:underline"
                  >
                    {project.project_metadata.test_link}
                  </a>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <div className="text-xs text-gray-500">
            <span>Создан: {new Date(project.created_at).toLocaleString('ru-RU')}</span>
            <span className="mx-2">•</span>
            <span>Обновлен: {new Date(project.updated_at).toLocaleString('ru-RU')}</span>
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
