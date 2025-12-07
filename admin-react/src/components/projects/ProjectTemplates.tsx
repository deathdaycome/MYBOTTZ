import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Edit2, Copy, FileText, Star } from 'lucide-react'

interface ProjectTemplate {
  id: number
  name: string
  description: string
  category: string
  project_type: string
  complexity: string
  estimated_hours: number
  estimated_cost: number
  tasks: Array<{
    title: string
    description: string
    estimated_hours: number
  }>
  isFavorite: boolean
  usageCount: number
}

interface ProjectTemplatesProps {
  isOpen: boolean
  onClose: () => void
  onSelectTemplate: (template: ProjectTemplate) => void
}

const CATEGORIES = [
  'Веб-разработка',
  'Мобильная разработка',
  'Дизайн',
  'Маркетинг',
  'Консалтинг',
  'Другое',
]

export const ProjectTemplates = ({
  isOpen,
  onClose,
  onSelectTemplate,
}: ProjectTemplatesProps) => {
  const [templates, setTemplates] = useState<ProjectTemplate[]>([])
  const [loading, setLoading] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: CATEGORIES[0],
    project_type: 'Разработка',
    complexity: 'medium',
    estimated_hours: 0,
    estimated_cost: 0,
    tasks: [] as Array<{ title: string; description: string; estimated_hours: number }>,
  })

  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    estimated_hours: 0,
  })

  useEffect(() => {
    if (isOpen) {
      loadTemplates()

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

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8001/admin/api/project-templates', {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setTemplates(data.templates || [])
      } else {
        setTemplates(getMockTemplates())
      }
    } catch (err) {
      console.error('Error loading templates:', err)
      setTemplates(getMockTemplates())
    } finally {
      setLoading(false)
    }
  }

  const getMockTemplates = (): ProjectTemplate[] => {
    return [
      {
        id: 1,
        name: 'Интернет-магазин (базовый)',
        description: 'Стандартный интернет-магазин с каталогом, корзиной и оплатой',
        category: 'Веб-разработка',
        project_type: 'Интернет-магазин',
        complexity: 'medium',
        estimated_hours: 120,
        estimated_cost: 150000,
        tasks: [
          { title: 'Дизайн макетов', description: 'Создание дизайна', estimated_hours: 20 },
          { title: 'Верстка', description: 'HTML/CSS верстка', estimated_hours: 30 },
          { title: 'Бэкенд', description: 'API и база данных', estimated_hours: 40 },
          { title: 'Интеграция оплаты', description: 'Подключение платежей', estimated_hours: 20 },
          { title: 'Тестирование', description: 'QA тестирование', estimated_hours: 10 },
        ],
        isFavorite: true,
        usageCount: 15,
      },
      {
        id: 2,
        name: 'Корпоративный сайт',
        description: 'Многостраничный сайт компании с админ-панелью',
        category: 'Веб-разработка',
        project_type: 'Корпоративный сайт',
        complexity: 'simple',
        estimated_hours: 80,
        estimated_cost: 100000,
        tasks: [
          { title: 'Дизайн', description: 'Дизайн страниц', estimated_hours: 15 },
          { title: 'Верстка', description: 'Адаптивная верстка', estimated_hours: 25 },
          { title: 'CMS', description: 'Система управления', estimated_hours: 30 },
          { title: 'Наполнение', description: 'Контент', estimated_hours: 10 },
        ],
        isFavorite: false,
        usageCount: 8,
      },
      {
        id: 3,
        name: 'Мобильное приложение',
        description: 'Кроссплатформенное приложение на React Native',
        category: 'Мобильная разработка',
        project_type: 'Мобильное приложение',
        complexity: 'complex',
        estimated_hours: 200,
        estimated_cost: 250000,
        tasks: [
          { title: 'UX/UI дизайн', description: 'Дизайн интерфейса', estimated_hours: 30 },
          { title: 'Разработка iOS', description: 'iOS версия', estimated_hours: 70 },
          { title: 'Разработка Android', description: 'Android версия', estimated_hours: 70 },
          { title: 'Backend API', description: 'Серверная часть', estimated_hours: 30 },
        ],
        isFavorite: true,
        usageCount: 5,
      },
    ]
  }

  const handleCreate = async () => {
    if (!formData.name || !formData.description) {
      alert('Заполните обязательные поля')
      return
    }

    try {
      const response = await fetch('http://localhost:8001/admin/api/project-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await loadTemplates()
        resetForm()
      }
    } catch (err) {
      console.error('Error creating template:', err)
    }
  }

  const handleUpdate = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8001/admin/api/project-templates/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await loadTemplates()
        setEditingId(null)
        resetForm()
      }
    } catch (err) {
      console.error('Error updating template:', err)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить шаблон?')) return

    try {
      const response = await fetch(`http://localhost:8001/admin/api/project-templates/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        await loadTemplates()
      }
    } catch (err) {
      console.error('Error deleting template:', err)
    }
  }

  const handleToggleFavorite = async (id: number) => {
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/project-templates/${id}/favorite`,
        {
          method: 'POST',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadTemplates()
      }
    } catch (err) {
      console.error('Error toggling favorite:', err)
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: CATEGORIES[0],
      project_type: 'Разработка',
      complexity: 'medium',
      estimated_hours: 0,
      estimated_cost: 0,
      tasks: [],
    })
    setIsCreating(false)
    setEditingId(null)
  }

  const startEdit = (template: ProjectTemplate) => {
    setFormData({
      name: template.name,
      description: template.description,
      category: template.category,
      project_type: template.project_type,
      complexity: template.complexity,
      estimated_hours: template.estimated_hours,
      estimated_cost: template.estimated_cost,
      tasks: [...template.tasks],
    })
    setEditingId(template.id)
    setIsCreating(true)
  }

  const addTask = () => {
    if (!newTask.title) return

    setFormData({
      ...formData,
      tasks: [...formData.tasks, { ...newTask }],
    })
    setNewTask({ title: '', description: '', estimated_hours: 0 })
  }

  const removeTask = (index: number) => {
    setFormData({
      ...formData,
      tasks: formData.tasks.filter((_, i) => i !== index),
    })
  }

  const filteredTemplates = templates
    .filter((t) => selectedCategory === 'all' || t.category === selectedCategory)
    .filter((t) => t.name.toLowerCase().includes(searchTerm.toLowerCase()))

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Шаблоны проектов</h3>
              <p className="text-violet-100 text-sm mt-1">
                Создавайте проекты быстрее с готовыми шаблонами
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

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-4 mb-3">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Поиск шаблонов..."
              className="flex-1 px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 outline-none"
            />
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-gray-700">Категория:</span>
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Все
            </button>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === cat
                    ? 'bg-violet-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Create/Edit Form */}
          {isCreating ? (
            <div className="bg-violet-50 border-2 border-violet-200 rounded-xl p-6 mb-6">
              <h4 className="text-lg font-bold text-gray-900 mb-4">
                {editingId ? 'Редактировать шаблон' : 'Создать новый шаблон'}
              </h4>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Название *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Категория
                    </label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 outline-none"
                    >
                      {CATEGORIES.map((cat) => (
                        <option key={cat} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Описание *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 outline-none"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Часы</label>
                    <input
                      type="number"
                      value={formData.estimated_hours}
                      onChange={(e) =>
                        setFormData({ ...formData, estimated_hours: Number(e.target.value) })
                      }
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Стоимость
                    </label>
                    <input
                      type="number"
                      value={formData.estimated_cost}
                      onChange={(e) =>
                        setFormData({ ...formData, estimated_cost: Number(e.target.value) })
                      }
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Сложность
                    </label>
                    <select
                      value={formData.complexity}
                      onChange={(e) => setFormData({ ...formData, complexity: e.target.value })}
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-violet-500 outline-none"
                    >
                      <option value="simple">Простой</option>
                      <option value="medium">Средний</option>
                      <option value="complex">Сложный</option>
                    </select>
                  </div>
                </div>

                {/* Tasks */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Задачи</label>
                  <div className="space-y-2 mb-3">
                    {formData.tasks.map((task, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-2 p-3 bg-white border border-gray-300 rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="font-medium text-sm">{task.title}</div>
                          <div className="text-xs text-gray-500">
                            {task.estimated_hours} часов
                          </div>
                        </div>
                        <button
                          onClick={() => removeTask(index)}
                          className="p-1 text-red-600 hover:bg-red-100 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newTask.title}
                      onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                      placeholder="Название задачи"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                    />
                    <input
                      type="number"
                      value={newTask.estimated_hours}
                      onChange={(e) =>
                        setNewTask({ ...newTask, estimated_hours: Number(e.target.value) })
                      }
                      placeholder="Часы"
                      className="w-24 px-3 py-2 border border-gray-300 rounded-lg"
                    />
                    <button
                      onClick={addTask}
                      className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="flex gap-2 pt-4">
                  <button
                    onClick={() => (editingId ? handleUpdate(editingId) : handleCreate())}
                    className="flex-1 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors font-semibold"
                  >
                    {editingId ? 'Сохранить' : 'Создать'}
                  </button>
                  <button
                    onClick={resetForm}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsCreating(true)}
              className="w-full px-4 py-3 mb-6 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl hover:from-violet-700 hover:to-purple-700 transition-all font-semibold flex items-center justify-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Создать шаблон
            </button>
          )}

          {/* Templates Grid */}
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка...</div>
          ) : filteredTemplates.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Шаблоны не найдены</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredTemplates.map((template) => (
                <div
                  key={template.id}
                  className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-violet-300 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="text-lg font-bold text-gray-900">{template.name}</h4>
                        {template.isFavorite && (
                          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="px-2 py-1 bg-violet-100 text-violet-700 rounded text-xs font-medium">
                          {template.category}
                        </span>
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {template.estimated_hours} ч
                        </span>
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                          {template.estimated_cost.toLocaleString()}₽
                        </span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                          {template.tasks.length} задач
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-1">
                      <button
                        onClick={() => handleToggleFavorite(template.id)}
                        className="p-2 hover:bg-gray-100 rounded transition-colors"
                        title="В избранное"
                      >
                        <Star
                          className={`w-4 h-4 ${
                            template.isFavorite
                              ? 'text-yellow-500 fill-yellow-500'
                              : 'text-gray-400'
                          }`}
                        />
                      </button>
                      <button
                        onClick={() => startEdit(template)}
                        className="p-2 hover:bg-gray-100 rounded transition-colors"
                        title="Редактировать"
                      >
                        <Edit2 className="w-4 h-4 text-gray-600" />
                      </button>
                      <button
                        onClick={() => handleDelete(template.id)}
                        className="p-2 hover:bg-gray-100 rounded transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => {
                        onSelectTemplate(template)
                        onClose()
                      }}
                      className="flex-1 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors font-semibold flex items-center justify-center gap-2"
                    >
                      <Copy className="w-4 h-4" />
                      Использовать
                    </button>
                  </div>

                  <div className="mt-2 text-xs text-gray-500 text-right">
                    Использован {template.usageCount} раз
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Всего шаблонов: <strong>{filteredTemplates.length}</strong>
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
