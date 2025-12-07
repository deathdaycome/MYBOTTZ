import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import axiosInstance from '../services/api'

/**
 * Типы ролей в системе
 */
export type UserRole = 'OWNER' | 'TEAMLEAD' | 'EXECUTOR' | 'CLIENT'

/**
 * Интерфейс данных пользователя
 */
export interface User {
  id?: number
  username: string
  email?: string
  role: UserRole
  firstName?: string
  lastName?: string
  telegramId?: string
}

/**
 * Данные аутентификации из localStorage
 */
interface AuthData {
  username: string
  password: string
  role: UserRole
  firstName?: string
  lastName?: string
  email?: string
}

/**
 * Интерфейс контекста аутентификации
 */
interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void

  // Утилиты для проверки ролей
  isOwner: () => boolean
  isTeamlead: () => boolean
  isExecutor: () => boolean
  isClient: () => boolean

  // Проверка прав доступа
  hasRole: (roles: UserRole | UserRole[]) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

/**
 * Провайдер контекста аутентификации
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  /**
   * Загрузка пользователя из localStorage при инициализации
   */
  useEffect(() => {
    const loadUser = () => {
      try {
        const authData = localStorage.getItem('auth')
        if (authData) {
          const parsed: AuthData = JSON.parse(authData)
          setUser({
            username: parsed.username,
            role: parsed.role,
            email: parsed.email,
            firstName: parsed.firstName,
            lastName: parsed.lastName,
          })
        }
      } catch (error) {
        console.error('Error loading user from localStorage:', error)
        localStorage.removeItem('auth')
      } finally {
        setIsLoading(false)
      }
    }

    loadUser()
  }, [])

  /**
   * Вход в систему
   */
  const login = async (username: string, password: string): Promise<void> => {
    try {
      // Проверяем учетные данные через API
      const response = await axiosInstance.get('/admin/api/auth/me', {
        auth: { username, password },
      })

      if (response.status === 200) {
        const userData = response.data

        // Формируем данные для сохранения
        const authData: AuthData = {
          username,
          password,
          role: userData.role as UserRole,
          firstName: userData.first_name,
          lastName: userData.last_name,
          email: userData.email,
        }

        // Сохраняем в localStorage
        localStorage.setItem('auth', JSON.stringify(authData))

        // Обновляем состояние
        setUser({
          id: userData.id,
          username,
          role: userData.role,
          email: userData.email,
          firstName: userData.first_name,
          lastName: userData.last_name,
          telegramId: userData.telegram_id,
        })
      }
    } catch (error: any) {
      console.error('Login error:', error)
      throw error
    }
  }

  /**
   * Выход из системы
   */
  const logout = () => {
    localStorage.removeItem('auth')
    setUser(null)

    // Перенаправляем на страницу входа
    const basePath = import.meta.env.MODE === 'production' ? '/admin' : ''
    window.location.href = basePath + '/login'
  }

  /**
   * Проверка роли OWNER
   */
  const isOwner = (): boolean => {
    return user?.role === 'OWNER'
  }

  /**
   * Проверка роли TEAMLEAD
   */
  const isTeamlead = (): boolean => {
    return user?.role === 'TEAMLEAD'
  }

  /**
   * Проверка роли EXECUTOR
   */
  const isExecutor = (): boolean => {
    return user?.role === 'EXECUTOR'
  }

  /**
   * Проверка роли CLIENT
   */
  const isClient = (): boolean => {
    return user?.role === 'CLIENT'
  }

  /**
   * Универсальная проверка наличия роли
   * @param roles - одна роль или массив ролей
   */
  const hasRole = (roles: UserRole | UserRole[]): boolean => {
    if (!user) return false

    if (Array.isArray(roles)) {
      return roles.includes(user.role)
    }

    return user.role === roles
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    isOwner,
    isTeamlead,
    isExecutor,
    isClient,
    hasRole,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Хук для использования контекста аутентификации
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}

export default AuthContext
