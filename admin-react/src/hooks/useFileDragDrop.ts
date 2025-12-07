import { useState, useCallback, DragEvent } from 'react'

export const useFileDragDrop = (onFilesSelected: (files: File[]) => void) => {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragEnter = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()

    // Проверяем, что мы действительно покинули зону drop
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX
    const y = e.clientY

    if (
      x < rect.left ||
      x >= rect.right ||
      y < rect.top ||
      y >= rect.bottom
    ) {
      setIsDragging(false)
    }
  }, [])

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        onFilesSelected(files)
      }
    },
    [onFilesSelected]
  )

  return {
    isDragging,
    dragHandlers: {
      onDragEnter: handleDragEnter,
      onDragLeave: handleDragLeave,
      onDragOver: handleDragOver,
      onDrop: handleDrop,
    },
  }
}
