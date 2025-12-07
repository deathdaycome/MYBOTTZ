import React, { useState, useEffect } from 'react'
import { Sliders, Plus, X, Edit2, Trash2, Type, Hash, Calendar as CalendarIcon, ToggleLeft, List, FileText } from 'lucide-react'

interface CustomFieldsProps {
  projectId: number
  onClose: () => void
}

interface CustomField {
  id: number
  name: string
  type: 'text' | 'number' | 'date' | 'boolean' | 'select' | 'textarea'
  required: boolean
  defaultValue?: string
  options?: string[]
  description: string
  createdAt: string
}

const CustomFields: React.FC<CustomFieldsProps> = ({ projectId, onClose }) => {
  const [fields, setFields] = useState<CustomField[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)

  const [newField, setNewField] = useState({
    name: '',
    type: 'text' as CustomField['type'],
    required: false,
    defaultValue: '',
    options: [] as string[],
    description: '',
  })

  const [newOption, setNewOption] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = 'unset' }
  }, [])

  useEffect(() => {
    fetchFields()
  }, [projectId])

  const fetchFields = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/custom-fields`, {
        headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
      })
      if (response.ok) {
        const data = await response.json()
        setFields(data)
      } else {
        setFields([
          {
            id: 1,
            name: 'Номер контракта',
            type: 'text',
            required: true,
            defaultValue: '',
            description: 'Уникальный номер контракта с клиентом',
            createdAt: '2024-03-01',
          },
          {
            id: 2,
            name: 'Стоимость проекта',
            type: 'number',
            required: true,
            defaultValue: '0',
            description: 'Общая стоимость проекта в рублях',
            createdAt: '2024-03-01',
          },
          {
            id: 3,
            name: 'Дата подписания',
            type: 'date',
            required: false,
            description: 'Дата подписания контракта',
            createdAt: '2024-03-01',
          },
          {
            id: 4,
            name: 'NDA подписан',
            type: 'boolean',
            required: false,
            defaultValue: 'false',
            description: 'Подписано ли соглашение о неразглашении',
            createdAt: '2024-03-01',
          },
          {
            id: 5,
            name: 'Приоритет клиента',
            type: 'select',
            required: false,
            options: ['VIP', 'Высокий', 'Средний', 'Низкий'],
            description: 'Приоритет обслуживания клиента',
            createdAt: '2024-03-01',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching fields:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddField = async () => {
    if (!newField.name) {
      alert('Введите название поля')
      return
    }

    const fieldData: CustomField = {
      ...newField,
      id: Date.now(),
      createdAt: new Date().toISOString(),
    }

    setFields([...fields, fieldData])
    setShowAddModal(false)
    setNewField({
      name: '',
      type: 'text',
      required: false,
      defaultValue: '',
      options: [],
      description: '',
    })
  }

  const handleDeleteField = (fieldId: number) => {
    if (!confirm('Удалить поле?')) return
    setFields(fields.filter((f) => f.id !== fieldId))
  }

  const getFieldIcon = (type: string) => {
    const icons = {
      text: Type,
      number: Hash,
      date: CalendarIcon,
      boolean: ToggleLeft,
      select: List,
      textarea: FileText,
    }
    return icons[type as keyof typeof icons] || Type
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка полей...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Sliders className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Пользовательские поля</h2>
              <p className="text-orange-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex justify-between items-center p-6 bg-white border-b">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Всего полей: {fields.length}</h3>
            <p className="text-sm text-gray-500">Настраиваемые поля для проекта</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить поле
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fields.map((field) => {
              const FieldIcon = getFieldIcon(field.type)
              return (
                <div key={field.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-3 flex-1">
                      <FieldIcon className="w-8 h-8 text-orange-600 flex-shrink-0 mt-1" />
                      <div className="flex-1">
                        <h3 className="font-bold text-lg text-gray-900 mb-1">{field.name}</h3>
                        {field.required && (
                          <span className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded-full">Обязательное</span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteField(field.id)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">{field.description}</p>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Тип:</span>
                      <span className="font-medium text-gray-900 capitalize">{field.type}</span>
                    </div>
                    {field.defaultValue && (
                      <div className="flex justify-between">
                        <span className="text-gray-500">Значение по умолчанию:</span>
                        <span className="font-medium text-gray-900">{field.defaultValue}</span>
                      </div>
                    )}
                    {field.options && field.options.length > 0 && (
                      <div>
                        <p className="text-gray-500 mb-1">Варианты:</p>
                        <div className="flex flex-wrap gap-1">
                          {field.options.map((opt, idx) => (
                            <span key={idx} className="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded">
                              {opt}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {fields.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Sliders className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Нет пользовательских полей</p>
            </div>
          )}
        </div>

        {showAddModal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">Создать поле</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название *</label>
                  <input
                    type="text"
                    value={newField.name}
                    onChange={(e) => setNewField({ ...newField, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Тип</label>
                  <select
                    value={newField.type}
                    onChange={(e) => setNewField({ ...newField, type: e.target.value as CustomField['type'] })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  >
                    <option value="text">Текст</option>
                    <option value="number">Число</option>
                    <option value="date">Дата</option>
                    <option value="boolean">Да/Нет</option>
                    <option value="select">Выбор из списка</option>
                    <option value="textarea">Многострочный текст</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                  <textarea
                    value={newField.description}
                    onChange={(e) => setNewField({ ...newField, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={newField.required}
                      onChange={(e) => setNewField({ ...newField, required: e.target.checked })}
                      className="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Обязательное поле</span>
                  </label>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Значение по умолчанию</label>
                  <input
                    type="text"
                    value={newField.defaultValue}
                    onChange={(e) => setNewField({ ...newField, defaultValue: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>
                {newField.type === 'select' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Варианты выбора</label>
                    <div className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={newOption}
                        onChange={(e) => setNewOption(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && newOption) {
                            setNewField({ ...newField, options: [...(newField.options || []), newOption] })
                            setNewOption('')
                          }
                        }}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        placeholder="Добавить вариант (Enter)"
                      />
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(newField.options || []).map((opt, idx) => (
                        <span key={idx} className="inline-flex items-center gap-1 text-sm px-3 py-1 bg-orange-100 text-orange-700 rounded-full">
                          {opt}
                          <button
                            onClick={() =>
                              setNewField({ ...newField, options: (newField.options || []).filter((_, i) => i !== idx) })
                            }
                            className="hover:text-orange-900"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddField}
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                >
                  Создать
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CustomFields
