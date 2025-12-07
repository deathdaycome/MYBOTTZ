import { useState, useEffect } from 'react'
import { X, Save, Key } from 'lucide-react'
import contractorsApi from '../../api/contractors'
import type { Contractor, UpdateContractorData } from '../../api/contractors'

interface ContractorEditModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  contractor: Contractor
}

export const ContractorEditModal = ({
  isOpen,
  onClose,
  onSuccess,
  contractor,
}: ContractorEditModalProps) => {
  const [loading, setLoading] = useState(false)
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [passwordLoading, setPasswordLoading] = useState(false)

  const [formData, setFormData] = useState<UpdateContractorData>({
    username: contractor.username,
    email: contractor.email,
    first_name: contractor.first_name || '',
    last_name: contractor.last_name || '',
    telegram_id: contractor.telegram_id,
    is_active: contractor.is_active,
  })

  useEffect(() => {
    if (isOpen) {
      // Update form data when contractor changes
      setFormData({
        username: contractor.username,
        email: contractor.email,
        first_name: contractor.first_name || '',
        last_name: contractor.last_name || '',
        telegram_id: contractor.telegram_id,
        is_active: contractor.is_active,
      })
      setShowPasswordForm(false)
      setNewPassword('')
    }
  }, [isOpen, contractor])

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

    if (!formData.username?.trim()) {
      alert('Введите имя пользователя')
      return
    }

    if (!formData.email?.trim()) {
      alert('Введите email')
      return
    }

    try {
      setLoading(true)
      const response = await contractorsApi.updateContractor(contractor.id, formData)

      if (response.success) {
        onSuccess()
      }
    } catch (error) {
      console.error('Error updating contractor:', error)
      alert('Ошибка обновления исполнителя')
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newPassword.trim()) {
      alert('Введите новый пароль')
      return
    }

    if (newPassword.length < 6) {
      alert('Пароль должен содержать не менее 6 символов')
      return
    }

    try {
      setPasswordLoading(true)
      const response = await contractorsApi.changePassword(contractor.id, newPassword)

      if (response.success) {
        alert('Пароль успешно изменен')
        setShowPasswordForm(false)
        setNewPassword('')
      }
    } catch (error) {
      console.error('Error changing password:', error)
      alert('Ошибка изменения пароля')
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleChange = (field: keyof UpdateContractorData, value: any) => {
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
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <Save className="w-6 h-6" />
            <h3 className="text-xl font-bold">Редактировать исполнителя</h3>
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
          {/* Username */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Имя пользователя <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => handleChange('username', e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="Введите имя пользователя"
              required
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="Введите email"
              required
            />
          </div>

          {/* First Name and Last Name */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Имя</label>
              <input
                type="text"
                value={formData.first_name}
                onChange={(e) => handleChange('first_name', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                placeholder="Введите имя"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Фамилия</label>
              <input
                type="text"
                value={formData.last_name}
                onChange={(e) => handleChange('last_name', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                placeholder="Введите фамилию"
              />
            </div>
          </div>

          {/* Telegram ID */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Telegram ID</label>
            <input
              type="number"
              value={formData.telegram_id || ''}
              onChange={(e) => handleChange('telegram_id', e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="Введите Telegram ID"
            />
          </div>

          {/* Is Active */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => handleChange('is_active', e.target.checked)}
              className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <label htmlFor="is_active" className="text-sm font-semibold text-gray-700">
              Активный
            </label>
          </div>

          {/* Password Change Button */}
          <div className="pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setShowPasswordForm(!showPasswordForm)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-all font-semibold"
            >
              <Key className="w-4 h-4" />
              {showPasswordForm ? 'Отменить смену пароля' : 'Изменить пароль'}
            </button>
          </div>

          {/* Password Change Form */}
          {showPasswordForm && (
            <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-4 space-y-3">
              <h4 className="font-semibold text-gray-700">Смена пароля</h4>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Новый пароль <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                  placeholder="Минимум 6 символов"
                  minLength={6}
                />
              </div>
              <button
                type="button"
                onClick={handlePasswordChange}
                disabled={passwordLoading}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {passwordLoading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                ) : (
                  <>
                    <Key className="w-4 h-4" />
                    Сменить пароль
                  </>
                )}
              </button>
            </div>
          )}

          {/* Footer */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Сохранить изменения
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
