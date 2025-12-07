import { User, Mail, Calendar } from 'lucide-react'
import { formatDate } from '../../utils/formatters'

interface UserData {
  id: number
  name: string
  email: string
  registered_at: string
  avatar?: string
}

export const RecentUsers = () => {
  // Demo data - replace with API when backend is ready
  const users: UserData[] = [
    {
      id: 1,
      name: 'Иван Петров',
      email: 'ivan@example.com',
      registered_at: new Date(Date.now() - 2 * 3600000).toISOString(),
    },
    {
      id: 2,
      name: 'Мария Сидорова',
      email: 'maria@example.com',
      registered_at: new Date(Date.now() - 5 * 3600000).toISOString(),
    },
    {
      id: 3,
      name: 'Алексей Смирнов',
      email: 'alex@example.com',
      registered_at: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: 4,
      name: 'Елена Ковалева',
      email: 'elena@example.com',
      registered_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    },
  ]

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getAvatarColor = (id: number) => {
    const colors = [
      'from-blue-400 to-blue-600',
      'from-purple-400 to-purple-600',
      'from-pink-400 to-pink-600',
      'from-green-400 to-green-600',
      'from-orange-400 to-orange-600',
      'from-cyan-400 to-cyan-600',
    ]
    return colors[id % colors.length]
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <User className="w-5 h-5 text-purple-600" />
          Новые пользователи
        </h3>
        <button className="text-sm text-purple-600 hover:text-purple-700 font-semibold hover:underline transition-all">
          Все пользователи →
        </button>
      </div>

      {users.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <User className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>Нет новых пользователей</p>
        </div>
      ) : (
        <div className="space-y-3">
          {users.map((user) => (
            <div
              key={user.id}
              className="flex items-center gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer group"
            >
              {/* Avatar */}
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getAvatarColor(
                  user.id
                )} flex items-center justify-center text-white font-bold shadow-md group-hover:scale-110 transition-transform duration-200`}
              >
                {getInitials(user.name)}
              </div>

              {/* User Info */}
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-gray-900 truncate group-hover:text-purple-600 transition-colors">
                  {user.name}
                </h4>
                <div className="flex items-center gap-4 mt-1">
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <Mail className="w-3 h-3" />
                    <span className="truncate">{user.email}</span>
                  </div>
                </div>
              </div>

              {/* Registration Date */}
              <div className="flex items-center gap-1 text-xs text-gray-500 flex-shrink-0">
                <Calendar className="w-3 h-3" />
                <span>
                  {formatDate(user.registered_at, {
                    month: 'short',
                    day: 'numeric',
                  })}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
