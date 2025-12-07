/**
 * Конфигурация меню для разных ролей пользователей
 */

import { UserRole } from '../contexts/AuthContext'

export interface MenuItem {
  path: string
  text: string
  image: string
  roles: UserRole[] // Массив ролей, которые имеют доступ к этому пункту
  readOnly?: boolean // Только для просмотра (для TEAMLEAD)
}

/**
 * Полный список пунктов меню с указанием ролей доступа
 * Согласно ТЗ:
 * - OWNER: полный доступ
 * - TEAMLEAD: Dashboard, Leads, Deals, Projects, Tasks, Chats, Clients, Executors (read-only), Documents (read-only), Transcriptions, AI Calls
 * - EXECUTOR: My Projects, My Tasks, Chats
 * - CLIENT: нет меню (mini-app)
 */
export const menuItems: MenuItem[] = [
  {
    path: '/',
    text: 'Дашборд',
    image: 'https://picsum.photos/600/400?random=1',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/projects',
    text: 'Проекты',
    image: 'https://picsum.photos/600/400?random=2',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/project-files',
    text: 'База проектов',
    image: 'https://picsum.photos/600/400?random=3',
    roles: ['OWNER'],
  },
  {
    path: '/tasks',
    text: 'Задачи',
    image: 'https://picsum.photos/600/400?random=4',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/tasks-archive',
    text: 'Архив задач',
    image: 'https://picsum.photos/600/400?random=5',
    roles: ['OWNER'],
  },
  {
    path: '/my-tasks',
    text: 'Мои задачи',
    image: 'https://picsum.photos/600/400?random=6',
    roles: ['OWNER', 'EXECUTOR'],
  },
  {
    path: '/revisions',
    text: 'Ревизии',
    image: 'https://picsum.photos/600/400?random=7',
    roles: ['OWNER'],
  },
  {
    path: '/clients',
    text: 'Клиенты',
    image: 'https://picsum.photos/600/400?random=8',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/leads',
    text: 'Лиды',
    image: 'https://picsum.photos/600/400?random=9',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/deals',
    text: 'Сделки',
    image: 'https://picsum.photos/600/400?random=10',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/contractors',
    text: 'Исполнители',
    image: 'https://picsum.photos/600/400?random=11',
    roles: ['OWNER', 'TEAMLEAD'],
    readOnly: true, // Для TEAMLEAD только чтение
  },
  {
    path: '/chats',
    text: 'Чаты',
    image: 'https://picsum.photos/600/400?random=12',
    roles: ['OWNER', 'TEAMLEAD', 'EXECUTOR'],
  },
  {
    path: '/avito',
    text: 'Avito',
    image: 'https://picsum.photos/600/400?random=13',
    roles: ['OWNER'],
  },
  {
    path: '/documents',
    text: 'Документы',
    image: 'https://picsum.photos/600/400?random=14',
    roles: ['OWNER', 'TEAMLEAD'],
    readOnly: true, // Для TEAMLEAD только чтение
  },
  {
    path: '/transcription',
    text: 'Транскрибация',
    image: 'https://picsum.photos/600/400?random=27',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/ai-calls',
    text: 'AI Звонки',
    image: 'https://picsum.photos/600/400?random=29',
    roles: ['OWNER', 'TEAMLEAD'],
  },
  {
    path: '/portfolio',
    text: 'Портфолио',
    image: 'https://picsum.photos/600/400?random=15',
    roles: ['OWNER'],
  },
  {
    path: '/finance',
    text: 'Финансы',
    image: 'https://picsum.photos/600/400?random=16',
    roles: ['OWNER'],
  },
  {
    path: '/services',
    text: 'Услуги',
    image: 'https://picsum.photos/600/400?random=17',
    roles: ['OWNER'],
  },
  {
    path: '/analytics',
    text: 'Аналитика',
    image: 'https://picsum.photos/600/400?random=18',
    roles: ['OWNER'],
  },
  {
    path: '/reports',
    text: 'Отчеты',
    image: 'https://picsum.photos/600/400?random=19',
    roles: ['OWNER'],
  },
  {
    path: '/notifications',
    text: 'Уведомления',
    image: 'https://picsum.photos/600/400?random=20',
    roles: ['OWNER'],
  },
  {
    path: '/automation',
    text: 'Автоматизация',
    image: 'https://picsum.photos/600/400?random=21',
    roles: ['OWNER'],
  },
  {
    path: '/hosting',
    text: 'Хостинг',
    image: 'https://picsum.photos/600/400?random=23',
    roles: ['OWNER'],
  },
  {
    path: '/permissions',
    text: 'Права доступа',
    image: 'https://picsum.photos/600/400?random=24',
    roles: ['OWNER'],
  },
  {
    path: '/timlead-regulations',
    text: 'Регламенты',
    image: 'https://picsum.photos/600/400?random=28',
    roles: ['OWNER'],
  },
  {
    path: '/users',
    text: 'Пользователи',
    image: 'https://picsum.photos/600/400?random=25',
    roles: ['OWNER'],
  },
  {
    path: '/settings',
    text: 'Настройки',
    image: 'https://picsum.photos/600/400?random=26',
    roles: ['OWNER', 'TEAMLEAD', 'EXECUTOR'],
  },
]

/**
 * Получить пункты меню для конкретной роли
 */
export const getMenuItemsForRole = (role: UserRole | undefined): MenuItem[] => {
  if (!role) return []

  // CLIENT не имеет доступа к меню
  if (role === 'CLIENT') return []

  // Фильтруем пункты меню по роли
  return menuItems.filter((item) => item.roles.includes(role))
}

/**
 * Проверить, имеет ли роль доступ к определенному пути
 */
export const hasAccessToPath = (role: UserRole | undefined, path: string): boolean => {
  if (!role) return false

  const menuItem = menuItems.find((item) => item.path === path)
  if (!menuItem) return false

  return menuItem.roles.includes(role)
}

/**
 * Проверить, доступен ли путь только для чтения
 */
export const isReadOnlyPath = (role: UserRole | undefined, path: string): boolean => {
  if (!role) return false

  const menuItem = menuItems.find((item) => item.path === path)
  if (!menuItem) return false

  return menuItem.readOnly === true && role === 'TEAMLEAD'
}
