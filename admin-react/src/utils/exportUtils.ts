// Export utilities for projects data

// Export format types
export type ExportFormat = 'csv' | 'excel' | 'json' | 'pdf'

interface Project {
  id: number
  name: string
  status?: string
  project_cost?: number
  paid_total?: number
  executor_cost?: number
  assigned_to?: { username?: string; first_name?: string }
  user?: { first_name?: string; telegram_username?: string }
  deadline?: string
  created_at?: string
  description?: string
}

// Export to CSV
export const exportToCSV = (projects: Project[], filename: string = 'projects') => {
  const headers = [
    'ID',
    'Название',
    'Статус',
    'Стоимость',
    'Оплачено',
    'Остаток',
    'Стоимость исполнителю',
    'Прибыль',
    'Исполнитель',
    'Клиент',
    'Дедлайн',
    'Создан',
  ]

  const rows = projects.map((project) => {
    const remaining = (project.project_cost || 0) - (project.paid_total || 0)
    const profit = (project.project_cost || 0) - (project.executor_cost || 0)

    return [
      project.id,
      `"${(project.name || '').replace(/"/g, '""')}"`,
      project.status || '',
      project.project_cost || 0,
      project.paid_total || 0,
      remaining,
      project.executor_cost || 0,
      profit,
      project.assigned_to?.username || project.assigned_to?.first_name || '',
      project.user?.first_name || project.user?.telegram_username || '',
      project.deadline || '',
      project.created_at || '',
    ]
  })

  const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadBlob(blob, `${filename}.csv`)
}

// Export to Excel (actually CSV with .xlsx extension for simplicity)
export const exportToExcel = (projects: Project[], filename: string = 'projects') => {
  // For a real Excel export, you'd use a library like xlsx or exceljs
  // This is a simplified version
  exportToCSV(projects, filename)
}

// Export to JSON
export const exportToJSON = (projects: Project[], filename: string = 'projects') => {
  const jsonContent = JSON.stringify(projects, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json' })
  downloadBlob(blob, `${filename}.json`)
}

// Export to PDF (simple text-based, for proper PDF use jsPDF)
export const exportToPDF = (projects: Project[], filename: string = 'projects') => {
  let pdfContent = `ОТЧЕТ ПО ПРОЕКТАМ\n`
  pdfContent += `Дата формирования: ${new Date().toLocaleString('ru-RU')}\n`
  pdfContent += `Всего проектов: ${projects.length}\n\n`
  pdfContent += `${'='.repeat(80)}\n\n`

  projects.forEach((project, index) => {
    const remaining = (project.project_cost || 0) - (project.paid_total || 0)
    const profit = (project.project_cost || 0) - (project.executor_cost || 0)

    pdfContent += `${index + 1}. ${project.name}\n`
    pdfContent += `   ID: ${project.id}\n`
    pdfContent += `   Статус: ${project.status || 'Не указан'}\n`
    pdfContent += `   Стоимость: ${(project.project_cost || 0).toLocaleString('ru-RU')} ₽\n`
    pdfContent += `   Оплачено: ${(project.paid_total || 0).toLocaleString('ru-RU')} ₽\n`
    pdfContent += `   Остаток: ${remaining.toLocaleString('ru-RU')} ₽\n`
    pdfContent += `   Стоимость исполнителю: ${(project.executor_cost || 0).toLocaleString('ru-RU')} ₽\n`
    pdfContent += `   Прибыль: ${profit.toLocaleString('ru-RU')} ₽\n`

    if (project.assigned_to) {
      pdfContent += `   Исполнитель: ${project.assigned_to.username || project.assigned_to.first_name}\n`
    }

    if (project.user) {
      pdfContent += `   Клиент: ${project.user.first_name || project.user.telegram_username}\n`
    }

    if (project.deadline) {
      pdfContent += `   Дедлайн: ${new Date(project.deadline).toLocaleDateString('ru-RU')}\n`
    }

    if (project.description) {
      const shortDesc =
        project.description.length > 100
          ? project.description.substring(0, 100) + '...'
          : project.description
      pdfContent += `   Описание: ${shortDesc}\n`
    }

    pdfContent += `\n${'-'.repeat(80)}\n\n`
  })

  // Summary statistics
  const totalCost = projects.reduce((sum, p) => sum + (p.project_cost || 0), 0)
  const totalPaid = projects.reduce((sum, p) => sum + (p.paid_total || 0), 0)
  const totalExecutorCost = projects.reduce((sum, p) => sum + (p.executor_cost || 0), 0)
  const totalProfit = totalCost - totalExecutorCost

  pdfContent += `${'='.repeat(80)}\n`
  pdfContent += `ИТОГОВАЯ СТАТИСТИКА\n`
  pdfContent += `${'='.repeat(80)}\n\n`
  pdfContent += `Общая стоимость проектов: ${totalCost.toLocaleString('ru-RU')} ₽\n`
  pdfContent += `Всего оплачено: ${totalPaid.toLocaleString('ru-RU')} ₽\n`
  pdfContent += `Всего к оплате исполнителям: ${totalExecutorCost.toLocaleString('ru-RU')} ₽\n`
  pdfContent += `Общая прибыль: ${totalProfit.toLocaleString('ru-RU')} ₽\n`

  const blob = new Blob([pdfContent], { type: 'text/plain;charset=utf-8' })
  downloadBlob(blob, `${filename}.txt`)
}

// Helper function to download blob
const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Export dispatcher
export const exportProjects = (
  projects: Project[],
  format: ExportFormat,
  filename: string = 'projects'
) => {
  switch (format) {
    case 'csv':
      exportToCSV(projects, filename)
      break
    case 'excel':
      exportToExcel(projects, filename)
      break
    case 'json':
      exportToJSON(projects, filename)
      break
    case 'pdf':
      exportToPDF(projects, filename)
      break
    default:
      console.error(`Unknown export format: ${format}`)
  }
}

// Get file extension for format
export const getFileExtension = (format: ExportFormat): string => {
  switch (format) {
    case 'csv':
      return 'csv'
    case 'excel':
      return 'xlsx'
    case 'json':
      return 'json'
    case 'pdf':
      return 'txt'
    default:
      return 'txt'
  }
}

// Re-export for module refresh
export { ExportFormat as Format }
