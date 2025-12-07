import { useState, useEffect } from 'react'
import { X, Tag, Plus, Trash2, Edit2, Check, Search, Filter } from 'lucide-react'

interface Label {
  id: number
  name: string
  color: string
  description: string
  projectCount: number
  createdAt: string
}

interface ProjectLabelsProps {
  isOpen: boolean
  onClose: () => void
  onLabelsUpdated?: () => void
}

const PRESET_COLORS = [
  '#EF4444', // red
  '#F59E0B', // orange
  '#10B981', // green
  '#3B82F6', // blue
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#14B8A6', // teal
  '#6B7280', // gray
  '#F97316', // deep orange
  '#06B6D4', // cyan
  '#84CC16', // lime
  '#A855F7', // violet
]

export const ProjectLabels = ({
  isOpen,
  onClose,
  onLabelsUpdated,
}: ProjectLabelsProps) => {
  const [labels, setLabels] = useState<Label[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    color: PRESET_COLORS[0],
    description: '',
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      loadLabels()
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

  const loadLabels = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8001/admin/api/labels', {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setLabels(data.labels || [])
      } else {
        // Mock data
        setLabels([
          {
            id: 1,
            name: 'Срочно',
            color: '#EF4444',
            description: 'Требует немедленного внимания',
            projectCount: 5,
            createdAt: new Date().toISOString(),
          },
          {
            id: 2,
            name: 'Веб-разработка',
            color: '#3B82F6',
            description: 'Проекты веб-разработки',
            projectCount: 12,
            createdAt: new Date().toISOString(),
          },
          {
            id: 3,
            name: 'Мобильное приложение',
            color: '#10B981',
            description: 'Разработка мобильных приложений',
            projectCount: 8,
            createdAt: new Date().toISOString(),
          },
          {
            id: 4,
            name: 'Дизайн',
            color: '#EC4899',
            description: 'Дизайн-проекты',
            projectCount: 15,
            createdAt: new Date().toISOString(),
          },
          {
            id: 5,
            name: 'Консалтинг',
            color: '#8B5CF6',
            description: 'Консалтинговые услуги',
            projectCount: 6,
            createdAt: new Date().toISOString(),
          },
          {
            id: 6,
            name: 'Поддержка',
            color: '#F59E0B',
            description: 'Техническая поддержка',
            projectCount: 20,
            createdAt: new Date().toISOString(),
          },
        ])
      }
    } catch (err) {
      console.error('Error loading labels:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateLabel = async () => {
    if (!formData.name.trim()) return

    try {
      const response = await fetch('http://localhost:8001/admin/api/labels', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setFormData({ name: '', color: PRESET_COLORS[0], description: '' })
        setIsCreating(false)
        await loadLabels()
        if (onLabelsUpdated) onLabelsUpdated()
      }
    } catch (err) {
      console.error('Error creating label:', err)
    }
  }

  const handleUpdateLabel = async (labelId: number) => {
    if (!formData.name.trim()) return

    try {
      const response = await fetch(`http://localhost:8001/admin/api/labels/${labelId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setFormData({ name: '', color: PRESET_COLORS[0], description: '' })
        setEditingId(null)
        await loadLabels()
        if (onLabelsUpdated) onLabelsUpdated()
      }
    } catch (err) {
      console.error('Error updating label:', err)
    }
  }

  const handleDeleteLabel = async (labelId: number) => {
    const label = labels.find((l) => l.id === labelId)
    if (
      label &&
      label.projectCount > 0 &&
      !confirm(
        `Метка "${label.name}" используется в ${label.projectCount} проектах. Удалить?`
      )
    ) {
      return
    }

    try {
      const response = await fetch(`http://localhost:8001/admin/api/labels/${labelId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        await loadLabels()
        if (onLabelsUpdated) onLabelsUpdated()
      }
    } catch (err) {
      console.error('Error deleting label:', err)
    }
  }

  const startEdit = (label: Label) => {
    setEditingId(label.id)
    setFormData({
      name: label.name,
      color: label.color,
      description: label.description,
    })
    setIsCreating(false)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setIsCreating(false)
    setFormData({ name: '', color: PRESET_COLORS[0], description: '' })
  }

  const filteredLabels = labels.filter((label) =>
    label.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-pink-600 to-rose-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Tag className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Метки проектов</h3>
              <p className="text-pink-100 text-sm mt-1">Управление метками для фильтрации</p>
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

        {/* Search and Add */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex-shrink-0">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border-2 border-gray-300 rounded-lg focus:border-pink-500 outline-none"
                placeholder="Поиск меток..."
              />
            </div>

            {!isCreating && !editingId && (
              <button
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-2 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors font-semibold"
              >
                <Plus className="w-5 h-5" />
                Создать метку
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Create/Edit Form */}
          {(isCreating || editingId) && (
            <div className="mb-6 bg-pink-50 border-2 border-pink-200 rounded-xl p-4">
              <h4 className="font-bold text-gray-900 mb-4">
                {editingId ? 'Редактировать метку' : 'Новая метка'}
              </h4>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Название
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-pink-300 rounded-lg focus:border-pink-500 outline-none"
                    placeholder="Название метки"
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Описание
                  </label>
                  <input
                    type="text"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-pink-300 rounded-lg focus:border-pink-500 outline-none"
                    placeholder="Краткое описание"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Цвет</label>
                  <div className="flex flex-wrap gap-2">
                    {PRESET_COLORS.map((color) => (
                      <button
                        key={color}
                        onClick={() => setFormData({ ...formData, color })}
                        className={`w-10 h-10 rounded-lg border-4 transition-all ${
                          formData.color === color
                            ? 'border-gray-900 scale-110'
                            : 'border-gray-300 hover:scale-105'
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>

                  {/* Preview */}
                  <div className="mt-3 p-3 bg-white rounded-lg border-2 border-gray-200">
                    <div className="text-xs text-gray-600 mb-2">Предпросмотр:</div>
                    <span
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-white text-sm font-semibold"
                      style={{ backgroundColor: formData.color }}
                    >
                      <Tag className="w-4 h-4" />
                      {formData.name || 'Название метки'}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => (editingId ? handleUpdateLabel(editingId) : handleCreateLabel())}
                    disabled={!formData.name.trim()}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                  >
                    <Check className="w-4 h-4" />
                    {editingId ? 'Сохранить' : 'Создать'}
                  </button>
                  <button
                    onClick={cancelEdit}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Labels List */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка меток...</div>
          ) : filteredLabels.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Tag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">
                {searchQuery ? 'Метки не найдены' : 'Нет меток'}
              </p>
              <p className="text-sm mt-2">
                {searchQuery ? 'Попробуйте другой поисковый запрос' : 'Создайте первую метку'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {filteredLabels.map((label) => (
                <div
                  key={label.id}
                  className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-pink-400 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div
                        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-white text-sm font-semibold mb-2"
                        style={{ backgroundColor: label.color }}
                      >
                        <Tag className="w-4 h-4" />
                        {label.name}
                      </div>

                      {label.description && (
                        <p className="text-sm text-gray-600 mb-2">{label.description}</p>
                      )}

                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Filter className="w-3.5 h-3.5" />
                        <span>Используется в {label.projectCount} проектах</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 ml-3">
                      <button
                        onClick={() => startEdit(label)}
                        className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                        title="Редактировать"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteLabel(label.id)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            Всего меток: <span className="font-bold text-pink-600">{labels.length}</span>
          </div>
          <button
            type="button"
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
