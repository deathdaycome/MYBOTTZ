import { useState, useEffect, useCallback } from 'react'
import {
  FileText,
  Upload,
  Download,
  Trash2,
  Search,
  Filter,
  File,
  Loader2,
  RefreshCw,
  X,
} from 'lucide-react'
// API imports
import documentsApi from '../api/documents'
import type { Document, DocumentStats, Project } from '../api/documents'

export const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [stats, setStats] = useState<DocumentStats>({
    total: 0,
    contracts: 0,
    invoices: 0,
    acts: 0,
    other: 0,
  })
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  // Фильтры
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [projectFilter, setProjectFilter] = useState<string>('')

  // Модальное окно загрузки
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadForm, setUploadForm] = useState({
    name: '',
    type: 'invoice' as 'contract' | 'invoice' | 'act' | 'other',
    number: '',
    description: '',
    project_id: '',
    file: null as File | null,
  })

  // Toast уведомления
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  // Загрузка данных
  const loadDocuments = useCallback(async () => {
    try {
      const [docsData, statsData, projectsData] = await Promise.all([
        documentsApi.getDocuments(),
        documentsApi.getStats(),
        documentsApi.getProjects(),
      ])

      setDocuments(docsData)
      setFilteredDocuments(docsData)
      setStats(statsData)
      setProjects(projectsData)
    } catch (error: any) {
      console.error('Error loading documents:', error)
      showToast('Ошибка загрузки документов', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  // Фильтрация документов
  useEffect(() => {
    let filtered = [...documents]

    // Поиск
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (doc) =>
          doc.name.toLowerCase().includes(query) ||
          doc.number?.toLowerCase().includes(query) ||
          doc.description?.toLowerCase().includes(query)
      )
    }

    // Фильтр по типу
    if (typeFilter) {
      filtered = filtered.filter((doc) => doc.type === typeFilter)
    }

    // Фильтр по проекту
    if (projectFilter) {
      filtered = filtered.filter((doc) => doc.project_id?.toString() === projectFilter)
    }

    setFilteredDocuments(filtered)
  }, [documents, searchQuery, typeFilter, projectFilter])

  // Загрузка документа
  const handleUploadDocument = async () => {
    if (!uploadForm.name || !uploadForm.type || !uploadForm.file) {
      showToast('Заполните обязательные поля', 'error')
      return
    }

    setUploading(true)

    try {
      const result = await documentsApi.uploadDocument({
        file: uploadForm.file,
        name: uploadForm.name,
        type: uploadForm.type,
        description: uploadForm.description || undefined,
        number: uploadForm.number || undefined,
        project_id: uploadForm.project_id ? parseInt(uploadForm.project_id) : undefined,
      })

      if (result.success) {
        showToast(result.message, 'success')
        setShowUploadModal(false)
        setUploadForm({
          name: '',
          type: 'invoice',
          number: '',
          description: '',
          project_id: '',
          file: null,
        })
        await loadDocuments()
      } else {
        showToast(result.message, 'error')
      }
    } catch (error: any) {
      console.error('Error uploading document:', error)
      if (error.response?.status === 403) {
        showToast('Недостаточно прав для загрузки этого типа документов', 'error')
      } else {
        showToast('Ошибка загрузки документа', 'error')
      }
    } finally {
      setUploading(false)
    }
  }

  // Скачивание документа
  const handleDownloadDocument = async (doc: Document) => {
    try {
      const blob = await documentsApi.downloadDocument(doc.id)

      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // Извлекаем расширение из file_path или используем имя документа
      const extension = doc.file_path.split('.').pop() || ''
      link.download = extension ? `${doc.name}.${extension}` : doc.name

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      showToast('Документ загружен', 'success')
    } catch (error: any) {
      console.error('Error downloading document:', error)
      if (error.response?.status === 403) {
        showToast('Нет доступа к этому документу', 'error')
      } else if (error.response?.status === 404) {
        showToast('Файл не найден', 'error')
      } else {
        showToast('Ошибка скачивания документа', 'error')
      }
    }
  }

  // Удаление документа
  const handleDeleteDocument = async (doc: Document) => {
    if (!window.confirm(`Вы уверены, что хотите удалить документ "${doc.name}"?`)) {
      return
    }

    try {
      const result = await documentsApi.deleteDocument(doc.id)

      if (result.success) {
        showToast(result.message, 'success')
        await loadDocuments()
      } else {
        showToast(result.message, 'error')
      }
    } catch (error: any) {
      console.error('Error deleting document:', error)
      if (error.response?.status === 403) {
        showToast('Недостаточно прав для удаления этого документа', 'error')
      } else {
        showToast('Ошибка удаления документа', 'error')
      }
    }
  }

  // Форматирование размера файла
  const formatFileSize = (bytes: number): string => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
  }

  // Форматирование даты
  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '—'
    const date = new Date(dateStr)
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Получение иконки файла
  const getFileIcon = (fileType: string) => {
    if (fileType.includes('pdf')) return <File className="w-5 h-5 text-red-500" />
    if (fileType.includes('word') || fileType.includes('document')) return <FileText className="w-5 h-5 text-blue-500" />
    if (fileType.includes('excel') || fileType.includes('spreadsheet'))
      return <FileText className="w-5 h-5 text-green-500" />
    if (fileType.includes('image')) return <File className="w-5 h-5 text-purple-500" />
    return <File className="w-5 h-5 text-gray-500" />
  }

  // Получение стиля бейджа типа
  const getTypeBadge = (type: string) => {
    const styles = {
      contract: 'bg-red-100 text-red-800',
      invoice: 'bg-blue-100 text-blue-800',
      act: 'bg-green-100 text-green-800',
      other: 'bg-gray-100 text-gray-800',
    }

    const labels = {
      contract: 'Договор',
      invoice: 'Счет',
      act: 'Акт',
      other: 'Другое',
    }

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[type as keyof typeof styles]}`}>
        {labels[type as keyof typeof labels]}
      </span>
    )
  }

  // Получение иконки типа для статистики
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'contract':
        return <FileText className="w-8 h-8" />
      case 'invoice':
        return <FileText className="w-8 h-8" />
      case 'act':
        return <FileText className="w-8 h-8" />
      default:
        return <File className="w-8 h-8" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
            Документы
          </h1>
          <p className="text-gray-600 mt-2">Управление документами проектов</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => loadDocuments()}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Обновить
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-lg hover:from-amber-700 hover:to-orange-700 transition-all flex items-center gap-2 shadow-lg"
          >
            <Upload className="w-4 h-4" />
            Загрузить документ
          </button>
        </div>
      </div>

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-3 rounded-lg shadow-lg text-white ${
              toast.type === 'success' ? 'bg-green-500' : toast.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
            } animate-slide-in`}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium mb-1">Всего документов</p>
              <p className="text-3xl font-bold">{stats.total}</p>
            </div>
            <div className="opacity-75">{getTypeIcon('other')}</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm font-medium mb-1">Договоры</p>
              <p className="text-3xl font-bold">{stats.contracts}</p>
            </div>
            <div className="opacity-75">{getTypeIcon('contract')}</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium mb-1">Счета</p>
              <p className="text-3xl font-bold">{stats.invoices}</p>
            </div>
            <div className="opacity-75">{getTypeIcon('invoice')}</div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium mb-1">Акты</p>
              <p className="text-3xl font-bold">{stats.acts}</p>
            </div>
            <div className="opacity-75">{getTypeIcon('act')}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-md p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по названию, номеру, описанию..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 appearance-none bg-white"
            >
              <option value="">Все типы</option>
              <option value="contract">Договоры</option>
              <option value="invoice">Счета</option>
              <option value="act">Акты</option>
              <option value="other">Другое</option>
            </select>
          </div>

          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <select
              value={projectFilter}
              onChange={(e) => setProjectFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 appearance-none bg-white"
            >
              <option value="">Все проекты</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.title}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800 text-white">
              <tr>
                <th className="px-6 py-4 text-left font-semibold">Название</th>
                <th className="px-6 py-4 text-left font-semibold">Тип</th>
                <th className="px-6 py-4 text-left font-semibold">Номер</th>
                <th className="px-6 py-4 text-left font-semibold">Проект</th>
                <th className="px-6 py-4 text-left font-semibold">Размер</th>
                <th className="px-6 py-4 text-left font-semibold">Дата создания</th>
                <th className="px-6 py-4 text-left font-semibold">Создал</th>
                <th className="px-6 py-4 text-center font-semibold">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredDocuments.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center">
                    <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg">Нет документов</p>
                    <p className="text-gray-400 text-sm mt-2">Загрузите первый документ</p>
                  </td>
                </tr>
              ) : (
                filteredDocuments.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        {getFileIcon(doc.file_type)}
                        <div>
                          <p className="font-semibold text-gray-800">{doc.name}</p>
                          {doc.description && <p className="text-sm text-gray-500 mt-1">{doc.description}</p>}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">{getTypeBadge(doc.type)}</td>
                    <td className="px-6 py-4 text-gray-600">{doc.number || '—'}</td>
                    <td className="px-6 py-4 text-gray-600">{doc.project_name || '—'}</td>
                    <td className="px-6 py-4 text-gray-600">{formatFileSize(doc.file_size)}</td>
                    <td className="px-6 py-4 text-gray-600 text-sm">{formatDate(doc.created_at)}</td>
                    <td className="px-6 py-4 text-gray-600">{doc.created_by || '—'}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => handleDownloadDocument(doc)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Скачать"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteDocument(doc)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-800">Загрузить документ</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {/* Название */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Название <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={uploadForm.name}
                  onChange={(e) => setUploadForm({ ...uploadForm, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="Введите название документа"
                />
              </div>

              {/* Тип документа */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Тип документа <span className="text-red-500">*</span>
                </label>
                <select
                  value={uploadForm.type}
                  onChange={(e) =>
                    setUploadForm({ ...uploadForm, type: e.target.value as 'contract' | 'invoice' | 'act' | 'other' })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option value="invoice">Счет</option>
                  <option value="act">Акт</option>
                  <option value="contract">Договор</option>
                  <option value="other">Другое</option>
                </select>
              </div>

              {/* Номер документа */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Номер документа</label>
                <input
                  type="text"
                  value={uploadForm.number}
                  onChange={(e) => setUploadForm({ ...uploadForm, number: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                  placeholder="№123"
                />
              </div>

              {/* Проект */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Проект</label>
                <select
                  value={uploadForm.project_id}
                  onChange={(e) => setUploadForm({ ...uploadForm, project_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option value="">Без привязки</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.title} {project.client_name && `(${project.client_name})`}
                    </option>
                  ))}
                </select>
              </div>

              {/* Описание */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Описание</label>
                <textarea
                  value={uploadForm.description}
                  onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 resize-none"
                  placeholder="Дополнительная информация о документе"
                />
              </div>

              {/* Файл */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Файл <span className="text-red-500">*</span>
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-amber-500 transition-colors">
                  <input
                    type="file"
                    onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files?.[0] || null })}
                    className="hidden"
                    id="file-upload"
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    {uploadForm.file ? (
                      <div>
                        <p className="text-sm font-semibold text-gray-700">{uploadForm.file.name}</p>
                        <p className="text-xs text-gray-500 mt-1">{formatFileSize(uploadForm.file.size)}</p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm font-semibold text-gray-700 mb-1">Нажмите для выбора файла</p>
                        <p className="text-xs text-gray-500">PDF, Word, Excel, изображения</p>
                      </div>
                    )}
                  </label>
                </div>
              </div>
            </div>

            <div className="sticky bottom-0 bg-gray-50 px-6 py-4 flex items-center justify-end gap-3 border-t border-gray-200">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleUploadDocument}
                disabled={uploading}
                className="px-6 py-2 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-lg hover:from-amber-700 hover:to-orange-700 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Загрузка...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Загрузить
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
