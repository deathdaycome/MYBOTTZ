import { useEffect } from 'react'

export interface KeyboardShortcut {
  key: string
  ctrlKey?: boolean
  shiftKey?: boolean
  altKey?: boolean
  metaKey?: boolean
  action: () => void
  description: string
}

// Object-based shortcuts interface for simpler usage
export interface SimpleShortcuts {
  onNew?: () => void
  onRefresh?: () => void
  onSearch?: () => void
  onHelp?: () => void
  onEscape?: () => void
  onSave?: () => void
  onClose?: () => void
}

export const useKeyboardShortcuts = (shortcuts: KeyboardShortcut[] | SimpleShortcuts, enabled: boolean = true) => {
  useEffect(() => {
    if (!enabled) return

    // Convert SimpleShortcuts object to array format
    let shortcutsArray: KeyboardShortcut[] = []

    if (Array.isArray(shortcuts)) {
      shortcutsArray = shortcuts
    } else {
      // Convert object to array
      const simpleShortcuts = shortcuts as SimpleShortcuts
      if (simpleShortcuts.onNew) {
        shortcutsArray.push({ key: 'n', ctrlKey: true, action: simpleShortcuts.onNew, description: 'New' })
      }
      if (simpleShortcuts.onRefresh) {
        shortcutsArray.push({ key: 'r', action: simpleShortcuts.onRefresh, description: 'Refresh' })
      }
      if (simpleShortcuts.onSearch) {
        shortcutsArray.push({ key: 'f', ctrlKey: true, action: simpleShortcuts.onSearch, description: 'Search' })
        shortcutsArray.push({ key: '/', action: simpleShortcuts.onSearch, description: 'Search' })
      }
      if (simpleShortcuts.onHelp) {
        shortcutsArray.push({ key: '?', action: simpleShortcuts.onHelp, description: 'Help' })
        shortcutsArray.push({ key: 'h', action: simpleShortcuts.onHelp, description: 'Help' })
      }
      if (simpleShortcuts.onEscape) {
        shortcutsArray.push({ key: 'Escape', action: simpleShortcuts.onEscape, description: 'Close' })
      }
      if (simpleShortcuts.onSave) {
        shortcutsArray.push({ key: 's', ctrlKey: true, action: simpleShortcuts.onSave, description: 'Save' })
      }
      if (simpleShortcuts.onClose) {
        shortcutsArray.push({ key: 'Escape', action: simpleShortcuts.onClose, description: 'Close' })
      }
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore shortcuts when user is typing in input fields
      const target = event.target as HTMLElement
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return
      }

      for (const shortcut of shortcutsArray) {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase()
        const ctrlMatch = shortcut.ctrlKey ? event.ctrlKey : !event.ctrlKey
        const shiftMatch = shortcut.shiftKey ? event.shiftKey : !event.shiftKey
        const altMatch = shortcut.altKey ? event.altKey : !event.altKey
        const metaMatch = shortcut.metaKey ? event.metaKey : !event.metaKey

        if (keyMatch && ctrlMatch && shiftMatch && altMatch && metaMatch) {
          event.preventDefault()
          shortcut.action()
          break
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [shortcuts, enabled])
}

// Predefined shortcuts for Projects page
export const projectsShortcuts = {
  // Navigation
  search: { key: '/', description: 'Поиск проектов' },
  refresh: { key: 'r', description: 'Обновить список' },

  // Actions
  newProject: { key: 'n', description: 'Создать проект' },
  export: { key: 'e', ctrlKey: true, description: 'Экспорт проектов' },
  selectAll: { key: 'a', ctrlKey: true, description: 'Выбрать все' },

  // Filters
  clearFilters: { key: 'c', shiftKey: true, description: 'Сбросить фильтры' },

  // View
  toggleGrouping: { key: 'g', description: 'Переключить группировку' },

  // Help
  showHelp: { key: '?', description: 'Показать горячие клавиши' },
}

// Hook for showing keyboard shortcuts help
export const useShortcutsHelp = () => {
  return {
    formatShortcut: (shortcut: KeyboardShortcut) => {
      const keys: string[] = []

      if (shortcut.ctrlKey) keys.push('Ctrl')
      if (shortcut.shiftKey) keys.push('Shift')
      if (shortcut.altKey) keys.push('Alt')
      if (shortcut.metaKey) keys.push('⌘')

      keys.push(shortcut.key.toUpperCase())

      return keys.join(' + ')
    },
  }
}
