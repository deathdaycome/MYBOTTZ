import React, { useState, useEffect } from 'react'
import {
  Users,
  UserPlus,
  X,
  Search,
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle,
  Filter,
  Calendar,
  BarChart3,
  Settings,
  Mail,
  Phone,
  Award,
} from 'lucide-react'

interface TeamResourceManagementProps {
  projectId: number
  onClose: () => void
}

interface TeamMember {
  id: number
  name: string
  email: string
  phone: string
  role: string
  department: string
  avatar?: string
  availability: number // Процент доступности (0-100)
  allocatedHours: number // Выделенные часы
  actualHours: number // Фактически отработанные часы
  skills: string[]
  performance: number // Оценка производительности (1-5)
  status: 'available' | 'busy' | 'overloaded' | 'vacation'
  tasks: number // Количество активных задач
  completionRate: number // Процент выполненных задач
  joinedAt: string
}

interface Allocation {
  id: number
  memberId: number
  projectId: number
  hoursPerWeek: number
  startDate: string
  endDate: string
  notes: string
}

interface Skill {
  name: string
  level: number // 1-5
  category: string
}

const TeamResourceManagement: React.FC<TeamResourceManagementProps> = ({ projectId, onClose }) => {
  const [team, setTeam] = useState<TeamMember[]>([])
  const [allocations, setAllocations] = useState<Allocation[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterRole, setFilterRole] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [showAddMember, setShowAddMember] = useState(false)
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'allocation' | 'skills' | 'performance'>('overview')

  // Новый член команды
  const [newMember, setNewMember] = useState({
    name: '',
    email: '',
    phone: '',
    role: 'developer',
    department: 'development',
    availability: 100,
    allocatedHours: 40,
    skills: [] as string[],
  })

  // Новая аллокация
  const [newAllocation, setNewAllocation] = useState({
    memberId: 0,
    hoursPerWeek: 40,
    startDate: new Date().toISOString().slice(0, 10),
    endDate: '',
    notes: '',
  })

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchTeam()
  }, [projectId])

  const fetchTeam = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/team`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setTeam(data.team || [])
        setAllocations(data.allocations || [])
      } else {
        // Mock data
        setTeam([
          {
            id: 1,
            name: 'Алексей Иванов',
            email: 'alexey@company.com',
            phone: '+7 (999) 123-45-67',
            role: 'Team Lead',
            department: 'Development',
            availability: 80,
            allocatedHours: 32,
            actualHours: 35,
            skills: ['React', 'Node.js', 'TypeScript', 'Leadership'],
            performance: 4.8,
            status: 'busy',
            tasks: 8,
            completionRate: 92,
            joinedAt: '2024-01-15',
          },
          {
            id: 2,
            name: 'Мария Петрова',
            email: 'maria@company.com',
            phone: '+7 (999) 234-56-78',
            role: 'Frontend Developer',
            department: 'Development',
            availability: 100,
            allocatedHours: 40,
            actualHours: 38,
            skills: ['React', 'CSS', 'JavaScript', 'Figma'],
            performance: 4.5,
            status: 'available',
            tasks: 5,
            completionRate: 88,
            joinedAt: '2024-02-01',
          },
          {
            id: 3,
            name: 'Дмитрий Смирнов',
            email: 'dmitry@company.com',
            phone: '+7 (999) 345-67-89',
            role: 'Backend Developer',
            department: 'Development',
            availability: 50,
            allocatedHours: 20,
            actualHours: 22,
            skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
            performance: 4.7,
            status: 'busy',
            tasks: 12,
            completionRate: 85,
            joinedAt: '2024-01-20',
          },
          {
            id: 4,
            name: 'Елена Козлова',
            email: 'elena@company.com',
            phone: '+7 (999) 456-78-90',
            role: 'QA Engineer',
            department: 'Quality Assurance',
            availability: 120,
            allocatedHours: 48,
            actualHours: 52,
            skills: ['Testing', 'Selenium', 'Jira', 'API Testing'],
            performance: 4.2,
            status: 'overloaded',
            tasks: 15,
            completionRate: 78,
            joinedAt: '2024-02-15',
          },
          {
            id: 5,
            name: 'Сергей Новиков',
            email: 'sergey@company.com',
            phone: '+7 (999) 567-89-01',
            role: 'DevOps Engineer',
            department: 'Operations',
            availability: 0,
            allocatedHours: 0,
            actualHours: 0,
            skills: ['Docker', 'Kubernetes', 'AWS', 'CI/CD'],
            performance: 4.9,
            status: 'vacation',
            tasks: 0,
            completionRate: 95,
            joinedAt: '2024-01-10',
          },
        ])
        setAllocations([
          {
            id: 1,
            memberId: 1,
            projectId,
            hoursPerWeek: 32,
            startDate: '2024-01-15',
            endDate: '2024-06-30',
            notes: 'Руководитель проекта, отвечает за архитектуру',
          },
          {
            id: 2,
            memberId: 2,
            projectId,
            hoursPerWeek: 40,
            startDate: '2024-02-01',
            endDate: '2024-12-31',
            notes: 'Основная разработка UI компонентов',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching team:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddMember = async () => {
    if (!newMember.name || !newMember.email) {
      alert('Заполните обязательные поля (имя и email)')
      return
    }

    const memberData = {
      ...newMember,
      id: Date.now(),
      actualHours: 0,
      performance: 0,
      status: 'available' as const,
      tasks: 0,
      completionRate: 0,
      joinedAt: new Date().toISOString().slice(0, 10),
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/team`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(memberData),
      })

      if (response.ok) {
        const data = await response.json()
        setTeam([...team, data])
      } else {
        setTeam([...team, memberData])
      }

      setShowAddMember(false)
      setNewMember({
        name: '',
        email: '',
        phone: '',
        role: 'developer',
        department: 'development',
        availability: 100,
        allocatedHours: 40,
        skills: [],
      })
    } catch (error) {
      console.error('Error adding member:', error)
    }
  }

  const handleRemoveMember = async (memberId: number) => {
    if (!confirm('Удалить члена команды из проекта?')) return

    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/team/${memberId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      setTeam(team.filter((m) => m.id !== memberId))
      setAllocations(allocations.filter((a) => a.memberId !== memberId))
    } catch (error) {
      console.error('Error removing member:', error)
    }
  }

  const handleAddAllocation = async () => {
    if (!newAllocation.memberId || !newAllocation.endDate) {
      alert('Выберите члена команды и дату окончания')
      return
    }

    const allocationData = {
      ...newAllocation,
      id: Date.now(),
      projectId,
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/allocations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(allocationData),
      })

      if (response.ok) {
        const data = await response.json()
        setAllocations([...allocations, data])
      } else {
        setAllocations([...allocations, allocationData])
      }

      setNewAllocation({
        memberId: 0,
        hoursPerWeek: 40,
        startDate: new Date().toISOString().slice(0, 10),
        endDate: '',
        notes: '',
      })
    } catch (error) {
      console.error('Error adding allocation:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      available: { label: 'Доступен', color: 'bg-green-100 text-green-800' },
      busy: { label: 'Занят', color: 'bg-yellow-100 text-yellow-800' },
      overloaded: { label: 'Перегружен', color: 'bg-red-100 text-red-800' },
      vacation: { label: 'Отпуск', color: 'bg-gray-100 text-gray-800' },
    }
    return badges[status as keyof typeof badges] || badges.available
  }

  const getPerformanceColor = (performance: number) => {
    if (performance >= 4.5) return 'text-green-600'
    if (performance >= 4.0) return 'text-blue-600'
    if (performance >= 3.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  const filteredTeam = team.filter((member) => {
    const matchesSearch =
      member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.role.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRole = filterRole === 'all' || member.role === filterRole
    const matchesStatus = filterStatus === 'all' || member.status === filterStatus
    return matchesSearch && matchesRole && matchesStatus
  })

  const calculateTeamStats = () => {
    const totalMembers = team.length
    const totalAllocatedHours = team.reduce((sum, m) => sum + m.allocatedHours, 0)
    const totalActualHours = team.reduce((sum, m) => sum + m.actualHours, 0)
    const avgPerformance = team.length > 0 ? team.reduce((sum, m) => sum + m.performance, 0) / team.length : 0
    const overloadedCount = team.filter((m) => m.status === 'overloaded').length
    const availableCount = team.filter((m) => m.status === 'available').length

    return {
      totalMembers,
      totalAllocatedHours,
      totalActualHours,
      avgPerformance,
      overloadedCount,
      availableCount,
      utilizationRate: totalAllocatedHours > 0 ? (totalActualHours / totalAllocatedHours) * 100 : 0,
    }
  }

  const stats = calculateTeamStats()

  const roles = Array.from(new Set(team.map((m) => m.role)))

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка команды...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Управление командой и ресурсами</h2>
              <p className="text-purple-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            aria-label="Закрыть"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Users className="w-4 h-4" />
              <span>Команда</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalMembers}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Clock className="w-4 h-4" />
              <span>Выделено ч/нед</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalAllocatedHours}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <TrendingUp className="w-4 h-4" />
              <span>Факт. ч/нед</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalActualHours}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <BarChart3 className="w-4 h-4" />
              <span>Использование</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.utilizationRate.toFixed(0)}%</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Award className="w-4 h-4" />
              <span>Ср. оценка</span>
            </div>
            <div className={`text-2xl font-bold ${getPerformanceColor(stats.avgPerformance)}`}>
              {stats.avgPerformance.toFixed(1)}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <AlertTriangle className="w-4 h-4" />
              <span>Перегружено</span>
            </div>
            <div className="text-2xl font-bold text-red-600">{stats.overloadedCount}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-4 bg-white border-b">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'overview' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Обзор команды
          </button>
          <button
            onClick={() => setActiveTab('allocation')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'allocation' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Распределение ресурсов
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'skills' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Навыки
          </button>
          <button
            onClick={() => setActiveTab('performance')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'performance' ? 'bg-purple-100 text-purple-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Производительность
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Search and Filters */}
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Поиск по имени, email, роли..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <select
                  value={filterRole}
                  onChange={(e) => setFilterRole(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="all">Все роли</option>
                  {roles.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="all">Все статусы</option>
                  <option value="available">Доступен</option>
                  <option value="busy">Занят</option>
                  <option value="overloaded">Перегружен</option>
                  <option value="vacation">Отпуск</option>
                </select>
                <button
                  onClick={() => setShowAddMember(true)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                >
                  <UserPlus className="w-5 h-5" />
                  Добавить члена
                </button>
              </div>

              {/* Team Members */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredTeam.map((member) => {
                  const badge = getStatusBadge(member.status)
                  const allocation = allocations.find((a) => a.memberId === member.id)
                  return (
                    <div key={member.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start gap-3">
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold text-lg">
                            {member.name.charAt(0)}
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{member.name}</h3>
                            <p className="text-sm text-gray-500">{member.role}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <span className={`text-xs px-2 py-1 rounded-full ${badge.color}`}>{badge.label}</span>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveMember(member.id)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          aria-label="Удалить"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>

                      <div className="grid grid-cols-2 gap-2 mb-3">
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Mail className="w-4 h-4" />
                          <span className="truncate">{member.email}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Phone className="w-4 h-4" />
                          <span>{member.phone}</span>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Доступность:</span>
                          <span className="font-medium">{member.availability}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              member.availability <= 80
                                ? 'bg-green-500'
                                : member.availability <= 100
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min(member.availability, 100)}%` }}
                          ></div>
                        </div>

                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Часы (выделено/факт):</span>
                          <span className="font-medium">
                            {member.allocatedHours} / {member.actualHours}
                          </span>
                        </div>

                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Активные задачи:</span>
                          <span className="font-medium">{member.tasks}</span>
                        </div>

                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Выполнение:</span>
                          <span className="font-medium">{member.completionRate}%</span>
                        </div>

                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Производительность:</span>
                          <span className={`font-bold ${getPerformanceColor(member.performance)}`}>
                            {member.performance.toFixed(1)} / 5.0
                          </span>
                        </div>
                      </div>

                      <div className="mt-3 pt-3 border-t">
                        <p className="text-xs text-gray-500 mb-2">Навыки:</p>
                        <div className="flex flex-wrap gap-1">
                          {member.skills.map((skill, idx) => (
                            <span key={idx} className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>

                      {allocation && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-xs text-gray-500">
                            Аллокация: {allocation.hoursPerWeek} ч/нед ({allocation.startDate} - {allocation.endDate})
                          </p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>

              {filteredTeam.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Нет членов команды, соответствующих фильтрам</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'allocation' && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Добавить распределение ресурсов</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Член команды *</label>
                    <select
                      value={newAllocation.memberId}
                      onChange={(e) => setNewAllocation({ ...newAllocation, memberId: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value={0}>Выберите члена команды</option>
                      {team.map((member) => (
                        <option key={member.id} value={member.id}>
                          {member.name} - {member.role}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Часов в неделю</label>
                    <input
                      type="number"
                      min="1"
                      max="168"
                      value={newAllocation.hoursPerWeek}
                      onChange={(e) => setNewAllocation({ ...newAllocation, hoursPerWeek: parseInt(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Дата начала</label>
                    <input
                      type="date"
                      value={newAllocation.startDate}
                      onChange={(e) => setNewAllocation({ ...newAllocation, startDate: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Дата окончания *</label>
                    <input
                      type="date"
                      value={newAllocation.endDate}
                      onChange={(e) => setNewAllocation({ ...newAllocation, endDate: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Примечания</label>
                    <textarea
                      value={newAllocation.notes}
                      onChange={(e) => setNewAllocation({ ...newAllocation, notes: e.target.value })}
                      rows={2}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Дополнительная информация о распределении..."
                    />
                  </div>
                </div>
                <div className="flex justify-end mt-4">
                  <button
                    onClick={handleAddAllocation}
                    className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Добавить распределение
                  </button>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Член команды</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Роль</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Часов/нед</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Период</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Примечания</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {allocations.map((allocation) => {
                        const member = team.find((m) => m.id === allocation.memberId)
                        if (!member) return null
                        return (
                          <tr key={allocation.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4">
                              <div className="font-medium text-gray-900">{member.name}</div>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">{member.role}</td>
                            <td className="px-6 py-4 text-sm text-gray-900 font-medium">{allocation.hoursPerWeek}</td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              {allocation.startDate} - {allocation.endDate}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">{allocation.notes || '-'}</td>
                            <td className="px-6 py-4 text-right">
                              <button
                                onClick={() => setAllocations(allocations.filter((a) => a.id !== allocation.id))}
                                className="text-red-600 hover:text-red-800 text-sm font-medium"
                              >
                                Удалить
                              </button>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                  {allocations.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                      <Calendar className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p>Нет распределений ресурсов</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'skills' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {team.map((member) => (
                  <div key={member.id} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold">
                        {member.name.charAt(0)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{member.name}</h3>
                        <p className="text-sm text-gray-500">{member.role}</p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      {member.skills.map((skill, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <span className="text-sm text-gray-700 flex-1">{skill}</span>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((level) => (
                              <div
                                key={level}
                                className={`w-2 h-6 rounded ${
                                  level <= 3 + idx % 2 ? 'bg-purple-600' : 'bg-gray-200'
                                }`}
                              ></div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Член команды</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Роль</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Оценка</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Задачи</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Выполнение</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Часы (план/факт)</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Статус</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {team
                        .sort((a, b) => b.performance - a.performance)
                        .map((member) => {
                          const badge = getStatusBadge(member.status)
                          return (
                            <tr key={member.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4">
                                <div className="flex items-center gap-3">
                                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-bold text-sm">
                                    {member.name.charAt(0)}
                                  </div>
                                  <span className="font-medium text-gray-900">{member.name}</span>
                                </div>
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">{member.role}</td>
                              <td className="px-6 py-4 text-center">
                                <span className={`font-bold text-lg ${getPerformanceColor(member.performance)}`}>
                                  {member.performance.toFixed(1)}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-center text-sm text-gray-900">{member.tasks}</td>
                              <td className="px-6 py-4 text-center">
                                <span className="font-medium text-gray-900">{member.completionRate}%</span>
                              </td>
                              <td className="px-6 py-4 text-center text-sm text-gray-900">
                                {member.allocatedHours} / {member.actualHours}
                              </td>
                              <td className="px-6 py-4 text-center">
                                <span className={`text-xs px-2 py-1 rounded-full ${badge.color}`}>{badge.label}</span>
                              </td>
                            </tr>
                          )
                        })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Add Member Modal */}
        {showAddMember && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">Добавить члена команды</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Имя *</label>
                  <input
                    type="text"
                    value={newMember.name}
                    onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Иван Иванов"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                  <input
                    type="email"
                    value={newMember.email}
                    onChange={(e) => setNewMember({ ...newMember, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="ivan@company.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Телефон</label>
                  <input
                    type="tel"
                    value={newMember.phone}
                    onChange={(e) => setNewMember({ ...newMember, phone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="+7 (999) 123-45-67"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Роль</label>
                  <input
                    type="text"
                    value={newMember.role}
                    onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Frontend Developer"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Отдел</label>
                  <input
                    type="text"
                    value={newMember.department}
                    onChange={(e) => setNewMember({ ...newMember, department: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Development"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Доступность (%) - {newMember.availability}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="200"
                    step="10"
                    value={newMember.availability}
                    onChange={(e) => setNewMember({ ...newMember, availability: parseInt(e.target.value) })}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Выделенные часы в неделю</label>
                  <input
                    type="number"
                    min="1"
                    max="168"
                    value={newMember.allocatedHours}
                    onChange={(e) => setNewMember({ ...newMember, allocatedHours: parseInt(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddMember(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddMember}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Добавить
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TeamResourceManagement
