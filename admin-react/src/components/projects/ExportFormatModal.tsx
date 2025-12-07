import { useState, useEffect } from 'react'
import { X, Download, FileText, FileSpreadsheet, FileJson, FileCode } from 'lucide-react'
import type { ExportFormat } from '../../utils/exportUtils'

interface ExportFormatModalProps {
  isOpen: boolean
  onClose: () => void
  onExport: (format: ExportFormat, filename: string) => void
  projectCount: number
}

export const ExportFormatModal = ({
  isOpen,
  onClose,
  onExport,
  projectCount,
}: ExportFormatModalProps) => {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('csv')
  const [filename, setFilename] = useState('projects')

  useEffect(() => {
    if (isOpen) {
      const date = new Date().toISOString().split('T')[0]
      setFilename(`projects_${date}`)
      setSelectedFormat('csv')
    }
  }, [isOpen])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  const handleExport = () => {
    onExport(selectedFormat, filename)
    onClose()
  }

  if (!isOpen) return null

  const formats: Array<{
    value: ExportFormat
    icon: React.ReactNode
    name: string
    description: string
    extension: string
  }> = [
    {
      value: 'csv',
      icon: <FileSpreadsheet className="w-6 h-6" />,
      name: 'CSV',
      description: 'Таблица для Excel/Google Sheets',
      extension: '.csv',
    },
    {
      value: 'excel',
      icon: <FileSpreadsheet className="w-6 h-6" />,
      name: 'Excel',
      description: 'Файл Microsoft Excel',
      extension: '.xlsx',
    },
    {
      value: 'json',
      icon: <FileCode className="w-6 h-6" />,
      name: 'JSON',
      description: 'Для API и разработки',
      extension: '.json',
    },
    {
      value: 'pdf',
      icon: <FileText className="w-6 h-6" />,
      name: 'PDF/TXT',
      description: 'Текстовый отчет',
      extension: '.txt',
    },
  ]

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Download className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Экспорт проектов</h3>
              <p className="text-blue-100 text-sm mt-1">
                Будет экспортировано проектов: {projectCount}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Format Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Выберите формат экспорта
            </label>
            <div className="grid grid-cols-2 gap-3">
              {formats.map((format) => (
                <button
                  key={format.value}
                  type="button"
                  onClick={() => setSelectedFormat(format.value)}
                  className={`flex items-start gap-3 p-4 rounded-xl border-2 transition-all ${
                    selectedFormat === format.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                >
                  <div
                    className={`flex-shrink-0 ${
                      selectedFormat === format.value ? 'text-blue-600' : 'text-gray-400'
                    }`}
                  >
                    {format.icon}
                  </div>
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-gray-900">{format.name}</span>
                      <span className="text-xs text-gray-500 font-mono">{format.extension}</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{format.description}</p>
                  </div>
                  {selectedFormat === format.value && (
                    <div className="flex-shrink-0">
                      <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Filename */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Название файла
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="Введите название файла"
              />
              <span className="text-sm text-gray-500 font-mono">
                {formats.find((f) => f.value === selectedFormat)?.extension}
              </span>
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <span className="font-semibold">ℹ️ Информация:</span> Экспорт включает все данные
              проектов: название, статус, финансы, исполнителей, клиентов и даты.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
          <button
            type="button"
            onClick={handleExport}
            disabled={!filename.trim()}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-5 h-5" />
            Экспортировать
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  )
}
