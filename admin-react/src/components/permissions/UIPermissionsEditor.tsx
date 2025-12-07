import { useState, useEffect } from 'react'
import {
  Eye,
  EyeOff,
  Save,
  RotateCcw,
  Copy,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  FileText,
  MousePointer,
  Layout,
  Columns,
  Menu,
  Zap
} from 'lucide-react'
import {
  getUIStructure,
  getUserUIPermissions,
  updateUserUIPermissions,
  resetUserUIPermissions,
  groupPermissionsByModuleAndType,
  flattenGroupedPermissions
} from '../../api/uiPermissions'
import type { UIStructure, UserUIPermissions } from '../../types/uiPermissions'

interface UIPermissionsEditorProps {
  userId: number
  username: string
  onSave?: () => void
}

interface ElementGroup {
  id: string
  name: string
  enabled: boolean
}

interface GroupedElements {
  field: ElementGroup[]
  button: ElementGroup[]
  section: ElementGroup[]
  column: ElementGroup[]
  tab: ElementGroup[]
  action: ElementGroup[]
}

const elementTypeIcons = {
  field: FileText,
  button: MousePointer,
  section: Layout,
  column: Columns,
  tab: Menu,
  action: Zap
}

const elementTypeNames = {
  field: 'Поля',
  button: 'Кнопки',
  section: 'Секции',
  column: 'Колонки',
  tab: 'Вкладки',
  action: 'Действия'
}

export const UIPermissionsEditor = ({ userId, username, onSave }: UIPermissionsEditorProps) => {
  const [structure, setStructure] = useState<UIStructure | null>(null)
  const [permissions, setPermissions] = useState<UserUIPermissions>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set())
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    loadData()
  }, [userId])

  const loadData = async () => {
    setLoading(true)
    try {
      const [structureData, permissionsData] = await Promise.all([
        getUIStructure(),
        getUserUIPermissions(userId)
      ])
      setStructure(structureData)
      setPermissions(permissionsData.permissions)
      setHasChanges(false)
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleModule = (moduleKey: string) => {
    const newExpanded = new Set(expandedModules)
    if (newExpanded.has(moduleKey)) {
      newExpanded.delete(moduleKey)
    } else {
      newExpanded.add(moduleKey)
    }
    setExpandedModules(newExpanded)
  }

  const toggleElement = (moduleKey: string, elementId: string) => {
    const fullId = `${moduleKey}.${elementId}`
    const currentValue = permissions[fullId]?.is_enabled ?? true

    setPermissions(prev => ({
      ...prev,
      [fullId]: {
        ...prev[fullId],
        is_enabled: !currentValue,
        element_type: prev[fullId]?.element_type || 'field'
      }
    }))
    setHasChanges(true)
  }

  const toggleAllInModule = (moduleKey: string, enabled: boolean) => {
    if (!structure) return

    const newPermissions = { ...permissions }
    const moduleElements = structure[moduleKey]?.elements || {}

    Object.keys(moduleElements).forEach(elementId => {
      const fullId = `${moduleKey}.${elementId}`
      newPermissions[fullId] = {
        is_enabled: enabled,
        element_type: moduleElements[elementId].type
      }
    })

    setPermissions(newPermissions)
    setHasChanges(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      // Преобразуем права в формат для API
      const permissionsToSave: Record<string, boolean> = {}
      Object.entries(permissions).forEach(([key, value]) => {
        permissionsToSave[key] = value.is_enabled
      })

      await updateUserUIPermissions(userId, permissionsToSave)
      setHasChanges(false)
      onSave?.()
    } catch (error) {
      console.error('Ошибка сохранения:', error)
      alert('Ошибка при сохранении прав доступа')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = async () => {
    if (!confirm('Вы уверены? Это удалит все ограничения и даст полный доступ.')) return

    setSaving(true)
    try {
      await resetUserUIPermissions(userId)
      await loadData()
      onSave?.()
    } catch (error) {
      console.error('Ошибка сброса:', error)
      alert('Ошибка при сбросе прав доступа')
    } finally {
      setSaving(false)
    }
  }

  const expandAll = () => {
    if (!structure) return
    setExpandedModules(new Set(Object.keys(structure)))
  }

  const collapseAll = () => {
    setExpandedModules(new Set())
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  if (!structure) {
    return (
      <div className="text-center p-12 text-gray-600">
        Не удалось загрузить структуру элементов
      </div>
    )
  }

  const grouped = groupPermissionsByModuleAndType(structure, permissions)

  return (
    <div className="space-y-4">
      {/* Заголовок и действия */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Детальные права доступа
            </h3>
            <p className="text-sm text-gray-600">
              Управление доступом к каждому полю, кнопке и разделу для {username}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={expandAll}
              className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              Развернуть все
            </button>
            <button
              onClick={collapseAll}
              className="px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              Свернуть все
            </button>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleSave}
            disabled={!hasChanges || saving}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              hasChanges && !saving
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Save className="w-4 h-4" />
            {saving ? 'Сохранение...' : 'Сохранить изменения'}
          </button>

          <button
            onClick={handleReset}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Сбросить (полный доступ)
          </button>

          <button
            onClick={loadData}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Отменить изменения
          </button>
        </div>

        {hasChanges && (
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
            У вас есть несохраненные изменения
          </div>
        )}
      </div>

      {/* Список модулей */}
      <div className="space-y-3">
        {grouped.map(group => {
          const isExpanded = expandedModules.has(group.module)
          const totalElements = Object.values(group.elementsByType).reduce(
            (sum, arr) => sum + arr.length,
            0
          )
          const enabledElements = Object.values(group.elementsByType).reduce(
            (sum, arr) => sum + arr.filter(e => e.enabled).length,
            0
          )
          const allEnabled = enabledElements === totalElements
          const someEnabled = enabledElements > 0 && enabledElements < totalElements

          return (
            <div key={group.module} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              {/* Заголовок модуля */}
              <div className="p-4 bg-gradient-to-r from-gray-50 to-white border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => toggleModule(group.module)}
                    className="flex items-center gap-3 flex-1 text-left"
                  >
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-500" />
                    )}
                    <div>
                      <h4 className="font-semibold text-gray-900">{group.moduleName}</h4>
                      <p className="text-sm text-gray-600">
                        {enabledElements} из {totalElements} элементов доступно
                      </p>
                    </div>
                  </button>

                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleAllInModule(group.module, true)
                      }}
                      className="px-3 py-1 text-sm text-green-700 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4 inline mr-1" />
                      Все вкл
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleAllInModule(group.module, false)
                      }}
                      className="px-3 py-1 text-sm text-red-700 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                    >
                      <EyeOff className="w-4 h-4 inline mr-1" />
                      Все выкл
                    </button>
                  </div>
                </div>
              </div>

              {/* Элементы модуля */}
              {isExpanded && (
                <div className="p-4 space-y-4">
                  {Object.entries(group.elementsByType).map(([type, elements]) => {
                    if (elements.length === 0) return null

                    const Icon = elementTypeIcons[type as keyof typeof elementTypeIcons]
                    const typeName = elementTypeNames[type as keyof typeof elementTypeNames]

                    return (
                      <div key={type} className="space-y-2">
                        <div className="flex items-center gap-2 mb-2">
                          <Icon className="w-4 h-4 text-gray-500" />
                          <h5 className="font-medium text-gray-700">{typeName}</h5>
                          <span className="text-xs text-gray-500">({elements.length})</span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                          {elements.map(element => (
                            <button
                              key={element.id}
                              onClick={() => toggleElement(group.module, element.id)}
                              className={`flex items-center gap-2 p-2 rounded-lg border transition-all ${
                                element.enabled
                                  ? 'bg-green-50 border-green-200 text-green-900 hover:bg-green-100'
                                  : 'bg-red-50 border-red-200 text-red-900 hover:bg-red-100'
                              }`}
                            >
                              {element.enabled ? (
                                <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                              )}
                              <span className="text-sm truncate">{element.name}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
