/**
 * TypeScript types for UI Element Permissions System
 */

export type UIElementType = 'field' | 'button' | 'section' | 'tab' | 'column' | 'action'

export interface UIElement {
  type: UIElementType
  name: string
}

export interface UIModuleElements {
  [elementId: string]: UIElement
}

export interface UIModule {
  name: string
  elements: UIModuleElements
}

export interface UIStructure {
  [moduleKey: string]: UIModule
}

export interface UIPermission {
  is_enabled: boolean
  element_type: UIElementType
  description?: string
}

export interface UserUIPermissions {
  [fullElementId: string]: UIPermission  // e.g., "projects.field.title"
}

export interface UIPermissionRecord {
  id: number
  admin_user_id: number
  module: string
  element_type: UIElementType
  element_id: string
  is_enabled: boolean
  description?: string
  created_at: string
  updated_at: string
}

export interface GetUserUIPermissionsResponse {
  success: boolean
  user_id: number
  username: string
  role: string
  permissions: UserUIPermissions
}

export interface GetUIStructureResponse {
  success: boolean
  structure: UIStructure
}

export interface UpdateUIPermissionsRequest {
  permissions: {
    [fullElementId: string]: boolean  // e.g., {"projects.field.title": true}
  }
}

export interface UpdateUIPermissionsResponse {
  success: boolean
  message: string
  updated: number
  created: number
}

export interface UIPermissionCheckResponse {
  success: boolean
  has_access: boolean
  reason: 'owner_full_access' | 'explicit_permission' | 'default_allow'
  permission?: UIPermissionRecord
}

export interface UIPermissionsStatistics {
  total_users: number
  users_with_custom_permissions: number
  total_permission_records: number
  total_available_elements: number
  modules_count: number
  most_restricted_elements: Array<{
    module: string
    element_id: string
    restriction_count: number
  }>
}

export interface GetModuleElementsResponse {
  success: boolean
  module: string
  name: string
  elements: UIModuleElements
}

// Группировка элементов для UI редактора
export interface UIPermissionGroup {
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
}
