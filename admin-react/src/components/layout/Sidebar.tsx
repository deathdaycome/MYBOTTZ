import { useEffect, useMemo } from 'react'
import { Zap, X, LogOut } from 'lucide-react'
import FlowingMenu from '../common/FlowingMenu'
import { useAuth } from '../../contexts/AuthContext'
import { getMenuItemsForRole } from '../../config/menuConfig'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  const { user, logout } = useAuth()

  // Получаем пункты меню для роли пользователя
  const menuItemsForRole = useMemo(() => {
    return getMenuItemsForRole(user?.role).map((item) => ({
      path: item.path,
      text: item.text,
      image: item.image,
      onClick: onClose,
    }))
  }, [user?.role, onClose])

  // Prevent body scroll when sidebar is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  // Обработчик выхода
  const handleLogout = () => {
    logout()
    onClose()
  }

  // Получаем инициалы пользователя
  const getUserInitials = () => {
    if (user?.firstName && user?.lastName) {
      return `${user.firstName.charAt(0)}${user.lastName.charAt(0)}`.toUpperCase()
    }
    if (user?.username) {
      return user.username.charAt(0).toUpperCase()
    }
    return '?'
  }

  // Получаем отображаемое имя
  const getDisplayName = () => {
    if (user?.firstName && user?.lastName) {
      return `${user.firstName} ${user.lastName}`
    }
    return user?.username || 'Пользователь'
  }

  // Получаем название роли на русском
  const getRoleName = () => {
    switch (user?.role) {
      case 'OWNER':
        return 'Владелец'
      case 'TEAMLEAD':
        return 'Тимлид'
      case 'EXECUTOR':
        return 'Исполнитель'
      case 'CLIENT':
        return 'Клиент'
      default:
        return 'Пользователь'
    }
  }

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 w-80 bg-gradient-to-b from-[#1a1d2e] via-[#1a1d2e] to-[#14161f] h-screen flex flex-col shadow-2xl overflow-hidden z-50 transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Decorative gradient overlay */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-600/10 to-pink-600/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-gradient-to-tr from-blue-600/10 to-cyan-600/10 rounded-full blur-3xl -ml-32 -mb-32"></div>

        {/* Logo Section with Close Button */}
        <div className="relative px-6 py-6 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-4 group cursor-pointer">
            <div className="relative">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center font-bold text-white text-xl shadow-lg group-hover:shadow-purple-500/50 transition-all duration-300 group-hover:scale-110">
                <Zap className="w-6 h-6" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-[#1a1d2e] animate-pulse"></div>
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-bold text-white group-hover:text-purple-300 transition-colors">
                CRM System
              </h1>
              <p className="text-xs text-gray-400 group-hover:text-gray-300 transition-colors">Nikolaev Studio</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-all"
            title="Закрыть меню"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <div className="flex-1 relative overflow-y-auto overflow-x-hidden scrollbar-hide" style={{ height: '600px' }}>
          {menuItemsForRole.length > 0 ? (
            <FlowingMenu items={menuItemsForRole} />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-400 text-sm">Нет доступных разделов</p>
            </div>
          )}
        </div>

        {/* User Section */}
        <div className="relative px-4 py-6 border-t border-white/5">
          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-2xl p-4 backdrop-blur-sm border border-white/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold shadow-lg">
                {getUserInitials()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white truncate">{getDisplayName()}</p>
                <p className="text-xs text-gray-400 truncate">{user?.email || getRoleName()}</p>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs gap-2">
              <div className="flex items-center gap-1 text-green-400">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Онлайн</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 px-2 py-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                title="Выйти"
              >
                <LogOut className="w-3 h-3" />
                <span>Выйти</span>
              </button>
            </div>
          </div>

          {/* Version */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">© 2025 CRM System</p>
            <p className="text-xs text-gray-600 mt-1">v2.0.0</p>
          </div>
        </div>
      </aside>
    </>
  )
}
