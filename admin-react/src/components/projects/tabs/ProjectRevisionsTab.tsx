import { useState, useEffect } from 'react'
import { Plus, GitBranch, Clock, CheckCircle, AlertCircle } from 'lucide-react'

interface Revision {
  id: number
  title: string
  description: string
  status: string
  created_at: string
  resolved_at: string | null
}

interface ProjectRevisionsTabProps {
  projectId: number
  onCountChange?: (count: number) => void
  onRefresh?: () => void
}

export const ProjectRevisionsTab = ({ projectId, onCountChange, onRefresh }: ProjectRevisionsTabProps) => {
  const [revisions, setRevisions] = useState<Revision[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRevisions()
  }, [projectId])

  const loadRevisions = async () => {
    try {
      setLoading(true)
      // TODO: Загрузить правки через API (Task с type=REVISION)
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/revisions`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        const revisionsList = data.revisions || []
        setRevisions(revisionsList)
        if (onCountChange) {
          onCountChange(revisionsList.length)
        }
      } else {
        setRevisions([])
        if (onCountChange) {
          onCountChange(0)
        }
      }
    } catch (err) {
      console.error('Ошибка загрузки правок:', err)
      setRevisions([])
      if (onCountChange) {
        onCountChange(0)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">Правки по проекту</h3>
        <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-medium shadow-md">
          <Plus className="w-4 h-4" />
          Добавить правку
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      ) : revisions.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <GitBranch className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Правок пока нет</p>
          <p className="text-gray-400 text-sm mt-1">Клиент может добавить правки через мини-апп или чат</p>
        </div>
      ) : (
        <div className="space-y-3">
          {revisions.map((revision) => (
            <div
              key={revision.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-1">{revision.title}</h4>
                  {revision.description && <p className="text-sm text-gray-600">{revision.description}</p>}
                </div>
                {revision.status === 'completed' ? (
                  <span className="flex items-center gap-1 text-green-600 text-sm font-medium">
                    <CheckCircle className="w-4 h-4" />
                    Готово
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-yellow-600 text-sm font-medium">
                    <Clock className="w-4 h-4" />
                    В работе
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>{new Date(revision.created_at).toLocaleDateString('ru-RU')}</span>
                <span className="text-xs text-gray-400">#{revision.id}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
