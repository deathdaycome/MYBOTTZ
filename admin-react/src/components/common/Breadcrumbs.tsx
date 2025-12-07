import { ChevronRight, Home } from 'lucide-react'
import { Link } from 'react-router-dom'

interface BreadcrumbItem {
  label: string
  path?: string
  icon?: React.ReactNode
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  showHome?: boolean
}

export const Breadcrumbs = ({ items, showHome = true }: BreadcrumbsProps) => {
  const allItems: BreadcrumbItem[] = showHome
    ? [{ label: 'Главная', path: '/', icon: <Home className="w-4 h-4" /> }, ...items]
    : items

  return (
    <nav className="flex items-center gap-2 text-sm">
      {allItems.map((item, index) => {
        const isLast = index === allItems.length - 1

        return (
          <div key={index} className="flex items-center gap-2">
            {item.path && !isLast ? (
              <Link
                to={item.path}
                className="flex items-center gap-1.5 text-gray-600 hover:text-blue-600 transition-colors font-medium"
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            ) : (
              <div
                className={`flex items-center gap-1.5 ${
                  isLast ? 'text-gray-900 font-semibold' : 'text-gray-500'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </div>
            )}

            {!isLast && <ChevronRight className="w-4 h-4 text-gray-400" />}
          </div>
        )
      })}
    </nav>
  )
}

// Helper to generate breadcrumbs from path
export const generateBreadcrumbsFromPath = (pathname: string): BreadcrumbItem[] => {
  const segments = pathname.split('/').filter(Boolean)

  return segments.map((segment, index) => {
    const path = '/' + segments.slice(0, index + 1).join('/')
    const label = segment
      .split('-')
      .filter((word) => word.length > 0)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')

    return {
      label,
      path: index < segments.length - 1 ? path : undefined,
    }
  })
}
