import { useState } from 'react'
import { CheckSquare, Square, Archive, Trash2, RefreshCw, Download } from 'lucide-react'

interface BulkActionsProps {
  selectedIds: number[]
  onSelectAll: () => void
  onDeselectAll: () => void
  onBulkArchive: () => void
  onBulkDelete: () => void
  onBulkStatusChange: () => void
  onBulkExport: () => void
  totalCount: number
}

export const BulkActions = ({
  selectedIds,
  onSelectAll,
  onDeselectAll,
  onBulkArchive,
  onBulkDelete,
  onBulkStatusChange,
  onBulkExport,
  totalCount,
}: BulkActionsProps) => {
  const hasSelection = selectedIds.length > 0
  const allSelected = selectedIds.length === totalCount && totalCount > 0

  if (!hasSelection) {
    return (
      <div className="flex items-center gap-4">
        <button
          onClick={onSelectAll}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium text-gray-700"
        >
          <Square className="w-4 h-4" />
          Выбрать все
        </button>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-4 p-4 bg-blue-50 border-2 border-blue-200 rounded-xl">
      <div className="flex items-center gap-2">
        <button
          onClick={allSelected ? onDeselectAll : onSelectAll}
          className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-gray-50 rounded-lg transition-colors text-sm font-semibold text-blue-700 border border-blue-300"
        >
          {allSelected ? <Square className="w-4 h-4" /> : <CheckSquare className="w-4 h-4" />}
          {allSelected ? 'Снять выбор' : `Выбрать все (${totalCount})`}
        </button>
        <span className="text-sm font-medium text-blue-900">
          Выбрано: <span className="font-bold">{selectedIds.length}</span>
        </span>
      </div>

      <div className="flex-1" />

      <div className="flex items-center gap-2">
        <button
          onClick={onBulkStatusChange}
          className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors text-sm font-semibold"
        >
          <RefreshCw className="w-4 h-4" />
          Изменить статус
        </button>
        <button
          onClick={onBulkArchive}
          className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors text-sm font-semibold"
        >
          <Archive className="w-4 h-4" />
          В архив
        </button>
        <button
          onClick={onBulkExport}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-semibold"
        >
          <Download className="w-4 h-4" />
          Экспорт
        </button>
        <button
          onClick={onBulkDelete}
          className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm font-semibold"
        >
          <Trash2 className="w-4 h-4" />
          Удалить
        </button>
      </div>
    </div>
  )
}

// Компонент для группировки проектов
interface GroupedProjectsProps {
  groupBy: 'status' | 'executor' | 'client' | 'none'
  onGroupByChange: (groupBy: 'status' | 'executor' | 'client' | 'none') => void
}

export const ProjectGrouping = ({ groupBy, onGroupByChange }: GroupedProjectsProps) => {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-gray-700">Группировка:</span>
      <select
        value={groupBy}
        onChange={(e) => onGroupByChange(e.target.value as any)}
        className="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-sm font-medium"
      >
        <option value="none">Без группировки</option>
        <option value="status">По статусу</option>
        <option value="executor">По исполнителю</option>
        <option value="client">По клиенту</option>
      </select>
    </div>
  )
}

// Утилита для группировки проектов
export const groupProjects = (projects: any[], groupBy: string) => {
  if (groupBy === 'none') {
    return { Все: projects }
  }

  const grouped: Record<string, any[]> = {}

  projects.forEach((project) => {
    let key = 'Не указано'

    switch (groupBy) {
      case 'status':
        key = project.status || 'Не указано'
        break
      case 'executor':
        key = project.assigned_to?.username || 'Не назначен'
        break
      case 'client':
        key = project.user?.first_name || 'Не указан'
        break
    }

    if (!grouped[key]) {
      grouped[key] = []
    }
    grouped[key].push(project)
  })

  return grouped
}
