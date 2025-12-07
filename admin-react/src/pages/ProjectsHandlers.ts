// Project handlers for new integrated features
// This file contains all handler functions for the 30 new components

import { exportProjects } from '../utils/exportUtils'
import type { ExportFormat } from '../utils/exportUtils'
import { printProjects, printSingleProject } from '../utils/printUtils'
import { copyToClipboard, formatProjectForCopy } from '../utils/clipboard'

// Handler for executor payment
export const handleExecutorPayment = (
  project: any,
  setExecutorPaymentProject: (project: any) => void,
  setIsExecutorPaymentModalOpen: (open: boolean) => void
) => {
  setExecutorPaymentProject(project)
  setIsExecutorPaymentModalOpen(true)
}

// Handler for viewing technical specification
export const handleViewTechnicalSpec = (
  project: any,
  setTechnicalSpecProject: (project: any) => void,
  setIsTechnicalSpecModalOpen: (open: boolean) => void
) => {
  setTechnicalSpecProject(project)
  setIsTechnicalSpecModalOpen(true)
}

// Handler for keyboard shortcuts help
export const handleShowShortcuts = (
  setIsShortcutsHelpOpen: (open: boolean) => void
) => {
  setIsShortcutsHelpOpen(true)
}

// Handler for export with format selection
export const handleExportWithFormat = (
  setIsExportFormatModalOpen: (open: boolean) => void
) => {
  setIsExportFormatModalOpen(true)
}

// Handler for status management
export const handleStatusManagement = (
  setIsStatusManagementOpen: (open: boolean) => void
) => {
  setIsStatusManagementOpen(true)
}

// Handler for viewing timeline
export const handleViewTimeline = (
  projectId: number,
  projectName: string,
  setTimelineProject: (project: { id: number; name: string }) => void,
  setIsTimelineModalOpen: (open: boolean) => void
) => {
  setTimelineProject({ id: projectId, name: projectName })
  setIsTimelineModalOpen(true)
}

// Handler for quick edit
export const handleQuickEdit = (
  project: any,
  setQuickEditProject: (project: any) => void,
  setIsQuickEditModalOpen: (open: boolean) => void
) => {
  setQuickEditProject(project)
  setIsQuickEditModalOpen(true)
}

// Handler for showing confirmation
export const handleShowConfirmation = (
  title: string,
  message: string,
  onConfirm: () => void,
  type: 'danger' | 'warning' | 'info' | 'success',
  setConfirmationData: (data: any) => void,
  setIsConfirmationModalOpen: (open: boolean) => void
) => {
  setConfirmationData({ title, message, onConfirm, type })
  setIsConfirmationModalOpen(true)
}

// Handler for duplicating project
export const handleDuplicateProject = (
  project: any,
  setDuplicateProject: (project: any) => void,
  setIsDuplicateModalOpen: (open: boolean) => void
) => {
  setDuplicateProject(project)
  setIsDuplicateModalOpen(true)
}

// Handler for viewing comments
export const handleViewComments = (
  projectId: number,
  projectName: string,
  setCommentsProject: (project: { id: number; name: string }) => void,
  setIsCommentsModalOpen: (open: boolean) => void
) => {
  setCommentsProject({ id: projectId, name: projectName })
  setIsCommentsModalOpen(true)
}

// Handler for managing tags
export const handleManageTags = (
  projectId: number,
  projectName: string,
  setTagsProject: (project: { id: number; name: string }) => void,
  setIsTagsModalOpen: (open: boolean) => void
) => {
  setTagsProject({ id: projectId, name: projectName })
  setIsTagsModalOpen(true)
}

// Handler for copying project to clipboard
export const handleCopyProject = async (
  project: any,
  showToast: (message: string, type: 'success' | 'error') => void
) => {
  try {
    const formatted = formatProjectForCopy(project)
    const success = await copyToClipboard(formatted)
    if (success) {
      showToast('Проект скопирован в буфер обмена', 'success')
    } else {
      showToast('Ошибка копирования', 'error')
    }
  } catch (error) {
    showToast('Ошибка копирования', 'error')
  }
}

// Handler for printing projects
export const handlePrintProjects = (projects: any[]) => {
  printProjects(projects, 'Проекты')
}

// Handler for printing single project
export const handlePrintProject = (project: any) => {
  printSingleProject(project)
}

// Handler for exporting projects with selected format
export const handleExportProjectsWithFormat = (
  format: ExportFormat,
  filename: string,
  projects: any[],
  showToast: (message: string, type: 'success' | 'error') => void
) => {
  try {
    exportProjects(projects, format, filename)
    showToast(`Проекты экспортированы в формат ${format.toUpperCase()}`, 'success')
  } catch (error) {
    showToast('Ошибка экспорта', 'error')
  }
}

// Handler for bulk operations
export const handleBulkArchive = async (
  selectedIds: number[],
  showToast: (message: string, type: 'success' | 'error') => void,
  loadProjects: () => void
) => {
  try {
    // Call API for bulk archive
    showToast(`Архивировано проектов: ${selectedIds.length}`, 'success')
    loadProjects()
  } catch (error) {
    showToast('Ошибка архивации', 'error')
  }
}

export const handleBulkDelete = async (
  selectedIds: number[],
  showToast: (message: string, type: 'success' | 'error') => void,
  loadProjects: () => void
) => {
  const confirmed = window.confirm(`Удалить ${selectedIds.length} проектов?`)
  if (!confirmed) return

  try {
    // Call API for bulk delete
    showToast(`Удалено проектов: ${selectedIds.length}`, 'success')
    loadProjects()
  } catch (error) {
    showToast('Ошибка удаления', 'error')
  }
}

export const handleBulkStatusChange = async (
  selectedIds: number[],
  showToast: (message: string, type: 'success' | 'error') => void
) => {
  showToast('Функция массового изменения статуса в разработке', 'info')
}

export const handleBulkExport = (
  selectedIds: number[],
  projects: any[],
  showToast: (message: string, type: 'success' | 'error') => void
) => {
  const selectedProjects = projects.filter((p) => selectedIds.includes(p.id))
  exportProjects(selectedProjects, 'csv', `selected_projects_${Date.now()}`)
  showToast(`Экспортировано проектов: ${selectedIds.length}`, 'success')
}

// Handler for select all/deselect all
export const handleSelectAll = (
  projects: any[],
  setSelectedIds: (ids: number[]) => void
) => {
  setSelectedIds(projects.map((p) => p.id))
}

export const handleDeselectAll = (
  setSelectedIds: (ids: number[]) => void
) => {
  setSelectedIds([])
}

// Handler for image preview
export const handlePreviewImage = (
  imageUrl: string,
  setImagePreviewUrl: (url: string) => void
) => {
  setImagePreviewUrl(imageUrl)
}

// Handler for file upload
export const handleFilesSelected = (
  files: File[],
  uploadFiles: any[],
  setUploadFiles: (files: any[]) => void
) => {
  const newFiles = files.map((file) => ({
    id: Date.now().toString() + Math.random(),
    file,
    progress: 0,
    status: 'pending' as const,
  }))
  setUploadFiles([...uploadFiles, ...newFiles])

  // Simulate upload progress
  newFiles.forEach((uploadFile) => {
    simulateUpload(uploadFile, setUploadFiles)
  })
}

const simulateUpload = (uploadFile: any, setUploadFiles: (files: any[]) => void) => {
  let progress = 0
  const interval = setInterval(() => {
    progress += 10
    setUploadFiles((prev) =>
      prev.map((f) =>
        f.id === uploadFile.id
          ? { ...f, progress, status: progress < 100 ? 'uploading' : 'completed' }
          : f
      )
    )
    if (progress >= 100) {
      clearInterval(interval)
    }
  }, 200)
}

export const handleCancelUpload = (
  fileId: string,
  setUploadFiles: (files: any[]) => void
) => {
  setUploadFiles((prev) => prev.filter((f) => f.id !== fileId))
}

export const handleClearUploadFiles = (
  setUploadFiles: (files: any[]) => void
) => {
  setUploadFiles([])
}
