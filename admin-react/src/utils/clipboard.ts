/**
 * Копирует текст в буфер обмена
 * @param text Текст для копирования
 * @returns Promise<boolean> - успешно ли скопировано
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    // Современный API Clipboard
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      return true
    }

    // Fallback для старых браузеров
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()

    const successful = document.execCommand('copy')
    document.body.removeChild(textArea)

    return successful
  } catch (err) {
    console.error('Failed to copy:', err)
    return false
  }
}

/**
 * Форматирует проект для копирования
 */
export const formatProjectForCopy = (project: any): string => {
  const lines = [
    `ПРОЕКТ #${project.id}`,
    ``,
    `Название: ${project.title}`,
    `Клиент: ${project.user?.first_name || 'Не указан'} (@${project.user?.username || 'нет'})`,
    `Статус: ${project.status}`,
    `Тип: ${project.project_type || 'Не указан'}`,
    `Сложность: ${project.complexity}`,
    ``,
    `ФИНАНСЫ:`,
    `Стоимость: ${project.estimated_cost?.toLocaleString('ru-RU') || 0} ₽`,
    `Оплачено клиентом: ${project.client_paid_total?.toLocaleString('ru-RU') || 0} ₽`,
    `Остаток: ${((project.estimated_cost || 0) - (project.client_paid_total || 0)).toLocaleString('ru-RU')} ₽`,
    ``,
    `Стоимость исполнителю: ${project.executor_cost?.toLocaleString('ru-RU') || 0} ₽`,
    `Выплачено исполнителю: ${project.executor_paid_total?.toLocaleString('ru-RU') || 0} ₽`,
    ``,
    `ОПИСАНИЕ:`,
    `${project.description || 'Нет описания'}`,
  ]

  if (project.deadline) {
    lines.push(``, `Дедлайн: ${project.deadline}`)
  }

  if (project.assigned_to) {
    lines.push(`Исполнитель: ${project.assigned_to.username}`)
  }

  lines.push(``, `Создан: ${project.created_at}`)

  return lines.join('\n')
}
