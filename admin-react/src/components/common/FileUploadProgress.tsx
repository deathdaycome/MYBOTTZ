import { Upload, X, CheckCircle, AlertCircle, File } from 'lucide-react'

export interface UploadFile {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
}

interface FileUploadProgressProps {
  files: UploadFile[]
  onCancel: (id: string) => void
  onClear: () => void
}

export const FileUploadProgress = ({ files, onCancel, onClear }: FileUploadProgressProps) => {
  if (files.length === 0) return null

  const allCompleted = files.every((f) => f.status === 'completed')
  const hasErrors = files.some((f) => f.status === 'error')

  return (
    <div className="fixed bottom-4 right-4 z-[9998] w-96 bg-white rounded-xl shadow-2xl border-2 border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="flex items-center gap-2">
          <Upload className="w-5 h-5" />
          <span className="font-semibold">
            {allCompleted ? 'Загрузка завершена' : 'Загрузка файлов'}
          </span>
        </div>
        <button
          onClick={onClear}
          className="hover:bg-white/20 rounded-lg p-1 transition-colors"
          title="Закрыть"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Files List */}
      <div className="max-h-80 overflow-y-auto p-4 space-y-3">
        {files.map((uploadFile) => (
          <div
            key={uploadFile.id}
            className={`p-3 rounded-lg border-2 transition-all ${
              uploadFile.status === 'completed'
                ? 'border-green-200 bg-green-50'
                : uploadFile.status === 'error'
                ? 'border-red-200 bg-red-50'
                : 'border-blue-200 bg-blue-50'
            }`}
          >
            <div className="flex items-start gap-3">
              {/* Icon */}
              <div className="flex-shrink-0 mt-0.5">
                {uploadFile.status === 'completed' ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : uploadFile.status === 'error' ? (
                  <AlertCircle className="w-5 h-5 text-red-600" />
                ) : (
                  <File className="w-5 h-5 text-blue-600" />
                )}
              </div>

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {uploadFile.file.name}
                  </span>
                  {uploadFile.status === 'uploading' && (
                    <button
                      onClick={() => onCancel(uploadFile.id)}
                      className="flex-shrink-0 text-gray-500 hover:text-gray-700"
                      title="Отменить"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <span>{formatFileSize(uploadFile.file.size)}</span>
                  {uploadFile.status === 'completed' && (
                    <span className="text-green-600 font-semibold">✓ Загружено</span>
                  )}
                  {uploadFile.status === 'error' && (
                    <span className="text-red-600 font-semibold">✗ Ошибка</span>
                  )}
                  {uploadFile.status === 'uploading' && (
                    <span className="text-blue-600 font-semibold">{uploadFile.progress}%</span>
                  )}
                </div>

                {/* Progress Bar */}
                {uploadFile.status === 'uploading' && (
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300 ease-out"
                      style={{ width: `${uploadFile.progress}%` }}
                    />
                  </div>
                )}

                {/* Error Message */}
                {uploadFile.status === 'error' && uploadFile.error && (
                  <div className="mt-1 text-xs text-red-600">{uploadFile.error}</div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      {(allCompleted || hasErrors) && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <span className="text-xs text-gray-600">
            {files.filter((f) => f.status === 'completed').length} из {files.length} загружено
          </span>
          <button
            onClick={onClear}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
          >
            Очистить
          </button>
        </div>
      )}
    </div>
  )
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Б'
  const k = 1024
  const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}
