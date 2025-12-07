import { useState, useEffect, useRef } from 'react'
import { X, Send, MessageCircle, User, Trash2, Edit2, Check } from 'lucide-react'

interface Comment {
  id: number
  text: string
  user: { first_name: string; username?: string }
  created_at: string
  updated_at?: string
}

interface ProjectCommentsModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

export const ProjectCommentsModal = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: ProjectCommentsModalProps) => {
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editText, setEditText] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const commentsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen && projectId) {
      loadComments()
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

  useEffect(() => {
    scrollToBottom()
  }, [comments])

  const scrollToBottom = () => {
    commentsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadComments = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/comments`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setComments(data.comments || [])
      }
    } catch (err) {
      console.error('Error loading comments:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSendComment = async () => {
    if (!newComment.trim() || !projectId) return

    setSending(true)
    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({ text: newComment }),
      })

      if (response.ok) {
        setNewComment('')
        await loadComments()
        textareaRef.current?.focus()
      }
    } catch (err) {
      console.error('Error sending comment:', err)
    } finally {
      setSending(false)
    }
  }

  const handleEditComment = async (commentId: number) => {
    if (!editText.trim()) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/comments/${commentId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify({ text: editText }),
        }
      )

      if (response.ok) {
        setEditingId(null)
        setEditText('')
        await loadComments()
      }
    } catch (err) {
      console.error('Error editing comment:', err)
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Удалить комментарий?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/comments/${commentId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadComments()
      }
    } catch (err) {
      console.error('Error deleting comment:', err)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSendComment()
    }
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

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Комментарии</h3>
              <p className="text-blue-100 text-sm mt-1">{projectName}</p>
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

        {/* Comments List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка комментариев...</div>
          ) : comments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Комментариев пока нет. Напишите первый!
            </div>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center text-white font-bold">
                    <User className="w-5 h-5" />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <span className="font-semibold text-gray-900">
                          {comment.user.first_name || comment.user.username}
                        </span>
                        <span className="text-xs text-gray-500 ml-2">
                          {formatDate(comment.created_at)}
                        </span>
                        {comment.updated_at && comment.updated_at !== comment.created_at && (
                          <span className="text-xs text-gray-400 ml-1">(изменено)</span>
                        )}
                      </div>

                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => {
                            setEditingId(comment.id)
                            setEditText(comment.text)
                          }}
                          className="p-1 text-blue-600 hover:bg-blue-100 rounded transition-colors"
                          title="Редактировать"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="p-1 text-red-600 hover:bg-red-100 rounded transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {editingId === comment.id ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          className="flex-1 px-3 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
                          autoFocus
                        />
                        <button
                          onClick={() => handleEditComment(comment.id)}
                          className="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setEditingId(null)
                            setEditText('')
                          }}
                          className="p-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <p className="text-gray-700 whitespace-pre-wrap">{comment.text}</p>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={commentsEndRef} />
        </div>

        {/* Input Form */}
        <div className="px-6 py-4 bg-white border-t border-gray-200 flex-shrink-0">
          <div className="flex items-end gap-3">
            <textarea
              ref={textareaRef}
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              onKeyDown={handleKeyPress}
              className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none transition-all"
              placeholder="Напишите комментарий... (Ctrl+Enter для отправки)"
              rows={2}
              disabled={sending}
            />
            <button
              onClick={handleSendComment}
              disabled={!newComment.trim() || sending}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              {sending ? 'Отправка...' : 'Отправить'}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Нажмите <kbd className="px-1 py-0.5 bg-gray-200 rounded">Ctrl+Enter</kbd> для отправки
          </p>
        </div>
      </div>
    </div>
  )
}
