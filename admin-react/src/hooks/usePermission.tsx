import { useState, useEffect, useCallback } from 'react'
import { checkUIPermission } from '../api/uiPermissions'

interface UsePermissionResult {
  hasAccess: boolean
  loading: boolean
  reason?: 'owner_full_access' | 'explicit_permission' | 'default_allow'
}

/**
 * React hook для проверки прав доступа к UI элементу
 *
 * @param module - Модуль (например, "projects", "tasks")
 * @param elementId - ID элемента (например, "field.title", "button.edit")
 * @param userId - ID пользователя (опционально, по умолчанию текущий)
 *
 * @example
 * ```tsx
 * const { hasAccess, loading } = usePermission('projects', 'button.delete')
 *
 * if (!hasAccess) return null
 *
 * return <button>Удалить</button>
 * ```
 */
export const usePermission = (
  module: string,
  elementId: string,
  userId?: number
): UsePermissionResult => {
  const [hasAccess, setHasAccess] = useState(true) // По умолчанию разрешено
  const [loading, setLoading] = useState(false)
  const [reason, setReason] = useState<UsePermissionResult['reason']>()

  useEffect(() => {
    let isMounted = true

    const checkPermission = async () => {
      setLoading(true)
      try {
        const result = await checkUIPermission(module, elementId, userId)
        if (isMounted) {
          setHasAccess(result.has_access)
          setReason(result.reason)
        }
      } catch (error) {
        console.error('Ошибка проверки прав:', error)
        // В случае ошибки разрешаем доступ (fail-open)
        if (isMounted) {
          setHasAccess(true)
          setReason('default_allow')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    checkPermission()

    return () => {
      isMounted = false
    }
  }, [module, elementId, userId])

  return { hasAccess, loading, reason }
}

/**
 * Множественная проверка прав для нескольких элементов
 *
 * @example
 * ```tsx
 * const permissions = useMultiplePermissions('projects', [
 *   'field.title',
 *   'field.description',
 *   'button.edit'
 * ])
 *
 * if (!permissions['button.edit'].hasAccess) {
 *   return null
 * }
 * ```
 */
export const useMultiplePermissions = (
  module: string,
  elementIds: string[],
  userId?: number
): Record<string, UsePermissionResult> => {
  const [permissions, setPermissions] = useState<Record<string, UsePermissionResult>>({})

  useEffect(() => {
    let isMounted = true

    const checkPermissions = async () => {
      const results: Record<string, UsePermissionResult> = {}

      // Проверяем все элементы параллельно
      const promises = elementIds.map(async elementId => {
        try {
          const result = await checkUIPermission(module, elementId, userId)
          return {
            elementId,
            hasAccess: result.has_access,
            loading: false,
            reason: result.reason
          }
        } catch (error) {
          console.error(`Ошибка проверки прав для ${elementId}:`, error)
          return {
            elementId,
            hasAccess: true,
            loading: false,
            reason: 'default_allow' as const
          }
        }
      })

      const resolvedResults = await Promise.all(promises)

      resolvedResults.forEach(result => {
        results[result.elementId] = {
          hasAccess: result.hasAccess,
          loading: result.loading,
          reason: result.reason
        }
      })

      if (isMounted) {
        setPermissions(results)
      }
    }

    // Инициализируем loading состояние
    const initialState: Record<string, UsePermissionResult> = {}
    elementIds.forEach(id => {
      initialState[id] = { hasAccess: true, loading: true }
    })
    setPermissions(initialState)

    checkPermissions()

    return () => {
      isMounted = false
    }
  }, [module, JSON.stringify(elementIds), userId])

  return permissions
}

/**
 * HOC компонент для условного рендеринга на основе прав доступа
 *
 * @example
 * ```tsx
 * <ProtectedElement module="projects" elementId="button.delete">
 *   <button>Удалить</button>
 * </ProtectedElement>
 * ```
 */
interface ProtectedElementProps {
  module: string
  elementId: string
  userId?: number
  children: React.ReactNode
  fallback?: React.ReactNode
  showLoading?: boolean
}

export const ProtectedElement = ({
  module,
  elementId,
  userId,
  children,
  fallback = null,
  showLoading = false
}: ProtectedElementProps) => {
  const { hasAccess, loading } = usePermission(module, elementId, userId)

  if (loading && showLoading) {
    return <div className="animate-pulse bg-gray-200 rounded h-8 w-24"></div>
  }

  if (loading && !showLoading) {
    return <>{children}</>
  }

  if (!hasAccess) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

/**
 * Хук для условного отображения полей в формах
 * Возвращает функцию-фильтр для массива полей
 *
 * @example
 * ```tsx
 * const filterFields = useFieldsFilter('projects')
 * const visibleFields = fields.filter(filterFields)
 * ```
 */
export const useFieldsFilter = (module: string, userId?: number) => {
  const [fieldPermissions, setFieldPermissions] = useState<Record<string, boolean>>({})

  const addField = useCallback(async (fieldId: string) => {
    try {
      const result = await checkUIPermission(module, `field.${fieldId}`, userId)
      setFieldPermissions(prev => ({
        ...prev,
        [fieldId]: result.has_access
      }))
    } catch (error) {
      setFieldPermissions(prev => ({
        ...prev,
        [fieldId]: true
      }))
    }
  }, [module, userId])

  const hasFieldAccess = useCallback((fieldId: string): boolean => {
    return fieldPermissions[fieldId] ?? true
  }, [fieldPermissions])

  return { addField, hasFieldAccess, fieldPermissions }
}
