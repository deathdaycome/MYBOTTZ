import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type ThemeType = 'colorful' | 'monochrome' | 'dark' | 'blue' | 'green'

export interface ThemeStyles {
  text: string
  card: string
  border: string
  input: string
  primary: string
  hover: string
}

interface ThemeContextType {
  theme: ThemeType
  setTheme: (theme: ThemeType) => void
  currentTheme: ThemeStyles
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

const getThemeStyles = (theme: ThemeType): ThemeStyles => {
  switch (theme) {
    case 'colorful':
      return {
        text: 'text-gray-900',
        card: 'bg-white',
        border: 'border-gray-200',
        input: 'bg-white',
        primary: 'bg-blue-600',
        hover: 'hover:bg-gray-50'
      }
    case 'monochrome':
      return {
        text: 'text-gray-900',
        card: 'bg-white',
        border: 'border-gray-300',
        input: 'bg-gray-50',
        primary: 'bg-gray-700',
        hover: 'hover:bg-gray-100'
      }
    case 'dark':
      return {
        text: 'text-gray-100',
        card: 'bg-gray-800',
        border: 'border-gray-700',
        input: 'bg-gray-700',
        primary: 'bg-gray-600',
        hover: 'hover:bg-gray-700'
      }
    case 'blue':
      return {
        text: 'text-gray-900',
        card: 'bg-white',
        border: 'border-blue-200',
        input: 'bg-blue-50',
        primary: 'bg-blue-600',
        hover: 'hover:bg-blue-50'
      }
    case 'green':
      return {
        text: 'text-gray-900',
        card: 'bg-white',
        border: 'border-green-200',
        input: 'bg-green-50',
        primary: 'bg-green-600',
        hover: 'hover:bg-green-50'
      }
  }
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: ReactNode
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeType>(() => {
    const saved = localStorage.getItem('admin-theme')
    return (saved as ThemeType) || 'colorful'
  })

  const currentTheme = getThemeStyles(theme)

  useEffect(() => {
    // Применяем тему к body
    document.body.className = `theme-${theme}`
    localStorage.setItem('admin-theme', theme)
  }, [theme])

  const setTheme = (newTheme: ThemeType) => {
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme, currentTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const themes = {
  colorful: {
    name: 'Разноцветная',
    description: 'Яркая и современная тема с градиентами',
    primary: '#3b82f6',
    secondary: '#6366f1',
    accent: '#8b5cf6',
  },
  monochrome: {
    name: 'Черно-белая',
    description: 'Классическая монохромная тема',
    primary: '#374151',
    secondary: '#6b7280',
    accent: '#9ca3af',
  },
  dark: {
    name: 'Темная',
    description: 'Темная тема для работы в ночное время',
    primary: '#1f2937',
    secondary: '#374151',
    accent: '#4b5563',
  },
  blue: {
    name: 'Синяя',
    description: 'Профессиональная синяя тема',
    primary: '#0ea5e9',
    secondary: '#0284c7',
    accent: '#0369a1',
  },
  green: {
    name: 'Зеленая',
    description: 'Спокойная зеленая тема',
    primary: '#10b981',
    secondary: '#059669',
    accent: '#047857',
  },
}
