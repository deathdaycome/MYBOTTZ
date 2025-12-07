/**
 * Вкладка "Документы" проекта
 * Договоры, акты, счета
 */

import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { FileText, Upload, Download, Trash2, Eye, Plus, Loader2 } from 'lucide-react'
import axiosInstance from '../../services/api'

interface Project {
  id: number
  title: string
}

interface Document {
  id: number
  type: string
  name: string
  number?: string
  file_path?: string
  file_size?: number
  file_type?: string
  status: string
  date?: string
  signed_at?: string
  description?: string
  created_at: string
}

interface OutletContext {
  project: Project
}

export const ProjectDocuments = () => {
  const { project } = useOutletContext<OutletContext>()
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Загрузка документов
  useEffect(() => {
    loadDocuments()
  }, [project.id])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(`/admin/api/projects/${project.id}/documents`)

      if (response.data.success) {
        setDocuments(response.data.documents || [])
      }
      setError(null)
    } catch (err: any) {
      console.error('Error loading documents:', err)
      setError('Ошибка загрузки документов')
    } finally {
      setLoading(false)
    }
  }

  // Типы документов
  const documentTypes: Record<string, { label: string; color: string }> = {
    contract: { label: 'Договор', color: 'blue' },
    act: { label: 'Акт', color: 'green' },
    invoice: { label: 'Счет', color: 'purple' },
    specification: { label: 'Спецификация', color: 'orange' },
    other: { label: 'Другое', color: 'gray' },
  }

  // Статусы документов
  const documentStatuses: Record<string, { label: string; color: string }> = {
    draft: { label: 'Черновик', color: 'gray' },
    sent: { label: 'Отправлен', color: 'blue' },
    signed: { label: 'Подписан', color: 'green' },
    rejected: { label: 'Отклонен', color: 'red' },
  }

  const getDocumentTypeColor = (type: string) => {
    const typeInfo = documentTypes[type] || documentTypes.other
    return typeInfo.color
  }

  const getDocumentStatusColor = (status: string) => {
    const statusInfo = documentStatuses[status] || documentStatuses.draft
    return statusInfo.color
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '-'
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(2)} МБ`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Документы проекта</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Добавить документ</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Список документов */}
      {documents.length > 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Тип
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Название
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Номер
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Дата
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Размер
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {documents.map((doc) => (
                  <tr
                    key={doc.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${getDocumentTypeColor(
                          doc.type
                        )}-100 text-${getDocumentTypeColor(
                          doc.type
                        )}-700 dark:bg-${getDocumentTypeColor(doc.type)}-900/30 dark:text-${getDocumentTypeColor(
                          doc.type
                        )}-400`}
                      >
                        {documentTypes[doc.type]?.label || doc.type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-gray-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {doc.name}
                        </span>
                      </div>
                      {doc.description && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{doc.description}</p>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {doc.number || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${getDocumentStatusColor(
                          doc.status
                        )}-100 text-${getDocumentStatusColor(
                          doc.status
                        )}-700 dark:bg-${getDocumentStatusColor(
                          doc.status
                        )}-900/30 dark:text-${getDocumentStatusColor(doc.status)}-400`}
                      >
                        {documentStatuses[doc.status]?.label || doc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {doc.date
                        ? new Date(doc.date).toLocaleDateString('ru-RU')
                        : new Date(doc.created_at).toLocaleDateString('ru-RU')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatFileSize(doc.file_size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <div className="flex items-center justify-end gap-2">
                        {doc.file_path && (
                          <button
                            className="p-1.5 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
                            title="Скачать"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          className="p-1.5 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
                          title="Просмотр"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          className="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <FileText className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Документы не найдены</h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">Загрузите первый документ проекта</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors"
          >
            <Upload className="w-4 h-4" />
            <span>Загрузить документ</span>
          </button>
        </div>
      )}

      {/* TODO: Модалка создания документа */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Добавить документ
            </h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-4">
              Функционал добавления документов будет реализован
            </p>
            <button
              onClick={() => setShowCreateModal(false)}
              className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Закрыть
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectDocuments
