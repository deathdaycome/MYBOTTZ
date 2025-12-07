import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

// Updated: 2025-11-19 09:30
export const AVAILABLE_FONTS = [
  // Обычные профессиональные шрифты с кириллицей
  { name: 'Inter', value: 'Inter', description: 'Современный и универсальный', category: 'normal' },
  { name: 'Roboto', value: 'Roboto', description: 'Классика для бизнеса', category: 'normal' },
  { name: 'Open Sans', value: 'Open Sans', description: 'Чистый и профессиональный', category: 'normal' },
  { name: 'Poppins', value: 'Poppins', description: 'Стильный геометричный', category: 'normal' },
  { name: 'Montserrat', value: 'Montserrat', description: 'Современный гротеск', category: 'normal' },
  { name: 'Nunito', value: 'Nunito', description: 'Дружелюбный интерфейсный', category: 'normal' },
  { name: 'IBM Plex Sans', value: 'IBM Plex Sans', description: 'Корпоративный стиль', category: 'normal' },
  { name: 'Manrope', value: 'Manrope', description: 'Геометричный модерн', category: 'normal' },
  { name: 'Space Grotesk', value: 'Space Grotesk', description: 'Технологичный стиль', category: 'normal' },
  { name: 'Red Hat Display', value: 'Red Hat Display', description: 'Корпоративный Tech', category: 'normal' },
  { name: 'Archivo', value: 'Archivo', description: 'Универсальный гротеск', category: 'normal' },
  { name: 'Public Sans', value: 'Public Sans', description: 'Нейтральный чистый', category: 'normal' },
  { name: 'Rubik', value: 'Rubik', description: 'Скругленный современный', category: 'normal' },
  { name: 'Quicksand', value: 'Quicksand', description: 'Дружелюбный скругленный', category: 'normal' },
  { name: 'Raleway', value: 'Raleway', description: 'Элегантный тонкий', category: 'normal' },
  { name: 'Source Sans 3', value: 'Source Sans 3', description: 'От Adobe Systems', category: 'normal' },
  { name: 'Jost', value: 'Jost', description: 'Геометричный Futura-style', category: 'normal' },
  { name: 'Karla', value: 'Karla', description: 'Гротескный универсальный', category: 'normal' },
  { name: 'PT Sans', value: 'PT Sans', description: 'Российский универсальный', category: 'normal' },
  { name: 'Fira Sans', value: 'Fira Sans', description: 'Современный гуманистичный', category: 'normal' },
  { name: 'Ubuntu', value: 'Ubuntu', description: 'Дружелюбный Ubuntu', category: 'normal' },
  { name: 'Exo 2', value: 'Exo 2', description: 'Технологичный футуристичный', category: 'normal' },

  // Странные шрифты с кириллицей
  { name: 'Press Start 2P', value: 'Press Start 2P', description: '8-бит ретро игры', category: 'strange' },
  { name: 'Comfortaa', value: 'Comfortaa', description: 'Скругленный футуристичный', category: 'strange' },
  { name: 'Philosopher', value: 'Philosopher', description: 'Философский элегантный', category: 'strange' },
  { name: 'Play', value: 'Play', description: 'Технологичный геометричный', category: 'strange' },
  { name: 'Podkova', value: 'Podkova', description: 'Слэб с характером', category: 'strange' },
  { name: 'Cuprum', value: 'Cuprum', description: 'Узкий индустриальный', category: 'strange' },
  { name: 'Bad Script', value: 'Bad Script', description: 'Небрежный рукописный', category: 'strange' },
  { name: 'Lobster', value: 'Lobster', description: 'Ретро скриптовый', category: 'strange' },
  { name: 'Pacifico', value: 'Pacifico', description: 'Пляжный серфинг', category: 'strange' },
  { name: 'Stalinist One', value: 'Stalinist One', description: 'Индустриальный мощный', category: 'strange' },
  { name: 'Underdog', value: 'Underdog', description: 'Жирный странный', category: 'strange' },
  { name: 'Yeseva One', value: 'Yeseva One', description: 'Элегантный декоративный', category: 'strange' },
  { name: 'Marck Script', value: 'Marck Script', description: 'Рукописный элегантный', category: 'strange' },
  { name: 'Kelly Slab', value: 'Kelly Slab', description: 'Странный слэб', category: 'strange' },
  { name: 'Ruslan Display', value: 'Ruslan Display', description: 'Русский декоративный', category: 'strange' },
]

interface FontContextType {
  currentFont: string
  setFont: (font: string) => void
}

const FontContext = createContext<FontContextType | undefined>(undefined)

export const FontProvider = ({ children }: { children: ReactNode }) => {
  const [currentFont, setCurrentFont] = useState<string>(() => {
    return localStorage.getItem('selectedFont') || 'IBM Plex Sans'
  })

  useEffect(() => {
    // Применяем шрифт к body
    document.body.style.fontFamily = `'${currentFont}', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif`
    // Сохраняем в localStorage
    localStorage.setItem('selectedFont', currentFont)
  }, [currentFont])

  const setFont = (font: string) => {
    setCurrentFont(font)
  }

  return (
    <FontContext.Provider value={{ currentFont, setFont }}>
      {children}
    </FontContext.Provider>
  )
}

export const useFont = () => {
  const context = useContext(FontContext)
  if (!context) {
    throw new Error('useFont must be used within FontProvider')
  }
  return context
}
