import { FileText, Download, Eye, Upload } from 'lucide-react'
import { useState } from 'react'

interface Document {
  id: number
  title: string
  type: string
  file_url: string
  created_at: string
  size: number
}

interface ProjectDocumentsTabProps {
  projectId: number
  dealId?: number
}

export const ProjectDocumentsTab = ({ projectId, dealId }: ProjectDocumentsTabProps) => {
  const [documents, setDocuments] = useState<Document[]>([])

  const documentTypes = [
    { key: 'tz', label: 'Техническое задание', icon: '📋' },
    { key: 'contract', label: 'Договор', icon: '📄' },
    { key: 'act', label: 'Акт выполненных работ', icon: '✅' },
    { key: 'invoice', label: 'Счёт', icon: '💰' },
    { key: 'other', label: 'Прочие документы', icon: '📎' },
  ]

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">Документы проекта</h3>
        <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-medium shadow-md">
          <Upload className="w-4 h-4" />
          Загрузить документ
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {documentTypes.map((type) => (
          <div
            key={type.key}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">{type.icon}</span>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{type.label}</h4>
                <p className="text-xs text-gray-500">0 файлов</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm">
                <Eye className="w-4 h-4" />
                Просмотр
              </button>
              <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors text-sm">
                <Upload className="w-4 h-4" />
                Загрузить
              </button>
            </div>
          </div>
        ))}
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-12 mt-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Документы не загружены</p>
          <p className="text-gray-400 text-sm mt-1">
            Загрузите ТЗ, договор, акты и счета для удобного доступа
          </p>
        </div>
      ) : (
        <div className="mt-6 space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white border border-gray-200 rounded-lg p-4 flex items-center justify-between hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-purple-600" />
                <div>
                  <h4 className="font-semibold text-gray-900">{doc.title}</h4>
                  <p className="text-sm text-gray-500">
                    {new Date(doc.created_at).toLocaleDateString('ru-RU')} • {(doc.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                  <Eye className="w-5 h-5" />
                </button>
                <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                  <Download className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
