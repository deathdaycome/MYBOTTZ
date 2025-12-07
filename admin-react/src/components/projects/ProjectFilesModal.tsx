import { useState, useEffect, useRef } from 'react'
import {
  X,
  Upload,
  Download,
  Trash2,
  File,
  FileText,
  Image,
  Archive,
} from 'lucide-react'
import { apiService } from '../../services/api'

interface ProjectFile {
  id: number
  filename: string
  file_type: string
  file_size: number
  file_path: string
  uploaded_at: string
}

interface ProjectFilesModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
}

// Helper function to get file icon based on file type
const getFileIcon = (fileType: string) => {
  const type = fileType.toLowerCase()

  if (type.includes('image') || type.includes('jpg') || type.includes('png') || type.includes('gif')) {
    return <Image className="w-5 h-5 text-blue-600" />
  }
  if (type.includes('pdf') || type.includes('doc') || type.includes('txt')) {
    return <FileText className="w-5 h-5 text-red-600" />
  }
  if (type.includes('zip') || type.includes('rar') || type.includes('7z')) {
    return <Archive className="w-5 h-5 text-orange-600" />
  }
  return <File className="w-5 h-5 text-gray-600" />
}

// Helper function to format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Helper function to format date
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const ProjectFilesModal = ({ isOpen, onClose, projectId }: ProjectFilesModalProps) => {
  const [files, setFiles] = useState<ProjectFile[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const modalContentRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Block body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'

      // Reset modal content scroll to top
      if (modalContentRef.current) {
        modalContentRef.current.scrollTop = 0
      }

      // Load files
      loadFiles()
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
    return () => {
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
    }
  }, [isOpen, projectId])

  const loadFiles = async () => {
    if (!projectId) return

    try {
      setLoading(true)
      const response = await apiService.getProjectFiles(projectId)
      setFiles(response || [])
    } catch (error) {
      console.error('Error loading files:', error)
      alert('Ошибка при загрузке файлов')
    } finally {
      setLoading(false)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (!selectedFile || !projectId) return

    try {
      setUploading(true)

      await apiService.uploadProjectFile(projectId, selectedFile)
      alert('Файл успешно загружен!')

      // After successful upload, reload files
      await loadFiles()
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Ошибка при загрузке файла')
    } finally {
      setUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDownload = async (file: ProjectFile) => {
    if (!projectId) return

    try {
      const blob = await apiService.downloadProjectFile(projectId, file.id)

      // Create a download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = file.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading file:', error)
      alert('Ошибка при скачивании файла')
    }
  }

  const handleDelete = async (fileId: number, filename: string) => {
    if (!projectId) return

    const confirmed = window.confirm(`Вы уверены, что хотите удалить файл "${filename}"?`)
    if (!confirmed) return

    try {
      await apiService.deleteProjectFile(projectId, fileId)
      alert('Файл успешно удален!')

      // After successful deletion, reload files
      await loadFiles()
    } catch (error) {
      console.error('Error deleting file:', error)
      alert('Ошибка при удалении файла')
    }
  }

  if (!isOpen || !projectId) return null

  return (
    <>
      <style>{`
        .modal-content-scrollable {
          scrollbar-width: none !important;
          -ms-overflow-style: none !important;
        }
        .modal-content-scrollable::-webkit-scrollbar {
          display: none !important;
          width: 0 !important;
          height: 0 !important;
        }
      `}</style>
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-2"
        style={{ overflow: 'hidden' }}
      >
        <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-3 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold">Файлы проекта</h3>
                <p className="text-indigo-100 text-xs mt-0.5">Проект #{projectId}</p>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="text-white hover:bg-white/20 rounded-lg p-1.5 transition-colors flex-shrink-0"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Body - Scrollable */}
          <div ref={modalContentRef} className="modal-content-scrollable px-4 py-3 overflow-y-auto flex-1">
            {/* Upload Section */}
            <div className="mb-4">
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                className="hidden"
              />
              <button
                onClick={handleUploadClick}
                disabled={uploading}
                className="w-full px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Upload className="w-5 h-5" />
                {uploading ? 'Загрузка...' : 'Загрузить файл'}
              </button>
            </div>

            {/* Files List */}
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-gray-600">Загрузка файлов...</p>
                </div>
              </div>
            ) : files.length === 0 ? (
              <div className="bg-gray-50 rounded-lg p-12 text-center">
                <File className="w-16 h-16 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-600 font-medium">Нет загруженных файлов</p>
                <p className="text-gray-500 text-sm mt-1">
                  Загрузите первый файл для этого проекта
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {files.map((file) => (
                  <div
                    key={file.id}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:border-indigo-300 hover:shadow-md transition-all"
                  >
                    <div className="flex items-center gap-4">
                      {/* File Icon */}
                      <div className="flex-shrink-0">
                        {getFileIcon(file.file_type)}
                      </div>

                      {/* File Info */}
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-gray-900 truncate">
                          {file.filename}
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <File className="w-3 h-3" />
                            {formatFileSize(file.file_size)}
                          </span>
                          <span>•</span>
                          <span>{formatDate(file.uploaded_at)}</span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          onClick={() => handleDownload(file)}
                          className="px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-all text-sm font-semibold flex items-center gap-1"
                          title="Скачать"
                        >
                          <Download className="w-4 h-4" />
                          Скачать
                        </button>
                        <button
                          onClick={() => handleDelete(file.id, file.filename)}
                          className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all text-sm font-semibold flex items-center gap-1"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                          Удалить
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2.5 bg-gray-50 border-t border-gray-200 flex gap-2 flex-shrink-0">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold text-sm"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
