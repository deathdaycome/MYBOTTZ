import { useState } from 'react'
import { X, Code, Copy, Check, ChevronDown, ChevronRight } from 'lucide-react'

interface APIEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  path: string
  description: string
  parameters?: Array<{
    name: string
    type: string
    required: boolean
    description: string
  }>
  requestBody?: {
    contentType: string
    example: string
  }
  response?: {
    statusCode: number
    contentType: string
    example: string
  }
  authentication: boolean
}

interface APIDocumentationProps {
  isOpen: boolean
  onClose: () => void
}

const API_ENDPOINTS: APIEndpoint[] = [
  {
    method: 'GET',
    path: '/admin/api/projects',
    description: 'Получить список всех проектов',
    parameters: [
      {
        name: 'archived',
        type: 'boolean',
        required: false,
        description: 'Включить архивные проекты',
      },
      {
        name: 'status',
        type: 'string',
        required: false,
        description: 'Фильтр по статусу',
      },
    ],
    response: {
      statusCode: 200,
      contentType: 'application/json',
      example: JSON.stringify(
        {
          projects: [
            {
              id: 1,
              title: 'Проект 1',
              status: 'in_progress',
              estimated_cost: 100000,
            },
          ],
        },
        null,
        2
      ),
    },
    authentication: true,
  },
  {
    method: 'GET',
    path: '/admin/api/projects/{id}',
    description: 'Получить информацию о проекте',
    parameters: [
      {
        name: 'id',
        type: 'integer',
        required: true,
        description: 'ID проекта',
      },
    ],
    response: {
      statusCode: 200,
      contentType: 'application/json',
      example: JSON.stringify(
        {
          id: 1,
          title: 'Проект 1',
          description: 'Описание проекта',
          status: 'in_progress',
          estimated_cost: 100000,
          created_at: '2024-01-01T00:00:00Z',
        },
        null,
        2
      ),
    },
    authentication: true,
  },
  {
    method: 'POST',
    path: '/admin/api/projects',
    description: 'Создать новый проект',
    requestBody: {
      contentType: 'application/json',
      example: JSON.stringify(
        {
          title: 'Новый проект',
          description: 'Описание проекта',
          project_type: 'Разработка',
          status: 'new',
          complexity: 'medium',
          estimated_cost: 100000,
        },
        null,
        2
      ),
    },
    response: {
      statusCode: 201,
      contentType: 'application/json',
      example: JSON.stringify(
        {
          id: 1,
          title: 'Новый проект',
          status: 'new',
          created_at: '2024-01-01T00:00:00Z',
        },
        null,
        2
      ),
    },
    authentication: true,
  },
  {
    method: 'PUT',
    path: '/admin/api/projects/{id}',
    description: 'Обновить проект',
    parameters: [
      {
        name: 'id',
        type: 'integer',
        required: true,
        description: 'ID проекта',
      },
    ],
    requestBody: {
      contentType: 'application/json',
      example: JSON.stringify(
        {
          title: 'Обновленное название',
          status: 'in_progress',
        },
        null,
        2
      ),
    },
    response: {
      statusCode: 200,
      contentType: 'application/json',
      example: JSON.stringify(
        {
          success: true,
          message: 'Проект обновлен',
        },
        null,
        2
      ),
    },
    authentication: true,
  },
  {
    method: 'DELETE',
    path: '/admin/api/projects/{id}',
    description: 'Удалить проект',
    parameters: [
      {
        name: 'id',
        type: 'integer',
        required: true,
        description: 'ID проекта',
      },
    ],
    response: {
      statusCode: 204,
      contentType: 'application/json',
      example: JSON.stringify(
        {
          success: true,
          message: 'Проект удален',
        },
        null,
        2
      ),
    },
    authentication: true,
  },
]

export const APIDocumentation = ({ isOpen, onClose }: APIDocumentationProps) => {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [copiedPath, setCopiedPath] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const toggleExpand = (path: string) => {
    const newExpanded = new Set(expandedIds)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedIds(newExpanded)
  }

  const copyToClipboard = (text: string, path: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedPath(path)
      setTimeout(() => setCopiedPath(null), 2000)
    })
  }

  const getMethodColor = (method: string) => {
    const colors = {
      GET: 'bg-blue-100 text-blue-700',
      POST: 'bg-green-100 text-green-700',
      PUT: 'bg-yellow-100 text-yellow-700',
      DELETE: 'bg-red-100 text-red-700',
      PATCH: 'bg-purple-100 text-purple-700',
    }
    return colors[method as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-600 to-blue-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Code className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">API Документация</h3>
              <p className="text-cyan-100 text-sm mt-1">
                Справочник по REST API эндпоинтам
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

        {/* Navigation */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-700">Категории:</span>
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Все
            </button>
            <button
              onClick={() => setSelectedCategory('projects')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === 'projects'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Проекты
            </button>
            <button
              onClick={() => setSelectedCategory('tasks')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === 'tasks'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Задачи
            </button>
            <button
              onClick={() => setSelectedCategory('users')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === 'users'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Пользователи
            </button>
          </div>
        </div>

        {/* API Info */}
        <div className="px-6 py-4 bg-blue-50 border-b border-blue-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-semibold text-gray-700">Base URL:</span>
              <code className="ml-2 px-2 py-1 bg-white border border-gray-300 rounded text-xs">
                http://localhost:8001
              </code>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Authentication:</span>
              <code className="ml-2 px-2 py-1 bg-white border border-gray-300 rounded text-xs">
                Basic Auth (admin:qwerty123)
              </code>
            </div>
          </div>
        </div>

        {/* Endpoints List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {API_ENDPOINTS.map((endpoint, index) => {
              const isExpanded = expandedIds.has(endpoint.path)
              const isCopied = copiedPath === endpoint.path

              return (
                <div
                  key={index}
                  className="bg-white border-2 border-gray-200 rounded-xl overflow-hidden"
                >
                  {/* Endpoint Header */}
                  <button
                    onClick={() => toggleExpand(endpoint.path)}
                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      {isExpanded ? (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      )}

                      <span
                        className={`px-3 py-1 rounded-lg text-xs font-bold ${getMethodColor(
                          endpoint.method
                        )}`}
                      >
                        {endpoint.method}
                      </span>

                      <code className="text-sm font-mono text-gray-900">{endpoint.path}</code>

                      {endpoint.authentication && (
                        <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs font-medium">
                          🔒 Auth
                        </span>
                      )}
                    </div>

                    <div className="text-sm text-gray-600">{endpoint.description}</div>
                  </button>

                  {/* Endpoint Details */}
                  {isExpanded && (
                    <div className="px-4 pb-4 pt-2 bg-gray-50 border-t border-gray-200">
                      {/* Parameters */}
                      {endpoint.parameters && endpoint.parameters.length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-bold text-gray-900 mb-2">Параметры:</h5>
                          <div className="space-y-2">
                            {endpoint.parameters.map((param, i) => (
                              <div key={i} className="bg-white p-3 rounded-lg border border-gray-200">
                                <div className="flex items-center gap-2 mb-1">
                                  <code className="text-sm font-mono font-bold text-blue-600">
                                    {param.name}
                                  </code>
                                  <span className="text-xs text-gray-500">{param.type}</span>
                                  {param.required && (
                                    <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-bold">
                                      required
                                    </span>
                                  )}
                                </div>
                                <div className="text-sm text-gray-600">{param.description}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Request Body */}
                      {endpoint.requestBody && (
                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <h5 className="text-sm font-bold text-gray-900">Request Body:</h5>
                            <button
                              onClick={() =>
                                copyToClipboard(endpoint.requestBody!.example, endpoint.path)
                              }
                              className="p-1 hover:bg-gray-200 rounded transition-colors"
                              title="Копировать"
                            >
                              {isCopied ? (
                                <Check className="w-4 h-4 text-green-600" />
                              ) : (
                                <Copy className="w-4 h-4 text-gray-600" />
                              )}
                            </button>
                          </div>
                          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                            <pre className="text-xs font-mono">{endpoint.requestBody.example}</pre>
                          </div>
                        </div>
                      )}

                      {/* Response */}
                      {endpoint.response && (
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <h5 className="text-sm font-bold text-gray-900">
                              Response ({endpoint.response.statusCode}):
                            </h5>
                            <button
                              onClick={() =>
                                copyToClipboard(endpoint.response!.example, endpoint.path + '-response')
                              }
                              className="p-1 hover:bg-gray-200 rounded transition-colors"
                              title="Копировать"
                            >
                              {copiedPath === endpoint.path + '-response' ? (
                                <Check className="w-4 h-4 text-green-600" />
                              ) : (
                                <Copy className="w-4 h-4 text-gray-600" />
                              )}
                            </button>
                          </div>
                          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                            <pre className="text-xs font-mono">{endpoint.response.example}</pre>
                          </div>
                        </div>
                      )}

                      {/* curl Example */}
                      <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="text-sm font-bold text-gray-900">cURL Example:</h5>
                          <button
                            onClick={() =>
                              copyToClipboard(
                                `curl -X ${endpoint.method} http://localhost:8001${endpoint.path} \\
  -H "Authorization: Basic YWRtaW46cXdlcnR5MTIz" \\
  -H "Content-Type: application/json"${
    endpoint.requestBody
      ? ` \\
  -d '${endpoint.requestBody.example.replace(/\n/g, '').replace(/\s+/g, ' ')}'`
      : ''
  }`,
                                endpoint.path + '-curl'
                              )
                            }
                            className="p-1 hover:bg-gray-200 rounded transition-colors"
                            title="Копировать"
                          >
                            {copiedPath === endpoint.path + '-curl' ? (
                              <Check className="w-4 h-4 text-green-600" />
                            ) : (
                              <Copy className="w-4 h-4 text-gray-600" />
                            )}
                          </button>
                        </div>
                        <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                          <pre className="text-xs font-mono">
                            {`curl -X ${endpoint.method} http://localhost:8001${endpoint.path} \\
  -H "Authorization: Basic YWRtaW46cXdlcnR5MTIz" \\
  -H "Content-Type: application/json"${
    endpoint.requestBody
      ? ` \\
  -d '${endpoint.requestBody.example.replace(/\n/g, '').replace(/\s+/g, ' ')}'`
      : ''
  }`}
                          </pre>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Всего эндпоинтов: <strong>{API_ENDPOINTS.length}</strong>
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
