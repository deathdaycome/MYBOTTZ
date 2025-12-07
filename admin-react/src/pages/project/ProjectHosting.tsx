/**
 * Вкладка "Хостинг" проекта
 * Информация о хостинге, домене, FTP
 */

import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Server, Globe, Key, HardDrive, Loader2, ExternalLink, Copy, CheckCircle } from 'lucide-react'
import axiosInstance from '../../services/api'

interface Project {
  id: number
  title: string
}

interface HostingInfo {
  id: number
  server_id: number
  domain?: string
  ftp_login?: string
  status: string
  created_at: string
  expires_at?: string
  server_name?: string
  ip_address?: string
}

interface OutletContext {
  project: Project
}

export const ProjectHosting = () => {
  const { project } = useOutletContext<OutletContext>()
  const [hosting, setHosting] = useState<HostingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copiedField, setCopiedField] = useState<string | null>(null)

  // Загрузка информации о хостинге
  useEffect(() => {
    loadHosting()
  }, [project.id])

  const loadHosting = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(`/admin/api/projects/${project.id}/hosting`)

      if (response.data.success) {
        setHosting(response.data.hosting)
      }
      setError(null)
    } catch (err: any) {
      console.error('Error loading hosting:', err)
      setError('Ошибка загрузки информации о хостинге')
    } finally {
      setLoading(false)
    }
  }

  // Копирование в буфер обмена
  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  // Статусы хостинга
  const hostingStatuses: Record<string, { label: string; color: string }> = {
    active: { label: 'Активен', color: 'green' },
    suspended: { label: 'Приостановлен', color: 'yellow' },
    expired: { label: 'Истек', color: 'red' },
    pending: { label: 'Ожидает', color: 'blue' },
  }

  const getHostingStatus = (status: string) => {
    return hostingStatuses[status] || hostingStatuses.pending
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
      <h2 className="text-xl font-bold text-gray-900 dark:text-white">Хостинг проекта</h2>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {hosting ? (
        <>
          {/* Статус хостинга */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Статус хостинга</h3>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium bg-${
                  getHostingStatus(hosting.status).color
                }-100 text-${getHostingStatus(hosting.status).color}-700 dark:bg-${
                  getHostingStatus(hosting.status).color
                }-900/30 dark:text-${getHostingStatus(hosting.status).color}-400`}
              >
                {getHostingStatus(hosting.status).label}
              </span>
            </div>

            {hosting.expires_at && (
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <span className="font-medium">Истекает:</span>{' '}
                {new Date(hosting.expires_at).toLocaleDateString('ru-RU')}
              </div>
            )}
          </div>

          {/* Карточки с информацией */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Домен */}
            <div className="bg-gradient-to-br from-sky-50 to-sky-100 dark:from-sky-900/20 dark:to-sky-800/20 rounded-lg p-6 border border-sky-200 dark:border-sky-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-sky-500 rounded-lg">
                  <Globe className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-sky-900 dark:text-sky-100">Домен</h3>
              </div>

              {hosting.domain ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <p className="text-gray-900 dark:text-white font-mono text-sm">{hosting.domain}</p>
                    <button
                      onClick={() => copyToClipboard(hosting.domain!, 'domain')}
                      className="p-1 hover:bg-sky-200 dark:hover:bg-sky-800 rounded transition-colors"
                      title="Копировать"
                    >
                      {copiedField === 'domain' ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4 text-sky-600" />
                      )}
                    </button>
                    <a
                      href={`https://${hosting.domain}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 hover:bg-sky-200 dark:hover:bg-sky-800 rounded transition-colors"
                      title="Открыть в новой вкладке"
                    >
                      <ExternalLink className="w-4 h-4 text-sky-600" />
                    </a>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-sm">Домен не настроен</p>
              )}
            </div>

            {/* Сервер */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-6 border border-purple-200 dark:border-purple-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-purple-500 rounded-lg">
                  <Server className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100">Сервер</h3>
              </div>

              {hosting.server_name ? (
                <div className="space-y-2">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    <span className="font-medium">Название:</span> {hosting.server_name}
                  </p>
                  {hosting.ip_address && (
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-medium">IP:</span>{' '}
                        <span className="font-mono">{hosting.ip_address}</span>
                      </p>
                      <button
                        onClick={() => copyToClipboard(hosting.ip_address!, 'ip')}
                        className="p-1 hover:bg-purple-200 dark:hover:bg-purple-800 rounded transition-colors"
                        title="Копировать IP"
                      >
                        {copiedField === 'ip' ? (
                          <CheckCircle className="w-3 h-3 text-green-600" />
                        ) : (
                          <Copy className="w-3 h-3 text-purple-600" />
                        )}
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-sm">Сервер не привязан</p>
              )}
            </div>

            {/* FTP доступ */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg p-6 border border-orange-200 dark:border-orange-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-orange-500 rounded-lg">
                  <Key className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-orange-900 dark:text-orange-100">FTP доступ</h3>
              </div>

              {hosting.ftp_login ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-medium">Логин:</span>{' '}
                      <span className="font-mono">{hosting.ftp_login}</span>
                    </p>
                    <button
                      onClick={() => copyToClipboard(hosting.ftp_login!, 'ftp')}
                      className="p-1 hover:bg-orange-200 dark:hover:bg-orange-800 rounded transition-colors"
                      title="Копировать логин"
                    >
                      {copiedField === 'ftp' ? (
                        <CheckCircle className="w-3 h-3 text-green-600" />
                      ) : (
                        <Copy className="w-3 h-3 text-orange-600" />
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Пароль хранится в безопасном месте
                  </p>
                </div>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-sm">FTP не настроен</p>
              )}
            </div>

            {/* База данных */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-6 border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-green-500 rounded-lg">
                  <HardDrive className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">База данных</h3>
              </div>

              <p className="text-gray-500 dark:text-gray-400 text-sm">
                Информация о БД будет добавлена
              </p>
            </div>
          </div>

          {/* Дополнительная информация */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              <strong>Создан:</strong> {new Date(hosting.created_at).toLocaleDateString('ru-RU')}
            </p>
          </div>
        </>
      ) : (
        /* Пустое состояние */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-sky-50 to-sky-100 dark:from-sky-900/20 dark:to-sky-800/20 rounded-lg p-6 border border-sky-200 dark:border-sky-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-sky-500 rounded-lg">
                <Globe className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-sky-900 dark:text-sky-100">Домен</h3>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">Домен не настроен</p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-6 border border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-purple-500 rounded-lg">
                <Server className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100">Сервер</h3>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">Сервер не привязан</p>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg p-6 border border-orange-200 dark:border-orange-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-orange-500 rounded-lg">
                <Key className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-orange-900 dark:text-orange-100">FTP доступ</h3>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">FTP не настроен</p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-6 border border-green-200 dark:border-green-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-green-500 rounded-lg">
                <HardDrive className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">База данных</h3>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">БД не создана</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectHosting
