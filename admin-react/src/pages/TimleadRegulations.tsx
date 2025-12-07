import { useState, useEffect } from 'react'
import {
  ClipboardCheck,
  Book,
  CheckSquare,
  Users,
  CalendarCheck,
  TrendingUp,
  FileText,
  Settings,
  Shield,
  Clock,
  Eye,
  Edit,
  X,
  Save,
} from 'lucide-react'
import axiosInstance from '../services/api'

interface Regulation {
  id: number
  regulation_number: number
  title: string
  content: string
  icon: string
  allowed_roles: string[]
  created_at: string
  updated_at: string
}

const iconMap: Record<string, React.ReactNode> = {
  Book: <Book className="w-6 h-6" />,
  CheckSquare: <CheckSquare className="w-6 h-6" />,
  Users: <Users className="w-6 h-6" />,
  CalendarCheck: <CalendarCheck className="w-6 h-6" />,
  TrendingUp: <TrendingUp className="w-6 h-6" />,
  FileText: <FileText className="w-6 h-6" />,
  Settings: <Settings className="w-6 h-6" />,
  Shield: <Shield className="w-6 h-6" />,
}

export const TimleadRegulations = () => {
  const [regulations, setRegulations] = useState<Regulation[]>([])
  const [loading, setLoading] = useState(true)
  const [editingRegulation, setEditingRegulation] = useState<Regulation | null>(null)
  const [editForm, setEditForm] = useState({ title: '', content: '', icon: '', allowed_roles: [] as string[] })
  const [saving, setSaving] = useState(false)
  const [userRole, setUserRole] = useState<string>('')

  useEffect(() => {
    loadRegulations()
    loadUserRole()
  }, [])

  const loadUserRole = async () => {
    const auth = localStorage.getItem('auth')
    if (auth) {
      try {
        const authData = JSON.parse(auth)

        // Если роль уже есть в localStorage, используем её
        if (authData.role) {
          setUserRole(authData.role)
          return
        }

        // Если роли нет, получаем её с сервера
        console.log('Role not in localStorage, fetching from server...')
        const response = await axiosInstance.get('/admin/api/auth/me')
        const userRole = response.data.role

        // Сохраняем роль в localStorage для будущих запросов
        authData.role = userRole
        localStorage.setItem('auth', JSON.stringify(authData))
        setUserRole(userRole)

        console.log('User role fetched and saved:', userRole)
      } catch (e) {
        console.error('Error loading user role:', e)
      }
    }
  }

  const loadRegulations = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get('/admin/api/timlead-regulations/')
      setRegulations(response.data)
    } catch (error) {
      console.error('Error loading regulations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (regulation: Regulation) => {
    setEditingRegulation(regulation)
    setEditForm({
      title: regulation.title,
      content: regulation.content,
      icon: regulation.icon,
      allowed_roles: regulation.allowed_roles || [],
    })
  }

  const handleSave = async () => {
    if (!editingRegulation) return

    try {
      setSaving(true)
      await axiosInstance.put(`/admin/api/timlead-regulations/${editingRegulation.id}`, editForm)
      await loadRegulations()
      setEditingRegulation(null)
    } catch (error: any) {
      console.error('Error saving regulation:', error)
      alert(error.response?.data?.detail || 'Ошибка при сохранении')
    } finally {
      setSaving(false)
    }
  }

  const isOwner = userRole === 'owner'

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-gray-600 dark:text-gray-400">Загрузка...</div>
      </div>
    )
  }


  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <ClipboardCheck className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            ТИМЛИД — РЕГЛАМЕНТЫ
          </h1>
        </div>

        {/* Info Block */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="bg-blue-500 rounded-full p-1 mt-0.5">
              <svg
                className="w-4 h-4 text-white"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-blue-900 dark:text-blue-100">
                Раздел для тимлида:
              </p>
              <p className="text-blue-800 dark:text-blue-200 mt-1">
                Здесь размещены основные регламенты и руководства по работе команды.
                {isOwner && ' Вы можете редактировать содержимое регламентов.'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Regulations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {regulations.map((regulation) => (
          <div
            key={regulation.id}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
          >
            {/* Icon & Title */}
            <div className="flex items-center gap-4 mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center text-white flex-shrink-0">
                {iconMap[regulation.icon] || <FileText className="w-6 h-6" />}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                {regulation.title}
              </h3>
            </div>

            {/* Status Badge */}
            <div className="mb-4">
              <span className={`inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md ${
                regulation.content.includes('будет добавлено')
                  ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
                  : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
              }`}>
                <Clock className="w-4 h-4" />
                {regulation.content.includes('будет добавлено') ? 'В разработке' : 'Активен'}
              </span>
            </div>

            {/* Description */}
            <div className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed mb-6 min-h-[60px]">
              {regulation.content.length > 150
                ? `${regulation.content.substring(0, 150)}...`
                : regulation.content}
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => handleEdit(regulation)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                <Eye className="w-4 h-4" />
                Просмотр
              </button>
              {isOwner && (
                <button
                  onClick={() => handleEdit(regulation)}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors"
                >
                  <Edit className="w-4 h-4" />
                  Редактировать
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Edit Modal */}
      {editingRegulation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {isOwner ? 'Редактирование регламента' : 'Просмотр регламента'}
              </h2>
              <button
                onClick={() => setEditingRegulation(null)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Название регламента
                </label>
                <input
                  type="text"
                  value={editForm.title}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  disabled={!isOwner}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-100 dark:disabled:bg-gray-600 disabled:cursor-not-allowed"
                />
              </div>

              {/* Content */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Содержимое
                </label>
                <textarea
                  value={editForm.content}
                  onChange={(e) => setEditForm({ ...editForm, content: e.target.value })}
                  disabled={!isOwner}
                  rows={15}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-100 dark:disabled:bg-gray-600 disabled:cursor-not-allowed font-mono text-sm"
                  placeholder="Введите содержимое регламента..."
                />
              </div>

              {/* Icon Selection */}
              {isOwner && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Иконка
                  </label>
                  <select
                    value={editForm.icon}
                    onChange={(e) => setEditForm({ ...editForm, icon: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {Object.keys(iconMap).map((iconName) => (
                      <option key={iconName} value={iconName}>
                        {iconName}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Roles Selection */}
              {isOwner && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Доступно для ролей
                  </label>
                  <div className="space-y-2">
                    {[
                      { value: 'owner', label: 'Владелец' },
                      { value: 'admin', label: 'Администратор' },
                      { value: 'timlead', label: 'Тимлид' },
                      { value: 'executor', label: 'Исполнитель' },
                      { value: 'salesperson', label: 'Продажник' },
                      { value: 'developer', label: 'Разработчик' },
                    ].map((role) => (
                      <label
                        key={role.value}
                        className="flex items-center gap-3 p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={editForm.allowed_roles.includes(role.value)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setEditForm({
                                ...editForm,
                                allowed_roles: [...editForm.allowed_roles, role.value],
                              })
                            } else {
                              setEditForm({
                                ...editForm,
                                allowed_roles: editForm.allowed_roles.filter((r) => r !== role.value),
                              })
                            }
                          }}
                          className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
                        />
                        <span className="text-gray-900 dark:text-white font-medium">{role.label}</span>
                      </label>
                    ))}
                  </div>
                  <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    Выберите роли, которые смогут видеть этот регламент
                  </p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            {isOwner && (
              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setEditingRegulation(null)}
                  disabled={saving}
                  className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg font-medium transition-colors disabled:opacity-50"
                >
                  Отмена
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {saving ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Сохранение...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Сохранить
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TimleadRegulations
