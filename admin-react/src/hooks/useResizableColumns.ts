import { useEffect, useRef, useState } from 'react'

interface ColumnWidth {
  [key: string]: number
}

export const useResizableColumns = (initialWidths: ColumnWidth, storageKey: string = 'column-widths') => {
  const [columnWidths, setColumnWidths] = useState<ColumnWidth>(() => {
    const saved = localStorage.getItem(storageKey)
    return saved ? JSON.parse(saved) : initialWidths
  })

  const isResizing = useRef(false)
  const currentColumn = useRef<string | null>(null)
  const startX = useRef(0)
  const startWidth = useRef(0)

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(columnWidths))
  }, [columnWidths, storageKey])

  const startResize = (columnKey: string, clientX: number) => {
    isResizing.current = true
    currentColumn.current = columnKey
    startX.current = clientX
    startWidth.current = columnWidths[columnKey] || 150

    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing.current || !currentColumn.current) return

    const diff = e.clientX - startX.current
    const newWidth = Math.max(50, startWidth.current + diff)

    setColumnWidths((prev) => ({
      ...prev,
      [currentColumn.current!]: newWidth,
    }))
  }

  const handleMouseUp = () => {
    isResizing.current = false
    currentColumn.current = null
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [])

  const resetWidths = () => {
    setColumnWidths(initialWidths)
    localStorage.removeItem(storageKey)
  }

  return {
    columnWidths,
    startResize,
    resetWidths,
  }
}
