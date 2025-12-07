import { useState, useEffect } from 'react'
import { X, ZoomIn, ZoomOut, RotateCw, Download, Maximize2 } from 'lucide-react'

interface ImagePreviewModalProps {
  isOpen: boolean
  onClose: () => void
  imageUrl: string
  imageName?: string
  canDownload?: boolean
}

export const ImagePreviewModal = ({
  isOpen,
  onClose,
  imageUrl,
  imageName = 'image',
  canDownload = true,
}: ImagePreviewModalProps) => {
  const [zoom, setZoom] = useState(1)
  const [rotation, setRotation] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setZoom(1)
      setRotation(0)
      setIsFullscreen(false)

      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === '+' || e.key === '=') {
        handleZoomIn()
      } else if (e.key === '-') {
        handleZoomOut()
      } else if (e.key === 'r' || e.key === 'R') {
        handleRotate()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, zoom, rotation])

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 0.25, 3))
  }

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 0.25, 0.5))
  }

  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360)
  }

  const handleDownload = async () => {
    try {
      const response = await fetch(imageUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = imageName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download failed:', err)
    }
  }

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/90 z-[9999] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-black/50 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <h3 className="text-white font-semibold truncate max-w-md">{imageName}</h3>
        </div>

        <div className="flex items-center gap-2">
          {/* Zoom Controls */}
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 0.5}
            className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Уменьшить (клавиша -)"
          >
            <ZoomOut className="w-5 h-5" />
          </button>
          <span className="text-white text-sm font-mono min-w-[3rem] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            disabled={zoom >= 3}
            className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Увеличить (клавиша +)"
          >
            <ZoomIn className="w-5 h-5" />
          </button>

          {/* Rotate */}
          <div className="w-px h-6 bg-white/20 mx-2" />
          <button
            onClick={handleRotate}
            className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
            title="Повернуть (клавиша R)"
          >
            <RotateCw className="w-5 h-5" />
          </button>

          {/* Fullscreen */}
          <button
            onClick={handleFullscreen}
            className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
            title="На весь экран"
          >
            <Maximize2 className="w-5 h-5" />
          </button>

          {/* Download */}
          {canDownload && (
            <>
              <div className="w-px h-6 bg-white/20 mx-2" />
              <button
                onClick={handleDownload}
                className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
                title="Скачать"
              >
                <Download className="w-5 h-5" />
              </button>
            </>
          )}

          {/* Close */}
          <div className="w-px h-6 bg-white/20 mx-2" />
          <button
            onClick={onClose}
            className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
            title="Закрыть (Esc)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Image Container */}
      <div
        className={`flex-1 flex items-center justify-center overflow-auto p-4 ${
          isFullscreen ? 'p-0' : ''
        }`}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            onClose()
          }
        }}
      >
        <img
          src={imageUrl}
          alt={imageName}
          className="max-w-full max-h-full object-contain transition-all duration-300 ease-out"
          style={{
            transform: `scale(${zoom}) rotate(${rotation}deg)`,
            cursor: zoom > 1 ? 'grab' : 'default',
          }}
          draggable={false}
        />
      </div>

      {/* Footer - Shortcuts Help */}
      <div className="px-6 py-3 bg-black/50 backdrop-blur-sm">
        <div className="flex items-center justify-center gap-6 text-xs text-gray-400">
          <span>
            <kbd className="px-2 py-1 bg-white/10 rounded">Esc</kbd> Закрыть
          </span>
          <span>
            <kbd className="px-2 py-1 bg-white/10 rounded">+/-</kbd> Масштаб
          </span>
          <span>
            <kbd className="px-2 py-1 bg-white/10 rounded">R</kbd> Поворот
          </span>
        </div>
      </div>
    </div>
  )
}

// Hook for previewing multiple images with navigation
export const useImageGallery = (images: string[]) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isOpen, setIsOpen] = useState(false)

  const openGallery = (index: number = 0) => {
    setCurrentIndex(index)
    setIsOpen(true)
  }

  const closeGallery = () => {
    setIsOpen(false)
  }

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length)
  }

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length)
  }

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        nextImage()
      } else if (e.key === 'ArrowLeft') {
        prevImage()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, images.length])

  return {
    currentImage: images[currentIndex] || '',
    currentIndex,
    isOpen,
    openGallery,
    closeGallery,
    nextImage,
    prevImage,
    hasNext: currentIndex < images.length - 1,
    hasPrev: currentIndex > 0,
    totalImages: images.length,
  }
}
