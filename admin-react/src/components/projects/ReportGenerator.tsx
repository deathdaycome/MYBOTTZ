import React, { useState, useEffect } from 'react'
import { FileText, Download, Calendar, BarChart2, Users, DollarSign, Clock, Target, TrendingUp, Filter, X, CheckSquare } from 'lucide-react'

interface ReportGeneratorProps {
  projectId: number
  onClose: () => void
}

interface ReportTemplate {
  id: number
  name: string
  description: string
  type: 'progress' | 'financial' | 'time' | 'team' | 'quality' | 'custom'
  sections: string[]
  format: 'pdf' | 'xlsx' | 'docx' | 'html'
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({ projectId, onClose }) => {
  const [templates, setTemplates] = useState<ReportTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null)
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState(new Date().toISOString().slice(0, 10))
  const [selectedSections, setSelectedSections] = useState<string[]>([])
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'xlsx' | 'docx' | 'html'>('pdf')
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = 'unset' }
  }, [])

  useEffect(() => {
    fetchTemplates()
  }, [projectId])

  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/report-templates`, {
        headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
      })
      if (response.ok) {
        const data = await response.json()
        setTemplates(data)
      } else {
        setTemplates([
          {
            id: 1,
            name: 'Отчет о прогрессе',
            description: 'Общий прогресс выполнения проекта',
            type: 'progress',
            sections: ['Статус задач', 'Вехи', 'Прогресс (%)', 'Риски', 'Проблемы'],
            format: 'pdf',
          },
          {
            id: 2,
            name: 'Финансовый отчет',
            description: 'Бюджет и расходы проекта',
            type: 'financial',
            sections: ['Бюджет', 'Расходы по категориям', 'Прогноз', 'Отклонения'],
            format: 'xlsx',
          },
          {
            id: 3,
            name: 'Отчет по времени',
            description: 'Учет времени команды',
            type: 'time',
            sections: ['Часы по задачам', 'Часы по участникам', 'Billable/Non-billable', 'Эффективность'],
            format: 'xlsx',
          },
          {
            id: 4,
            name: 'Отчет по команде',
            description: 'Производительность команды',
            type: 'team',
            sections: ['Участники', 'Загрузка', 'Выполненные задачи', 'Метрики производительности'],
            format: 'pdf',
          },
          {
            id: 5,
            name: 'Отчет по качеству',
            description: 'QA метрики и баги',
            type: 'quality',
            sections: ['Тесты', 'Баги', 'Code coverage', 'Технический долг'],
            format: 'pdf',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!selectedTemplate) {
      alert('Выберите шаблон отчета')
      return
    }

    if (!dateFrom || !dateTo) {
      alert('Укажите период отчета')
      return
    }

    setGenerating(true)

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          templateId: selectedTemplate.id,
          dateFrom,
          dateTo,
          sections: selectedSections.length > 0 ? selectedSections : selectedTemplate.sections,
          format: selectedFormat,
        }),
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `report-${selectedTemplate.name}-${new Date().toISOString().slice(0, 10)}.${selectedFormat}`
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
        alert('Отчет сгенерирован и скачан')
      } else {
        alert('Отчет будет сгенерирован в фоновом режиме')
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Отчет будет сгенерирован в фоновом режиме')
    } finally {
      setGenerating(false)
    }
  }

  const getTemplateIcon = (type: string) => {
    const icons = {
      progress: Target,
      financial: DollarSign,
      time: Clock,
      team: Users,
      quality: BarChart2,
      custom: FileText,
    }
    return icons[type as keyof typeof icons] || FileText
  }

  const handleToggleSection = (section: string) => {
    if (selectedSections.includes(section)) {
      setSelectedSections(selectedSections.filter((s) => s !== section))
    } else {
      setSelectedSections([...selectedSections, section])
    }
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка шаблонов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-teal-600 to-cyan-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <FileText className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Генератор отчетов</h2>
              <p className="text-teal-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Templates */}
            <div className="lg:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Шаблоны отчетов</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map((template) => {
                  const TemplateIcon = getTemplateIcon(template.type)
                  const isSelected = selectedTemplate?.id === template.id

                  return (
                    <button
                      key={template.id}
                      onClick={() => {
                        setSelectedTemplate(template)
                        setSelectedSections([])
                        setSelectedFormat(template.format)
                      }}
                      className={`text-left bg-white border-2 rounded-lg p-6 hover:shadow-md transition-all ${
                        isSelected ? 'border-teal-600 bg-teal-50' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <TemplateIcon className={`w-8 h-8 flex-shrink-0 ${isSelected ? 'text-teal-600' : 'text-gray-600'}`} />
                        <div className="flex-1">
                          <h4 className="font-bold text-gray-900 mb-1">{template.name}</h4>
                          <p className="text-sm text-gray-600">{template.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>{template.sections.length} разделов</span>
                        <span>•</span>
                        <span>{template.format.toUpperCase()}</span>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Настройки отчета</h3>
              <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="w-4 h-4 inline mr-2" />
                    Период отчета
                  </label>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">От</label>
                      <input
                        type="date"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">До</label>
                      <input
                        type="date"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {selectedTemplate && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <CheckSquare className="w-4 h-4 inline mr-2" />
                        Разделы отчета
                      </label>
                      <div className="space-y-2">
                        {selectedTemplate.sections.map((section) => (
                          <label key={section} className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={selectedSections.length === 0 || selectedSections.includes(section)}
                              onChange={() => handleToggleSection(section)}
                              className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
                            />
                            <span className="text-sm text-gray-700">{section}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <FileText className="w-4 h-4 inline mr-2" />
                        Формат файла
                      </label>
                      <div className="grid grid-cols-2 gap-2">
                        {(['pdf', 'xlsx', 'docx', 'html'] as const).map((format) => (
                          <button
                            key={format}
                            onClick={() => setSelectedFormat(format)}
                            className={`px-4 py-2 rounded-lg border-2 transition-colors ${
                              selectedFormat === format
                                ? 'border-teal-600 bg-teal-50 text-teal-700 font-medium'
                                : 'border-gray-200 text-gray-700 hover:bg-gray-50'
                            }`}
                          >
                            {format.toUpperCase()}
                          </button>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={handleGenerateReport}
                      disabled={generating || !dateFrom || !dateTo}
                      className="w-full px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
                    >
                      {generating ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          Генерация...
                        </>
                      ) : (
                        <>
                          <Download className="w-5 h-5" />
                          Сгенерировать отчет
                        </>
                      )}
                    </button>
                  </>
                )}

                {!selectedTemplate && (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Выберите шаблон отчета</p>
                  </div>
                )}
              </div>

              {selectedTemplate && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="text-sm font-medium text-blue-900 mb-2">Описание</h4>
                  <p className="text-sm text-blue-700">{selectedTemplate.description}</p>
                  <div className="mt-3 pt-3 border-t border-blue-200">
                    <p className="text-xs text-blue-600">
                      Отчет будет содержать{' '}
                      {selectedSections.length > 0 ? selectedSections.length : selectedTemplate.sections.length} разделов
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportGenerator
