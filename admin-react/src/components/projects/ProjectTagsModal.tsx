import { useState, useEffect } from 'react'
import { X, Tag, Plus, Trash2, Check } from 'lucide-react'

interface ProjectTag {
  id: number
  name: string
  color: string
}

interface ProjectTagsModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
  onTagsUpdated: () => void
}

const PRESET_COLORS = [
  '#EF4444', // red
  '#F59E0B', // orange
  '#10B981', // green
  '#3B82F6', // blue
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#14B8A6', // teal
  '#6B7280', // gray
]

export const ProjectTagsModal = ({
  isOpen,
  onClose,
  projectId,
  projectName,
  onTagsUpdated,
}: ProjectTagsModalProps) => {
  const [availableTags, setAvailableTags] = useState<ProjectTag[]>([])
  const [projectTags, setProjectTags] = useState<ProjectTag[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [newTagColor, setNewTagColor] = useState(PRESET_COLORS[0])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadTags()
      loadProjectTags()
    }
  }, [isOpen, projectId])

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

  const loadTags = async () => {
    try {
      const response = await fetch('http://localhost:8001/admin/api/tags', {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setAvailableTags(data.tags || [])
      }
    } catch (err) {
      console.error('Error loading tags:', err)
    }
  }

  const loadProjectTags = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/tags`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setProjectTags(data.tags || [])
      }
    } catch (err) {
      console.error('Error loading project tags:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return

    try {
      const response = await fetch('http://localhost:8001/admin/api/tags', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          name: newTagName,
          color: newTagColor,
        }),
      })

      if (response.ok) {
        setNewTagName('')
        setNewTagColor(PRESET_COLORS[0])
        setIsCreating(false)
        await loadTags()
      }
    } catch (err) {
      console.error('Error creating tag:', err)
    }
  }

  const handleAddTag = async (tagId: number) => {
    if (!projectId) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/tags/${tagId}`,
        {
          method: 'POST',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadProjectTags()
        onTagsUpdated()
      }
    } catch (err) {
      console.error('Error adding tag:', err)
    }
  }

  const handleRemoveTag = async (tagId: number) => {
    if (!projectId) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/tags/${tagId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadProjectTags()
        onTagsUpdated()
      }
    } catch (err) {
      console.error('Error removing tag:', err)
    }
  }

  if (!isOpen) return null

  const projectTagIds = new Set(projectTags.map((t) => t.id))
  const availableToAdd = availableTags.filter((t) => !projectTagIds.has(t.id))

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-pink-600 to-rose-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Tag className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Теги проекта</h3>
              <p className="text-pink-100 text-sm mt-1">{projectName}</p>
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
        <div className="p-6 space-y-6 max-h-[600px] overflow-y-auto">
          {/* Current Tags */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Текущие теги</h4>
            {loading ? (
              <div className="text-sm text-gray-500">Загрузка...</div>
            ) : projectTags.length === 0 ? (
              <div className="text-sm text-gray-500 py-4 text-center border-2 border-dashed border-gray-300 rounded-lg">
                Теги не добавлены
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {projectTags.map((tag) => (
                  <div
                    key={tag.id}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full text-white text-sm font-medium shadow-md"
                    style={{ backgroundColor: tag.color }}
                  >
                    <span>{tag.name}</span>
                    <button
                      onClick={() => handleRemoveTag(tag.id)}
                      className="hover:bg-white/20 rounded-full p-0.5 transition-colors"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Add Tags */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Доступные теги</h4>
            {availableToAdd.length === 0 ? (
              <div className="text-sm text-gray-500 py-4 text-center border-2 border-dashed border-gray-300 rounded-lg">
                Все теги уже добавлены
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {availableToAdd.map((tag) => (
                  <button
                    key={tag.id}
                    onClick={() => handleAddTag(tag.id)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full text-white text-sm font-medium shadow-md hover:opacity-80 transition-opacity"
                    style={{ backgroundColor: tag.color }}
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>{tag.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Create New Tag */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Создать новый тег</h4>
            {!isCreating ? (
              <button
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-pink-600 to-rose-600 text-white rounded-lg hover:from-pink-700 hover:to-rose-700 transition-all font-semibold text-sm"
              >
                <Plus className="w-4 h-4" />
                Создать тег
              </button>
            ) : (
              <div className="bg-pink-50 border-2 border-pink-200 rounded-lg p-4 space-y-3">
                <input
                  type="text"
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  className="w-full px-4 py-2 border-2 border-pink-300 rounded-lg focus:border-pink-500 focus:ring-2 focus:ring-pink-200 outline-none"
                  placeholder="Название тега"
                  autoFocus
                />
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-2">Цвет:</label>
                  <div className="flex flex-wrap gap-2">
                    {PRESET_COLORS.map((color) => (
                      <button
                        key={color}
                        onClick={() => setNewTagColor(color)}
                        className={`w-8 h-8 rounded-full border-2 transition-all ${
                          newTagColor === color ? 'border-gray-900 scale-110' : 'border-gray-300'
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleCreateTag}
                    disabled={!newTagName.trim()}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                  >
                    <Check className="w-4 h-4" />
                    Создать
                  </button>
                  <button
                    onClick={() => {
                      setIsCreating(false)
                      setNewTagName('')
                      setNewTagColor(PRESET_COLORS[0])
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
