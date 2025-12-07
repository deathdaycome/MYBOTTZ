import { useState, useEffect, useMemo, useCallback } from 'react'
import {
  FolderKanban,
  Plus,
  Search,
  Filter,
  Table as TableIcon,
  LayoutGrid,
  RefreshCw,
  Archive,
  Download,
  Eye,
  Edit,
  Trash2,
  MessageCircle,
  DollarSign,
  Archive as ArchiveIcon,
  CheckCircle,
  File,
  Users,
} from 'lucide-react'
import { apiService } from '../services/api'
import { ProjectCard } from '../components/projects/ProjectCard'
import { ProjectCreateModal } from '../components/projects/ProjectCreateModal'
import { ProjectEditModal } from '../components/projects/ProjectEditModal'
import { ProjectViewModal } from '../components/projects/ProjectViewModal'
import { ProjectFilesModal } from '../components/projects/ProjectFilesModal'
import { StatusChangeModal } from '../components/projects/StatusChangeModal'
import { AssignExecutorModal } from '../components/projects/AssignExecutorModal'
import { AddPaymentModal } from '../components/projects/AddPaymentModal'
import { ToastContainer } from '../components/common/Toast'

// New integrated components
import { ExecutorPaymentModal } from '../components/projects/ExecutorPaymentModal'
import { AdvancedFilters } from '../components/projects/AdvancedFilters'
import type { FilterValues } from '../components/projects/AdvancedFilters'
import { TechnicalSpecificationModal } from '../components/projects/TechnicalSpecificationModal'
import { BulkActions, groupProjects, ProjectGrouping } from '../components/projects/BulkActions'
import { EnhancedProjectCard } from '../components/projects/EnhancedProjectCard'
import { ShortcutsHelpModal } from '../components/projects/ShortcutsHelpModal'
import { ExportFormatModal } from '../components/projects/ExportFormatModal'
import { StatusManagementModal } from '../components/projects/StatusManagementModal'
import { FileUploadProgress } from '../components/common/FileUploadProgress'
import type { UploadFile } from '../components/common/FileUploadProgress'
import { ImagePreviewModal } from '../components/common/ImagePreviewModal'
import { ProjectTimelineModal } from '../components/projects/ProjectTimelineModal'
import { QuickEditModal } from '../components/projects/QuickEditModal'
import { ConfirmationModal } from '../components/common/ConfirmationModal'
import { DuplicateProjectModal } from '../components/projects/DuplicateProjectModal'
import { Breadcrumbs } from '../components/common/Breadcrumbs'
import { ColumnVisibilityControl, useColumnVisibility } from '../components/projects/ColumnVisibilityControl'
import type { ColumnConfig } from '../components/projects/ColumnVisibilityControl'
import { ProjectCommentsModal } from '../components/projects/ProjectCommentsModal'
import { ProjectTagsModal } from '../components/projects/ProjectTagsModal'
import { AnalyticsDashboard } from '../components/projects/AnalyticsDashboard'

// New components (Functions 31-65)
// Named exports (functions 31-50)
import { ProjectCalendar } from '../components/projects/ProjectCalendar'
import { FullTextSearch } from '../components/projects/FullTextSearch'
import { ChangeHistoryModal as ChangeHistory } from '../components/projects/ChangeHistoryModal'
import { WebhooksManagement } from '../components/projects/WebhooksManagement'
import { APIDocumentation as APIKeysManagement } from '../components/projects/APIDocumentation'
import { ProjectTemplates } from '../components/projects/ProjectTemplates'
import { AutoSaveDrafts as AutoSaveIndicator } from '../components/projects/AutoSaveDrafts'
import { EmailNotifications } from '../components/projects/EmailNotifications'
import { ProjectSharing } from '../components/projects/ProjectSharing'
import { BudgetTracking as BudgetManagement } from '../components/projects/BudgetTracking'
import { IntegrationSettings as IntegrationsPanel } from '../components/projects/IntegrationSettings'
import { RiskManagement } from '../components/projects/RiskManagement'
import { PerformanceAnalytics as PerformanceMetrics } from '../components/projects/PerformanceAnalytics'
import { ProjectVersioning as VersionControl } from '../components/projects/ProjectVersioning'
import { SmartReminders as ProjectReminders } from '../components/projects/SmartReminders'
import { TaskDependencyMap as TaskDependency } from '../components/projects/TaskDependencyMap'
import { ContractManagement } from '../components/projects/ContractManagement'
import { ProjectLabels as LabelsManager } from '../components/projects/ProjectLabels'
import { VersionComparison } from '../components/projects/VersionComparison'
import { ProjectAdvancedSettings as AdvancedProjectSettings } from '../components/projects/ProjectAdvancedSettings'
// Default exports (functions 51-65)
import TeamResourceManagement from '../components/projects/TeamResourceManagement'
import TimeTracking from '../components/projects/TimeTracking'
import MilestoneTracking from '../components/projects/MilestoneTracking'
import DocumentLibrary from '../components/projects/DocumentLibrary'
import ClientPortal from '../components/projects/ClientPortal'
import QualityAssurance from '../components/projects/QualityAssurance'
import KnowledgeBase from '../components/projects/KnowledgeBase'
import MeetingNotes from '../components/projects/MeetingNotes'
import CustomFields from '../components/projects/CustomFields'
import ReportGenerator from '../components/projects/ReportGenerator'
import AuditLog from '../components/projects/AuditLog'
import Invoicing from '../components/projects/Invoicing'
import ExpenseTracking from '../components/projects/ExpenseTracking'
import Feedback from '../components/projects/Feedback'
import ProjectAnalyticsDashboard from '../components/projects/ProjectAnalyticsDashboard'

// Utilities
import { copyToClipboard, formatProjectForCopy } from '../utils/clipboard'
import { exportProjects } from '../utils/exportUtils'
import type { ExportFormat } from '../utils/exportUtils'
import { printProjects, printSingleProject } from '../utils/printUtils'
import { loadFilterPresets, saveFilterPreset, deleteFilterPreset, getBuiltInPresets, clearFilters as clearAllFilters } from '../utils/filterPresets'
import { sortProjects as sortProjectsUtil, saveSortPreferences, getDefaultSort } from '../utils/sortPreferences'
import type { SortOption } from '../utils/sortPreferences'

// Hooks
import { useResizableColumns } from '../hooks/useResizableColumns'
import { useFileDragDrop } from '../hooks/useFileDragDrop'
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts'

// Handlers
import * as ProjectHandlers from './ProjectsHandlers'

// Types
interface Project {
  id: number
  title: string
  description: string
  project_type: string
  status: string
  complexity: string
  priority: string
  color: string
  estimated_cost: number
  executor_cost: number
  final_cost: number
  estimated_hours: number
  prepayment_amount: number
  client_paid_total: number
  executor_paid_total: number
  assigned_executor_id: number | null
  deadline: string | null
  is_archived: boolean
  created_at: string
  updated_at: string
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
  } | null
}

// Helper functions for table display
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
    new: 'bg-blue-100 text-blue-700',
    review: 'bg-orange-100 text-orange-700',
    accepted: 'bg-purple-100 text-purple-700',
    in_progress: 'bg-yellow-100 text-yellow-700',
    testing: 'bg-green-100 text-green-700',
    completed: 'bg-green-200 text-green-800',
    cancelled: 'bg-red-100 text-red-700',
    on_hold: 'bg-gray-100 text-gray-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}

const getRowColor = (status: string) => {
  const colors: Record<string, string> = {
    new: 'bg-blue-50/30 hover:bg-blue-50',
    review: 'bg-orange-50/30 hover:bg-orange-50',
    accepted: 'bg-purple-50/30 hover:bg-purple-50',
    in_progress: 'bg-yellow-50/30 hover:bg-yellow-50',
    testing: 'bg-green-50/30 hover:bg-green-50',
    completed: 'bg-green-50/50 hover:bg-green-100',
    cancelled: 'bg-red-50/30 hover:bg-red-50',
    on_hold: 'bg-gray-50/30 hover:bg-gray-50',
  }
  return colors[status] || 'hover:bg-gray-50'
}

const getComplexityDisplay = (complexity: string) => {
  const displays: Record<string, string> = {
    simple: '🟢 Простой',
    medium: '🟡 Средний',
    complex: '🟠 Сложный',
    premium: '🔴 Премиум',
  }
  return displays[complexity] || complexity
}

const calculateProgress = (status: string) => {
  const progress: Record<string, number> = {
    new: 10,
    review: 25,
    accepted: 40,
    in_progress: 60,
    testing: 80,
    completed: 100,
    cancelled: 0,
    on_hold: 0,
  }
  return progress[status] || 0
}

export const Projects = () => {
  // State
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showArchived, setShowArchived] = useState(false) // По умолчанию показываем активные проекты (не архивные)
  const [currentView, setCurrentView] = useState<'table' | 'cards'>('cards')
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isViewModalOpen, setIsViewModalOpen] = useState(false)
  const [isFilesModalOpen, setIsFilesModalOpen] = useState(false)
  const [isStatusChangeModalOpen, setIsStatusChangeModalOpen] = useState(false)
  const [isAssignExecutorModalOpen, setIsAssignExecutorModalOpen] = useState(false)
  const [isAddPaymentModalOpen, setIsAddPaymentModalOpen] = useState(false)
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [filesProjectId, setFilesProjectId] = useState<number | null>(null)
  const [statusChangeProject, setStatusChangeProject] = useState<{ id: number; status: string } | null>(null)
  const [assignExecutorProject, setAssignExecutorProject] = useState<Project | null>(null)
  const [paymentProject, setPaymentProject] = useState<Project | null>(null)

  // New modal states
  const [isExecutorPaymentModalOpen, setIsExecutorPaymentModalOpen] = useState(false)
  const [executorPaymentProject, setExecutorPaymentProject] = useState<Project | null>(null)
  const [isTechnicalSpecModalOpen, setIsTechnicalSpecModalOpen] = useState(false)
  const [technicalSpecProject, setTechnicalSpecProject] = useState<Project | null>(null)
  const [isShortcutsHelpOpen, setIsShortcutsHelpOpen] = useState(false)
  const [isExportFormatModalOpen, setIsExportFormatModalOpen] = useState(false)
  const [isStatusManagementOpen, setIsStatusManagementOpen] = useState(false)
  const [isTimelineModalOpen, setIsTimelineModalOpen] = useState(false)
  const [timelineProject, setTimelineProject] = useState<{ id: number; name: string } | null>(null)
  const [isQuickEditModalOpen, setIsQuickEditModalOpen] = useState(false)
  const [quickEditProject, setQuickEditProject] = useState<Project | null>(null)
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] = useState(false)
  const [confirmationData, setConfirmationData] = useState<{
    title: string
    message: string
    onConfirm: () => void
    type?: 'danger' | 'warning' | 'info' | 'success'
  } | null>(null)
  const [isDuplicateModalOpen, setIsDuplicateModalOpen] = useState(false)
  const [duplicateProject, setDuplicateProject] = useState<Project | null>(null)
  const [isCommentsModalOpen, setIsCommentsModalOpen] = useState(false)
  const [commentsProject, setCommentsProject] = useState<{ id: number; name: string } | null>(null)
  const [isTagsModalOpen, setIsTagsModalOpen] = useState(false)
  const [tagsProject, setTagsProject] = useState<{ id: number; name: string } | null>(null)
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null)
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [groupBy, setGroupBy] = useState<'status' | 'executor' | 'client' | 'none'>('none')
  const [advancedFilters, setAdvancedFilters] = useState<FilterValues>({
    executorId: null,
    clientId: null,
    colorFilter: '',
    dateFrom: '',
    dateTo: '',
    hasPayment: '',
  })

  // New modal states (Functions 31-65)
  const [isCalendarModalOpen, setIsCalendarModalOpen] = useState(false)
  const [isFullTextSearchOpen, setIsFullTextSearchOpen] = useState(false)
  const [isChangeHistoryOpen, setIsChangeHistoryOpen] = useState(false)
  const [changeHistoryProject, setChangeHistoryProject] = useState<{ id: number; name: string } | null>(null)
  const [isWebhooksOpen, setIsWebhooksOpen] = useState(false)
  const [webhooksProject, setWebhooksProject] = useState<number | null>(null)
  const [isAPIKeysOpen, setIsAPIKeysOpen] = useState(false)
  const [isTemplatesOpen, setIsTemplatesOpen] = useState(false)
  const [isEmailNotificationsOpen, setIsEmailNotificationsOpen] = useState(false)
  const [emailNotificationsProject, setEmailNotificationsProject] = useState<number | null>(null)
  const [isSharingOpen, setIsSharingOpen] = useState(false)
  const [sharingProject, setSharingProject] = useState<number | null>(null)
  const [isBudgetOpen, setIsBudgetOpen] = useState(false)
  const [budgetProject, setBudgetProject] = useState<number | null>(null)
  const [isIntegrationsOpen, setIsIntegrationsOpen] = useState(false)
  const [integrationsProject, setIntegrationsProject] = useState<number | null>(null)
  const [isRiskManagementOpen, setIsRiskManagementOpen] = useState(false)
  const [riskProject, setRiskProject] = useState<number | null>(null)
  const [isPerformanceMetricsOpen, setIsPerformanceMetricsOpen] = useState(false)
  const [performanceProject, setPerformanceProject] = useState<number | null>(null)
  const [isVersionControlOpen, setIsVersionControlOpen] = useState(false)
  const [versionControlProject, setVersionControlProject] = useState<number | null>(null)
  const [isRemindersOpen, setIsRemindersOpen] = useState(false)
  const [remindersProject, setRemindersProject] = useState<number | null>(null)
  const [isTaskDependencyOpen, setIsTaskDependencyOpen] = useState(false)
  const [taskDependencyProject, setTaskDependencyProject] = useState<number | null>(null)
  const [isContractOpen, setIsContractOpen] = useState(false)
  const [contractProject, setContractProject] = useState<number | null>(null)
  const [isLabelsOpen, setIsLabelsOpen] = useState(false)
  const [labelsProject, setLabelsProject] = useState<number | null>(null)
  const [isVersionComparisonOpen, setIsVersionComparisonOpen] = useState(false)
  const [versionComparisonProject, setVersionComparisonProject] = useState<number | null>(null)
  const [isAdvancedSettingsOpen, setIsAdvancedSettingsOpen] = useState(false)
  const [advancedSettingsProject, setAdvancedSettingsProject] = useState<number | null>(null)
  const [isTeamResourceOpen, setIsTeamResourceOpen] = useState(false)
  const [teamResourceProject, setTeamResourceProject] = useState<number | null>(null)
  const [isTimeTrackingOpen, setIsTimeTrackingOpen] = useState(false)
  const [timeTrackingProject, setTimeTrackingProject] = useState<number | null>(null)
  const [isMilestoneOpen, setIsMilestoneOpen] = useState(false)
  const [milestoneProject, setMilestoneProject] = useState<number | null>(null)
  const [isDocumentLibraryOpen, setIsDocumentLibraryOpen] = useState(false)
  const [documentLibraryProject, setDocumentLibraryProject] = useState<number | null>(null)
  const [isClientPortalOpen, setIsClientPortalOpen] = useState(false)
  const [clientPortalProject, setClientPortalProject] = useState<number | null>(null)
  const [isQAOpen, setIsQAOpen] = useState(false)
  const [qaProject, setQAProject] = useState<number | null>(null)
  const [isKnowledgeBaseOpen, setIsKnowledgeBaseOpen] = useState(false)
  const [knowledgeBaseProject, setKnowledgeBaseProject] = useState<number | null>(null)
  const [isMeetingNotesOpen, setIsMeetingNotesOpen] = useState(false)
  const [meetingNotesProject, setMeetingNotesProject] = useState<number | null>(null)
  const [isCustomFieldsOpen, setIsCustomFieldsOpen] = useState(false)
  const [customFieldsProject, setCustomFieldsProject] = useState<number | null>(null)
  const [isReportGeneratorOpen, setIsReportGeneratorOpen] = useState(false)
  const [reportGeneratorProject, setReportGeneratorProject] = useState<number | null>(null)
  const [isAuditLogOpen, setIsAuditLogOpen] = useState(false)
  const [auditLogProject, setAuditLogProject] = useState<number | null>(null)
  const [isInvoicingOpen, setIsInvoicingOpen] = useState(false)
  const [invoicingProject, setInvoicingProject] = useState<number | null>(null)
  const [isExpenseTrackingOpen, setIsExpenseTrackingOpen] = useState(false)
  const [expenseTrackingProject, setExpenseTrackingProject] = useState<number | null>(null)
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false)
  const [feedbackProject, setFeedbackProject] = useState<number | null>(null)
  const [isProjectAnalyticsOpen, setIsProjectAnalyticsOpen] = useState(false)
  const [projectAnalyticsProject, setProjectAnalyticsProject] = useState<number | null>(null)

  // Toast notifications
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' | 'warning' }>>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  // Load projects
  const loadProjects = useCallback(async () => {
    try {
      setLoading(true)
      const response = await apiService.getProjects(showArchived)
      if (response.projects) {
        setProjects(response.projects)
      }
    } catch (error) {
      console.error('Error loading projects:', error)
      showToast('Ошибка загрузки проектов', 'error')
    } finally {
      setLoading(false)
    }
  }, [showArchived, showToast])

  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [complexityFilter, setComplexityFilter] = useState('')
  const [sortBy, setSortBy] = useState('created_at')

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onNew: () => setIsCreateModalOpen(true),
    onRefresh: loadProjects,
    onSearch: () => {
      const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement
      searchInput?.focus()
    },
    onHelp: () => setIsShortcutsHelpOpen(true),
    onEscape: () => {
      // Close all modals
      setIsCreateModalOpen(false)
      setIsEditModalOpen(false)
      setIsViewModalOpen(false)
      setIsFilesModalOpen(false)
      setIsExecutorPaymentModalOpen(false)
      setIsTechnicalSpecModalOpen(false)
      setIsShortcutsHelpOpen(false)
      setIsExportFormatModalOpen(false)
      setIsStatusManagementOpen(false)
      setIsTimelineModalOpen(false)
      setIsQuickEditModalOpen(false)
      setIsConfirmationModalOpen(false)
      setIsDuplicateModalOpen(false)
      setIsCommentsModalOpen(false)
      setIsTagsModalOpen(false)
      // New modals (Functions 31-65)
      setIsCalendarModalOpen(false)
      setIsFullTextSearchOpen(false)
      setIsChangeHistoryOpen(false)
      setIsWebhooksOpen(false)
      setIsAPIKeysOpen(false)
      setIsTemplatesOpen(false)
      setIsEmailNotificationsOpen(false)
      setIsSharingOpen(false)
      setIsBudgetOpen(false)
      setIsIntegrationsOpen(false)
      setIsRiskManagementOpen(false)
      setIsPerformanceMetricsOpen(false)
      setIsVersionControlOpen(false)
      setIsRemindersOpen(false)
      setIsTaskDependencyOpen(false)
      setIsContractOpen(false)
      setIsLabelsOpen(false)
      setIsVersionComparisonOpen(false)
      setIsAdvancedSettingsOpen(false)
      setIsTeamResourceOpen(false)
      setIsTimeTrackingOpen(false)
      setIsMilestoneOpen(false)
      setIsDocumentLibraryOpen(false)
      setIsClientPortalOpen(false)
      setIsQAOpen(false)
      setIsKnowledgeBaseOpen(false)
      setIsMeetingNotesOpen(false)
      setIsCustomFieldsOpen(false)
      setIsReportGeneratorOpen(false)
      setIsAuditLogOpen(false)
      setIsInvoicingOpen(false)
      setIsExpenseTrackingOpen(false)
      setIsFeedbackOpen(false)
      setIsProjectAnalyticsOpen(false)
    },
  })

  // Load projects
  useEffect(() => {
    loadProjects()
  }, [showArchived])

  // Filter and search with useMemo for performance
  const filteredProjects = useMemo(() => {
    let filtered = [...projects]

    // Search
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      filtered = filtered.filter(
        (p) =>
          p.title.toLowerCase().includes(searchLower) ||
          p.user?.first_name?.toLowerCase().includes(searchLower) ||
          p.user?.username?.toLowerCase().includes(searchLower)
      )
    }

    // Status filter
    if (statusFilter) {
      filtered = filtered.filter((p) => p.status === statusFilter)
    }

    // Complexity filter
    if (complexityFilter) {
      filtered = filtered.filter((p) => p.complexity === complexityFilter)
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'created_at' || sortBy === 'updated_at') {
        return new Date(b[sortBy]).getTime() - new Date(a[sortBy]).getTime()
      } else if (sortBy === 'estimated_cost') {
        return (b.estimated_cost || 0) - (a.estimated_cost || 0)
      } else if (sortBy === 'title') {
        return a.title.localeCompare(b.title)
      }
      return 0
    })

    return filtered
  }, [projects, searchTerm, statusFilter, complexityFilter, sortBy])

  const clearFilters = useCallback(() => {
    setSearchTerm('')
    setStatusFilter('')
    setComplexityFilter('')
    setSortBy('created_at')
  }, [])

  const handleRefresh = useCallback(() => {
    loadProjects()
  }, [loadProjects])

  const handleExport = async () => {
    try {
      await apiService.exportProjects()
      showToast('Экспорт проектов успешно выполнен!', 'success')
    } catch (error) {
      console.error('Error exporting projects:', error)
      showToast('Ошибка при экспорте проектов', 'error')
    }
  }

  // Project Actions
  const handleView = useCallback(async (projectId: number) => {
    try {
      const response = await apiService.getProject(projectId)
      // Backend возвращает {success: true, project: {...}}
      setSelectedProject(response.project || response)
      setIsViewModalOpen(true)
    } catch (error) {
      console.error('Error loading project:', error)
      showToast('Ошибка при загрузке проекта', 'error')
    }
  }, [showToast])

  const handleEdit = useCallback((projectId: number) => {
    setSelectedProjectId(projectId)
    setIsEditModalOpen(true)
  }, [])

  const handleDelete = async (projectId: number) => {
    const confirmed = window.confirm('Вы уверены, что хотите удалить этот проект?')
    if (!confirmed) return

    try {
      await apiService.deleteProject(projectId)
      showToast('Проект успешно удален!', 'success')
      loadProjects()
    } catch (error) {
      console.error('Error deleting project:', error)
      showToast('Ошибка при удалении проекта', 'error')
    }
  }

  const handleArchive = async (projectId: number) => {
    try {
      const project = projects.find((p) => p.id === projectId)
      // Backend использует toggle - один эндпоинт /archive для архивации и восстановления
      await apiService.archiveProject(projectId)
      if (project?.is_archived) {
        showToast('Проект восстановлен из архива!', 'success')
      } else {
        showToast('Проект добавлен в архив!', 'success')
      }
      loadProjects()
    } catch (error) {
      console.error('Error archiving project:', error)
      showToast('Ошибка при работе с архивом', 'error')
    }
  }

  const handleContact = async (telegramId: number) => {
    const message = window.prompt('Введите сообщение для клиента:')
    if (!message) return

    try {
      await apiService.sendMessageToClient(telegramId, message)
      showToast('Сообщение отправлено!', 'success')
    } catch (error) {
      console.error('Error sending message:', error)
      showToast('Ошибка при отправке сообщения', 'error')
    }
  }

  const handleComplete = async (projectId: number) => {
    const confirmed = window.confirm('Вы уверены, что хотите завершить этот проект?')
    if (!confirmed) return

    try {
      await apiService.completeProject(projectId)
      showToast('Проект успешно завершен!', 'success')
      loadProjects()
    } catch (error) {
      console.error('Error completing project:', error)
      showToast('Ошибка при завершении проекта', 'error')
    }
  }

  const handleViewFiles = (projectId: number) => {
    setFilesProjectId(projectId)
    setIsFilesModalOpen(true)
  }

  const handleAddPayment = (projectId: number) => {
    const project = projects.find((p) => p.id === projectId)
    if (project) {
      setPaymentProject(project)
      setIsAddPaymentModalOpen(true)
    }
  }

  const handleChangeStatus = (projectId: number, currentStatus: string) => {
    setStatusChangeProject({ id: projectId, status: currentStatus })
    setIsStatusChangeModalOpen(true)
  }

  const handleAssignExecutor = (projectId: number) => {
    const project = projects.find((p) => p.id === projectId)
    if (project) {
      setAssignExecutorProject(project)
      setIsAssignExecutorModalOpen(true)
    }
  }

  const handleExecutorPayment = (projectId: number) => {
    const project = projects.find((p) => p.id === projectId)
    if (project) {
      setExecutorPaymentProject(project)
      setIsExecutorPaymentModalOpen(true)
    }
  }

  const handleChangeColor = async (projectId: number, currentColor: string) => {
    const colors = ['default', 'green', 'yellow', 'red']
    const colorNames: Record<string, string> = {
      default: 'Серый',
      green: 'Зеленый',
      yellow: 'Желтый',
      red: 'Красный',
    }

    const currentIndex = colors.indexOf(currentColor || 'default')
    const nextColor = colors[(currentIndex + 1) % colors.length]

    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({ color: nextColor }),
      })

      if (response.ok) {
        showToast(`Цвет изменен на ${colorNames[nextColor]}`, 'success')
        loadProjects()
      } else {
        showToast('Ошибка изменения цвета', 'error')
      }
    } catch (error) {
      console.error('Error changing color:', error)
      showToast('Ошибка изменения цвета', 'error')
    }
  }

  // Statistics
  const totalProjects = projects.length
  const activeProjects = projects.filter((p) =>
    ['new', 'review', 'accepted', 'in_progress', 'testing'].includes(p.status)
  ).length
  const completedProjects = projects.filter((p) => p.status === 'completed').length
  const totalRevenue = projects.reduce((sum, p) => sum + (p.estimated_cost || 0), 0)
  const totalPaid = projects.reduce((sum, p) => sum + (p.client_paid_total || 0), 0)
  const remainingPayment = totalRevenue - totalPaid
  const totalPrepayments = projects.reduce((sum, p) => sum + (p.prepayment_amount || 0), 0)
  const totalExecutorPayments = projects.reduce((sum, p) => sum + (p.executor_paid_total || 0), 0)
  const totalExecutorCost = projects.reduce((sum, p) => sum + (p.executor_cost || 0), 0)
  const remainingExecutorPayments = totalExecutorCost - totalExecutorPayments
  const currentProfit = totalPaid - totalExecutorPayments

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <RefreshCw className="w-12 h-12 text-purple-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Загрузка проектов...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6 bg-gradient-to-br from-purple-50 via-pink-50 to-red-50">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: 'Главная', path: '/' },
          { label: 'Проекты', path: '/projects' },
        ]}
      />

      {/* Analytics Dashboard Toggle */}
      {showAnalytics && (
        <AnalyticsDashboard
          projects={filteredProjects}
          onClose={() => setShowAnalytics(false)}
        />
      )}

      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 rounded-3xl p-8 text-white shadow-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Управление проектами</h1>
            <p className="text-purple-100">Всего проектов: {filteredProjects.length}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl font-semibold transition-all flex items-center gap-2"
              title="Обновить (R)"
            >
              <RefreshCw className="w-4 h-4" />
              Обновить
            </button>
            <button
              onClick={() => setShowArchived(!showArchived)}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl font-semibold transition-all flex items-center gap-2"
            >
              <Archive className="w-4 h-4" />
              {showArchived ? 'Скрыть архив' : 'Показать архив'}
            </button>
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl font-semibold transition-all flex items-center gap-2"
            >
              📊 Аналитика
            </button>
            <button
              onClick={() => setIsExportFormatModalOpen(true)}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl font-semibold transition-all flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Экспорт
            </button>
            <button
              onClick={() => setIsShortcutsHelpOpen(true)}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl font-semibold transition-all flex items-center gap-2"
              title="Горячие клавиши (? или H)"
            >
              ⌨️
            </button>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-6 py-2 bg-white text-purple-600 rounded-xl font-semibold hover:shadow-xl transition-all flex items-center gap-2"
              title="Создать проект (Ctrl+N)"
            >
              <Plus className="w-5 h-5" />
              Создать проект
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-md border border-purple-100 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-2xl font-bold text-gray-900">{totalProjects}</div>
          <div className="text-xs text-gray-600 mt-2 leading-tight">Всего<br/>проектов</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-green-100 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-2xl font-bold text-gray-900">{activeProjects}</div>
          <div className="text-xs text-gray-600 mt-2">Активные</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-green-200 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-2xl font-bold text-gray-900">{completedProjects}</div>
          <div className="text-xs text-gray-600 mt-2">Завершенные</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-orange-100 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-xl font-bold text-gray-900">{totalRevenue.toLocaleString()}₽</div>
          <div className="text-xs text-gray-600 mt-2 leading-tight">Общая<br/>стоимость</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-cyan-100 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-xl font-bold text-gray-900">{totalPaid.toLocaleString()}₽</div>
          <div className="text-xs text-gray-600 mt-2">Получено</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-red-100 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-xl font-bold text-gray-900">{remainingPayment.toLocaleString()}₽</div>
          <div className="text-xs text-gray-600 mt-2">Остаток</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-gray-100 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-xl font-bold text-gray-900">{totalPrepayments.toLocaleString()}₽</div>
          <div className="text-xs text-gray-600 mt-2">Предоплаты</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-orange-200 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-xl font-bold text-gray-900">{totalExecutorPayments.toLocaleString()}₽</div>
          <div className="text-xs text-gray-600 mt-2">Выплачено</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-red-200 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-xl font-bold text-gray-900">{remainingExecutorPayments.toLocaleString()}₽</div>
          <div className="text-xs text-gray-600 mt-2 leading-tight">К выплате</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md border border-purple-200 flex flex-col items-center justify-center text-center min-h-[100px]">
          <div className="text-xl font-bold text-gray-900">{currentProfit.toLocaleString()}₽</div>
          <div className="text-xs text-gray-600 mt-2">Прибыль</div>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedIds.length > 0 && (
        <BulkActions
          selectedIds={selectedIds}
          onSelectAll={() => ProjectHandlers.handleSelectAll(filteredProjects, setSelectedIds)}
          onDeselectAll={() => ProjectHandlers.handleDeselectAll(setSelectedIds)}
          onBulkArchive={() => ProjectHandlers.handleBulkArchive(selectedIds, showToast, loadProjects)}
          onBulkDelete={() => ProjectHandlers.handleBulkDelete(selectedIds, showToast, loadProjects)}
          onBulkStatusChange={() => ProjectHandlers.handleBulkStatusChange(selectedIds, showToast)}
          onBulkExport={() => ProjectHandlers.handleBulkExport(selectedIds, filteredProjects, showToast)}
          totalCount={filteredProjects.length}
        />
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[300px] relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по названию или клиенту... (Ctrl+F)"
              className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Все статусы</option>
            <option value="new">Новые</option>
            <option value="review">На рассмотрении</option>
            <option value="accepted">Принятые</option>
            <option value="in_progress">В работе</option>
            <option value="testing">Тестирование</option>
            <option value="completed">Завершенные</option>
            <option value="cancelled">Отмененные</option>
          </select>
          <select
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
            value={complexityFilter}
            onChange={(e) => setComplexityFilter(e.target.value)}
          >
            <option value="">Все сложности</option>
            <option value="simple">Простые</option>
            <option value="medium">Средние</option>
            <option value="complex">Сложные</option>
            <option value="premium">Премиум</option>
          </select>
          <select
            className="px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="created_at">По дате создания</option>
            <option value="updated_at">По дате обновления</option>
            <option value="estimated_cost">По стоимости</option>
            <option value="title">По названию</option>
          </select>
          <button
            onClick={clearFilters}
            className="px-6 py-3 bg-red-50 text-red-600 rounded-xl hover:bg-red-100 transition-all font-medium"
          >
            Очистить
          </button>
        </div>

        {/* Advanced Filters and Grouping */}
        <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-200">
          <AdvancedFilters
            filters={advancedFilters}
            onChange={setAdvancedFilters}
            onClear={() => {
              setAdvancedFilters({
                executorId: null,
                clientId: null,
                colorFilter: '',
                dateFrom: '',
                dateTo: '',
                hasPayment: '',
              })
            }}
          />

          <ProjectGrouping
            groupBy={groupBy}
            onChange={setGroupBy}
          />

          <div className="flex-1" />

          <button
            onClick={() => ProjectHandlers.handlePrintProjects(filteredProjects)}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-all font-medium flex items-center gap-2"
            title="Печать списка проектов"
          >
            🖨️ Печать
          </button>

          <button
            onClick={() => setIsStatusManagementOpen(true)}
            className="px-4 py-2 bg-purple-100 text-purple-700 rounded-xl hover:bg-purple-200 transition-all font-medium flex items-center gap-2"
            title="Управление статусами"
          >
            ⚙️ Статусы
          </button>
        </div>
      </div>

      {/* View Switcher */}
      <div className="flex items-center justify-between bg-white rounded-2xl p-4 shadow-lg border border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-gray-600 font-medium">Отображение:</span>
          <div className="flex gap-2 bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setCurrentView('table')}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                currentView === 'table'
                  ? 'bg-white text-purple-600 shadow-md'
                  : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <TableIcon className="w-4 h-4" />
              Таблица
            </button>
            <button
              onClick={() => setCurrentView('cards')}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                currentView === 'cards'
                  ? 'bg-white text-purple-600 shadow-md'
                  : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <LayoutGrid className="w-4 h-4" />
              Карточки
            </button>
          </div>
        </div>
      </div>

      {/* Projects Display */}
      {filteredProjects.length === 0 ? (
        <div className="bg-white rounded-3xl p-16 shadow-xl border border-gray-100">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-pink-100 rounded-3xl flex items-center justify-center mb-6">
              <FolderKanban className="w-12 h-12 text-purple-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Нет проектов</h3>
            <p className="text-gray-600 mb-6 max-w-md">
              {searchTerm || statusFilter || complexityFilter
                ? 'По заданным фильтрам проекты не найдены'
                : 'Создайте свой первый проект, чтобы начать работу'}
            </p>
          </div>
        </div>
      ) : currentView === 'cards' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onView={handleView}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onArchive={handleArchive}
              onContact={handleContact}
              onAddPayment={handleAddPayment}
              onComplete={handleComplete}
              onViewFiles={handleViewFiles}
              onAssignExecutor={handleAssignExecutor}
              onExecutorPayment={handleExecutorPayment}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
                <tr>
                  <th className="px-3 py-4 text-center text-xs font-bold uppercase w-[50px]">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === filteredProjects.length && filteredProjects.length > 0}
                      onChange={(e) => {
                        if (e.target.checked) {
                          ProjectHandlers.handleSelectAll(filteredProjects, setSelectedIds)
                        } else {
                          ProjectHandlers.handleDeselectAll(setSelectedIds)
                        }
                      }}
                      className="w-4 h-4 rounded"
                      title="Выбрать все"
                    />
                  </th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">ID</th>
                  <th className="px-3 py-4 text-center text-xs font-bold uppercase w-[50px]">Цвет</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase min-w-[200px]">Название</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Клиент</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Исполнитель</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Статус</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Сложность</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Прогресс</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Стоимость</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Оплаты</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Дедлайн</th>
                  <th className="px-3 py-4 text-left text-xs font-bold uppercase">Создан</th>
                  <th className="px-3 py-4 text-center text-xs font-bold uppercase min-w-[400px]">Действия</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredProjects.map((project) => {
                  const progress = calculateProgress(project.status)
                  const statusColorClass = getStatusColor(project.status)
                  const rowColorClass = getRowColor(project.status)

                  return (
                    <tr key={project.id} className={`transition-colors ${rowColorClass}`}>
                      {/* Checkbox */}
                      <td className="px-3 py-4 text-center">
                        <input
                          type="checkbox"
                          checked={selectedIds.includes(project.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedIds([...selectedIds, project.id])
                            } else {
                              setSelectedIds(selectedIds.filter((id) => id !== project.id))
                            }
                          }}
                          className="w-4 h-4 rounded"
                          onClick={(e) => e.stopPropagation()}
                        />
                      </td>

                      {/* ID */}
                      <td className="px-3 py-4">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-1 bg-gray-700 text-white rounded-lg text-xs font-bold">
                            #{project.id}
                          </span>
                        </div>
                      </td>

                      {/* Color Indicator */}
                      <td className="px-3 py-4">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleChangeColor(project.id, project.color || 'default')
                          }}
                          className={`w-6 h-6 rounded-full border-2 border-gray-300 hover:scale-110 transition-transform cursor-pointer ${
                            project.color === 'green'
                              ? 'bg-green-500'
                              : project.color === 'yellow'
                              ? 'bg-yellow-500'
                              : project.color === 'red'
                              ? 'bg-red-500'
                              : 'bg-gray-400'
                          }`}
                          title={`Изменить цвет (текущий: ${
                            project.color === 'green'
                              ? 'Зеленый'
                              : project.color === 'yellow'
                              ? 'Желтый'
                              : project.color === 'red'
                              ? 'Красный'
                              : 'Серый'
                          })`}
                        />
                      </td>

                      {/* Title */}
                      <td className="px-3 py-4">
                        <div className="font-semibold text-gray-900 text-sm mb-1">{project.title}</div>
                        <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded inline-block">
                          {project.project_type || 'Не указано'}
                        </div>
                      </td>

                      {/* Client */}
                      <td className="px-3 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {project.user?.first_name || 'Неизвестно'}
                        </div>
                        <div className="text-xs text-gray-500">@{project.user?.username || 'нет'}</div>
                      </td>

                      {/* Executor */}
                      <td className="px-3 py-4">
                        {project.assigned_to ? (
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {project.assigned_to.username}
                            </div>
                            {project.executor_cost > 0 && (
                              <div className="text-xs text-orange-600 font-semibold">
                                {project.executor_paid_total?.toLocaleString() || 0}₽ / {project.executor_cost?.toLocaleString()}₽
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400 italic">Не назначен</span>
                        )}
                      </td>

                      {/* Status */}
                      <td className="px-3 py-4">
                        <span className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${statusColorClass}`}>
                          {getStatusName(project.status)}
                        </span>
                      </td>

                      {/* Complexity */}
                      <td className="px-3 py-4">
                        <span className="text-sm font-medium">
                          {getComplexityDisplay(project.complexity)}
                        </span>
                      </td>

                      {/* Progress */}
                      <td className="px-3 py-4">
                        <div className="w-24">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-xs font-bold text-purple-600">{progress}%</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500 rounded-full"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Cost */}
                      <td className="px-3 py-4">
                        <div className="text-sm font-bold text-purple-600">
                          {(project.estimated_cost || 0).toLocaleString()}₽
                        </div>
                      </td>

                      {/* Payments */}
                      <td className="px-3 py-4">
                        <div className="text-sm">
                          <div className="font-bold text-green-600">
                            {(project.client_paid_total || 0).toLocaleString()}₽
                          </div>
                          <div className="text-xs text-gray-500">
                            Остаток: {((project.estimated_cost || 0) - (project.client_paid_total || 0)).toLocaleString()}₽
                          </div>
                        </div>
                      </td>

                      {/* Deadline */}
                      <td className="px-3 py-4">
                        {project.deadline ? (
                          <div className="text-xs text-orange-700 font-semibold">
                            📅 {project.deadline.slice(0, 10)}
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400">—</span>
                        )}
                      </td>

                      {/* Created */}
                      <td className="px-3 py-4">
                        <div className="text-xs text-gray-500">
                          {project.created_at?.slice(0, 10)}
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="px-3 py-4">
                        <div className="flex flex-wrap gap-1.5 justify-center">
                          <button
                            onClick={() => handleView(project.id)}
                            className="px-2 py-1.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Просмотр"
                          >
                            <Eye className="w-3 h-3" />
                            Просмотр
                          </button>
                          <button
                            onClick={() => handleEdit(project.id)}
                            className="px-2 py-1.5 bg-cyan-100 text-cyan-700 rounded-lg hover:bg-cyan-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Редактировать"
                          >
                            <Edit className="w-3 h-3" />
                            Править
                          </button>
                          <button
                            onClick={() => handleChangeStatus(project.id, project.status)}
                            className="px-2 py-1.5 bg-teal-100 text-teal-700 rounded-lg hover:bg-teal-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Изменить статус"
                          >
                            <RefreshCw className="w-3 h-3" />
                            Статус
                          </button>
                          <button
                            onClick={() => handleAssignExecutor(project.id)}
                            className="px-2 py-1.5 bg-violet-100 text-violet-700 rounded-lg hover:bg-violet-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Назначить исполнителя"
                          >
                            <Users className="w-3 h-3" />
                            Исполнитель
                          </button>
                          {(project.status === 'testing' || project.status === 'in_progress') && (
                            <button
                              onClick={() => handleComplete(project.id)}
                              className="px-2 py-1.5 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-all text-xs font-semibold flex items-center gap-1"
                              title="Завершить проект"
                            >
                              <CheckCircle className="w-3 h-3" />
                              Завершить
                            </button>
                          )}
                          {project.user?.telegram_id && (
                            <button
                              onClick={() => handleContact(project.user.telegram_id)}
                              className="px-2 py-1.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-all text-xs font-semibold flex items-center gap-1"
                              title="Связаться"
                            >
                              <MessageCircle className="w-3 h-3" />
                              Связь
                            </button>
                          )}
                          <button
                            onClick={() => handleAddPayment(project.id)}
                            className="px-2 py-1.5 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Добавить оплату"
                          >
                            <DollarSign className="w-3 h-3" />
                            Оплата
                          </button>
                          <button
                            onClick={() => handleViewFiles(project.id)}
                            className="px-2 py-1.5 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Просмотр файлов"
                          >
                            <File className="w-3 h-3" />
                            Файлы
                          </button>
                          <button
                            onClick={() => ProjectHandlers.handleViewComments(
                              project.id,
                              project.title,
                              setCommentsProject,
                              setIsCommentsModalOpen
                            )}
                            className="px-2 py-1.5 bg-sky-100 text-sky-700 rounded-lg hover:bg-sky-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Комментарии"
                          >
                            💬
                          </button>
                          <button
                            onClick={() => ProjectHandlers.handleManageTags(
                              project.id,
                              project.title,
                              setTagsProject,
                              setIsTagsModalOpen
                            )}
                            className="px-2 py-1.5 bg-pink-100 text-pink-700 rounded-lg hover:bg-pink-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Теги"
                          >
                            🏷️
                          </button>
                          <button
                            onClick={() => ProjectHandlers.handleViewTimeline(
                              project.id,
                              project.title,
                              setTimelineProject,
                              setIsTimelineModalOpen
                            )}
                            className="px-2 py-1.5 bg-lime-100 text-lime-700 rounded-lg hover:bg-lime-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="История"
                          >
                            📅
                          </button>
                          <button
                            onClick={() => ProjectHandlers.handleQuickEdit(
                              project,
                              setQuickEditProject,
                              setIsQuickEditModalOpen
                            )}
                            className="px-2 py-1.5 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Быстрое редактирование"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => ProjectHandlers.handleCopyProject(project, showToast)}
                            className="px-2 py-1.5 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Копировать в буфер"
                          >
                            📋
                          </button>
                          <button
                            onClick={() => handleArchive(project.id)}
                            className="px-2 py-1.5 bg-amber-100 text-amber-700 rounded-lg hover:bg-amber-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title={project.is_archived ? 'Восстановить' : 'Архивировать'}
                          >
                            <ArchiveIcon className="w-3 h-3" />
                            {project.is_archived ? 'Восст.' : 'Архив'}
                          </button>
                          <button
                            onClick={() => handleDelete(project.id)}
                            className="px-2 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all text-xs font-semibold flex items-center gap-1"
                            title="Удалить"
                          >
                            <Trash2 className="w-3 h-3" />
                            Удалить
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Project Modal */}
      <ProjectCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={loadProjects}
      />

      {/* Edit Project Modal */}
      <ProjectEditModal
        projectId={selectedProjectId}
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false)
          setSelectedProjectId(null)
        }}
        onSuccess={loadProjects}
      />

      {/* View Project Modal */}
      <ProjectViewModal
        isOpen={isViewModalOpen}
        onClose={() => {
          setIsViewModalOpen(false)
          setSelectedProject(null)
        }}
        onEdit={(id) => {
          setIsViewModalOpen(false)
          setSelectedProjectId(id)
          setIsEditModalOpen(true)
        }}
        onContact={handleContact}
        project={selectedProject}
      />

      {/* Project Files Modal */}
      <ProjectFilesModal
        isOpen={isFilesModalOpen}
        onClose={() => {
          setIsFilesModalOpen(false)
          setFilesProjectId(null)
        }}
        projectId={filesProjectId}
      />

      {/* Status Change Modal */}
      <StatusChangeModal
        isOpen={isStatusChangeModalOpen}
        onClose={() => {
          setIsStatusChangeModalOpen(false)
          setStatusChangeProject(null)
        }}
        projectId={statusChangeProject?.id || null}
        currentStatus={statusChangeProject?.status || ''}
        onStatusChanged={loadProjects}
      />

      {/* Assign Executor Modal */}
      <AssignExecutorModal
        isOpen={isAssignExecutorModalOpen}
        onClose={() => {
          setIsAssignExecutorModalOpen(false)
          setAssignExecutorProject(null)
        }}
        projectId={assignExecutorProject?.id || null}
        currentExecutor={assignExecutorProject?.assigned_to}
        currentCost={assignExecutorProject?.executor_cost}
        onAssigned={loadProjects}
      />

      {/* Add Payment Modal */}
      <AddPaymentModal
        isOpen={isAddPaymentModalOpen}
        onClose={() => {
          setIsAddPaymentModalOpen(false)
          setPaymentProject(null)
        }}
        projectId={paymentProject?.id || null}
        projectCost={paymentProject?.estimated_cost || 0}
        paidTotal={paymentProject?.client_paid_total || 0}
        onPaymentAdded={loadProjects}
      />

      {/* New Integrated Modals */}

      {/* Executor Payment Modal */}
      <ExecutorPaymentModal
        isOpen={isExecutorPaymentModalOpen}
        onClose={() => {
          setIsExecutorPaymentModalOpen(false)
          setExecutorPaymentProject(null)
        }}
        projectId={executorPaymentProject?.id || null}
        executorCost={executorPaymentProject?.executor_cost || 0}
        executorPaidTotal={executorPaymentProject?.executor_paid_total || 0}
        executorName={executorPaymentProject?.assigned_to?.username}
        onPaymentAdded={loadProjects}
      />

      {/* Technical Specification Modal */}
      <TechnicalSpecificationModal
        isOpen={isTechnicalSpecModalOpen}
        onClose={() => {
          setIsTechnicalSpecModalOpen(false)
          setTechnicalSpecProject(null)
        }}
        project={technicalSpecProject}
      />

      {/* Shortcuts Help Modal */}
      <ShortcutsHelpModal
        isOpen={isShortcutsHelpOpen}
        onClose={() => setIsShortcutsHelpOpen(false)}
      />

      {/* Export Format Modal */}
      <ExportFormatModal
        isOpen={isExportFormatModalOpen}
        onClose={() => setIsExportFormatModalOpen(false)}
        onExport={(format, filename) => {
          ProjectHandlers.handleExportProjectsWithFormat(
            format,
            filename,
            filteredProjects,
            showToast
          )
          setIsExportFormatModalOpen(false)
        }}
      />

      {/* Status Management Modal */}
      <StatusManagementModal
        isOpen={isStatusManagementOpen}
        onClose={() => setIsStatusManagementOpen(false)}
        onStatusesUpdated={loadProjects}
      />

      {/* Timeline Modal */}
      <ProjectTimelineModal
        isOpen={isTimelineModalOpen}
        onClose={() => {
          setIsTimelineModalOpen(false)
          setTimelineProject(null)
        }}
        projectId={timelineProject?.id || null}
        projectName={timelineProject?.name || ''}
      />

      {/* Quick Edit Modal */}
      <QuickEditModal
        isOpen={isQuickEditModalOpen}
        onClose={() => {
          setIsQuickEditModalOpen(false)
          setQuickEditProject(null)
        }}
        project={quickEditProject}
        onSaved={loadProjects}
      />

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={isConfirmationModalOpen}
        onClose={() => {
          setIsConfirmationModalOpen(false)
          setConfirmationData(null)
        }}
        title={confirmationData?.title || ''}
        message={confirmationData?.message || ''}
        onConfirm={() => {
          confirmationData?.onConfirm()
          setIsConfirmationModalOpen(false)
          setConfirmationData(null)
        }}
        type={confirmationData?.type}
      />

      {/* Duplicate Project Modal */}
      <DuplicateProjectModal
        isOpen={isDuplicateModalOpen}
        onClose={() => {
          setIsDuplicateModalOpen(false)
          setDuplicateProject(null)
        }}
        project={duplicateProject}
        onDuplicated={loadProjects}
      />

      {/* Comments Modal */}
      <ProjectCommentsModal
        isOpen={isCommentsModalOpen}
        onClose={() => {
          setIsCommentsModalOpen(false)
          setCommentsProject(null)
        }}
        projectId={commentsProject?.id || null}
        projectName={commentsProject?.name || ''}
      />

      {/* Tags Modal */}
      <ProjectTagsModal
        isOpen={isTagsModalOpen}
        onClose={() => {
          setIsTagsModalOpen(false)
          setTagsProject(null)
        }}
        projectId={tagsProject?.id || null}
        projectName={tagsProject?.name || ''}
        onTagsUpdated={loadProjects}
      />

      {/* Image Preview Modal */}
      <ImagePreviewModal
        imageUrl={imagePreviewUrl}
        onClose={() => setImagePreviewUrl(null)}
      />

      {/* File Upload Progress */}
      {uploadFiles.length > 0 && (
        <FileUploadProgress
          files={uploadFiles}
          onCancel={(fileId) => ProjectHandlers.handleCancelUpload(fileId, setUploadFiles)}
          onClear={() => ProjectHandlers.handleClearUploadFiles(setUploadFiles)}
        />
      )}

      {/* New Integrated Components (Functions 31-65) */}

      {/* Project Calendar */}
      {isCalendarModalOpen && (
        <ProjectCalendar
          projects={filteredProjects}
          onClose={() => setIsCalendarModalOpen(false)}
        />
      )}

      {/* Full Text Search */}
      {isFullTextSearchOpen && (
        <FullTextSearch
          projects={projects}
          onClose={() => setIsFullTextSearchOpen(false)}
          onProjectSelect={(project) => {
            setSelectedProject(project)
            setIsViewModalOpen(true)
            setIsFullTextSearchOpen(false)
          }}
        />
      )}

      {/* Change History */}
      {isChangeHistoryOpen && changeHistoryProject && (
        <ChangeHistory
          projectId={changeHistoryProject.id}
          projectName={changeHistoryProject.name}
          onClose={() => {
            setIsChangeHistoryOpen(false)
            setChangeHistoryProject(null)
          }}
        />
      )}

      {/* Webhooks Management */}
      {isWebhooksOpen && webhooksProject && (
        <WebhooksManagement
          projectId={webhooksProject}
          onClose={() => {
            setIsWebhooksOpen(false)
            setWebhooksProject(null)
          }}
        />
      )}

      {/* API Keys Management */}
      {isAPIKeysOpen && (
        <APIKeysManagement
          onClose={() => setIsAPIKeysOpen(false)}
        />
      )}

      {/* Project Templates */}
      {isTemplatesOpen && (
        <ProjectTemplates
          onClose={() => setIsTemplatesOpen(false)}
          onTemplateSelect={(template) => {
            setIsTemplatesOpen(false)
            setIsCreateModalOpen(true)
          }}
        />
      )}

      {/* AutoSave Indicator - can be always visible */}
      <AutoSaveIndicator />

      {/* Email Notifications */}
      {isEmailNotificationsOpen && emailNotificationsProject && (
        <EmailNotifications
          projectId={emailNotificationsProject}
          onClose={() => {
            setIsEmailNotificationsOpen(false)
            setEmailNotificationsProject(null)
          }}
        />
      )}

      {/* Project Sharing */}
      {isSharingOpen && sharingProject && (
        <ProjectSharing
          projectId={sharingProject}
          onClose={() => {
            setIsSharingOpen(false)
            setSharingProject(null)
          }}
        />
      )}

      {/* Budget Management */}
      {isBudgetOpen && budgetProject && (
        <BudgetManagement
          projectId={budgetProject}
          onClose={() => {
            setIsBudgetOpen(false)
            setBudgetProject(null)
          }}
        />
      )}

      {/* Integrations Panel */}
      {isIntegrationsOpen && integrationsProject && (
        <IntegrationsPanel
          projectId={integrationsProject}
          onClose={() => {
            setIsIntegrationsOpen(false)
            setIntegrationsProject(null)
          }}
        />
      )}

      {/* Risk Management */}
      {isRiskManagementOpen && riskProject && (
        <RiskManagement
          projectId={riskProject}
          onClose={() => {
            setIsRiskManagementOpen(false)
            setRiskProject(null)
          }}
        />
      )}

      {/* Performance Metrics */}
      {isPerformanceMetricsOpen && performanceProject && (
        <PerformanceMetrics
          projectId={performanceProject}
          onClose={() => {
            setIsPerformanceMetricsOpen(false)
            setPerformanceProject(null)
          }}
        />
      )}

      {/* Version Control */}
      {isVersionControlOpen && versionControlProject && (
        <VersionControl
          projectId={versionControlProject}
          onClose={() => {
            setIsVersionControlOpen(false)
            setVersionControlProject(null)
          }}
        />
      )}

      {/* Project Reminders */}
      {isRemindersOpen && remindersProject && (
        <ProjectReminders
          projectId={remindersProject}
          onClose={() => {
            setIsRemindersOpen(false)
            setRemindersProject(null)
          }}
        />
      )}

      {/* Task Dependency */}
      {isTaskDependencyOpen && taskDependencyProject && (
        <TaskDependency
          projectId={taskDependencyProject}
          onClose={() => {
            setIsTaskDependencyOpen(false)
            setTaskDependencyProject(null)
          }}
        />
      )}

      {/* Contract Management */}
      {isContractOpen && contractProject && (
        <ContractManagement
          projectId={contractProject}
          onClose={() => {
            setIsContractOpen(false)
            setContractProject(null)
          }}
        />
      )}

      {/* Labels Manager */}
      {isLabelsOpen && labelsProject && (
        <LabelsManager
          projectId={labelsProject}
          onClose={() => {
            setIsLabelsOpen(false)
            setLabelsProject(null)
          }}
        />
      )}

      {/* Version Comparison */}
      {isVersionComparisonOpen && versionComparisonProject && (
        <VersionComparison
          projectId={versionComparisonProject}
          onClose={() => {
            setIsVersionComparisonOpen(false)
            setVersionComparisonProject(null)
          }}
        />
      )}

      {/* Advanced Project Settings */}
      {isAdvancedSettingsOpen && advancedSettingsProject && (
        <AdvancedProjectSettings
          projectId={advancedSettingsProject}
          onClose={() => {
            setIsAdvancedSettingsOpen(false)
            setAdvancedSettingsProject(null)
          }}
        />
      )}

      {/* Team Resource Management */}
      {isTeamResourceOpen && teamResourceProject && (
        <TeamResourceManagement
          projectId={teamResourceProject}
          onClose={() => {
            setIsTeamResourceOpen(false)
            setTeamResourceProject(null)
          }}
        />
      )}

      {/* Time Tracking */}
      {isTimeTrackingOpen && timeTrackingProject && (
        <TimeTracking
          projectId={timeTrackingProject}
          onClose={() => {
            setIsTimeTrackingOpen(false)
            setTimeTrackingProject(null)
          }}
        />
      )}

      {/* Milestone Tracking */}
      {isMilestoneOpen && milestoneProject && (
        <MilestoneTracking
          projectId={milestoneProject}
          onClose={() => {
            setIsMilestoneOpen(false)
            setMilestoneProject(null)
          }}
        />
      )}

      {/* Document Library */}
      {isDocumentLibraryOpen && documentLibraryProject && (
        <DocumentLibrary
          projectId={documentLibraryProject}
          onClose={() => {
            setIsDocumentLibraryOpen(false)
            setDocumentLibraryProject(null)
          }}
        />
      )}

      {/* Client Portal */}
      {isClientPortalOpen && clientPortalProject && (
        <ClientPortal
          projectId={clientPortalProject}
          onClose={() => {
            setIsClientPortalOpen(false)
            setClientPortalProject(null)
          }}
        />
      )}

      {/* Quality Assurance */}
      {isQAOpen && qaProject && (
        <QualityAssurance
          projectId={qaProject}
          onClose={() => {
            setIsQAOpen(false)
            setQAProject(null)
          }}
        />
      )}

      {/* Knowledge Base */}
      {isKnowledgeBaseOpen && knowledgeBaseProject && (
        <KnowledgeBase
          projectId={knowledgeBaseProject}
          onClose={() => {
            setIsKnowledgeBaseOpen(false)
            setKnowledgeBaseProject(null)
          }}
        />
      )}

      {/* Meeting Notes */}
      {isMeetingNotesOpen && meetingNotesProject && (
        <MeetingNotes
          projectId={meetingNotesProject}
          onClose={() => {
            setIsMeetingNotesOpen(false)
            setMeetingNotesProject(null)
          }}
        />
      )}

      {/* Custom Fields */}
      {isCustomFieldsOpen && customFieldsProject && (
        <CustomFields
          projectId={customFieldsProject}
          onClose={() => {
            setIsCustomFieldsOpen(false)
            setCustomFieldsProject(null)
          }}
        />
      )}

      {/* Report Generator */}
      {isReportGeneratorOpen && reportGeneratorProject && (
        <ReportGenerator
          projectId={reportGeneratorProject}
          onClose={() => {
            setIsReportGeneratorOpen(false)
            setReportGeneratorProject(null)
          }}
        />
      )}

      {/* Audit Log */}
      {isAuditLogOpen && auditLogProject && (
        <AuditLog
          projectId={auditLogProject}
          onClose={() => {
            setIsAuditLogOpen(false)
            setAuditLogProject(null)
          }}
        />
      )}

      {/* Invoicing */}
      {isInvoicingOpen && invoicingProject && (
        <Invoicing
          projectId={invoicingProject}
          onClose={() => {
            setIsInvoicingOpen(false)
            setInvoicingProject(null)
          }}
        />
      )}

      {/* Expense Tracking */}
      {isExpenseTrackingOpen && expenseTrackingProject && (
        <ExpenseTracking
          projectId={expenseTrackingProject}
          onClose={() => {
            setIsExpenseTrackingOpen(false)
            setExpenseTrackingProject(null)
          }}
        />
      )}

      {/* Feedback */}
      {isFeedbackOpen && feedbackProject && (
        <Feedback
          projectId={feedbackProject}
          onClose={() => {
            setIsFeedbackOpen(false)
            setFeedbackProject(null)
          }}
        />
      )}

      {/* Project Analytics Dashboard */}
      {isProjectAnalyticsOpen && projectAnalyticsProject && (
        <ProjectAnalyticsDashboard
          projectId={projectAnalyticsProject}
          onClose={() => {
            setIsProjectAnalyticsOpen(false)
            setProjectAnalyticsProject(null)
          }}
        />
      )}

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  )
}
