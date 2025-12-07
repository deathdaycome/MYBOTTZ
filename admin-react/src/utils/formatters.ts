/**
 * Utility functions for formatting data
 */

// Format currency (RUB)
export const formatCurrency = (amount: number, currency = 'RUB'): string => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

// Format number
export const formatNumber = (
  num: number,
  options: Intl.NumberFormatOptions = {}
): string => {
  const defaults: Intl.NumberFormatOptions = {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }

  return new Intl.NumberFormat('ru-RU', {
    ...defaults,
    ...options,
  }).format(num)
}

// Format date
export const formatDate = (
  date: string | Date,
  options: Intl.DateTimeFormatOptions = {}
): string => {
  const defaults: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }

  return new Intl.DateTimeFormat('ru-RU', {
    ...defaults,
    ...options,
  }).format(new Date(date))
}

// Format time
export const formatTime = (
  date: string | Date,
  options: Intl.DateTimeFormatOptions = {}
): string => {
  const defaults: Intl.DateTimeFormatOptions = {
    hour: '2-digit',
    minute: '2-digit',
  }

  return new Intl.DateTimeFormat('ru-RU', {
    ...defaults,
    ...options,
  }).format(new Date(date))
}

// Format relative time (e.g., "2 hours ago")
export const formatRelativeTime = (date: string | Date): string => {
  const rtf = new Intl.RelativeTimeFormat('ru', { numeric: 'auto' })
  const now = new Date()
  const diff = new Date(date).getTime() - now.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (Math.abs(days) > 0) return rtf.format(days, 'day')
  if (Math.abs(hours) > 0) return rtf.format(hours, 'hour')
  if (Math.abs(minutes) > 0) return rtf.format(minutes, 'minute')
  return rtf.format(seconds, 'second')
}

// Format file size
export const formatFileSize = (bytes: number): string => {
  const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
  if (bytes === 0) return '0 Б'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

// Format percent
export const formatPercent = (value: number, total: number): string => {
  const percent = (value / total) * 100
  return `${percent.toFixed(1)}%`
}

// Format change indicator
export const formatChange = (
  change: number,
  isCurrency = false
): { text: string; isPositive: boolean } => {
  const isPositive = change >= 0
  const prefix = isPositive ? '+' : ''
  const text = isCurrency
    ? `${prefix}${formatCurrency(change)}`
    : `${prefix}${change.toFixed(1)}%`

  return { text, isPositive }
}
