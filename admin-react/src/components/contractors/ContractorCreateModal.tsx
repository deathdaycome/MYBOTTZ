import { useState, useEffect } from 'react'
import { X, Plus } from 'lucide-react'
import contractorsApi from '../../api/contractors'
import type { CreateContractorData } from '../../api/contractors'

interface ContractorCreateModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export const ContractorCreateModal = ({
  isOpen,
  onClose,
  onSuccess,
}: ContractorCreateModalProps) => {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<CreateContractorData>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'executor',
    is_active: true,
    admin_login: '',
    admin_password: '',
    force_password_change: false,
  })

  useEffect(() => {
    if (isOpen) {
      // Reset form on open
      setFormData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        role: 'executor',
        is_active: true,
        admin_login: '',
        admin_password: '',
        force_password_change: false,
      })
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.username.trim()) {
      alert('Введите username')
      return
    }

    if (!formData.email.trim()) {
      alert('Введите email')
      return
    }

    if (!formData.admin_password.trim()) {
      alert('Введите пароль для админки')
      return
    }

    try {
      setLoading(true)
      const response = await contractorsApi.createContractor(formData)

      if (response.success) {
        onSuccess()
      } else {
        alert('Ошибка создания исполнителя: ' + response.message)
      }
    } catch (error) {
      console.error('Error creating contractor:', error)
      alert('Ошибка создания исполнителя')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof CreateContractorData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <Plus className="w-6 h-6" />
            <h3 className="text-xl font-bold">Добавить исполнителя</h3>
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
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Username <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="Введите username"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="Введите email"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Имя</label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => handleChange('first_name', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="Введите имя"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Фамилия</label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => handleChange('last_name', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="Введите фамилию"
              />
            </div>
          </div>

          {/* Divider */}
          <hr className="my-6" />

          {/* Admin Access */}
          <h6 className="text-lg font-semibold text-gray-900 mb-4">Доступ к админке</h6>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Логин для админки
              </label>
              <input
                type="text"
                value={formData.admin_login}
                onChange={(e) => handleChange('admin_login', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="Будет использован username если не указан"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Пароль для админки <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                value={formData.admin_password}
                onChange={(e) => handleChange('admin_password', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="Введите пароль"
                required
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="forcePasswordChange"
              checked={formData.force_password_change}
              onChange={(e) => handleChange('force_password_change', e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="forcePasswordChange" className="text-sm text-gray-700">
              Потребовать смену пароля при первом входе
            </label>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              После создания исполнитель получит доступ к админке с указанными учетными
              данными.
            </p>
          </div>

          {/* Footer */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                <>
                  <Plus className="w-5 h-5" />
                  Создать исполнителя
                </>
              )}
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
        </form>
      </div>
    </div>
  )
}
