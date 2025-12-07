import { useState, useEffect, useCallback, useMemo } from 'react'
import { Users as UsersIcon, UserPlus, Search, Edit, Key, Eye, EyeOff, UserCheck, UserX, Trash2, CheckCircle2, AlertCircle, Crown, Shield as ShieldIcon, User as UserIcon, Briefcase } from 'lucide-react'
// API imports
import usersApi from '../api/users'
import type { User, CreateUserData, UpdateUserData } from '../api/users'

export const Users = () => {
  const [users, setUsers] = useState<User[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [showViewPasswordModal, setShowViewPasswordModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [viewPassword, setViewPassword] = useState('')

  // Form state
  const [newUserData, setNewUserData] = useState<CreateUserData>({
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'executor'
  })

  const [editUserData, setEditUserData] = useState<UpdateUserData>({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    is_active: true
  })

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  // Загрузка пользователей
  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = useCallback(async () => {
    setLoading(true)
    try {
      const response = await usersApi.getUsers()
      if (response.success) {
        setUsers(response.users)
      }
    } catch (error) {
      console.error('Error loading users:', error)
      showToast('Ошибка загрузки пользователей', 'error')
    } finally {
      setLoading(false)
    }
  }, [])

  // Показать уведомление
  const showToast = useCallback((message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }, [])

  // Фильтрация пользователей
  const filteredUsers = useMemo(() => {
    if (!searchQuery) return users

    const query = searchQuery.toLowerCase()
    return users.filter(user =>
      user.username.toLowerCase().includes(query) ||
      user.email?.toLowerCase().includes(query) ||
      user.first_name?.toLowerCase().includes(query) ||
      user.last_name?.toLowerCase().includes(query)
    )
  }, [users, searchQuery])

  // Статистика
  const stats = useMemo(() => ({
    total: users.length,
    owners: users.filter(u => u.role === 'owner').length,
    admins: users.filter(u => u.role === 'admin').length,
    executors: users.filter(u => u.role === 'executor').length,
    salespeople: users.filter(u => u.role === 'salesperson').length,
    timleads: users.filter(u => u.role === 'timlead').length
  }), [users])

  // Создать пользователя
  const handleCreateUser = useCallback(async () => {
    if (!newUserData.username || !newUserData.password) {
      showToast('Заполните обязательные поля', 'error')
      return
    }

    try {
      const response = await usersApi.createUser(newUserData)
      if (response.success) {
        showToast('Пользователь успешно создан', 'success')
        setShowAddModal(false)
        setNewUserData({
          username: '',
          password: '',
          email: '',
          first_name: '',
          last_name: '',
          role: 'executor'
        })
        loadUsers()
      } else {
        showToast(response.message || response.detail || 'Ошибка создания пользователя', 'error')
      }
    } catch (error: any) {
      console.error('Error creating user:', error)
      showToast(error.response?.data?.detail || 'Ошибка создания пользователя', 'error')
    }
  }, [newUserData, showToast, loadUsers])

  // Открыть модал редактирования
  const handleEditUser = useCallback(async (user: User) => {
    setSelectedUser(user)
    setEditUserData({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      email: user.email || '',
      password: '',
      is_active: user.is_active
    })
    setShowEditModal(true)
  }, [])

  // Обновить пользователя
  const handleUpdateUser = useCallback(async () => {
    if (!selectedUser) return

    try {
      const response = await usersApi.updateUser(selectedUser.id, editUserData)
      if (response.success) {
        showToast('Данные пользователя обновлены', 'success')
        setShowEditModal(false)
        setSelectedUser(null)
        loadUsers()
      } else {
        showToast(response.message || 'Ошибка обновления данных', 'error')
      }
    } catch (error) {
      console.error('Error updating user:', error)
      showToast('Ошибка обновления данных', 'error')
    }
  }, [selectedUser, editUserData, showToast, loadUsers])

  // Открыть модал смены пароля
  const handleChangePassword = useCallback((user: User) => {
    setSelectedUser(user)
    setNewPassword('')
    setConfirmPassword('')
    setShowPasswordModal(true)
  }, [])

  // Сменить пароль
  const handleSavePassword = useCallback(async () => {
    if (!selectedUser) return

    if (newPassword !== confirmPassword) {
      showToast('Пароли не совпадают', 'error')
      return
    }

    if (newPassword.length < 6) {
      showToast('Пароль должен содержать минимум 6 символов', 'error')
      return
    }

    try {
      const response = await usersApi.changePassword(selectedUser.id, newPassword)
      if (response.success) {
        showToast('Пароль успешно изменен', 'success')
        setShowPasswordModal(false)
        setSelectedUser(null)
        setNewPassword('')
        setConfirmPassword('')
      } else {
        showToast(response.message || 'Ошибка изменения пароля', 'error')
      }
    } catch (error) {
      console.error('Error changing password:', error)
      showToast('Ошибка изменения пароля', 'error')
    }
  }, [selectedUser, newPassword, confirmPassword, showToast])

  // Просмотр пароля
  const handleViewPassword = useCallback(async (user: User) => {
    try {
      const response = await usersApi.viewPassword(user.id)
      if (response.success) {
        setViewPassword(response.password)
        setSelectedUser(user)
        setShowViewPasswordModal(true)
      } else {
        showToast(response.message || 'Не удалось получить пароль', 'error')
      }
    } catch (error) {
      console.error('Error viewing password:', error)
      showToast('Ошибка при получении пароля', 'error')
    }
  }, [showToast])

  // Переключить статус пользователя
  const handleToggleStatus = useCallback(async (user: User) => {
    try {
      const response = await usersApi.toggleUserStatus(user.id, !user.is_active)
      if (response.success) {
        showToast(
          !user.is_active ? 'Пользователь активирован' : 'Пользователь деактивирован',
          'success'
        )
        loadUsers()
      } else {
        showToast(response.message || 'Ошибка изменения статуса', 'error')
      }
    } catch (error) {
      console.error('Error toggling status:', error)
      showToast('Ошибка изменения статуса', 'error')
    }
  }, [showToast, loadUsers])

  // Удалить пользователя
  const handleDeleteUser = useCallback(async (user: User) => {
    if (!confirm(`Вы уверены, что хотите удалить пользователя ${user.username}?`)) {
      return
    }

    try {
      const response = await usersApi.deactivateUser(user.id)
      if (response.success) {
        showToast('Пользователь удален', 'success')
        loadUsers()
      } else {
        showToast(response.message || 'Ошибка удаления пользователя', 'error')
      }
    } catch (error) {
      console.error('Error deleting user:', error)
      showToast('Ошибка удаления пользователя', 'error')
    }
  }, [showToast, loadUsers])

  // Копировать пароль
  const copyPassword = useCallback(() => {
    navigator.clipboard.writeText(viewPassword)
    showToast('Пароль скопирован в буфер обмена', 'success')
  }, [viewPassword, showToast])

  // Получить роль пользователя с иконкой
  const getRoleBadge = useCallback((role: string) => {
    switch (role) {
      case 'owner':
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-full text-sm font-semibold">
            <Crown className="w-4 h-4" />
            Владелец
          </div>
        )
      case 'admin':
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-full text-sm font-semibold">
            <ShieldIcon className="w-4 h-4" />
            Админ
          </div>
        )
      case 'salesperson':
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full text-sm font-semibold">
            <Briefcase className="w-4 h-4" />
            Продажник
          </div>
        )
      case 'timlead':
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-orange-500 to-amber-600 text-white rounded-full text-sm font-semibold">
            <UserIcon className="w-4 h-4" />
            Тимлид
          </div>
        )
      default:
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-pink-500 to-rose-600 text-white rounded-full text-sm font-semibold">
            <UserIcon className="w-4 h-4" />
            Исполнитель
          </div>
        )
    }
  }, [])

  return (
    <div className="bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-500 to-slate-600 text-white p-8 rounded-3xl shadow-2xl mb-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                <UsersIcon className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-4xl font-bold">Управление пользователями</h1>
                <p className="text-gray-100 mt-1">Управление учетными записями сотрудников</p>
              </div>
            </div>

            <button
              onClick={() => setShowAddModal(true)}
              className="px-6 py-3 bg-white text-gray-700 rounded-2xl hover:shadow-xl transition-all duration-300 flex items-center gap-3 font-semibold"
            >
              <UserPlus className="w-5 h-5" />
              Добавить пользователя
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-5 gap-4 mt-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 text-center">
              <div className="text-3xl font-bold">{stats.total}</div>
              <div className="text-sm text-gray-200 mt-1">Всего</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 text-center">
              <div className="text-3xl font-bold">{stats.owners}</div>
              <div className="text-sm text-gray-200 mt-1">Владельцев</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 text-center">
              <div className="text-3xl font-bold">{stats.admins}</div>
              <div className="text-sm text-gray-200 mt-1">Админов</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 text-center">
              <div className="text-3xl font-bold">{stats.executors}</div>
              <div className="text-sm text-gray-200 mt-1">Исполнителей</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 text-center">
              <div className="text-3xl font-bold">{stats.salespeople}</div>
              <div className="text-sm text-gray-200 mt-1">Продажников</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 pb-8">
        {/* Search Bar */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-4 mb-6 border border-gray-200">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по имени или username..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-white border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Users List */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-20">
              <div className="w-12 h-12 border-4 border-gray-200 border-t-gray-500 rounded-full animate-spin mx-auto mb-4"></div>
              <h4 className="text-gray-600 font-semibold">Загрузка пользователей...</h4>
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-center py-20 text-gray-400">
              <UsersIcon className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <h4 className="font-semibold text-gray-600">Пользователей пока нет</h4>
              <p className="text-sm">Добавьте первого пользователя для начала работы</p>
            </div>
          ) : (
            filteredUsers.map(user => (
              <div
                key={user.id}
                className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-all duration-300"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-500 to-slate-600 flex items-center justify-center text-white font-bold shadow-lg">
                      {user.username[0].toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <h5 className="text-lg font-bold text-gray-800">
                          {user.first_name && user.last_name
                            ? `${user.first_name} ${user.last_name}`
                            : user.username}
                        </h5>
                        <div className={`
                          px-2 py-1 rounded-lg text-xs font-semibold
                          ${user.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-red-100 text-red-700'
                          }
                        `}>
                          {user.is_active ? (
                            <span className="flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" />
                              Активен
                            </span>
                          ) : (
                            <span className="flex items-center gap-1">
                              <AlertCircle className="w-3 h-3" />
                              Неактивен
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-sm text-gray-600">@{user.username}</div>
                      {user.email && (
                        <div className="text-sm text-gray-500 mt-1">{user.email}</div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {getRoleBadge(user.role)}
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200">
                  <div>
                    <div className="text-2xl font-bold text-gray-700">{user.tasks_count || 0}</div>
                    <div className="text-xs text-gray-500 uppercase">Всего задач</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-700">{user.active_tasks || 0}</div>
                    <div className="text-xs text-gray-500 uppercase">Активных</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-700">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                    </div>
                    <div className="text-xs text-gray-500 uppercase">Регистрация</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-2 mt-4">
                  <button
                    onClick={() => handleEditUser(user)}
                    className="px-4 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors flex items-center gap-2 text-sm font-semibold"
                  >
                    <Edit className="w-4 h-4" />
                    Редактировать
                  </button>

                  <button
                    onClick={() => handleViewPassword(user)}
                    className="px-4 py-2 bg-cyan-500 text-white rounded-xl hover:bg-cyan-600 transition-colors flex items-center gap-2 text-sm font-semibold"
                  >
                    <Eye className="w-4 h-4" />
                    Показать пароль
                  </button>

                  <button
                    onClick={() => handleChangePassword(user)}
                    className="px-4 py-2 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors flex items-center gap-2 text-sm font-semibold"
                  >
                    <Key className="w-4 h-4" />
                    Сменить пароль
                  </button>

                  {user.role !== 'owner' && (
                    <>
                      <button
                        onClick={() => handleToggleStatus(user)}
                        className={`px-4 py-2 rounded-xl transition-colors flex items-center gap-2 text-sm font-semibold ${
                          user.is_active
                            ? 'bg-amber-500 text-white hover:bg-amber-600'
                            : 'bg-emerald-500 text-white hover:bg-emerald-600'
                        }`}
                      >
                        {user.is_active ? (
                          <>
                            <UserX className="w-4 h-4" />
                            Деактивировать
                          </>
                        ) : (
                          <>
                            <UserCheck className="w-4 h-4" />
                            Активировать
                          </>
                        )}
                      </button>

                      <button
                        onClick={() => handleDeleteUser(user)}
                        className="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors flex items-center gap-2 text-sm font-semibold"
                      >
                        <Trash2 className="w-4 h-4" />
                        Удалить
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Добавить пользователя</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Username *</label>
                <input
                  type="text"
                  value={newUserData.username}
                  onChange={(e) => setNewUserData({ ...newUserData, username: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Пароль *</label>
                <input
                  type="password"
                  value={newUserData.password}
                  onChange={(e) => setNewUserData({ ...newUserData, password: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Имя</label>
                  <input
                    type="text"
                    value={newUserData.first_name}
                    onChange={(e) => setNewUserData({ ...newUserData, first_name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Фамилия</label>
                  <input
                    type="text"
                    value={newUserData.last_name}
                    onChange={(e) => setNewUserData({ ...newUserData, last_name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  value={newUserData.email}
                  onChange={(e) => setNewUserData({ ...newUserData, email: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Роль</label>
                <select
                  value={newUserData.role}
                  onChange={(e) => setNewUserData({ ...newUserData, role: e.target.value as any })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                >
                  <option value="salesperson">Продажник</option>
                  <option value="executor">Исполнитель</option>
                  <option value="admin">Администратор</option>
                  <option value="owner">Владелец</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors font-semibold"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateUser}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-gray-500 to-slate-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 font-semibold"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Редактировать пользователя</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Username</label>
                <input
                  type="text"
                  value={selectedUser.username}
                  disabled
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Имя</label>
                  <input
                    type="text"
                    value={editUserData.first_name}
                    onChange={(e) => setEditUserData({ ...editUserData, first_name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Фамилия</label>
                  <input
                    type="text"
                    value={editUserData.last_name}
                    onChange={(e) => setEditUserData({ ...editUserData, last_name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  value={editUserData.email}
                  onChange={(e) => setEditUserData({ ...editUserData, email: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editUserData.is_active}
                    onChange={(e) => setEditUserData({ ...editUserData, is_active: e.target.checked })}
                    className="w-5 h-5 text-gray-500 rounded focus:ring-gray-500"
                  />
                  <span className="text-sm font-semibold text-gray-700">Активен</span>
                </label>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowEditModal(false)}
                className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors font-semibold"
              >
                Отмена
              </button>
              <button
                onClick={handleUpdateUser}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-gray-500 to-slate-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 font-semibold"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Change Password Modal */}
      {showPasswordModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Смена пароля</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Новый пароль *</label>
                <div className="relative">
                  <input
                    type={passwordVisible ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent pr-12"
                  />
                  <button
                    onClick={() => setPasswordVisible(!passwordVisible)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {passwordVisible ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Подтвердите пароль *</label>
                <input
                  type={passwordVisible ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowPasswordModal(false)}
                className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors font-semibold"
              >
                Отмена
              </button>
              <button
                onClick={handleSavePassword}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 font-semibold"
              >
                Изменить пароль
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Password Modal */}
      {showViewPasswordModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Пароль пользователя</h3>

            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 mb-4">
              <div className="flex items-center gap-2 text-blue-700 mb-2">
                <AlertCircle className="w-5 h-5" />
                <span className="font-semibold">Пользователь: {selectedUser.username}</span>
              </div>
            </div>

            <div className="mb-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={viewPassword}
                  readOnly
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-xl bg-gray-50"
                />
                <button
                  onClick={copyPassword}
                  className="px-4 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors"
                >
                  Копировать
                </button>
              </div>
            </div>

            <div className="text-xs text-gray-500 mb-6">
              <ShieldIcon className="w-4 h-4 inline mr-1" />
              Пароль хранится в зашифрованном виде
            </div>

            <button
              onClick={() => setShowViewPasswordModal(false)}
              className="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors font-semibold"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}

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
