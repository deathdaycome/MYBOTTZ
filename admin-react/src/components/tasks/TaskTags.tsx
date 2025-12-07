import { useState } from 'react'
import { X } from 'lucide-react'

interface TaskTagsProps {
  tags: string[]
  onRemove?: (tag: string) => void
  editable?: boolean
  size?: 'sm' | 'md'
  className?: string
}

const TAG_COLORS: Record<string, string> = {
  'bug': 'bg-red-100 text-red-800 border-red-300',
  'feature': 'bg-blue-100 text-blue-800 border-blue-300',
  'urgent': 'bg-orange-100 text-orange-800 border-orange-300',
  'design': 'bg-purple-100 text-purple-800 border-purple-300',
  'backend': 'bg-green-100 text-green-800 border-green-300',
  'frontend': 'bg-cyan-100 text-cyan-800 border-cyan-300',
  'mobile': 'bg-pink-100 text-pink-800 border-pink-300',
  'security': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  'testing': 'bg-indigo-100 text-indigo-800 border-indigo-300',
  'devops': 'bg-teal-100 text-teal-800 border-teal-300',
  'api': 'bg-lime-100 text-lime-800 border-lime-300',
  'database': 'bg-amber-100 text-amber-800 border-amber-300',
}

const getTagColor = (tag: string): string => {
  const lowerTag = tag.toLowerCase()

  // Точное совпадение
  if (TAG_COLORS[lowerTag]) {
    return TAG_COLORS[lowerTag]
  }

  // Частичное совпадение
  for (const [key, color] of Object.entries(TAG_COLORS)) {
    if (lowerTag.includes(key) || key.includes(lowerTag)) {
      return color
    }
  }

  // Дефолтный цвет
  return 'bg-gray-100 text-gray-800 border-gray-300'
}

export const TaskTags = ({ tags, onRemove, editable = false, size = 'sm', className = '' }: TaskTagsProps) => {
  if (!tags || tags.length === 0) return null

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
  }

  return (
    <div className={`flex flex-wrap gap-1.5 ${className}`}>
      {tags.map((tag, index) => (
        <span
          key={index}
          className={`inline-flex items-center gap-1 rounded-full border font-medium ${getTagColor(tag)} ${sizeClasses[size]} transition-all`}
        >
          <span>#{tag}</span>
          {editable && onRemove && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onRemove(tag)
              }}
              className="hover:bg-black/10 rounded-full p-0.5 transition-colors"
              title="Удалить тег"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </span>
      ))}
    </div>
  )
}

export const TagInput = ({
  value,
  onChange,
  suggestions = []
}: {
  value: string[]
  onChange: (tags: string[]) => void
  suggestions?: string[]
}) => {
  const [inputValue, setInputValue] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)

  const handleAddTag = (tag: string) => {
    const cleanTag = tag.trim().toLowerCase().replace(/^#/, '')
    if (cleanTag && !value.includes(cleanTag)) {
      onChange([...value, cleanTag])
    }
    setInputValue('')
    setShowSuggestions(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      handleAddTag(inputValue)
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      onChange(value.slice(0, -1))
    }
  }

  const filteredSuggestions = suggestions.filter(
    s => !value.includes(s) && s.toLowerCase().includes(inputValue.toLowerCase())
  )

  return (
    <div className="space-y-2">
      <div className="relative">
        <div className="flex flex-wrap gap-1.5 p-2 border border-gray-300 rounded-lg min-h-[42px] focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
          <TaskTags tags={value} editable onRemove={(tag) => onChange(value.filter(t => t !== tag))} />
          <input
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value)
              setShowSuggestions(true)
            }}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder={value.length === 0 ? "Добавить теги (Enter для добавления)..." : ""}
            className="flex-1 min-w-[120px] outline-none text-sm"
          />
        </div>

        {showSuggestions && filteredSuggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-40 overflow-y-auto">
            {filteredSuggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleAddTag(suggestion)}
                className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm flex items-center gap-2 transition-colors"
              >
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getTagColor(suggestion)}`}>
                  #{suggestion}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
      <p className="text-xs text-gray-500">
        💡 Нажмите Enter или запятую для добавления тега
      </p>
    </div>
  )
}
