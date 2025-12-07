import axiosInstance from '../services/api'
import type {
  UIStructure,
  GetUIStructureResponse,
  GetUserUIPermissionsResponse,
  UpdateUIPermissionsRequest,
  UpdateUIPermissionsResponse,
  UIPermissionCheckResponse,
  UIPermissionsStatistics,
  GetModuleElementsResponse,
  UserUIPermissions
} from '../types/uiPermissions'

const BASE_URL = '/api/ui-permissions'

/**
 * Получить структуру всех UI элементов системы
 */
export const getUIStructure = async (): Promise<UIStructure> => {
  const response = await axiosInstance.get<GetUIStructureResponse>(`${BASE_URL}/structure`)
  return response.data.structure
}

/**
 * Получить UI права конкретного пользователя
 */
export const getUserUIPermissions = async (userId: number): Promise<GetUserUIPermissionsResponse> => {
  const response = await axiosInstance.get<GetUserUIPermissionsResponse>(`${BASE_URL}/user/${userId}`)
  return response.data
}

/**
 * Обновить UI права пользователя
 */
export const updateUserUIPermissions = async (
  userId: number,
  permissions: UpdateUIPermissionsRequest['permissions']
): Promise<UpdateUIPermissionsResponse> => {
  const response = await axiosInstance.post<UpdateUIPermissionsResponse>(
    `${BASE_URL}/user/${userId}/update`,
    { permissions }
  )
  return response.data
}

/**
 * Сбросить все UI права пользователя (дать полный доступ)
 */
export const resetUserUIPermissions = async (userId: number): Promise<{ success: boolean; message: string; deleted: number }> => {
  const response = await axiosInstance.post(`${BASE_URL}/user/${userId}/reset`)
  return response.data
}

/**
 * Включить все UI элементы для пользователя
 */
export const enableAllUIPermissions = async (userId: number): Promise<UpdateUIPermissionsResponse> => {
  const response = await axiosInstance.post<UpdateUIPermissionsResponse>(`${BASE_URL}/user/${userId}/enable-all`)
  return response.data
}

/**
 * Скопировать UI права от другого пользователя
 */
export const copyUIPermissions = async (
  targetUserId: number,
  sourceUserId: number
): Promise<{ success: boolean; message: string; copied: number; source_user: string }> => {
  const response = await axiosInstance.post(
    `${BASE_URL}/user/${targetUserId}/copy-from/${sourceUserId}`
  )
  return response.data
}

/**
 * Получить список всех элементов конкретного модуля
 */
export const getModuleElements = async (moduleName: string): Promise<GetModuleElementsResponse> => {
  const response = await axiosInstance.get<GetModuleElementsResponse>(`${BASE_URL}/module/${moduleName}/elements`)
  return response.data
}

/**
 * Проверить доступ к конкретному UI элементу для пользователя
 */
export const checkUIPermission = async (
  module: string,
  elementId: string,
  userId?: number
): Promise<UIPermissionCheckResponse> => {
  const params = userId ? { module, element_id: elementId, user_id: userId } : { module, element_id: elementId }
  const response = await axiosInstance.get<UIPermissionCheckResponse>(`${BASE_URL}/check`, { params })
  return response.data
}

/**
 * Получить статистику по UI правам
 */
export const getUIPermissionsStatistics = async (): Promise<UIPermissionsStatistics> => {
  const response = await axiosInstance.get<{ success: boolean; statistics: UIPermissionsStatistics }>(
    `${BASE_URL}/statistics`
  )
  return response.data.statistics
}

/**
 * Утилита для группировки разрешений по модулям и типам элементов
 */
export const groupPermissionsByModuleAndType = (
  structure: UIStructure,
  userPermissions: UserUIPermissions
) => {
  const groups: Array<{
    module: string
    moduleName: string
    elementsByType: {
      field: Array<{ id: string; name: string; enabled: boolean }>
      button: Array<{ id: string; name: string; enabled: boolean }>
      section: Array<{ id: string; name: string; enabled: boolean }>
      column: Array<{ id: string; name: string; enabled: boolean }>
      tab: Array<{ id: string; name: string; enabled: boolean }>
      action: Array<{ id: string; name: string; enabled: boolean }>
    }
  }> = []

  Object.entries(structure).forEach(([moduleKey, moduleData]) => {
    const elementsByType: {
      field: Array<{ id: string; name: string; enabled: boolean }>
      button: Array<{ id: string; name: string; enabled: boolean }>
      section: Array<{ id: string; name: string; enabled: boolean }>
      column: Array<{ id: string; name: string; enabled: boolean }>
      tab: Array<{ id: string; name: string; enabled: boolean }>
      action: Array<{ id: string; name: string; enabled: boolean }>
    } = {
      field: [],
      button: [],
      section: [],
      column: [],
      tab: [],
      action: []
    }

    Object.entries(moduleData.elements).forEach(([elementId, elementInfo]) => {
      const fullId = `${moduleKey}.${elementId}`
      const permission = userPermissions[fullId]
      const enabled = permission ? permission.is_enabled : true // По умолчанию доступно

      const element = {
        id: elementId,
        name: elementInfo.name,
        enabled
      }

      if (elementInfo.type in elementsByType) {
        elementsByType[elementInfo.type].push(element)
      }
    })

    groups.push({
      module: moduleKey,
      moduleName: moduleData.name,
      elementsByType
    })
  })

  return groups
}

/**
 * Утилита для создания полного словаря разрешений из сгруппированных данных
 */
export const flattenGroupedPermissions = (
  groups: ReturnType<typeof groupPermissionsByModuleAndType>
): Record<string, boolean> => {
  const flat: Record<string, boolean> = {}

  groups.forEach(group => {
    Object.entries(group.elementsByType).forEach(([_type, elements]) => {
      elements.forEach(element => {
        const fullId = `${group.module}.${element.id}`
        flat[fullId] = element.enabled
      })
    })
  })

  return flat
}
