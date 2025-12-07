import { useState } from 'react'
import { Settings as SettingsIcon, User, Bell, Shield, Palette, Globe, Check } from 'lucide-react'
import { useTheme, themes } from '../contexts/ThemeContext'
import type { ThemeType } from '../contexts/ThemeContext'

export const Settings = () => {
  const { theme, setTheme } = useTheme()
  const [activeTab, setActiveTab] = useState<'overview' | 'appearance'>('overview')

  const settingsSections = [
    {
      icon: User,
      title: 'Профиль',
      description: 'Управление личной информацией',
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Bell,
      title: 'Уведомления',
      description: 'Настройка оповещений',
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      icon: Shield,
      title: 'Безопасность',
      description: 'Пароль и двухфакторная аутентификация',
      gradient: 'from-green-500 to-emerald-500',
    },
    {
      icon: Palette,
      title: 'Внешний вид',
      description: 'Темы и персонализация',
      gradient: 'from-orange-500 to-red-500',
    },
    {
      icon: Globe,
      title: 'Язык и регион',
      description: 'Локализация и часовой пояс',
      gradient: 'from-indigo-500 to-purple-500',
    },
    {
      icon: SettingsIcon,
      title: 'Дополнительно',
      description: 'Расширенные настройки системы',
      gradient: 'from-gray-500 to-gray-700',
    },
  ]

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Настройки</h1>
        <p className="text-gray-600">Управление настройками системы и профиля</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-6 py-3 font-semibold transition-all ${
            activeTab === 'overview'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Обзор
        </button>
        <button
          onClick={() => setActiveTab('appearance')}
          className={`px-6 py-3 font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'appearance'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Palette className="w-4 h-4" />
          Внешний вид
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <>
          {/* Settings Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {settingsSections.map((section, index) => {
              const Icon = section.icon
              return (
                <button
                  key={index}
                  onClick={() => section.title === 'Внешний вид' && setActiveTab('appearance')}
                  className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 border border-gray-100 text-left"
                >
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${section.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">
                    {section.title}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {section.description}
                  </p>
                </button>
              )
            })}
          </div>
        </>
      )}

      {activeTab === 'appearance' && (
        <div className="space-y-6">
          {/* Theme Selection */}
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Выбор темы оформления</h2>
            <p className="text-gray-600 mb-6">Выберите тему, которая вам больше нравится</p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(themes).map(([key, themeData]) => (
                <button
                  key={key}
                  onClick={() => setTheme(key as ThemeType)}
                  className={`relative bg-white rounded-xl p-6 border-2 transition-all duration-300 hover:shadow-lg ${
                    theme === key
                      ? 'border-blue-600 ring-4 ring-blue-100'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {/* Preview */}
                  <div className="mb-4">
                    <div className="flex gap-2 mb-2">
                      <div
                        className="w-12 h-12 rounded-lg shadow-sm"
                        style={{ background: themeData.primary }}
                      />
                      <div
                        className="w-12 h-12 rounded-lg shadow-sm"
                        style={{ background: themeData.secondary }}
                      />
                      <div
                        className="w-12 h-12 rounded-lg shadow-sm"
                        style={{ background: themeData.accent }}
                      />
                    </div>
                  </div>

                  {/* Title and Description */}
                  <h3 className="text-lg font-bold text-gray-900 mb-1">
                    {themeData.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    {themeData.description}
                  </p>

                  {/* Active Indicator */}
                  {theme === key && (
                    <div className="absolute top-4 right-4 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <Check className="w-5 h-5 text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Additional Info */}
      <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 rounded-3xl p-8 text-white shadow-xl">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Нужна помощь?</h2>
            <p className="text-purple-100 mb-4 max-w-xl">
              Ознакомьтесь с нашей документацией или свяжитесь с поддержкой для получения помощи
            </p>
            <div className="flex gap-3">
              <button className="bg-white text-purple-600 px-6 py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5">
                Документация
              </button>
              <button className="bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/30 transition-all duration-300">
                Связаться с поддержкой
              </button>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="w-32 h-32 bg-white/10 rounded-3xl flex items-center justify-center backdrop-blur-sm">
              <SettingsIcon className="w-16 h-16 text-white/80" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
