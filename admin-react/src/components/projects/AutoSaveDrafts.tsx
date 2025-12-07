import { useState, useEffect, useCallback } from 'react'
import { Save, Trash2, Clock, FileText, X, AlertCircle } from 'lucide-react'

interface Draft {
  id: string
  name: string
  description: string
  client_id: number | null
  project_type: string
  project_cost: number
  deadline: string
  assigned_to_id: number | null
  status: string
  savedAt: string
  autoSaved: boolean
}

interface AutoSaveDraftsProps {
  isOpen: boolean
  onClose: () => void
  onLoadDraft: (draft: Draft) => void
  currentFormData?: any
}

export const AutoSaveDrafts = ({
  isOpen,
  onClose,
  onLoadDraft,
  currentFormData,
}: AutoSaveDraftsProps) => {
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [selectedDraft, setSelectedDraft] = useState<Draft | null>(null)
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)
  const [autoSaveInterval, setAutoSaveInterval] = useState(30) // seconds

  useEffect(() => {
    if (isOpen) {
      loadDrafts()
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

  // Auto-save mechanism
  useEffect(() => {
    if (!autoSaveEnabled || !currentFormData) return

    const interval = setInterval(() => {
      if (isFormValid(currentFormData)) {
        autoSaveDraft(currentFormData)
      }
    }, autoSaveInterval * 1000)

    return () => clearInterval(interval)
  }, [autoSaveEnabled, autoSaveInterval, currentFormData])

  const isFormValid = (formData: any) => {
    return formData && formData.name && formData.name.trim().length > 0
  }

  const loadDrafts = async () => {
    try {
      // Try to load from backend
      const response = await fetch('http://localhost:8001/admin/api/drafts', {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setDrafts(data.drafts || [])
      } else {
        // Load from localStorage
        loadFromLocalStorage()
      }
    } catch (err) {
      console.error('Error loading drafts:', err)
      loadFromLocalStorage()
    }
  }

  const loadFromLocalStorage = () => {
    const stored = localStorage.getItem('project_drafts')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setDrafts(parsed)
      } catch (err) {
        console.error('Error parsing drafts:', err)
      }
    }
  }

  const saveToLocalStorage = (updatedDrafts: Draft[]) => {
    localStorage.setItem('project_drafts', JSON.stringify(updatedDrafts))
  }

  const autoSaveDraft = useCallback(
    async (formData: any) => {
      const draftId = 'auto_' + Date.now()
      const newDraft: Draft = {
        id: draftId,
        name: formData.name || 'Без названия',
        description: formData.description || '',
        client_id: formData.client_id || null,
        project_type: formData.project_type || '',
        project_cost: formData.project_cost || 0,
        deadline: formData.deadline || '',
        assigned_to_id: formData.assigned_to_id || null,
        status: formData.status || 'planned',
        savedAt: new Date().toISOString(),
        autoSaved: true,
      }

      try {
        const response = await fetch('http://localhost:8001/admin/api/drafts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify(newDraft),
        })

        if (response.ok) {
          await loadDrafts()
        } else {
          // Save to localStorage
          const updatedDrafts = [...drafts, newDraft]
          setDrafts(updatedDrafts)
          saveToLocalStorage(updatedDrafts)
        }
      } catch (err) {
        console.error('Error auto-saving draft:', err)
        const updatedDrafts = [...drafts, newDraft]
        setDrafts(updatedDrafts)
        saveToLocalStorage(updatedDrafts)
      }
    },
    [drafts]
  )

  const handleManualSave = async () => {
    if (!currentFormData || !isFormValid(currentFormData)) return

    const draftId = 'manual_' + Date.now()
    const newDraft: Draft = {
      id: draftId,
      name: currentFormData.name || 'Без названия',
      description: currentFormData.description || '',
      client_id: currentFormData.client_id || null,
      project_type: currentFormData.project_type || '',
      project_cost: currentFormData.project_cost || 0,
      deadline: currentFormData.deadline || '',
      assigned_to_id: currentFormData.assigned_to_id || null,
      status: currentFormData.status || 'planned',
      savedAt: new Date().toISOString(),
      autoSaved: false,
    }

    try {
      const response = await fetch('http://localhost:8001/admin/api/drafts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(newDraft),
      })

      if (response.ok) {
        await loadDrafts()
      } else {
        const updatedDrafts = [...drafts, newDraft]
        setDrafts(updatedDrafts)
        saveToLocalStorage(updatedDrafts)
      }
    } catch (err) {
      console.error('Error saving draft:', err)
      const updatedDrafts = [...drafts, newDraft]
      setDrafts(updatedDrafts)
      saveToLocalStorage(updatedDrafts)
    }
  }

  const handleDeleteDraft = async (draftId: string) => {
    if (!confirm('Удалить черновик?')) return

    try {
      const response = await fetch(`http://localhost:8001/admin/api/drafts/${draftId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        await loadDrafts()
      } else {
        const updatedDrafts = drafts.filter((d) => d.id !== draftId)
        setDrafts(updatedDrafts)
        saveToLocalStorage(updatedDrafts)
      }
    } catch (err) {
      console.error('Error deleting draft:', err)
      const updatedDrafts = drafts.filter((d) => d.id !== draftId)
      setDrafts(updatedDrafts)
      saveToLocalStorage(updatedDrafts)
    }
  }

  const handleLoadDraft = (draft: Draft) => {
    onLoadDraft(draft)
    onClose()
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const formatTimeDiff = (dateString: string) => {
    const now = Date.now()
    const then = new Date(dateString).getTime()
    const diff = now - then

    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'только что'
    if (minutes < 60) return `${minutes} мин назад`
    if (hours < 24) return `${hours} ч назад`
    return `${days} дн назад`
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Save className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Черновики проектов</h3>
              <p className="text-purple-100 text-sm mt-1">
                Автосохранение и управление черновиками
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

        {/* Settings Panel */}
        <div className="px-6 py-4 bg-purple-50 border-b border-purple-200 flex-shrink-0">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoSaveEnabled}
                  onChange={(e) => setAutoSaveEnabled(e.target.checked)}
                  className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
                />
                <span className="text-sm font-semibold text-gray-700">
                  Автосохранение
                </span>
              </label>

              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-600" />
                <span className="text-sm text-gray-600">Интервал:</span>
                <select
                  value={autoSaveInterval}
                  onChange={(e) => setAutoSaveInterval(Number(e.target.value))}
                  className="px-3 py-1 text-sm border-2 border-purple-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none"
                  disabled={!autoSaveEnabled}
                >
                  <option value={10}>10 сек</option>
                  <option value={30}>30 сек</option>
                  <option value={60}>1 мин</option>
                  <option value={120}>2 мин</option>
                  <option value={300}>5 мин</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleManualSave}
              disabled={!currentFormData || !isFormValid(currentFormData)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              Сохранить сейчас
            </button>
          </div>

          {autoSaveEnabled && (
            <div className="mt-2 flex items-center gap-2 text-xs text-purple-700">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Черновики сохраняются автоматически каждые {autoSaveInterval} секунд</span>
            </div>
          )}
        </div>

        {/* Drafts List */}
        <div className="flex-1 overflow-y-auto p-6">
          {drafts.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg font-semibold">Нет сохраненных черновиков</p>
              <p className="text-gray-400 text-sm mt-2">
                Черновики будут появляться здесь автоматически
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {drafts.map((draft) => (
                <div
                  key={draft.id}
                  className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-purple-400 hover:shadow-lg transition-all cursor-pointer group"
                  onClick={() => setSelectedDraft(draft)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-900 text-lg mb-1 line-clamp-1">
                        {draft.name}
                      </h4>
                      <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                        {draft.description || 'Без описания'}
                      </p>
                    </div>
                    {draft.autoSaved && (
                      <span className="ml-2 px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-semibold rounded-full">
                        Авто
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div className="text-xs text-gray-600">
                      <span className="font-semibold">Тип:</span> {draft.project_type || '—'}
                    </div>
                    <div className="text-xs text-gray-600">
                      <span className="font-semibold">Стоимость:</span>{' '}
                      {draft.project_cost ? `${draft.project_cost.toLocaleString()} ₽` : '—'}
                    </div>
                    <div className="text-xs text-gray-600">
                      <span className="font-semibold">Дедлайн:</span>{' '}
                      {draft.deadline ? new Date(draft.deadline).toLocaleDateString('ru-RU') : '—'}
                    </div>
                    <div className="text-xs text-gray-600">
                      <span className="font-semibold">Статус:</span> {draft.status || '—'}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{formatTimeDiff(draft.savedAt)}</span>
                      <span className="text-gray-400">({formatDate(draft.savedAt)})</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleLoadDraft(draft)
                        }}
                        className="px-3 py-1 bg-purple-600 text-white text-xs font-semibold rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        Загрузить
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteDraft(draft.id)
                        }}
                        className="p-1 text-red-600 hover:bg-red-100 rounded transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            Всего черновиков: <span className="font-bold text-purple-600">{drafts.length}</span>
          </div>
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
