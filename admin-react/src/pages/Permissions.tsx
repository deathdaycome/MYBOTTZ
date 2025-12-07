import { useState, useEffect, useCallback, useMemo } from 'react'
import { Shield, Users, Settings, Save, RotateCcw, ChevronDown, ChevronUp, AlertCircle, CheckCircle2, Code, Briefcase, Sliders } from 'lucide-react'
// API imports
import permissionsApi from '../api/permissions'
import type { UserPermissionsData, ModulePermission } from '../api/permissions'
// UI Permissions Editor
import { UIPermissionsEditor } from '../components/permissions/UIPermissionsEditor'

interface User {
  id: number
  name: string
  username: string
  email: string
  role: string
  is_active?: boolean
}

const MODULE_ICONS: Record<string, string> = {
  dashboard: '📊',
  projects: '📁',
  clients: '👥',
  leads: '🎯',
  deals: '🤝',
  finance: '💰',
  documents: '📄',
  reports: '📈',
  settings: '⚙️',
  users: '👤',
  avito: '💬'
}

export const Permissions = () => {
  const [users, setUsers] = useState<User[]>([])
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [userPermissionsData, setUserPermissionsData] = useState<UserPermissionsData | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set())
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [activeTab, setActiveTab] = useState<'module' | 'ui'>('module')

  // Загрузка списка пользователей
  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = useCallback(async () => {
    try {
      const response = await permissionsApi.getUsers()
      if (response.success) {
        // Фильтруем владельцев
        const filteredUsers = response.users.filter(u => u.role !== 'owner')
        setUsers(filteredUsers)
      }
    } catch (error) {
      console.error('Error loading users:', error)
      showToast('Ошибка загрузки пользователей', 'error')
    }
  }, [])

  // Загрузка прав пользователя
  const loadUserPermissions = useCallback(async (userId: number) => {
    setLoading(true)
    try {
      const data = await permissionsApi.getUserPermissions(userId)
      setUserPermissionsData(data)
      setSelectedUserId(userId)
    } catch (error) {
      console.error('Error loading user permissions:', error)
      showToast('Ошибка загрузки прав пользователя', 'error')
    } finally {
      setLoading(false)
    }
  }, [])

  // Показать уведомление
  const showToast = useCallback((message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }, [])

  // Переключить модуль
  const toggleModule = useCallback((moduleKey: string) => {
    setExpandedModules(prev => {
      const newSet = new Set(prev)
      if (newSet.has(moduleKey)) {
        newSet.delete(moduleKey)
      } else {
        newSet.add(moduleKey)
      }
      return newSet
    })
  }, [])

  // Включить/выключить модуль
  const toggleModuleEnabled = useCallback((moduleKey: string, enabled: boolean) => {
    if (!userPermissionsData) return

    setUserPermissionsData(prev => {
      if (!prev) return prev

      const newModulePermissions = { ...prev.module_permissions }
      if (!newModulePermissions[moduleKey]) {
        newModulePermissions[moduleKey] = {
          enabled: false,
          permissions: {},
          data_access: {
            type: 'none',
            can_view: false,
            can_edit: false,
            can_delete: false,
            can_export: false
          }
        }
      }

      newModulePermissions[moduleKey] = {
        ...newModulePermissions[moduleKey],
        enabled
      }

      // Если выключаем модуль, сбрасываем все права
      if (!enabled) {
        const permissions: Record<string, boolean> = {}
        Object.keys(newModulePermissions[moduleKey].permissions).forEach(key => {
          permissions[key] = false
        })
        newModulePermissions[moduleKey].permissions = permissions
      }

      return {
        ...prev,
        module_permissions: newModulePermissions
      }
    })
  }, [userPermissionsData])

  // Обновить разрешение
  const updatePermission = useCallback((moduleKey: string, permission: string, enabled: boolean) => {
    if (!userPermissionsData) return

    setUserPermissionsData(prev => {
      if (!prev) return prev

      const newModulePermissions = { ...prev.module_permissions }
      if (!newModulePermissions[moduleKey]) {
        newModulePermissions[moduleKey] = {
          enabled: false,
          permissions: {},
          data_access: {
            type: 'none',
            can_view: false,
            can_edit: false,
            can_delete: false,
            can_export: false
          }
        }
      }

      newModulePermissions[moduleKey] = {
        ...newModulePermissions[moduleKey],
        permissions: {
          ...newModulePermissions[moduleKey].permissions,
          [permission]: enabled
        }
      }

      return {
        ...prev,
        module_permissions: newModulePermissions
      }
    })
  }, [userPermissionsData])

  // Обновить доступ к данным
  const updateDataAccess = useCallback((moduleKey: string, field: string, value: any) => {
    if (!userPermissionsData) return

    setUserPermissionsData(prev => {
      if (!prev) return prev

      const newModulePermissions = { ...prev.module_permissions }
      if (!newModulePermissions[moduleKey]) {
        newModulePermissions[moduleKey] = {
          enabled: false,
          permissions: {},
          data_access: {
            type: 'none',
            can_view: false,
            can_edit: false,
            can_delete: false,
            can_export: false
          }
        }
      }

      newModulePermissions[moduleKey] = {
        ...newModulePermissions[moduleKey],
        data_access: {
          ...newModulePermissions[moduleKey].data_access,
          [field]: value
        }
      }

      return {
        ...prev,
        module_permissions: newModulePermissions
      }
    })
  }, [userPermissionsData])

  // Применить шаблон роли
  const applyTemplate = useCallback(async (roleName: string) => {
    if (!selectedUserId) {
      showToast('Выберите пользователя', 'error')
      return
    }

    try {
      const template = await permissionsApi.getRoleTemplate(roleName)

      setUserPermissionsData(prev => {
        if (!prev) return prev
        return {
          ...prev,
          module_permissions: template.modules
        }
      })

      showToast(`Применен шаблон "${template.name}"`, 'success')
    } catch (error) {
      console.error('Error applying template:', error)
      showToast('Ошибка применения шаблона', 'error')
    }
  }, [selectedUserId, showToast])

  // Сохранить права
  const savePermissions = useCallback(async () => {
    if (!selectedUserId || !userPermissionsData) {
      showToast('Выберите пользователя', 'error')
      return
    }

    setSaving(true)
    try {
      const result = await permissionsApi.updateUserPermissions(
        selectedUserId,
        userPermissionsData.module_permissions
      )

      if (result.success) {
        showToast('Права пользователя сохранены!', 'success')
      } else {
        throw new Error(result.message)
      }
    } catch (error) {
      console.error('Error saving permissions:', error)
      showToast('Ошибка сохранения прав', 'error')
    } finally {
      setSaving(false)
    }
  }, [selectedUserId, userPermissionsData, showToast])

  // Сбросить права
  const resetPermissions = useCallback(async () => {
    if (!selectedUserId) {
      showToast('Выберите пользователя', 'error')
      return
    }

    if (!confirm('Вы уверены, что хотите сбросить ВСЕ права этого пользователя?')) {
      return
    }

    try {
      const result = await permissionsApi.resetUserPermissions(selectedUserId)

      if (result.success) {
        showToast('Права пользователя сброшены', 'success')
        loadUserPermissions(selectedUserId)
      } else {
        throw new Error(result.message)
      }
    } catch (error) {
      console.error('Error resetting permissions:', error)
      showToast('Ошибка сброса прав', 'error')
    }
  }, [selectedUserId, showToast, loadUserPermissions])

  // Метки для разрешений
  const permissionLabels: Record<string, string> = useMemo(() => ({
    'view': '👀 Просмотр',
    'create': '➕ Создание',
    'edit': '✏️ Редактирование',
    'delete': '🗑️ Удаление',
    'export': '📤 Экспорт',
    'assign': '👤 Назначение',
    'convert': '🔄 Конвертация',
    'close': '✅ Закрытие',
    'contact': '📞 Контакты',
    'reports': '📊 Отчеты',
    'manage': '⚙️ Управление',
    'system.manage': '🛠️ Система',
    'permissions.manage': '🔐 Права',
    'widgets.manage': '📋 Виджеты',
    'messages.send': '💬 Сообщения',
    'chats.manage': '💭 Чаты',
    'settings.edit': '⚙️ Настройки',
    'generate': '📄 Генерация',
    'sign': '✍️ Подписание',
    'schedule': '📅 Планирование'
  }), [])

  return (
    <div className="bg-gradient-to-br from-red-50 via-pink-50 to-red-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-500 to-pink-600 text-white p-8 rounded-3xl shadow-2xl mb-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-4xl font-bold">Управление правами доступа</h1>
              <p className="text-red-100 mt-1">Настройка прав доступа для сотрудников системы</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto px-8 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Users Panel */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl p-6 border border-red-100">
            <div className="flex items-center gap-3 mb-6">
              <Users className="w-6 h-6 text-red-500" />
              <h3 className="text-xl font-bold text-gray-800">Сотрудники</h3>
            </div>

            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {users.map(user => (
                <div
                  key={user.id}
                  onClick={() => loadUserPermissions(user.id)}
                  className={`
                    p-4 rounded-2xl cursor-pointer transition-all duration-300
                    ${selectedUserId === user.id
                      ? 'bg-gradient-to-r from-red-100 to-pink-100 border-2 border-red-500 shadow-lg'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                    }
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center text-white font-bold shadow-lg">
                        {user.username[0].toUpperCase()}
                      </div>
                      <div>
                        <h5 className="font-semibold text-gray-800">{user.username}</h5>
                        <div className={`
                          text-xs px-2 py-1 rounded-full inline-block mt-1
                          ${user.role === 'executor' ? 'bg-green-100 text-green-700' : ''}
                          ${user.role === 'salesperson' ? 'bg-orange-100 text-orange-700' : ''}
                          ${user.role === 'admin' ? 'bg-purple-100 text-purple-700' : ''}
                        `}>
                          {user.role === 'executor' ? '👨‍💻 Исполнитель' : ''}
                          {user.role === 'salesperson' ? '💼 Продажник' : ''}
                          {user.role === 'admin' ? '👑 Администратор' : ''}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {users.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  <Users className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <h4 className="font-semibold text-gray-600">Нет сотрудников</h4>
                  <p className="text-sm">Добавьте сотрудников через раздел "Пользователи"</p>
                </div>
              )}
            </div>
          </div>

          {/* Settings Panel */}
          <div className="lg:col-span-2 bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl p-6 border border-red-100">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Settings className="w-6 h-6 text-red-500" />
                <h3 className="text-xl font-bold text-gray-800">Настройки прав</h3>
              </div>

              {selectedUserId && activeTab === 'module' && (
                <div className="flex gap-2">
                  <button
                    onClick={() => applyTemplate('executor')}
                    className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:shadow-lg transition-all duration-300 flex items-center gap-2"
                  >
                    <Code className="w-4 h-4" />
                    Исполнитель
                  </button>
                  <button
                    onClick={() => applyTemplate('salesperson')}
                    className="px-4 py-2 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl hover:shadow-lg transition-all duration-300 flex items-center gap-2"
                  >
                    <Briefcase className="w-4 h-4" />
                    Продажник
                  </button>
                </div>
              )}
            </div>

            {/* Вкладки */}
            {selectedUserId && (
              <div className="flex gap-2 mb-6 border-b border-gray-200">
                <button
                  onClick={() => setActiveTab('module')}
                  className={`px-4 py-2 font-medium transition-all ${
                    activeTab === 'module'
                      ? 'text-red-600 border-b-2 border-red-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Модульные права
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('ui')}
                  className={`px-4 py-2 font-medium transition-all ${
                    activeTab === 'ui'
                      ? 'text-red-600 border-b-2 border-red-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Sliders className="w-4 h-4" />
                    Детальные UI права
                  </div>
                </button>
              </div>
            )}

            {loading && (
              <div className="text-center py-20">
                <div className="w-12 h-12 border-4 border-red-200 border-t-red-500 rounded-full animate-spin mx-auto mb-4"></div>
                <h4 className="text-gray-600 font-semibold">Загружаем права пользователя...</h4>
              </div>
            )}

            {!loading && !userPermissionsData && (
              <div className="text-center py-20 text-gray-400">
                <Shield className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <h4 className="font-semibold text-gray-600">Выберите сотрудника</h4>
                <p className="text-sm">Выберите сотрудника из списка слева для настройки его прав доступа</p>
              </div>
            )}

            {!loading && userPermissionsData && activeTab === 'module' && (
              <div>
                {/* User Info */}
                <div className="bg-gradient-to-r from-red-50 to-pink-50 rounded-2xl p-5 mb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center text-white font-bold shadow-lg">
                      {userPermissionsData.user.username[0].toUpperCase()}
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-800">{userPermissionsData.user.username}</h4>
                      <p className="text-sm text-gray-600">{userPermissionsData.user.email}</p>
                    </div>
                  </div>
                </div>

                {/* Modules */}
                <div className="space-y-4 max-h-[500px] overflow-y-auto">
                  {Object.entries(userPermissionsData.available_modules).map(([moduleKey, moduleConfig]) => {
                    const userModule = userPermissionsData.module_permissions[moduleKey] || {
                      enabled: false,
                      permissions: {},
                      data_access: { type: 'none', can_view: false, can_edit: false, can_delete: false, can_export: false }
                    }
                    const isEnabled = userModule.enabled
                    const isExpanded = expandedModules.has(moduleKey)

                    return (
                      <div
                        key={moduleKey}
                        className={`
                          rounded-2xl overflow-hidden border-2 transition-all duration-300
                          ${isEnabled ? 'border-green-500 bg-green-50' : 'border-gray-200 bg-gray-50'}
                        `}
                      >
                        {/* Module Header */}
                        <div
                          className="p-4 cursor-pointer hover:bg-white/50 transition-colors"
                          onClick={() => toggleModule(moduleKey)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3 flex-1">
                              <div className="text-2xl">{MODULE_ICONS[moduleKey] || '📦'}</div>
                              <div>
                                <h6 className="font-semibold text-gray-800">{moduleConfig.name}</h6>
                                <small className="text-gray-500">{moduleConfig.description}</small>
                              </div>
                            </div>

                            <div className="flex items-center gap-4">
                              {/* Toggle Switch */}
                              <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                  type="checkbox"
                                  className="sr-only peer"
                                  checked={isEnabled}
                                  onChange={(e) => {
                                    e.stopPropagation()
                                    toggleModuleEnabled(moduleKey, e.target.checked)
                                  }}
                                />
                                <div className="w-14 h-7 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-green-500"></div>
                              </label>

                              {isExpanded ? (
                                <ChevronUp className="w-5 h-5 text-gray-400" />
                              ) : (
                                <ChevronDown className="w-5 h-5 text-gray-400" />
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Module Body */}
                        {isExpanded && (
                          <div className="p-5 bg-white/70 border-t border-gray-200">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                              {/* Permissions */}
                              <div>
                                <h6 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                                  <Shield className="w-4 h-4 text-red-500" />
                                  Разрешения
                                </h6>
                                <div className="space-y-2">
                                  {moduleConfig.permissions.map(permission => {
                                    const isChecked = userModule.permissions[permission] || false
                                    return (
                                      <label
                                        key={permission}
                                        className="flex items-center justify-between p-3 bg-white rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
                                      >
                                        <span className="text-sm text-gray-700">
                                          {permissionLabels[permission] || permission}
                                        </span>
                                        <input
                                          type="checkbox"
                                          className="w-5 h-5 text-green-500 rounded focus:ring-green-500"
                                          checked={isChecked}
                                          onChange={(e) => updatePermission(moduleKey, permission, e.target.checked)}
                                        />
                                      </label>
                                    )
                                  })}
                                </div>
                              </div>

                              {/* Data Access */}
                              <div>
                                <h6 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                                  <Settings className="w-4 h-4 text-red-500" />
                                  Доступ к данным
                                </h6>

                                <select
                                  className="w-full p-3 bg-white border border-gray-300 rounded-xl mb-3 focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                  value={userModule.data_access.type}
                                  onChange={(e) => updateDataAccess(moduleKey, 'type', e.target.value)}
                                >
                                  <option value="none">🚫 Нет доступа</option>
                                  <option value="own">👤 Только свои</option>
                                  <option value="team">👥 Команда</option>
                                  <option value="all">🌐 Все данные</option>
                                </select>

                                <div className="space-y-2">
                                  {['can_view', 'can_edit', 'can_delete', 'can_export'].map(field => (
                                    <label
                                      key={field}
                                      className="flex items-center justify-between p-3 bg-white rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
                                    >
                                      <span className="text-sm text-gray-700">
                                        {field === 'can_view' && '👀 Просмотр'}
                                        {field === 'can_edit' && '✏️ Изменение'}
                                        {field === 'can_delete' && '🗑️ Удаление'}
                                        {field === 'can_export' && '📤 Экспорт'}
                                      </span>
                                      <input
                                        type="checkbox"
                                        className="w-5 h-5 text-green-500 rounded focus:ring-green-500"
                                        checked={userModule.data_access[field as keyof typeof userModule.data_access] as boolean}
                                        onChange={(e) => updateDataAccess(moduleKey, field, e.target.checked)}
                                      />
                                    </label>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={savePermissions}
                    disabled={saving}
                    className="flex-1 px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-2xl hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-3 font-semibold disabled:opacity-50"
                  >
                    {saving ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Сохранение...
                      </>
                    ) : (
                      <>
                        <Save className="w-5 h-5" />
                        Сохранить права
                      </>
                    )}
                  </button>

                  <button
                    onClick={resetPermissions}
                    className="px-6 py-4 bg-white border-2 border-red-300 text-red-600 rounded-2xl hover:bg-red-50 transition-all duration-300 flex items-center gap-3 font-semibold"
                  >
                    <RotateCcw className="w-5 h-5" />
                    Сбросить все
                  </button>
                </div>
              </div>
            )}

            {/* UI Permissions Editor */}
            {!loading && selectedUserId && activeTab === 'ui' && (
              <UIPermissionsEditor
                userId={selectedUserId}
                username={userPermissionsData?.user.username || `User #${selectedUserId}`}
                onSave={() => {
                  showToast('Детальные UI права успешно обновлены', 'success')
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className={`
          fixed top-6 right-6 px-6 py-4 rounded-2xl shadow-2xl border-l-4 z-50
          animate-in slide-in-from-right duration-300
          ${toast.type === 'success'
            ? 'bg-white border-green-500'
            : 'bg-white border-red-500'
          }
        `}>
          <div className="flex items-center gap-3">
            {toast.type === 'success' ? (
              <CheckCircle2 className="w-6 h-6 text-green-500" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-500" />
            )}
            <span className="font-medium text-gray-800">{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  )
}
