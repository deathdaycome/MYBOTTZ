import { useState, useEffect, useRef } from 'react'
import {
  X,
  FileText,
  CheckSquare,
  GitBranch,
  MessageCircle,
  FolderOpen,
  DollarSign,
  Server,
  Calendar,
  Clock,
  User,
  TrendingUp,
} from 'lucide-react'

// Импорт вкладок
import { ProjectOverviewTab } from './tabs/ProjectOverviewTab'
import { ProjectTasksTab } from './tabs/ProjectTasksTab'
import { ProjectRevisionsTab } from './tabs/ProjectRevisionsTab'
import { ProjectChatTab } from './tabs/ProjectChatTab'
import { ProjectDocumentsTab } from './tabs/ProjectDocumentsTab'
import { ProjectFinanceTab } from './tabs/ProjectFinanceTab'
import { ProjectHostingTab } from './tabs/ProjectHostingTab'

interface Project {
  id: number
  title: string
  description: string
  project_type: string
  status: string
  complexity: string
  priority: string
  estimated_cost: number
  executor_cost: number
  final_cost: number
  estimated_hours: number
  actual_hours: number
  client_paid_total: number
  executor_paid_total: number
  deadline: string | null
  is_archived: boolean
  created_at: string
  updated_at: string
  stage?: string
  progress?: number
  deal_id?: number
  teamlead_id?: number
  executor_id?: number
  user: {
    id: number
    first_name: string
    username: string
    telegram_id: number
  } | null
  assigned_to: {
    id: number
    username: string
  } | null
  chat: {
    id: number
  } | null
  payments: any[]
  project_metadata: {
    test_link: string | null
    bot_token: string | null
    bot_username: string | null
    telegram_channel_id: string | null
    timeweb_login: string | null
    timeweb_password: string | null
    timeweb_server_id: string | null
  } | null
  technical_requirements: string | null
  additional_requirements: string | null
}

interface ProjectDetailModalProps {
  isOpen: boolean
  onClose: () => void
  onEdit?: (id: number) => void
  project: Project | null
  onRefresh?: () => void
}

type TabKey = 'overview' | 'tasks' | 'revisions' | 'chat' | 'documents' | 'finance' | 'hosting'

interface Tab {
  key: TabKey
  label: string
  icon: any
  count?: number
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    new: '🆕 Новый',
    review: '👀 Рассмотрение',
    accepted: '✅ Принят',
    in_progress: '🔄 В работе',
    testing: '🧪 Тестирование',
    completed: '🎉 Завершен',
    cancelled: '❌ Отменен',
    on_hold: '⏸️ Приостановлен',
  }
  return names[status] || status
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    new: 'from-blue-400 to-blue-600',
    review: 'from-orange-400 to-orange-600',
    accepted: 'from-purple-400 to-purple-600',
    in_progress: 'from-yellow-400 to-yellow-600',
    testing: 'from-green-400 to-green-600',
    completed: 'from-green-500 to-green-700',
    cancelled: 'from-red-400 to-red-600',
    on_hold: 'from-gray-400 to-gray-600',
  }
  return colors[status] || 'from-gray-400 to-gray-600'
}

export const ProjectDetailModal = ({ isOpen, onClose, onEdit, project, onRefresh }: ProjectDetailModalProps) => {
  const [activeTab, setActiveTab] = useState<TabKey>('overview')
  const [tasksCount, setTasksCount] = useState(0)
  const [revisionsCount, setRevisionsCount] = useState(0)
  const [unreadMessages, setUnreadMessages] = useState(0)
  const modalContentRef = useRef<HTMLDivElement>(null)

  // Блокировка прокрутки страницы при открытии модалки
  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'

      if (modalContentRef.current) {
        modalContentRef.current.scrollTop = 0
      }
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
  }, [isOpen])

  // Загрузка счётчиков для вкладок
  useEffect(() => {
    if (isOpen && project) {
      // TODO: Загрузить реальные данные через API
      // Временно используем заглушки
      setTasksCount(0)
      setRevisionsCount(0)
      setUnreadMessages(0)
    }
  }, [isOpen, project])

  if (!isOpen || !project) return null

  const statusColor = getStatusColor(project.status)
  const statusName = getStatusName(project.status)
  const progress = project.progress || 0

  const tabs: Tab[] = [
    { key: 'overview', label: 'Обзор', icon: TrendingUp },
    { key: 'tasks', label: 'Задачи', icon: CheckSquare, count: tasksCount },
    { key: 'revisions', label: 'Правки', icon: GitBranch, count: revisionsCount },
    { key: 'chat', label: 'Чат', icon: MessageCircle, count: unreadMessages },
    { key: 'documents', label: 'Документы', icon: FolderOpen },
    { key: 'finance', label: 'Финансы', icon: DollarSign },
    { key: 'hosting', label: 'Хостинг', icon: Server },
  ]

  return (
    <>
      <style>{`
        .modal-content-scrollable {
          scrollbar-width: thin;
          scrollbar-color: #cbd5e1 #f1f5f9;
        }
        .modal-content-scrollable::-webkit-scrollbar {
          width: 6px;
        }
        .modal-content-scrollable::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 10px;
        }
        .modal-content-scrollable::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 10px;
        }
        .modal-content-scrollable::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>

      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-2"
        style={{ overflow: 'hidden' }}
        onClick={onClose}
      >
        <div
          className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[95vh] flex flex-col overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className={`bg-gradient-to-r ${statusColor} text-white px-6 py-4 flex-shrink-0`}>
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <h2 className="text-2xl font-bold truncate">{project.title}</h2>
                <div className="flex items-center gap-4 mt-2 text-sm">
                  <span className="opacity-90">Проект #{project.id}</span>
                  <span className="opacity-90">•</span>
                  <span className="opacity-90">{statusName}</span>
                  {project.stage && (
                    <>
                      <span className="opacity-90">•</span>
                      <span className="opacity-90">{project.stage}</span>
                    </>
                  )}
                  {project.deadline && (
                    <>
                      <span className="opacity-90">•</span>
                      <span className="flex items-center gap-1 opacity-90">
                        <Calendar className="w-4 h-4" />
                        {new Date(project.deadline).toLocaleDateString('ru-RU')}
                      </span>
                    </>
                  )}
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors flex-shrink-0 ml-4"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Progress Bar */}
            {progress > 0 && (
              <div className="mt-3">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="opacity-90">Прогресс выполнения</span>
                  <span className="font-semibold">{progress}%</span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-white h-full rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Tabs Navigation */}
          <div className="flex-shrink-0 border-b border-gray-200 bg-gray-50">
            <div className="flex overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon
                const isActive = activeTab === tab.key

                return (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`
                      flex items-center gap-2 px-6 py-3 text-sm font-medium whitespace-nowrap
                      border-b-2 transition-all
                      ${
                        isActive
                          ? 'border-purple-600 text-purple-600 bg-white'
                          : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                    {tab.count !== undefined && tab.count > 0 && (
                      <span
                        className={`
                        px-2 py-0.5 rounded-full text-xs font-semibold
                        ${isActive ? 'bg-purple-100 text-purple-700' : 'bg-gray-200 text-gray-700'}
                      `}
                      >
                        {tab.count}
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div ref={modalContentRef} className="modal-content-scrollable flex-1 overflow-y-auto">
            {activeTab === 'overview' && <ProjectOverviewTab project={project} onEdit={onEdit} />}
            {activeTab === 'tasks' && (
              <ProjectTasksTab projectId={project.id} onCountChange={setTasksCount} onRefresh={onRefresh} />
            )}
            {activeTab === 'revisions' && (
              <ProjectRevisionsTab projectId={project.id} onCountChange={setRevisionsCount} onRefresh={onRefresh} />
            )}
            {activeTab === 'chat' && (
              <ProjectChatTab projectId={project.id} chatId={project.chat?.id} onUnreadChange={setUnreadMessages} />
            )}
            {activeTab === 'documents' && <ProjectDocumentsTab projectId={project.id} dealId={project.deal_id} />}
            {activeTab === 'finance' && (
              <ProjectFinanceTab
                projectId={project.id}
                estimatedCost={project.estimated_cost}
                executorCost={project.executor_cost}
                finalCost={project.final_cost}
                clientPaidTotal={project.client_paid_total}
                executorPaidTotal={project.executor_paid_total}
                payments={project.payments}
              />
            )}
            {activeTab === 'hosting' && (
              <ProjectHostingTab projectId={project.id} projectMetadata={project.project_metadata} />
            )}
          </div>
        </div>
      </div>
    </>
  )
}
