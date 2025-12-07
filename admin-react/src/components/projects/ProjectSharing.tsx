import { useState, useEffect } from 'react'
import { X, Share2, Copy, Mail, Link as LinkIcon, Users, Clock, Check, Trash2, Eye, Edit, Shield } from 'lucide-react'

interface SharedLink {
  id: string
  url: string
  token: string
  expiresAt: string | null
  accessLevel: 'view' | 'comment' | 'edit'
  password: string | null
  viewCount: number
  createdAt: string
  createdBy: string
}

interface SharedUser {
  id: number
  email: string
  firstName: string
  lastName?: string
  accessLevel: 'view' | 'comment' | 'edit'
  addedAt: string
  addedBy: string
}

interface ProjectSharingProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

export const ProjectSharing = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: ProjectSharingProps) => {
  const [sharedLinks, setSharedLinks] = useState<SharedLink[]>([])
  const [sharedUsers, setSharedUsers] = useState<SharedUser[]>([])
  const [newUserEmail, setNewUserEmail] = useState('')
  const [newUserAccessLevel, setNewUserAccessLevel] = useState<'view' | 'comment' | 'edit'>('view')
  const [linkAccessLevel, setLinkAccessLevel] = useState<'view' | 'comment' | 'edit'>('view')
  const [linkExpiryDays, setLinkExpiryDays] = useState<number | null>(7)
  const [linkPassword, setLinkPassword] = useState('')
  const [copiedLink, setCopiedLink] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'links' | 'users'>('links')

  useEffect(() => {
    if (isOpen && projectId) {
      loadSharing()
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

  const loadSharing = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/sharing`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setSharedLinks(data.links || [])
        setSharedUsers(data.users || [])
      } else {
        // Mock data
        setSharedLinks([
          {
            id: '1',
            url: 'https://crm.example.com/share/abc123def456',
            token: 'abc123def456',
            expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            accessLevel: 'view',
            password: null,
            viewCount: 15,
            createdAt: new Date().toISOString(),
            createdBy: 'admin',
          },
        ])
        setSharedUsers([
          {
            id: 1,
            email: 'manager@example.com',
            firstName: 'Иван',
            lastName: 'Менеджеров',
            accessLevel: 'comment',
            addedAt: new Date().toISOString(),
            addedBy: 'admin',
          },
        ])
      }
    } catch (err) {
      console.error('Error loading sharing:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateLink = async () => {
    if (!projectId) return

    try {
      const expiresAt = linkExpiryDays
        ? new Date(Date.now() + linkExpiryDays * 24 * 60 * 60 * 1000).toISOString()
        : null

      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/sharing/links`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          accessLevel: linkAccessLevel,
          expiresAt,
          password: linkPassword || null,
        }),
      })

      if (response.ok) {
        await loadSharing()
        setLinkPassword('')
      }
    } catch (err) {
      console.error('Error generating link:', err)
    }
  }

  const handleRevokeLink = async (linkId: string) => {
    if (!confirm('Отозвать ссылку? Она перестанет работать для всех.')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/sharing/links/${linkId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadSharing()
      }
    } catch (err) {
      console.error('Error revoking link:', err)
    }
  }

  const handleAddUser = async () => {
    if (!newUserEmail.trim() || !projectId) return

    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/sharing/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          email: newUserEmail,
          accessLevel: newUserAccessLevel,
        }),
      })

      if (response.ok) {
        setNewUserEmail('')
        await loadSharing()
      }
    } catch (err) {
      console.error('Error adding user:', err)
    }
  }

  const handleRemoveUser = async (userId: number) => {
    if (!confirm('Удалить доступ для этого пользователя?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/sharing/users/${userId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadSharing()
      }
    } catch (err) {
      console.error('Error removing user:', err)
    }
  }

  const handleChangeUserAccess = async (userId: number, newAccessLevel: 'view' | 'comment' | 'edit') => {
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/sharing/users/${userId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify({ accessLevel: newAccessLevel }),
        }
      )

      if (response.ok) {
        await loadSharing()
      }
    } catch (err) {
      console.error('Error changing access:', err)
    }
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedLink(id)
      setTimeout(() => setCopiedLink(null), 2000)
    })
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

  const getAccessLevelColor = (level: string) => {
    switch (level) {
      case 'view':
        return 'bg-blue-100 text-blue-700'
      case 'comment':
        return 'bg-green-100 text-green-700'
      case 'edit':
        return 'bg-orange-100 text-orange-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getAccessLevelIcon = (level: string) => {
    switch (level) {
      case 'view':
        return <Eye className="w-3.5 h-3.5" />
      case 'comment':
        return <Mail className="w-3.5 h-3.5" />
      case 'edit':
        return <Edit className="w-3.5 h-3.5" />
      default:
        return <Shield className="w-3.5 h-3.5" />
    }
  }

  const getAccessLevelName = (level: string) => {
    switch (level) {
      case 'view':
        return 'Просмотр'
      case 'comment':
        return 'Комментарии'
      case 'edit':
        return 'Редактирование'
      default:
        return level
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-600 to-cyan-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Share2 className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Совместный доступ</h3>
              <p className="text-teal-100 text-sm mt-1">{projectName}</p>
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

        {/* Tabs */}
        <div className="flex border-b border-gray-200 bg-gray-50 flex-shrink-0">
          <button
            onClick={() => setActiveTab('links')}
            className={`flex-1 px-6 py-3 font-semibold transition-colors flex items-center justify-center gap-2 ${
              activeTab === 'links'
                ? 'bg-white border-b-2 border-teal-600 text-teal-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <LinkIcon className="w-5 h-5" />
            Публичные ссылки ({sharedLinks.length})
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`flex-1 px-6 py-3 font-semibold transition-colors flex items-center justify-center gap-2 ${
              activeTab === 'users'
                ? 'bg-white border-b-2 border-teal-600 text-teal-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Users className="w-5 h-5" />
            Приглашенные пользователи ({sharedUsers.length})
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'links' ? (
            <div className="space-y-6">
              {/* Generate Link Form */}
              <div className="bg-teal-50 border-2 border-teal-200 rounded-xl p-4">
                <h4 className="font-bold text-gray-900 mb-4">Создать новую ссылку</h4>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Уровень доступа
                    </label>
                    <select
                      value={linkAccessLevel}
                      onChange={(e) => setLinkAccessLevel(e.target.value as any)}
                      className="w-full px-4 py-2 border-2 border-teal-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none"
                    >
                      <option value="view">Только просмотр</option>
                      <option value="comment">Просмотр и комментарии</option>
                      <option value="edit">Полное редактирование</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Срок действия
                    </label>
                    <select
                      value={linkExpiryDays || ''}
                      onChange={(e) => setLinkExpiryDays(e.target.value ? Number(e.target.value) : null)}
                      className="w-full px-4 py-2 border-2 border-teal-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none"
                    >
                      <option value="1">1 день</option>
                      <option value="7">7 дней</option>
                      <option value="30">30 дней</option>
                      <option value="">Без срока</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Пароль (опционально)
                    </label>
                    <input
                      type="text"
                      value={linkPassword}
                      onChange={(e) => setLinkPassword(e.target.value)}
                      className="w-full px-4 py-2 border-2 border-teal-300 rounded-lg focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none"
                      placeholder="Без пароля"
                    />
                  </div>
                </div>

                <button
                  onClick={handleGenerateLink}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-teal-600 to-cyan-600 text-white rounded-lg hover:from-teal-700 hover:to-cyan-700 transition-all font-semibold"
                >
                  <LinkIcon className="w-5 h-5" />
                  Создать ссылку
                </button>
              </div>

              {/* Existing Links */}
              {loading ? (
                <div className="text-center py-8 text-gray-500">Загрузка...</div>
              ) : sharedLinks.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Нет активных ссылок. Создайте первую!
                </div>
              ) : (
                <div className="space-y-3">
                  {sharedLinks.map((link) => (
                    <div
                      key={link.id}
                      className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-teal-400 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-semibold flex items-center gap-1 ${getAccessLevelColor(
                                link.accessLevel
                              )}`}
                            >
                              {getAccessLevelIcon(link.accessLevel)}
                              {getAccessLevelName(link.accessLevel)}
                            </span>
                            {link.password && (
                              <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-semibold flex items-center gap-1">
                                <Shield className="w-3.5 h-3.5" />
                                Защищена паролем
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-2 mb-2">
                            <input
                              type="text"
                              value={link.url}
                              readOnly
                              className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg text-sm font-mono"
                            />
                            <button
                              onClick={() => copyToClipboard(link.url, link.id)}
                              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors flex items-center gap-2 font-semibold"
                            >
                              {copiedLink === link.id ? (
                                <>
                                  <Check className="w-4 h-4" />
                                  Скопировано!
                                </>
                              ) : (
                                <>
                                  <Copy className="w-4 h-4" />
                                  Копировать
                                </>
                              )}
                            </button>
                          </div>

                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <div className="flex items-center gap-1">
                              <Eye className="w-3.5 h-3.5" />
                              <span>Просмотров: {link.viewCount}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />
                              <span>Создана: {formatDate(link.createdAt)}</span>
                            </div>
                            {link.expiresAt && (
                              <div className="flex items-center gap-1">
                                <Clock className="w-3.5 h-3.5" />
                                <span>Истекает: {formatDate(link.expiresAt)}</span>
                              </div>
                            )}
                          </div>
                        </div>

                        <button
                          onClick={() => handleRevokeLink(link.id)}
                          className="ml-4 p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                          title="Отозвать ссылку"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Add User Form */}
              <div className="bg-cyan-50 border-2 border-cyan-200 rounded-xl p-4">
                <h4 className="font-bold text-gray-900 mb-4">Пригласить пользователя</h4>

                <div className="flex gap-3">
                  <input
                    type="email"
                    value={newUserEmail}
                    onChange={(e) => setNewUserEmail(e.target.value)}
                    className="flex-1 px-4 py-2 border-2 border-cyan-300 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none"
                    placeholder="Email пользователя"
                  />
                  <select
                    value={newUserAccessLevel}
                    onChange={(e) => setNewUserAccessLevel(e.target.value as any)}
                    className="px-4 py-2 border-2 border-cyan-300 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none"
                  >
                    <option value="view">Просмотр</option>
                    <option value="comment">Комментарии</option>
                    <option value="edit">Редактирование</option>
                  </select>
                  <button
                    onClick={handleAddUser}
                    disabled={!newUserEmail.trim()}
                    className="px-6 py-2 bg-gradient-to-r from-teal-600 to-cyan-600 text-white rounded-lg hover:from-teal-700 hover:to-cyan-700 transition-all font-semibold disabled:opacity-50 flex items-center gap-2"
                  >
                    <Mail className="w-5 h-5" />
                    Пригласить
                  </button>
                </div>
              </div>

              {/* Existing Users */}
              {loading ? (
                <div className="text-center py-8 text-gray-500">Загрузка...</div>
              ) : sharedUsers.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Нет приглашенных пользователей
                </div>
              ) : (
                <div className="space-y-3">
                  {sharedUsers.map((user) => (
                    <div
                      key={user.id}
                      className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-cyan-400 transition-all"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-full flex items-center justify-center text-white font-bold">
                            {user.firstName[0]}
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">
                              {user.firstName} {user.lastName}
                            </div>
                            <div className="text-sm text-gray-600">{user.email}</div>
                            <div className="text-xs text-gray-500 mt-1">
                              Добавлен: {formatDate(user.addedAt)}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-3">
                          <select
                            value={user.accessLevel}
                            onChange={(e) => handleChangeUserAccess(user.id, e.target.value as any)}
                            className="px-3 py-2 border-2 border-cyan-300 rounded-lg focus:border-cyan-500 outline-none text-sm"
                          >
                            <option value="view">Просмотр</option>
                            <option value="comment">Комментарии</option>
                            <option value="edit">Редактирование</option>
                          </select>

                          <button
                            onClick={() => handleRemoveUser(user.id)}
                            className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                            title="Удалить доступ"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end flex-shrink-0">
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
