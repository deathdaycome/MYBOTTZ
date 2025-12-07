import axiosInstance from '../services/api'

export interface Permission {
  id: number
  name: string
  display_name: string
  module: string
  action: string
  description?: string
}

export interface Role {
  id: number
  name: string
  display_name: string
  description?: string
  permissions: Permission[]
}

export interface DataAccessRule {
  id: number
  user_id: number
  entity_type: string
  access_type: 'none' | 'own' | 'team' | 'all'
  can_view: boolean
  can_edit: boolean
  can_delete: boolean
  can_export: boolean
  priority: number
  is_active: boolean
}

export interface ModulePermission {
  enabled: boolean
  permissions: Record<string, boolean>
  data_access: {
    type: 'none' | 'own' | 'team' | 'all'
    can_view: boolean
    can_edit: boolean
    can_delete: boolean
    can_export: boolean
  }
}

export interface UserPermissionsData {
  user: {
    id: number
    username: string
    email: string
    role: string
    is_active: boolean
  }
  roles: Role[]
  module_permissions: Record<string, ModulePermission>
  available_modules: Record<string, {
    name: string
    permissions: string[]
    description: string
  }>
}

export interface PermissionsStatistics {
  users: {
    total: number
    active: number
    inactive: number
    by_role: Record<string, number>
  }
  modules: Record<string, number>
  permissions: {
    total_permissions: number
    active_rules: number
  }
}

export interface RoleTemplate {
  name: string
  modules: Record<string, ModulePermission>
}

const permissionsApi = {
  // Получить права пользователя
  getUserPermissions: async (userId: number) => {
    const response = await axiosInstance.get(`/admin/permissions/user/${userId}`)
    return response.data as UserPermissionsData
  },

  // Обновить права пользователя
  updateUserPermissions: async (userId: number, modulePermissions: Record<string, ModulePermission>) => {
    const response = await axiosInstance.post(`/admin/permissions/user/${userId}/update`, {
      module_permissions: modulePermissions
    })
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Получить шаблон роли
  getRoleTemplate: async (roleName: string) => {
    const response = await axiosInstance.get(`/admin/permissions/role/${roleName}/template`)
    return response.data as RoleTemplate
  },

  // Применить шаблон роли к пользователю
  applyRoleTemplate: async (userId: number, roleName: string) => {
    const response = await axiosInstance.post(`/admin/permissions/user/${userId}/apply-role-template`, null, {
      params: { role_name: roleName }
    })
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Получить статистику по правам
  getStatistics: async () => {
    const response = await axiosInstance.get('/admin/permissions/statistics')
    return response.data as PermissionsStatistics
  },

  // Сбросить все права пользователя
  resetUserPermissions: async (userId: number) => {
    const response = await axiosInstance.post(`/admin/permissions/user/${userId}/reset`)
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Получить всех пользователей для управления правами
  getUsers: async () => {
    const response = await axiosInstance.get('/admin/api/users/api')
    return response.data as {
      success: boolean
      users: Array<{
        id: number
        name: string
        username: string
        email: string
        role: string
        is_active?: boolean
      }>
    }
  }
}

export default permissionsApi
