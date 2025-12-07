import React, { useState, useEffect } from 'react'
import {
  Bug,
  CheckCircle,
  AlertCircle,
  XCircle,
  Clock,
  Filter,
  Search,
  Plus,
  X,
  Edit2,
  Trash2,
  FileText,
  User,
  Calendar,
  Tag,
  TrendingUp,
  TestTube,
  ListChecks,
  BarChart3,
  Target,
} from 'lucide-react'

interface QualityAssuranceProps {
  projectId: number
  onClose: () => void
}

interface TestCase {
  id: number
  title: string
  description: string
  type: 'unit' | 'integration' | 'e2e' | 'manual' | 'regression' | 'smoke'
  status: 'pending' | 'passed' | 'failed' | 'skipped'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignedTo: string
  lastRun: string | null
  duration: number // в секундах
  steps: string[]
  expectedResult: string
  actualResult: string
  createdAt: string
}

interface Bug {
  id: number
  title: string
  description: string
  severity: 'trivial' | 'minor' | 'major' | 'critical' | 'blocker'
  status: 'open' | 'in-progress' | 'resolved' | 'closed' | 'reopened'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignedTo: string
  reportedBy: string
  reportedAt: string
  resolvedAt: string | null
  environment: string
  stepsToReproduce: string[]
  attachments: string[]
  tags: string[]
  linkedTestCase?: number
}

interface TestRun {
  id: number
  name: string
  startedAt: string
  completedAt: string | null
  status: 'running' | 'completed' | 'failed' | 'aborted'
  totalTests: number
  passed: number
  failed: number
  skipped: number
  duration: number
}

const QualityAssurance: React.FC<QualityAssuranceProps> = ({ projectId, onClose }) => {
  const [testCases, setTestCases] = useState<TestCase[]>([])
  const [bugs, setBugs] = useState<Bug[]>([])
  const [testRuns, setTestRuns] = useState<TestRun[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'tests' | 'bugs' | 'runs' | 'stats'>('tests')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterPriority, setFilterPriority] = useState<string>('all')
  const [showAddTestModal, setShowAddTestModal] = useState(false)
  const [showAddBugModal, setShowAddBugModal] = useState(false)
  const [selectedTest, setSelectedTest] = useState<TestCase | null>(null)
  const [selectedBug, setSelectedBug] = useState<Bug | null>(null)

  const [newTest, setNewTest] = useState({
    title: '',
    description: '',
    type: 'manual' as TestCase['type'],
    priority: 'medium' as TestCase['priority'],
    assignedTo: '',
    steps: [] as string[],
    expectedResult: '',
  })

  const [newBug, setNewBug] = useState({
    title: '',
    description: '',
    severity: 'minor' as Bug['severity'],
    priority: 'medium' as Bug['priority'],
    assignedTo: '',
    environment: 'production',
    stepsToReproduce: [] as string[],
    tags: [] as string[],
  })

  const [newStep, setNewStep] = useState('')
  const [newTag, setNewTag] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchQAData()
  }, [projectId])

  const fetchQAData = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/qa`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setTestCases(data.testCases || [])
        setBugs(data.bugs || [])
        setTestRuns(data.testRuns || [])
      } else {
        // Mock data
        setTestCases([
          {
            id: 1,
            title: 'Тест авторизации пользователя',
            description: 'Проверка входа с корректными данными',
            type: 'e2e',
            status: 'passed',
            priority: 'critical',
            assignedTo: 'Елена Козлова',
            lastRun: '2024-03-15T14:30:00',
            duration: 12,
            steps: ['Открыть страницу входа', 'Ввести email', 'Ввести пароль', 'Нажать "Войти"'],
            expectedResult: 'Пользователь успешно авторизован и перенаправлен на главную',
            actualResult: 'Успешно',
            createdAt: '2024-02-01',
          },
          {
            id: 2,
            title: 'Проверка валидации формы регистрации',
            description: 'Тест полей формы регистрации на корректность',
            type: 'integration',
            status: 'failed',
            priority: 'high',
            assignedTo: 'Елена Козлова',
            lastRun: '2024-03-15T15:00:00',
            duration: 8,
            steps: ['Открыть форму регистрации', 'Оставить поля пустыми', 'Нажать "Зарегистрироваться"'],
            expectedResult: 'Показаны сообщения об ошибках',
            actualResult: 'Email поле не показывает ошибку',
            createdAt: '2024-02-05',
          },
          {
            id: 3,
            title: 'Создание нового проекта',
            description: 'Проверка создания проекта через форму',
            type: 'manual',
            status: 'pending',
            priority: 'medium',
            assignedTo: 'Иван Петров',
            lastRun: null,
            duration: 0,
            steps: ['Перейти на страницу проектов', 'Нажать "Создать проект"', 'Заполнить форму', 'Сохранить'],
            expectedResult: 'Проект создан и отображается в списке',
            actualResult: '',
            createdAt: '2024-03-01',
          },
          {
            id: 4,
            title: 'Загрузка файлов',
            description: 'Проверка функционала загрузки файлов',
            type: 'integration',
            status: 'passed',
            priority: 'high',
            assignedTo: 'Елена Козлова',
            lastRun: '2024-03-14T10:20:00',
            duration: 15,
            steps: ['Открыть форму загрузки', 'Выбрать файл', 'Нажать "Загрузить"'],
            expectedResult: 'Файл успешно загружен',
            actualResult: 'Успешно',
            createdAt: '2024-02-10',
          },
          {
            id: 5,
            title: 'Производительность главной страницы',
            description: 'Проверка времени загрузки главной страницы',
            type: 'smoke',
            status: 'skipped',
            priority: 'low',
            assignedTo: 'Дмитрий Смирнов',
            lastRun: '2024-03-10T09:00:00',
            duration: 5,
            steps: ['Открыть главную страницу', 'Замерить время загрузки'],
            expectedResult: 'Загрузка менее 2 секунд',
            actualResult: '',
            createdAt: '2024-02-20',
          },
        ])

        setBugs([
          {
            id: 1,
            title: 'Кнопка "Сохранить" не реагирует на клик',
            description: 'При нажатии на кнопку "Сохранить" в форме редактирования проекта ничего не происходит',
            severity: 'critical',
            status: 'in-progress',
            priority: 'critical',
            assignedTo: 'Алексей Иванов',
            reportedBy: 'Елена Козлова',
            reportedAt: '2024-03-15T16:00:00',
            resolvedAt: null,
            environment: 'production',
            stepsToReproduce: [
              'Открыть проект',
              'Нажать "Редактировать"',
              'Изменить название',
              'Нажать "Сохранить"',
            ],
            attachments: ['screenshot1.png'],
            tags: ['ui', 'форма', 'critical'],
            linkedTestCase: 3,
          },
          {
            id: 2,
            title: 'Некорректное отображение даты на мобильных',
            description: 'Дата отображается в неправильном формате на мобильных устройствах',
            severity: 'minor',
            status: 'open',
            priority: 'low',
            assignedTo: 'Мария Петрова',
            reportedBy: 'Иван Петров',
            reportedAt: '2024-03-14T11:30:00',
            resolvedAt: null,
            environment: 'staging',
            stepsToReproduce: ['Открыть сайт на мобильном', 'Проверить формат даты'],
            attachments: [],
            tags: ['mobile', 'ui', 'дата'],
          },
          {
            id: 3,
            title: 'Ошибка 500 при загрузке больших файлов',
            description: 'Сервер возвращает ошибку 500 при попытке загрузить файл размером более 10MB',
            severity: 'major',
            status: 'resolved',
            priority: 'high',
            assignedTo: 'Дмитрий Смирнов',
            reportedBy: 'Елена Козлова',
            reportedAt: '2024-03-10T14:00:00',
            resolvedAt: '2024-03-13T17:30:00',
            environment: 'production',
            stepsToReproduce: ['Попытаться загрузить файл > 10MB'],
            attachments: ['error_log.txt'],
            tags: ['backend', 'файлы', 'производительность'],
          },
          {
            id: 4,
            title: 'Утечка памяти в календаре',
            description: 'Компонент календаря не освобождает память при размонтировании',
            severity: 'major',
            status: 'open',
            priority: 'medium',
            assignedTo: 'Алексей Иванов',
            reportedBy: 'Дмитрий Смирнов',
            reportedAt: '2024-03-12T09:00:00',
            resolvedAt: null,
            environment: 'development',
            stepsToReproduce: [
              'Открыть календарь',
              'Переключить несколько месяцев',
              'Закрыть календарь',
              'Проверить потребление памяти',
            ],
            attachments: ['memory_profile.png'],
            tags: ['performance', 'memory', 'календарь'],
          },
        ])

        setTestRuns([
          {
            id: 1,
            name: 'Регрессионное тестирование v2.1',
            startedAt: '2024-03-15T14:00:00',
            completedAt: '2024-03-15T15:30:00',
            status: 'completed',
            totalTests: 45,
            passed: 42,
            failed: 2,
            skipped: 1,
            duration: 5400,
          },
          {
            id: 2,
            name: 'Smoke test после деплоя',
            startedAt: '2024-03-14T10:00:00',
            completedAt: '2024-03-14T10:15:00',
            status: 'completed',
            totalTests: 12,
            passed: 12,
            failed: 0,
            skipped: 0,
            duration: 900,
          },
          {
            id: 3,
            name: 'Интеграционные тесты API',
            startedAt: '2024-03-13T16:00:00',
            completedAt: null,
            status: 'running',
            totalTests: 28,
            passed: 15,
            failed: 0,
            skipped: 0,
            duration: 0,
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching QA data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddTest = async () => {
    if (!newTest.title) {
      alert('Введите название теста')
      return
    }

    const testData: TestCase = {
      ...newTest,
      id: Date.now(),
      status: 'pending',
      lastRun: null,
      duration: 0,
      actualResult: '',
      createdAt: new Date().toISOString(),
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/qa/tests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(testData),
      })

      if (response.ok) {
        const data = await response.json()
        setTestCases([...testCases, data])
      } else {
        setTestCases([...testCases, testData])
      }

      setShowAddTestModal(false)
      setNewTest({
        title: '',
        description: '',
        type: 'manual',
        priority: 'medium',
        assignedTo: '',
        steps: [],
        expectedResult: '',
      })
    } catch (error) {
      console.error('Error adding test:', error)
    }
  }

  const handleAddBug = async () => {
    if (!newBug.title) {
      alert('Введите название бага')
      return
    }

    const bugData: Bug = {
      ...newBug,
      id: Date.now(),
      status: 'open',
      reportedBy: 'Текущий пользователь',
      reportedAt: new Date().toISOString(),
      resolvedAt: null,
      attachments: [],
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/qa/bugs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(bugData),
      })

      if (response.ok) {
        const data = await response.json()
        setBugs([...bugs, data])
      } else {
        setBugs([...bugs, bugData])
      }

      setShowAddBugModal(false)
      setNewBug({
        title: '',
        description: '',
        severity: 'minor',
        priority: 'medium',
        assignedTo: '',
        environment: 'production',
        stepsToReproduce: [],
        tags: [],
      })
    } catch (error) {
      console.error('Error adding bug:', error)
    }
  }

  const handleDeleteTest = async (testId: number) => {
    if (!confirm('Удалить тест-кейс?')) return

    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/qa/tests/${testId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      setTestCases(testCases.filter((t) => t.id !== testId))
    } catch (error) {
      console.error('Error deleting test:', error)
    }
  }

  const handleDeleteBug = async (bugId: number) => {
    if (!confirm('Удалить баг?')) return

    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/qa/bugs/${bugId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      setBugs(bugs.filter((b) => b.id !== bugId))
    } catch (error) {
      console.error('Error deleting bug:', error)
    }
  }

  const getTestStatusBadge = (status: string) => {
    const badges = {
      pending: { label: 'Ожидает', color: 'bg-gray-100 text-gray-800', icon: Clock },
      passed: { label: 'Пройден', color: 'bg-green-100 text-green-800', icon: CheckCircle },
      failed: { label: 'Провален', color: 'bg-red-100 text-red-800', icon: XCircle },
      skipped: { label: 'Пропущен', color: 'bg-yellow-100 text-yellow-800', icon: AlertCircle },
    }
    return badges[status as keyof typeof badges] || badges.pending
  }

  const getBugStatusBadge = (status: string) => {
    const badges = {
      open: { label: 'Открыт', color: 'bg-red-100 text-red-800' },
      'in-progress': { label: 'В работе', color: 'bg-blue-100 text-blue-800' },
      resolved: { label: 'Решен', color: 'bg-green-100 text-green-800' },
      closed: { label: 'Закрыт', color: 'bg-gray-100 text-gray-800' },
      reopened: { label: 'Переоткрыт', color: 'bg-orange-100 text-orange-800' },
    }
    return badges[status as keyof typeof badges] || badges.open
  }

  const getSeverityBadge = (severity: string) => {
    const badges = {
      trivial: { label: 'Тривиальный', color: 'bg-gray-100 text-gray-700' },
      minor: { label: 'Минорный', color: 'bg-blue-100 text-blue-700' },
      major: { label: 'Значительный', color: 'bg-orange-100 text-orange-700' },
      critical: { label: 'Критический', color: 'bg-red-100 text-red-700' },
      blocker: { label: 'Блокер', color: 'bg-purple-100 text-purple-700' },
    }
    return badges[severity as keyof typeof badges] || badges.minor
  }

  const calculateStats = () => {
    const totalTests = testCases.length
    const passedTests = testCases.filter((t) => t.status === 'passed').length
    const failedTests = testCases.filter((t) => t.status === 'failed').length
    const pendingTests = testCases.filter((t) => t.status === 'pending').length

    const totalBugs = bugs.length
    const openBugs = bugs.filter((b) => b.status === 'open' || b.status === 'reopened').length
    const inProgressBugs = bugs.filter((b) => b.status === 'in-progress').length
    const resolvedBugs = bugs.filter((b) => b.status === 'resolved' || b.status === 'closed').length

    const criticalBugs = bugs.filter((b) => b.severity === 'critical' || b.severity === 'blocker').length

    const passRate = totalTests > 0 ? (passedTests / totalTests) * 100 : 0
    const bugResolutionRate = totalBugs > 0 ? (resolvedBugs / totalBugs) * 100 : 0

    return {
      totalTests,
      passedTests,
      failedTests,
      pendingTests,
      totalBugs,
      openBugs,
      inProgressBugs,
      resolvedBugs,
      criticalBugs,
      passRate,
      bugResolutionRate,
    }
  }

  const stats = calculateStats()

  const filteredTests = testCases.filter((test) => {
    const matchesSearch =
      test.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      test.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = filterStatus === 'all' || test.status === filterStatus
    const matchesPriority = filterPriority === 'all' || test.priority === filterPriority
    return matchesSearch && matchesStatus && matchesPriority
  })

  const filteredBugs = bugs.filter((bug) => {
    const matchesSearch =
      bug.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bug.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bug.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesStatus = filterStatus === 'all' || bug.status === filterStatus
    const matchesPriority = filterPriority === 'all' || bug.priority === filterPriority
    return matchesSearch && matchesStatus && matchesPriority
  })

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка данных QA...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-pink-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <TestTube className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Контроль качества (QA)</h2>
              <p className="text-red-100 text-sm">Проект #{projectId}</p>
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
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <ListChecks className="w-4 h-4" />
              <span>Тестов</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalTests}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <CheckCircle className="w-4 h-4" />
              <span>Пройдено</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.passedTests}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <XCircle className="w-4 h-4" />
              <span>Провалено</span>
            </div>
            <div className="text-2xl font-bold text-red-600">{stats.failedTests}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Bug className="w-4 h-4" />
              <span>Багов</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalBugs}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <AlertCircle className="w-4 h-4" />
              <span>Критических</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">{stats.criticalBugs}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Target className="w-4 h-4" />
              <span>Pass Rate</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.passRate.toFixed(0)}%</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-4 bg-white border-b">
          <button
            onClick={() => setActiveTab('tests')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'tests' ? 'bg-red-100 text-red-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <ListChecks className="w-5 h-5" />
            Тест-кейсы ({testCases.length})
          </button>
          <button
            onClick={() => setActiveTab('bugs')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'bugs' ? 'bg-red-100 text-red-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Bug className="w-5 h-5" />
            Баги ({bugs.length})
          </button>
          <button
            onClick={() => setActiveTab('runs')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'runs' ? 'bg-red-100 text-red-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <TrendingUp className="w-5 h-5" />
            Тестовые прогоны ({testRuns.length})
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'stats' ? 'bg-red-100 text-red-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <BarChart3 className="w-5 h-5" />
            Статистика
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'tests' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Поиск тестов..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                >
                  <option value="all">Все статусы</option>
                  <option value="pending">Ожидает</option>
                  <option value="passed">Пройден</option>
                  <option value="failed">Провален</option>
                  <option value="skipped">Пропущен</option>
                </select>
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                >
                  <option value="all">Все приоритеты</option>
                  <option value="low">Низкий</option>
                  <option value="medium">Средний</option>
                  <option value="high">Высокий</option>
                  <option value="critical">Критический</option>
                </select>
                <button
                  onClick={() => setShowAddTestModal(true)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Добавить тест
                </button>
              </div>

              {/* Tests Table */}
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Название</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Тип</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Статус</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Приоритет</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Исполнитель</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Последний прогон</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredTests.map((test) => {
                      const statusBadge = getTestStatusBadge(test.status)
                      const StatusIcon = statusBadge.icon
                      return (
                        <tr key={test.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div>
                              <p className="font-medium text-gray-900">{test.title}</p>
                              <p className="text-sm text-gray-500 truncate max-w-xs">{test.description}</p>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 capitalize">{test.type}</td>
                          <td className="px-6 py-4 text-center">
                            <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${statusBadge.color}`}>
                              <StatusIcon className="w-3 h-3" />
                              {statusBadge.label}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 capitalize">{test.priority}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{test.assignedTo}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {test.lastRun ? new Date(test.lastRun).toLocaleString('ru-RU') : 'Не запускался'}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <div className="flex justify-end gap-2">
                              <button
                                onClick={() => setSelectedTest(test)}
                                className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                                aria-label="Просмотр"
                              >
                                <FileText className="w-5 h-5" />
                              </button>
                              <button
                                onClick={() => handleDeleteTest(test.id)}
                                className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                                aria-label="Удалить"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
                {filteredTests.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <ListChecks className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Нет тест-кейсов</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'bugs' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Поиск багов..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                >
                  <option value="all">Все статусы</option>
                  <option value="open">Открыт</option>
                  <option value="in-progress">В работе</option>
                  <option value="resolved">Решен</option>
                  <option value="closed">Закрыт</option>
                  <option value="reopened">Переоткрыт</option>
                </select>
                <button
                  onClick={() => setShowAddBugModal(true)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <Plus className="w-5 h-5" />
                  Добавить баг
                </button>
              </div>

              {/* Bugs List */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {filteredBugs.map((bug) => {
                  const statusBadge = getBugStatusBadge(bug.status)
                  const severityBadge = getSeverityBadge(bug.severity)
                  return (
                    <div key={bug.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-start gap-3 flex-1">
                          <Bug className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
                          <div className="flex-1">
                            <h3 className="font-bold text-lg text-gray-900 mb-2">{bug.title}</h3>
                            <p className="text-sm text-gray-600 mb-3">{bug.description}</p>
                            <div className="flex flex-wrap gap-2">
                              <span className={`text-xs px-2 py-1 rounded-full ${statusBadge.color}`}>{statusBadge.label}</span>
                              <span className={`text-xs px-2 py-1 rounded-full ${severityBadge.color}`}>
                                {severityBadge.label}
                              </span>
                              {bug.tags.map((tag, idx) => (
                                <span key={idx} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteBug(bug.id)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          aria-label="Удалить"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>

                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2 text-gray-600">
                          <User className="w-4 h-4" />
                          <span>Назначен: {bug.assignedTo}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-600">
                          <User className="w-4 h-4" />
                          <span>Репортер: {bug.reportedBy}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-600">
                          <Calendar className="w-4 h-4" />
                          <span>Создан: {new Date(bug.reportedAt).toLocaleString('ru-RU')}</span>
                        </div>
                        {bug.resolvedAt && (
                          <div className="flex items-center gap-2 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            <span>Решен: {new Date(bug.resolvedAt).toLocaleString('ru-RU')}</span>
                          </div>
                        )}
                      </div>

                      <div className="mt-4 pt-4 border-t">
                        <p className="text-xs font-medium text-gray-700 mb-2">Шаги воспроизведения:</p>
                        <ol className="list-decimal list-inside space-y-1">
                          {bug.stepsToReproduce.map((step, idx) => (
                            <li key={idx} className="text-sm text-gray-600">
                              {step}
                            </li>
                          ))}
                        </ol>
                      </div>

                      <button
                        onClick={() => setSelectedBug(bug)}
                        className="w-full mt-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                      >
                        Подробнее
                      </button>
                    </div>
                  )
                })}
              </div>

              {filteredBugs.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <Bug className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Нет багов</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'runs' && (
            <div className="space-y-4">
              {testRuns.map((run) => {
                const isRunning = run.status === 'running'
                return (
                  <div key={run.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-bold text-lg text-gray-900">{run.name}</h3>
                        <p className="text-sm text-gray-500">
                          Начат: {new Date(run.startedAt).toLocaleString('ru-RU')}
                          {run.completedAt && ` • Завершен: ${new Date(run.completedAt).toLocaleString('ru-RU')}`}
                        </p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          run.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : run.status === 'running'
                            ? 'bg-blue-100 text-blue-800'
                            : run.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {run.status === 'completed'
                          ? 'Завершен'
                          : run.status === 'running'
                          ? 'Выполняется'
                          : run.status === 'failed'
                          ? 'Провален'
                          : 'Прерван'}
                      </span>
                    </div>

                    <div className="grid grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Всего тестов</p>
                        <p className="text-2xl font-bold text-gray-900">{run.totalTests}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Пройдено</p>
                        <p className="text-2xl font-bold text-green-600">{run.passed}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Провалено</p>
                        <p className="text-2xl font-bold text-red-600">{run.failed}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Пропущено</p>
                        <p className="text-2xl font-bold text-yellow-600">{run.skipped}</p>
                      </div>
                    </div>

                    <div className="w-full bg-gray-200 rounded-full h-4">
                      <div className="flex h-4 rounded-full overflow-hidden">
                        {run.passed > 0 && (
                          <div
                            className="bg-green-500"
                            style={{ width: `${(run.passed / run.totalTests) * 100}%` }}
                          ></div>
                        )}
                        {run.failed > 0 && (
                          <div
                            className="bg-red-500"
                            style={{ width: `${(run.failed / run.totalTests) * 100}%` }}
                          ></div>
                        )}
                        {run.skipped > 0 && (
                          <div
                            className="bg-yellow-500"
                            style={{ width: `${(run.skipped / run.totalTests) * 100}%` }}
                          ></div>
                        )}
                      </div>
                    </div>

                    {!isRunning && run.duration > 0 && (
                      <p className="text-sm text-gray-500 mt-2">
                        Длительность: {Math.floor(run.duration / 60)} мин {run.duration % 60} сек
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Статистика тестов</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-600">Pass Rate</span>
                        <span className="text-sm font-medium text-gray-900">{stats.passRate.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div className="bg-green-500 h-3 rounded-full" style={{ width: `${stats.passRate}%` }}></div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Пройдено</p>
                        <p className="text-2xl font-bold text-green-600">{stats.passedTests}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Провалено</p>
                        <p className="text-2xl font-bold text-red-600">{stats.failedTests}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Ожидает</p>
                        <p className="text-2xl font-bold text-gray-600">{stats.pendingTests}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Всего</p>
                        <p className="text-2xl font-bold text-blue-600">{stats.totalTests}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Статистика багов</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray-600">Процент решенных</span>
                        <span className="text-sm font-medium text-gray-900">{stats.bugResolutionRate.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-blue-500 h-3 rounded-full"
                          style={{ width: `${stats.bugResolutionRate}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Открыто</p>
                        <p className="text-2xl font-bold text-red-600">{stats.openBugs}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">В работе</p>
                        <p className="text-2xl font-bold text-blue-600">{stats.inProgressBugs}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Решено</p>
                        <p className="text-2xl font-bold text-green-600">{stats.resolvedBugs}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Критических</p>
                        <p className="text-2xl font-bold text-purple-600">{stats.criticalBugs}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Add Test Modal */}
        {showAddTestModal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 overflow-y-auto">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl my-8">
              <h3 className="text-xl font-bold mb-4">Добавить тест-кейс</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название *</label>
                  <input
                    type="text"
                    value={newTest.title}
                    onChange={(e) => setNewTest({ ...newTest, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                  <textarea
                    value={newTest.description}
                    onChange={(e) => setNewTest({ ...newTest, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Тип</label>
                    <select
                      value={newTest.type}
                      onChange={(e) => setNewTest({ ...newTest, type: e.target.value as TestCase['type'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="unit">Unit</option>
                      <option value="integration">Integration</option>
                      <option value="e2e">E2E</option>
                      <option value="manual">Manual</option>
                      <option value="regression">Regression</option>
                      <option value="smoke">Smoke</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Приоритет</label>
                    <select
                      value={newTest.priority}
                      onChange={(e) => setNewTest({ ...newTest, priority: e.target.value as TestCase['priority'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="low">Низкий</option>
                      <option value="medium">Средний</option>
                      <option value="high">Высокий</option>
                      <option value="critical">Критический</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Исполнитель</label>
                  <input
                    type="text"
                    value={newTest.assignedTo}
                    onChange={(e) => setNewTest({ ...newTest, assignedTo: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Шаги</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newStep}
                      onChange={(e) => setNewStep(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newStep) {
                          setNewTest({ ...newTest, steps: [...newTest.steps, newStep] })
                          setNewStep('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Добавить шаг (Enter)"
                    />
                    <button
                      onClick={() => {
                        if (newStep) {
                          setNewTest({ ...newTest, steps: [...newTest.steps, newStep] })
                          setNewStep('')
                        }
                      }}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <ol className="list-decimal list-inside space-y-1">
                    {newTest.steps.map((step, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-center justify-between bg-gray-50 p-2 rounded">
                        <span>{step}</span>
                        <button
                          onClick={() => setNewTest({ ...newTest, steps: newTest.steps.filter((_, i) => i !== idx) })}
                          className="text-red-600 hover:text-red-800"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Ожидаемый результат</label>
                  <textarea
                    value={newTest.expectedResult}
                    onChange={(e) => setNewTest({ ...newTest, expectedResult: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddTestModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddTest}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Добавить
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Add Bug Modal */}
        {showAddBugModal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 overflow-y-auto">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl my-8">
              <h3 className="text-xl font-bold mb-4">Добавить баг</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название *</label>
                  <input
                    type="text"
                    value={newBug.title}
                    onChange={(e) => setNewBug({ ...newBug, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                  <textarea
                    value={newBug.description}
                    onChange={(e) => setNewBug({ ...newBug, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Серьезность</label>
                    <select
                      value={newBug.severity}
                      onChange={(e) => setNewBug({ ...newBug, severity: e.target.value as Bug['severity'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="trivial">Тривиальный</option>
                      <option value="minor">Минорный</option>
                      <option value="major">Значительный</option>
                      <option value="critical">Критический</option>
                      <option value="blocker">Блокер</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Приоритет</label>
                    <select
                      value={newBug.priority}
                      onChange={(e) => setNewBug({ ...newBug, priority: e.target.value as Bug['priority'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="low">Низкий</option>
                      <option value="medium">Средний</option>
                      <option value="high">Высокий</option>
                      <option value="critical">Критический</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Назначен</label>
                    <input
                      type="text"
                      value={newBug.assignedTo}
                      onChange={(e) => setNewBug({ ...newBug, assignedTo: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Окружение</label>
                    <input
                      type="text"
                      value={newBug.environment}
                      onChange={(e) => setNewBug({ ...newBug, environment: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Шаги воспроизведения</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newStep}
                      onChange={(e) => setNewStep(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newStep) {
                          setNewBug({ ...newBug, stepsToReproduce: [...newBug.stepsToReproduce, newStep] })
                          setNewStep('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Добавить шаг (Enter)"
                    />
                    <button
                      onClick={() => {
                        if (newStep) {
                          setNewBug({ ...newBug, stepsToReproduce: [...newBug.stepsToReproduce, newStep] })
                          setNewStep('')
                        }
                      }}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <ol className="list-decimal list-inside space-y-1">
                    {newBug.stepsToReproduce.map((step, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-center justify-between bg-gray-50 p-2 rounded">
                        <span>{step}</span>
                        <button
                          onClick={() =>
                            setNewBug({
                              ...newBug,
                              stepsToReproduce: newBug.stepsToReproduce.filter((_, i) => i !== idx),
                            })
                          }
                          className="text-red-600 hover:text-red-800"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Теги</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newTag) {
                          setNewBug({ ...newBug, tags: [...newBug.tags, newTag] })
                          setNewTag('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Добавить тег (Enter)"
                    />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {newBug.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-full"
                      >
                        {tag}
                        <button
                          onClick={() => setNewBug({ ...newBug, tags: newBug.tags.filter((_, i) => i !== idx) })}
                          className="hover:text-gray-900"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddBugModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddBug}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
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

export default QualityAssurance
