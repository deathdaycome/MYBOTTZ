import { useState } from 'react'
import { Type } from 'lucide-react'
import { useFont, AVAILABLE_FONTS } from '../../contexts/FontContext'

export const FontSelector = () => {
  const { currentFont, setFont } = useFont()
  const [isOpen, setIsOpen] = useState(false)

  const handleFontChange = (fontValue: string) => {
    setFont(fontValue)
    setIsOpen(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-[#0a0a1a] border border-[#392e4e] rounded-lg hover:border-purple-500 transition-all"
        title="Выбрать шрифт"
      >
        <Type className="w-5 h-5 text-white" />
        <span className="text-sm text-white hidden md:inline">{currentFont}</span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-80 bg-[#0a0a1a] border border-[#392e4e] rounded-xl shadow-2xl z-50 overflow-hidden">
            <div className="p-4 border-b border-[#392e4e]">
              <h3 className="text-white font-semibold flex items-center gap-2">
                <Type className="w-5 h-5" />
                Выбор шрифта
              </h3>
              <p className="text-xs text-gray-400 mt-1">
                Выберите шрифт для всей системы
              </p>
            </div>

            <div className="max-h-96 overflow-y-auto">
              {/* Обычные шрифты */}
              <div className="px-3 py-2 bg-[#392e4e]/30 sticky top-0 z-10">
                <h4 className="text-xs font-semibold text-purple-400 uppercase tracking-wider">
                  Профессиональные шрифты
                </h4>
              </div>
              {AVAILABLE_FONTS.filter(f => f.category === 'normal').map((font) => (
                <button
                  key={font.value}
                  onClick={() => handleFontChange(font.value)}
                  className={`w-full text-left px-4 py-3 hover:bg-[#392e4e]/20 transition-all border-b border-[#392e4e]/50 ${
                    currentFont === font.value ? 'bg-purple-500/10 border-l-4 border-l-purple-500' : ''
                  }`}
                  style={{ fontFamily: `'${font.value}', sans-serif` }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="text-white font-medium mb-1">
                        {font.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {font.description}
                      </div>
                      <div className="text-sm text-gray-300 mt-2">
                        Быстрая коричневая лиса 123
                      </div>
                    </div>
                    {currentFont === font.value && (
                      <div className="flex-shrink-0 w-2 h-2 rounded-full bg-purple-500 mt-1"></div>
                    )}
                  </div>
                </button>
              ))}

              {/* Странные шрифты */}
              <div className="px-3 py-2 bg-[#392e4e]/30 sticky top-0 z-10 mt-2">
                <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wider flex items-center gap-2">
                  <span>🎮</span> Странные шрифты
                </h4>
              </div>
              {AVAILABLE_FONTS.filter(f => f.category === 'strange').map((font) => (
                <button
                  key={font.value}
                  onClick={() => handleFontChange(font.value)}
                  className={`w-full text-left px-4 py-3 hover:bg-red-500/10 transition-all border-b border-[#392e4e]/50 ${
                    currentFont === font.value ? 'bg-red-500/10 border-l-4 border-l-red-500' : ''
                  }`}
                  style={{ fontFamily: `'${font.value}', sans-serif` }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="text-white font-medium mb-1">
                        {font.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {font.description}
                      </div>
                      <div className="text-sm text-gray-300 mt-2">
                        Быстрая коричневая лиса 123
                      </div>
                    </div>
                    {currentFont === font.value && (
                      <div className="flex-shrink-0 w-2 h-2 rounded-full bg-red-500 mt-1"></div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
