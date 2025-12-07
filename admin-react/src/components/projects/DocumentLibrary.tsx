import React, { useState, useEffect } from 'react'
import {
  FolderOpen,
  File,
  FileText,
  FileImage,
  FileVideo,
  FileArchive,
  Download,
  Upload,
  Trash2,
  Search,
  Filter,
  X,
  Plus,
  Eye,
  Edit2,
  Share2,
  Star,
  Clock,
  User,
  Grid3x3,
  List,
  ChevronRight,
  Folder,
} from 'lucide-react'

interface DocumentLibraryProps {
  projectId: number
  onClose: () => void
}

interface Document {
  id: number
  name: string
  type: 'pdf' | 'doc' | 'xls' | 'ppt' | 'img' | 'video' | 'archive' | 'other'
  size: number
  uploadedBy: string
  uploadedAt: string
  modifiedAt: string
  folderId: number | null
  url: string
  favorite: boolean
  tags: string[]
  description: string
  version: number
  sharedWith: string[]
}

interface Folder {
  id: number
  name: string
  parentId: number | null
  createdAt: string
  documentsCount: number
}

const DocumentLibrary: React.FC<DocumentLibraryProps> = ({ projectId, onClose }) => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [folders, setFolders] = useState<Folder[]>([])
  const [currentFolderId, setCurrentFolderId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showNewFolderModal, setShowNewFolderModal] = useState(false)
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)

  // Upload form
  const [uploadForm, setUploadForm] = useState({
    file: null as File | null,
    description: '',
    tags: [] as string[],
  })

  const [newTag, setNewTag] = useState('')
  const [newFolderName, setNewFolderName] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
    fetchFolders()
  }, [projectId])

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/documents`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setDocuments(data)
      } else {
        // Mock data
        setDocuments([
          {
            id: 1,
            name: 'Техническое задание.pdf',
            type: 'pdf',
            size: 2456789,
            uploadedBy: 'Алексей Иванов',
            uploadedAt: '2024-03-01T10:00:00',
            modifiedAt: '2024-03-02T15:30:00',
            folderId: 1,
            url: '/documents/tz.pdf',
            favorite: true,
            tags: ['ТЗ', 'Важное'],
            description: 'Техническое задание на разработку проекта',
            version: 2,
            sharedWith: ['Мария Петрова', 'Дмитрий Смирнов'],
          },
          {
            id: 2,
            name: 'Дизайн макеты.fig',
            type: 'other',
            size: 15678900,
            uploadedBy: 'Мария Петрова',
            uploadedAt: '2024-03-05T14:20:00',
            modifiedAt: '2024-03-10T11:45:00',
            folderId: 2,
            url: '/documents/design.fig',
            favorite: false,
            tags: ['Дизайн', 'Макеты'],
            description: 'Финальные макеты всех экранов',
            version: 5,
            sharedWith: ['Алексей Иванов'],
          },
          {
            id: 3,
            name: 'Логотип.png',
            type: 'img',
            size: 567890,
            uploadedBy: 'Мария Петрова',
            uploadedAt: '2024-02-28T09:15:00',
            modifiedAt: '2024-02-28T09:15:00',
            folderId: 2,
            url: '/documents/logo.png',
            favorite: true,
            tags: ['Дизайн', 'Логотип'],
            description: 'Официальный логотип компании',
            version: 1,
            sharedWith: [],
          },
          {
            id: 4,
            name: 'API документация.docx',
            type: 'doc',
            size: 1234567,
            uploadedBy: 'Дмитрий Смирнов',
            uploadedAt: '2024-03-08T16:00:00',
            modifiedAt: '2024-03-12T10:20:00',
            folderId: 3,
            url: '/documents/api-docs.docx',
            favorite: false,
            tags: ['API', 'Документация'],
            description: 'Подробная документация по API endpoints',
            version: 3,
            sharedWith: ['Алексей Иванов', 'Елена Козлова'],
          },
          {
            id: 5,
            name: 'Финансовый отчет Q1.xlsx',
            type: 'xls',
            size: 890123,
            uploadedBy: 'Финансовый отдел',
            uploadedAt: '2024-03-15T11:30:00',
            modifiedAt: '2024-03-15T11:30:00',
            folderId: 4,
            url: '/documents/finance-q1.xlsx',
            favorite: false,
            tags: ['Финансы', 'Отчет'],
            description: 'Финансовый отчет за первый квартал',
            version: 1,
            sharedWith: [],
          },
          {
            id: 6,
            name: 'Презентация для клиента.pptx',
            type: 'ppt',
            size: 3456789,
            uploadedBy: 'Алексей Иванов',
            uploadedAt: '2024-03-10T13:45:00',
            modifiedAt: '2024-03-10T13:45:00',
            folderId: null,
            url: '/documents/presentation.pptx',
            favorite: true,
            tags: ['Презентация', 'Клиент'],
            description: 'Презентация проекта для клиента',
            version: 1,
            sharedWith: ['Мария Петрова'],
          },
          {
            id: 7,
            name: 'Демо видео.mp4',
            type: 'video',
            size: 45678900,
            uploadedBy: 'Мария Петрова',
            uploadedAt: '2024-03-12T17:00:00',
            modifiedAt: '2024-03-12T17:00:00',
            folderId: 5,
            url: '/documents/demo.mp4',
            favorite: false,
            tags: ['Видео', 'Демо'],
            description: 'Демонстрационное видео продукта',
            version: 1,
            sharedWith: [],
          },
          {
            id: 8,
            name: 'Исходники.zip',
            type: 'archive',
            size: 123456789,
            uploadedBy: 'Дмитрий Смирнов',
            uploadedAt: '2024-03-14T12:00:00',
            modifiedAt: '2024-03-14T12:00:00',
            folderId: null,
            url: '/documents/sources.zip',
            favorite: false,
            tags: ['Код', 'Архив'],
            description: 'Архив с исходным кодом проекта',
            version: 1,
            sharedWith: ['Алексей Иванов'],
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchFolders = async () => {
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/folders`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setFolders(data)
      } else {
        // Mock data
        setFolders([
          { id: 1, name: 'Документация', parentId: null, createdAt: '2024-02-01', documentsCount: 1 },
          { id: 2, name: 'Дизайн', parentId: null, createdAt: '2024-02-01', documentsCount: 2 },
          { id: 3, name: 'Разработка', parentId: null, createdAt: '2024-02-01', documentsCount: 1 },
          { id: 4, name: 'Финансы', parentId: null, createdAt: '2024-02-01', documentsCount: 1 },
          { id: 5, name: 'Маркетинг', parentId: null, createdAt: '2024-02-01', documentsCount: 1 },
        ])
      }
    } catch (error) {
      console.error('Error fetching folders:', error)
    }
  }

  const handleUpload = async () => {
    if (!uploadForm.file) {
      alert('Выберите файл')
      return
    }

    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('description', uploadForm.description)
    formData.append('tags', JSON.stringify(uploadForm.tags))
    formData.append('folderId', String(currentFolderId || ''))

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/documents`, {
        method: 'POST',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        setDocuments([data, ...documents])
      } else {
        // Mock success
        const newDoc: Document = {
          id: Date.now(),
          name: uploadForm.file.name,
          type: getFileType(uploadForm.file.name),
          size: uploadForm.file.size,
          uploadedBy: 'Текущий пользователь',
          uploadedAt: new Date().toISOString(),
          modifiedAt: new Date().toISOString(),
          folderId: currentFolderId,
          url: URL.createObjectURL(uploadForm.file),
          favorite: false,
          tags: uploadForm.tags,
          description: uploadForm.description,
          version: 1,
          sharedWith: [],
        }
        setDocuments([newDoc, ...documents])
      }

      setShowUploadModal(false)
      setUploadForm({ file: null, description: '', tags: [] })
    } catch (error) {
      console.error('Error uploading document:', error)
    }
  }

  const handleCreateFolder = async () => {
    if (!newFolderName) {
      alert('Введите название папки')
      return
    }

    const folderData = {
      name: newFolderName,
      parentId: currentFolderId,
      createdAt: new Date().toISOString(),
      documentsCount: 0,
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/folders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(folderData),
      })

      if (response.ok) {
        const data = await response.json()
        setFolders([...folders, data])
      } else {
        setFolders([...folders, { ...folderData, id: Date.now() }])
      }

      setShowNewFolderModal(false)
      setNewFolderName('')
    } catch (error) {
      console.error('Error creating folder:', error)
    }
  }

  const handleDeleteDocument = async (docId: number) => {
    if (!confirm('Удалить документ?')) return

    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/documents/${docId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      setDocuments(documents.filter((d) => d.id !== docId))
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }

  const handleToggleFavorite = async (doc: Document) => {
    const updated = { ...doc, favorite: !doc.favorite }
    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/documents/${doc.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(updated),
      })
      setDocuments(documents.map((d) => (d.id === doc.id ? updated : d)))
    } catch (error) {
      console.error('Error toggling favorite:', error)
    }
  }

  const getFileIcon = (type: string) => {
    const icons = {
      pdf: FileText,
      doc: FileText,
      xls: FileText,
      ppt: FileText,
      img: FileImage,
      video: FileVideo,
      archive: FileArchive,
      other: File,
    }
    return icons[type as keyof typeof icons] || File
  }

  const getFileType = (filename: string): Document['type'] => {
    const ext = filename.split('.').pop()?.toLowerCase()
    if (ext === 'pdf') return 'pdf'
    if (['doc', 'docx'].includes(ext || '')) return 'doc'
    if (['xls', 'xlsx'].includes(ext || '')) return 'xls'
    if (['ppt', 'pptx'].includes(ext || '')) return 'ppt'
    if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(ext || '')) return 'img'
    if (['mp4', 'avi', 'mov', 'wmv'].includes(ext || '')) return 'video'
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext || '')) return 'archive'
    return 'other'
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
  }

  const getCurrentFolderPath = (): Folder[] => {
    const path: Folder[] = []
    let current = folders.find((f) => f.id === currentFolderId)
    while (current) {
      path.unshift(current)
      current = folders.find((f) => f.id === current!.parentId)
    }
    return path
  }

  let filteredDocuments = documents.filter((doc) => {
    const matchesFolder = doc.folderId === currentFolderId
    const matchesSearch =
      doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesType = filterType === 'all' || doc.type === filterType
    const matchesFavorites = !showFavoritesOnly || doc.favorite

    return matchesFolder && matchesSearch && matchesType && matchesFavorites
  })

  // Sort
  filteredDocuments = filteredDocuments.sort((a, b) => {
    if (sortBy === 'name') return a.name.localeCompare(b.name)
    if (sortBy === 'date') return new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime()
    if (sortBy === 'size') return b.size - a.size
    return 0
  })

  const currentFolderFolders = folders.filter((f) => f.parentId === currentFolderId)

  const stats = {
    totalDocuments: documents.length,
    totalSize: documents.reduce((sum, d) => sum + d.size, 0),
    favorites: documents.filter((d) => d.favorite).length,
    foldersCount: folders.length,
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка документов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <FolderOpen className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Библиотека документов</h2>
              <p className="text-emerald-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            aria-label="Закрыть"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <File className="w-4 h-4" />
              <span>Документов</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalDocuments}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <FolderOpen className="w-4 h-4" />
              <span>Папок</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.foldersCount}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Star className="w-4 h-4" />
              <span>Избранное</span>
            </div>
            <div className="text-2xl font-bold text-yellow-600">{stats.favorites}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <FileArchive className="w-4 h-4" />
              <span>Размер</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{formatFileSize(stats.totalSize)}</div>
          </div>
        </div>

        {/* Breadcrumb */}
        <div className="px-6 py-3 bg-white border-b">
          <div className="flex items-center gap-2 text-sm">
            <button
              onClick={() => setCurrentFolderId(null)}
              className="text-emerald-600 hover:text-emerald-700 font-medium"
            >
              Корень
            </button>
            {getCurrentFolderPath().map((folder) => (
              <React.Fragment key={folder.id}>
                <ChevronRight className="w-4 h-4 text-gray-400" />
                <button
                  onClick={() => setCurrentFolderId(folder.id)}
                  className="text-emerald-600 hover:text-emerald-700 font-medium"
                >
                  {folder.name}
                </button>
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex flex-wrap justify-between items-center gap-4 p-6 bg-white border-b">
          <div className="flex flex-wrap gap-3 flex-1">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Поиск документов..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="all">Все типы</option>
              <option value="pdf">PDF</option>
              <option value="doc">Документы</option>
              <option value="xls">Таблицы</option>
              <option value="ppt">Презентации</option>
              <option value="img">Изображения</option>
              <option value="video">Видео</option>
              <option value="archive">Архивы</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'name' | 'date' | 'size')}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="date">По дате</option>
              <option value="name">По имени</option>
              <option value="size">По размеру</option>
            </select>
            <button
              onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
              className={`px-4 py-2 rounded-lg border transition-colors ${
                showFavoritesOnly
                  ? 'bg-yellow-100 border-yellow-300 text-yellow-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Star className={`w-5 h-5 ${showFavoritesOnly ? 'fill-current' : ''}`} />
            </button>
            <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded transition-colors ${viewMode === 'grid' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded transition-colors ${viewMode === 'list' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowNewFolderModal(true)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
            >
              <Folder className="w-5 h-5" />
              Создать папку
            </button>
            <button
              onClick={() => setShowUploadModal(true)}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2"
            >
              <Upload className="w-5 h-5" />
              Загрузить
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Folders */}
          {currentFolderFolders.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Папки</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {currentFolderFolders.map((folder) => (
                  <button
                    key={folder.id}
                    onClick={() => setCurrentFolderId(folder.id)}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow text-left"
                  >
                    <Folder className="w-12 h-12 text-yellow-500 mb-2" />
                    <p className="font-medium text-gray-900 truncate">{folder.name}</p>
                    <p className="text-xs text-gray-500">{folder.documentsCount} документов</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Documents */}
          {viewMode === 'grid' ? (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Документы</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {filteredDocuments.map((doc) => {
                  const FileIcon = getFileIcon(doc.type)
                  return (
                    <div
                      key={doc.id}
                      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow relative group"
                    >
                      <button
                        onClick={() => handleToggleFavorite(doc)}
                        className="absolute top-2 right-2 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Star className={`w-5 h-5 ${doc.favorite ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400'}`} />
                      </button>
                      <FileIcon className="w-12 h-12 text-emerald-600 mb-2" />
                      <p className="font-medium text-gray-900 truncate mb-1">{doc.name}</p>
                      <p className="text-xs text-gray-500 mb-2">{formatFileSize(doc.size)}</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setSelectedDocument(doc)}
                          className="flex-1 px-2 py-1 text-xs bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 transition-colors"
                        >
                          Просмотр
                        </button>
                        <button
                          onClick={() => handleDeleteDocument(doc.id)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ) : (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Документы</h3>
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Название</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Размер</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Автор</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredDocuments.map((doc) => {
                      const FileIcon = getFileIcon(doc.type)
                      return (
                        <tr key={doc.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <FileIcon className="w-8 h-8 text-emerald-600" />
                              <div>
                                <p className="font-medium text-gray-900">{doc.name}</p>
                                {doc.tags.length > 0 && (
                                  <div className="flex gap-1 mt-1">
                                    {doc.tags.slice(0, 2).map((tag, idx) => (
                                      <span key={idx} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                                        {tag}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">{formatFileSize(doc.size)}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{doc.uploadedBy}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {new Date(doc.uploadedAt).toLocaleDateString('ru-RU')}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div className="flex justify-end gap-2">
                              <button
                                onClick={() => handleToggleFavorite(doc)}
                                className="p-1 text-gray-400 hover:text-yellow-500 transition-colors"
                              >
                                <Star className={`w-5 h-5 ${doc.favorite ? 'fill-current text-yellow-500' : ''}`} />
                              </button>
                              <button
                                onClick={() => setSelectedDocument(doc)}
                                className="p-1 text-gray-400 hover:text-emerald-600 transition-colors"
                              >
                                <Eye className="w-5 h-5" />
                              </button>
                              <button
                                onClick={() => handleDeleteDocument(doc.id)}
                                className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {filteredDocuments.length === 0 && currentFolderFolders.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <FolderOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Нет документов</p>
            </div>
          )}
        </div>

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
              <h3 className="text-xl font-bold mb-4">Загрузить документ</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Файл *</label>
                  <input
                    type="file"
                    onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files?.[0] || null })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                  <textarea
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                    placeholder="Описание документа"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Теги</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newTag) {
                          setUploadForm({ ...uploadForm, tags: [...uploadForm.tags, newTag] })
                          setNewTag('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                      placeholder="Добавить тег (Enter)"
                    />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {uploadForm.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 text-sm px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full"
                      >
                        {tag}
                        <button
                          onClick={() => setUploadForm({ ...uploadForm, tags: uploadForm.tags.filter((_, i) => i !== idx) })}
                          className="hover:text-emerald-900"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleUpload}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                >
                  Загрузить
                </button>
              </div>
            </div>
          </div>
        )}

        {/* New Folder Modal */}
        {showNewFolderModal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-xl font-bold mb-4">Создать папку</h3>
              <input
                type="text"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent mb-4"
                placeholder="Название папки"
              />
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowNewFolderModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleCreateFolder}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
                >
                  Создать
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Document Detail Modal */}
        {selectedDocument && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-start gap-4">
                  {React.createElement(getFileIcon(selectedDocument.type), { className: 'w-12 h-12 text-emerald-600' })}
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{selectedDocument.name}</h3>
                    <p className="text-sm text-gray-500">Версия {selectedDocument.version}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedDocument(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Описание:</p>
                  <p className="text-gray-900">{selectedDocument.description || 'Нет описания'}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Размер:</p>
                    <p className="text-gray-900">{formatFileSize(selectedDocument.size)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Автор:</p>
                    <p className="text-gray-900">{selectedDocument.uploadedBy}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Загружено:</p>
                    <p className="text-gray-900">{new Date(selectedDocument.uploadedAt).toLocaleString('ru-RU')}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Изменено:</p>
                    <p className="text-gray-900">{new Date(selectedDocument.modifiedAt).toLocaleString('ru-RU')}</p>
                  </div>
                </div>
                {selectedDocument.tags.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Теги:</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedDocument.tags.map((tag, idx) => (
                        <span key={idx} className="text-sm px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {selectedDocument.sharedWith.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Доступ:</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedDocument.sharedWith.map((user, idx) => (
                        <span key={idx} className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-full">
                          {user}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex gap-3 pt-4 border-t">
                  <a
                    href={selectedDocument.url}
                    download={selectedDocument.name}
                    className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-center flex items-center justify-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Скачать
                  </a>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
                    <Share2 className="w-5 h-5" />
                    Поделиться
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentLibrary
