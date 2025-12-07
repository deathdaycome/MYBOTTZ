import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export const PrivateRoute = () => {
  const { isAuthenticated, isLoading } = useAuth()

  // Показываем загрузку пока проверяем авторизацию
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка...</p>
        </div>
      </div>
    )
  }

  // Если не авторизован, перенаправляем на страницу входа
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Рендерим дочерние роуты
  return <Outlet />
}

export default PrivateRoute
