import { Server, Link, Key, Database, Copy, ExternalLink, Edit } from 'lucide-react'
import { useState } from 'react'

interface ProjectMetadata {
  test_link: string | null
  bot_token: string | null
  bot_username: string | null
  telegram_channel_id: string | null
  timeweb_login: string | null
  timeweb_password: string | null
  timeweb_server_id: string | null
}

interface ProjectHostingTabProps {
  projectId: number
  projectMetadata: ProjectMetadata | null
}

const copyToClipboard = async (text: string, label: string) => {
  try {
    await navigator.clipboard.writeText(text)
    alert(`${label} скопировано в буфер обмена`)
  } catch (err) {
    alert('Ошибка копирования')
  }
}

const maskPassword = (password: string) => {
  if (password.length <= 4) return '••••'
  return password.substring(0, 2) + '••••' + password.substring(password.length - 2)
}

export const ProjectHostingTab = ({ projectId, projectMetadata }: ProjectHostingTabProps) => {
  const [showPasswords, setShowPasswords] = useState(false)

  const hasHostingInfo =
    projectMetadata &&
    (projectMetadata.timeweb_login || projectMetadata.timeweb_password || projectMetadata.timeweb_server_id)

  const hasBotInfo =
    projectMetadata && (projectMetadata.bot_token || projectMetadata.bot_username || projectMetadata.telegram_channel_id)

  const hasTestLink = projectMetadata && projectMetadata.test_link

  return (
    <div className="p-6 space-y-6">
      {/* Тестовая ссылка */}
      {hasTestLink && (
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Link className="w-5 h-5 text-blue-600" />
            <h4 className="font-semibold text-blue-900">Тестовая ссылка</h4>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={projectMetadata.test_link!}
              readOnly
              className="flex-1 px-3 py-2 bg-white border border-blue-300 rounded-lg text-sm font-mono"
            />
            <button
              onClick={() => window.open(projectMetadata.test_link!, '_blank')}
              className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              title="Открыть"
            >
              <ExternalLink className="w-5 h-5" />
            </button>
            <button
              onClick={() => copyToClipboard(projectMetadata.test_link!, 'Ссылка')}
              className="p-2 bg-white text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
              title="Копировать"
            >
              <Copy className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Telegram Bot Info */}
      {hasBotInfo && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-md">
          <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-gray-200 flex items-center justify-between rounded-t-lg">
            <h4 className="font-semibold text-gray-900 flex items-center gap-2">
              <Server className="w-5 h-5 text-purple-600" />
              Telegram Bot
            </h4>
            <button className="p-1 text-gray-600 hover:bg-white/50 rounded transition-colors">
              <Edit className="w-4 h-4" />
            </button>
          </div>
          <div className="p-4 space-y-4">
            {projectMetadata.bot_username && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username бота</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={`@${projectMetadata.bot_username}`}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                  />
                  <button
                    onClick={() => copyToClipboard(projectMetadata.bot_username!, 'Username')}
                    className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {projectMetadata.bot_token && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Токен бота</label>
                <div className="flex items-center gap-2">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    value={projectMetadata.bot_token}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                  />
                  <button
                    onClick={() => copyToClipboard(projectMetadata.bot_token!, 'Токен')}
                    className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {projectMetadata.telegram_channel_id && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ID канала/чата</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={projectMetadata.telegram_channel_id}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                  />
                  <button
                    onClick={() => copyToClipboard(projectMetadata.telegram_channel_id!, 'Channel ID')}
                    className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Hosting Info (Timeweb) */}
      {hasHostingInfo && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-md">
          <div className="px-4 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 flex items-center justify-between rounded-t-lg">
            <h4 className="font-semibold text-gray-900 flex items-center gap-2">
              <Database className="w-5 h-5 text-green-600" />
              Хостинг (Timeweb)
            </h4>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={showPasswords}
                  onChange={(e) => setShowPasswords(e.target.checked)}
                  className="rounded text-purple-600 focus:ring-purple-500"
                />
                <span className="text-gray-600">Показать пароли</span>
              </label>
              <button className="p-1 text-gray-600 hover:bg-white/50 rounded transition-colors">
                <Edit className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="p-4 space-y-4">
            {projectMetadata.timeweb_server_id && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ID сервера</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={projectMetadata.timeweb_server_id}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                  />
                  <button
                    onClick={() => copyToClipboard(projectMetadata.timeweb_server_id!, 'Server ID')}
                    className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {projectMetadata.timeweb_login && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Логин</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={projectMetadata.timeweb_login}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                  />
                  <button
                    onClick={() => copyToClipboard(projectMetadata.timeweb_login!, 'Логин')}
                    className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {projectMetadata.timeweb_password && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
                <div className="flex items-center gap-2">
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    value={projectMetadata.timeweb_password}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono"
                  />
                  <button
                    onClick={() => copyToClipboard(projectMetadata.timeweb_password!, 'Пароль')}
                    className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!hasTestLink && !hasBotInfo && !hasHostingInfo && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Server className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Информация о хостинге не указана</p>
          <p className="text-gray-400 text-sm mt-1">
            Добавьте данные о хостинге, боте и тестовых ссылках для быстрого доступа
          </p>
          <button className="mt-4 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-medium shadow-md">
            Добавить информацию
          </button>
        </div>
      )}
    </div>
  )
}
