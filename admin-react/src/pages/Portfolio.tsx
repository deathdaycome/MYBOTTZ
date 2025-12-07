import { useState, useEffect, useCallback, useMemo, FormEvent } from 'react'
import {
  Briefcase,
  Plus,
  Search,
  Filter,
  Grid,
  List,
  RefreshCw,
  Edit2,
  Trash2,
  X,
  Star,
  Eye,
  EyeOff,
  Heart,
  ExternalLink,
  Github,
  Upload,
  Loader2,
  Image as ImageIcon,
  Send,
  Calendar,
  DollarSign,
  Clock,
  TrendingUp,
  Package,
  Award,
} from 'lucide-react'
import portfolioApi from '../api/portfolio'
import type {
  PortfolioProject,
  PortfolioStats,
  Category,
  PortfolioCreateData,
} from '../api/portfolio'

export const Portfolio = () => {
  // ============= STATE =============
  const [loading, setLoading] = useState(true)
  const [projects, setProjects] = useState<PortfolioProject[]>([])
  const [stats, setStats] = useState<PortfolioStats | null>(null)
  const [categories, setCategories] = useState<Category[]>([])

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const itemsPerPage = 12

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [sortBy, setSortBy] = useState('created_desc')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  // Modals
  const [showModal, setShowModal] = useState(false)
  const [editingProject, setEditingProject] = useState<PortfolioProject | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Form data
  const [formData, setFormData] = useState<PortfolioCreateData>({
    title: '',
    subtitle: '',
    description: '',
    category: '',
    technologies: '',
    complexity: 'medium',
    complexity_level: 5,
    development_time: undefined,
    cost: undefined,
    cost_range: '',
    show_cost: false,
    demo_link: '',
    repository_link: '',
    external_links: '[]',
    is_featured: false,
    is_visible: true,
    sort_order: 0,
    tags: '',
    client_name: '',
    project_status: 'completed',
    completed_at: '',
  })

  const [mainImageFile, setMainImageFile] = useState<File | null>(null)
  const [mainImagePreview, setMainImagePreview] = useState<string>('')
  const [removeMainImage, setRemoveMainImage] = useState(false)

  // Toast notifications
  const [toasts, setToasts] = useState<
    Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>
  >([])

  const showToast = useCallback(
    (message: string, type: 'success' | 'error' | 'info' = 'info') => {
      const id = Date.now().toString()
      setToasts((prev) => [...prev, { id, message, type }])
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
      }, 4000)
    },
    []
  )

  // ============= LOAD DATA =============

  const loadData = useCallback(async () => {
    try {
      setLoading(true)

      const visibleOnly = statusFilter === 'active'
      const featuredOnly = statusFilter === 'featured'

      const [projectsRes, statsRes, categoriesRes] = await Promise.all([
        portfolioApi.getList({
          page: currentPage,
          per_page: itemsPerPage,
          category: categoryFilter || undefined,
          search: searchQuery || undefined,
          featured_only: featuredOnly,
          visible_only: visibleOnly,
          sort_by: sortBy,
        }),
        portfolioApi.getStats(),
        portfolioApi.getCategories(),
      ])

      if (projectsRes.success) {
        setProjects(projectsRes.data)
        setTotalPages(projectsRes.pagination.pages)
        setTotalItems(projectsRes.pagination.total)
      }

      if (statsRes.success) {
        setStats(statsRes.stats)
      }

      if (categoriesRes.success) {
        setCategories(categoriesRes.categories)
      }
    } catch (error: any) {
      console.error('Error loading portfolio:', error)
      showToast('Ошибка загрузки данных', 'error')
    } finally {
      setLoading(false)
    }
  }, [currentPage, categoryFilter, searchQuery, sortBy, statusFilter, showToast])

  useEffect(() => {
    loadData()
  }, [loadData])

  // ============= HANDLERS =============

  const handleOpenModal = (project?: PortfolioProject) => {
    if (project) {
      setEditingProject(project)
      setFormData({
        title: project.title,
        subtitle: project.subtitle || '',
        description: project.description,
        category: project.category,
        technologies: project.technologies || '',
        complexity: project.complexity,
        complexity_level: project.complexity_level,
        development_time: project.development_time,
        cost: project.cost,
        cost_range: project.cost_range || '',
        show_cost: project.show_cost,
        demo_link: project.demo_link || '',
        repository_link: project.repository_link || '',
        external_links: JSON.stringify(project.external_links || []),
        is_featured: project.is_featured,
        is_visible: project.is_visible,
        sort_order: project.sort_order,
        tags: project.tags || '',
        client_name: project.client_name || '',
        project_status: project.project_status,
        completed_at: project.completed_at || '',
      })
      if (project.main_image) {
        setMainImagePreview(`http://localhost:8001/uploads/portfolio/${project.main_image}`)
      }
    } else {
      setEditingProject(null)
      resetForm()
    }
    setShowModal(true)
    document.body.style.overflow = 'hidden'
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingProject(null)
    resetForm()
    document.body.style.overflow = 'auto'
  }

  const resetForm = () => {
    setFormData({
      title: '',
      subtitle: '',
      description: '',
      category: '',
      technologies: '',
      complexity: 'medium',
      complexity_level: 5,
      development_time: undefined,
      cost: undefined,
      cost_range: '',
      show_cost: false,
      demo_link: '',
      repository_link: '',
      external_links: '[]',
      is_featured: false,
      is_visible: true,
      sort_order: 0,
      tags: '',
      client_name: '',
      project_status: 'completed',
      completed_at: '',
    })
    setMainImageFile(null)
    setMainImagePreview('')
    setRemoveMainImage(false)
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        showToast('Файл слишком большой. Максимум 10MB', 'error')
        return
      }

      setMainImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setMainImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      setRemoveMainImage(false)
    }
  }

  const handleRemoveImage = () => {
    setMainImageFile(null)
    setMainImagePreview('')
    setRemoveMainImage(true)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!formData.title || !formData.description || !formData.category) {
      showToast('Заполните обязательные поля', 'error')
      return
    }

    try {
      setIsSubmitting(true)

      const submitData: PortfolioCreateData & { remove_main_image?: boolean } = {
        ...formData,
        main_image: mainImageFile || undefined,
      }

      if (editingProject) {
        submitData.remove_main_image = removeMainImage
        const response = await portfolioApi.update(editingProject.id, submitData)
        if (response.success) {
          showToast(response.message, 'success')
          handleCloseModal()
          loadData()
        }
      } else {
        const response = await portfolioApi.create(submitData)
        if (response.success) {
          showToast(response.message, 'success')
          handleCloseModal()
          loadData()
        }
      }
    } catch (error: any) {
      console.error('Error saving project:', error)
      showToast(error.response?.data?.detail || 'Ошибка сохранения проекта', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async (project: PortfolioProject) => {
    if (
      !confirm(
        `Вы уверены, что хотите удалить проект "${project.title}"? Это действие нельзя отменить.`
      )
    )
      return

    try {
      const response = await portfolioApi.delete(project.id)
      if (response.success) {
        showToast(response.message, 'success')
        loadData()
      }
    } catch (error: any) {
      console.error('Error deleting project:', error)
      showToast(error.response?.data?.detail || 'Ошибка удаления проекта', 'error')
    }
  }

  const handlePublishToTelegram = async (project: PortfolioProject) => {
    if (project.is_published) {
      showToast('Проект уже опубликован в Telegram', 'info')
      return
    }

    try {
      const response = await portfolioApi.publishToTelegram(project.id)
      if (response.success) {
        showToast(response.message, 'success')
        loadData()
      }
    } catch (error: any) {
      console.error('Error publishing to Telegram:', error)
      showToast(error.response?.data?.detail || 'Ошибка публикации в Telegram', 'error')
    }
  }

  // ============= HELPERS =============

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  }

  const getCategoryName = (categoryId: string) => {
    const categoryMap: Record<string, string> = {
      telegram_bots: 'Telegram боты',
      web_development: 'Веб-разработка',
      mobile_apps: 'Мобильные приложения',
      ai_integration: 'AI интеграции',
      automation: 'Автоматизация',
      ecommerce: 'E-commerce',
      other: 'Другое',
    }
    return categoryMap[categoryId] || categoryId
  }

  const getComplexityBadge = (complexity: string) => {
    const styles = {
      simple: 'bg-green-100 text-green-800',
      medium: 'bg-blue-100 text-blue-800',
      complex: 'bg-orange-100 text-orange-800',
      premium: 'bg-purple-100 text-purple-800',
    }

    const labels = {
      simple: 'Простой',
      medium: 'Средний',
      complex: 'Сложный',
      premium: 'Премиум',
    }

    return (
      <span
        className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[complexity as keyof typeof styles]}`}
      >
        {labels[complexity as keyof typeof labels]}
      </span>
    )
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      completed: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800',
      demo: 'bg-yellow-100 text-yellow-800',
    }

    const labels = {
      completed: 'Завершен',
      in_progress: 'В разработке',
      demo: 'Демо-версия',
    }

    return (
      <span
        className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status as keyof typeof styles]}`}
      >
        {labels[status as keyof typeof labels]}
      </span>
    )
  }

  // ============= RENDER =============

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 p-6">
      <div className="max-w-[2000px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Портфолио
            </h1>
            <p className="text-gray-600 mt-1">Управление проектами портфолио</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={loadData}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              <RefreshCw className="w-5 h-5" />
              Обновить
            </button>

            <button
              onClick={() => handleOpenModal()}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg"
            >
              <Plus className="w-5 h-5" />
              Добавить проект
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            {/* Total Projects */}
            <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl shadow-lg p-6 border border-purple-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-violet-500 flex items-center justify-center shadow-lg">
                  <Package className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-purple-700 mb-1">{stats.total}</div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Всего проектов</div>
            </div>

            {/* Visible Projects */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-lg p-6 border border-green-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg">
                  <Eye className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-green-700 mb-1">{stats.visible}</div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Видимых</div>
            </div>

            {/* Featured Projects */}
            <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-xl shadow-lg p-6 border border-yellow-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-amber-500 flex items-center justify-center shadow-lg">
                  <Award className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-yellow-700 mb-1">{stats.featured}</div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Рекомендуемых</div>
            </div>

            {/* Total Views */}
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl shadow-lg p-6 border border-blue-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-blue-700 mb-1">{stats.total_views}</div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Просмотров</div>
            </div>

            {/* Categories */}
            <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl shadow-lg p-6 border border-pink-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center shadow-lg">
                  <Briefcase className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-pink-700 mb-1">
                {Object.keys(stats.categories).length}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Категорий</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div className="lg:col-span-2 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по названию, описанию, технологиям..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setCurrentPage(1)
                }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value)
                setCurrentPage(1)
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Все категории</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name} ({cat.count})
                </option>
              ))}
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setCurrentPage(1)
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Все статусы</option>
              <option value="active">Активные</option>
              <option value="featured">Рекомендуемые</option>
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="created_desc">Новые первые</option>
              <option value="created_asc">Старые первые</option>
              <option value="title_asc">По названию А-Я</option>
              <option value="title_desc">По названию Я-А</option>
              <option value="order_asc">По порядку</option>
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-4 mt-4">
            <span className="text-sm text-gray-600">Вид:</span>
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-all ${
                  viewMode === 'grid'
                    ? 'bg-purple-100 text-purple-600'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-all ${
                  viewMode === 'list'
                    ? 'bg-purple-100 text-purple-600'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Projects Grid/List */}
        {projects.length === 0 ? (
          <div className="bg-white rounded-3xl p-16 shadow-xl border border-gray-100">
            <div className="flex flex-col items-center justify-center text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-pink-100 rounded-3xl flex items-center justify-center mb-6">
                <Briefcase className="w-12 h-12 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Нет проектов</h3>
              <p className="text-gray-600 mb-6 max-w-md">
                Добавьте первый проект в портфолио, чтобы начать
              </p>
              <button
                onClick={() => handleOpenModal()}
                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Добавить первый проект
              </button>
            </div>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className={`bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                  project.is_featured ? 'ring-2 ring-yellow-400' : ''
                }`}
              >
                {/* Image */}
                <div className="relative h-48 bg-gradient-to-br from-purple-500 to-pink-500">
                  {project.main_image ? (
                    <img
                      src={`http://localhost:8001/uploads/portfolio/${project.main_image}`}
                      alt={project.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <ImageIcon className="w-16 h-16 text-white opacity-50" />
                    </div>
                  )}
                  {project.is_featured && (
                    <div className="absolute top-3 right-3 bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                      <Star className="w-3 h-3" />
                      Рекомендуемый
                    </div>
                  )}
                  {!project.is_visible && (
                    <div className="absolute top-3 left-3 bg-gray-800 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                      <EyeOff className="w-3 h-3" />
                      Скрыт
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-5">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-bold text-gray-900 line-clamp-1">
                      {project.title}
                    </h3>
                  </div>

                  {project.subtitle && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-1">{project.subtitle}</p>
                  )}

                  <p className="text-sm text-gray-700 mb-4 line-clamp-2">{project.description}</p>

                  {/* Meta */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-semibold">
                      {getCategoryName(project.category)}
                    </span>
                    {getComplexityBadge(project.complexity)}
                    {getStatusBadge(project.project_status)}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 mb-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      {project.views_count}
                    </div>
                    <div className="flex items-center gap-1">
                      <Heart className="w-4 h-4" />
                      {project.likes_count}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleOpenModal(project)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all text-sm font-semibold"
                    >
                      <Edit2 className="w-4 h-4" />
                      Изменить
                    </button>
                    <button
                      onClick={() => handlePublishToTelegram(project)}
                      className="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-all"
                      title="Опубликовать в Telegram"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(project)}
                      className="px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all"
                      title="Удалить"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-md overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-800 text-white">
                <tr>
                  <th className="px-6 py-4 text-left font-semibold">Проект</th>
                  <th className="px-6 py-4 text-left font-semibold">Категория</th>
                  <th className="px-6 py-4 text-left font-semibold">Статус</th>
                  <th className="px-6 py-4 text-left font-semibold">Сложность</th>
                  <th className="px-6 py-4 text-left font-semibold">Просмотры</th>
                  <th className="px-6 py-4 text-left font-semibold">Дата</th>
                  <th className="px-6 py-4 text-center font-semibold">Действия</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project, index) => (
                  <tr
                    key={project.id}
                    className={`border-b border-gray-200 hover:bg-gray-50 transition-colors ${
                      index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                    }`}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex-shrink-0 overflow-hidden">
                          {project.main_image ? (
                            <img
                              src={`http://localhost:8001/uploads/portfolio/${project.main_image}`}
                              alt={project.title}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <ImageIcon className="w-6 h-6 text-white opacity-50" />
                            </div>
                          )}
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900 flex items-center gap-2">
                            {project.title}
                            {project.is_featured && <Star className="w-4 h-4 text-yellow-500" />}
                            {!project.is_visible && <EyeOff className="w-4 h-4 text-gray-400" />}
                          </div>
                          {project.subtitle && (
                            <div className="text-sm text-gray-600">{project.subtitle}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-semibold">
                        {getCategoryName(project.category)}
                      </span>
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(project.project_status)}</td>
                    <td className="px-6 py-4">{getComplexityBadge(project.complexity)}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <Eye className="w-4 h-4" />
                          {project.views_count}
                        </div>
                        <div className="flex items-center gap-1">
                          <Heart className="w-4 h-4" />
                          {project.likes_count}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {formatDate(project.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => handleOpenModal(project)}
                          className="p-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-all"
                          title="Изменить"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handlePublishToTelegram(project)}
                          className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-all"
                          title="Опубликовать в Telegram"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(project)}
                          className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between bg-white rounded-xl shadow-md p-4">
            <div className="text-sm text-gray-600">
              Показано {projects.length} из {totalItems} проектов
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Назад
              </button>
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum
                  if (totalPages <= 5) {
                    pageNum = i + 1
                  } else if (currentPage <= 3) {
                    pageNum = i + 1
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i
                  } else {
                    pageNum = currentPage - 2 + i
                  }

                  return (
                    <button
                      key={i}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`w-10 h-10 rounded-lg transition-all ${
                        currentPage === pageNum
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>
              <button
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Вперед
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            {/* Modal Header - Sticky */}
            <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 rounded-t-2xl flex items-center justify-between z-10">
              <h2 className="text-xl font-bold">
                {editingProject ? 'Редактировать проект' : 'Добавить проект'}
              </h2>
              <button
                onClick={handleCloseModal}
                className="p-2 hover:bg-white/20 rounded-lg transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body - Scrollable */}
            <div className="flex-1 overflow-y-auto p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left Column - Main Info */}
                  <div className="lg:col-span-2 space-y-4">
                    {/* Title */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Название проекта <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Telegram бот для интернет-магазина"
                        required
                      />
                    </div>

                    {/* Subtitle */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Краткое описание
                      </label>
                      <input
                        type="text"
                        value={formData.subtitle}
                        onChange={(e) => setFormData({ ...formData, subtitle: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Автоматизация продаж и поддержки клиентов"
                      />
                    </div>

                    {/* Description */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Подробное описание <span className="text-red-500">*</span>
                      </label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        rows={4}
                        placeholder="Детальное описание проекта, решаемых задач, особенностей реализации..."
                        required
                      />
                    </div>

                    {/* Category and Complexity */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Категория <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={formData.category}
                          onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          required
                        >
                          <option value="">Выберите категорию</option>
                          <option value="telegram_bots">Telegram боты</option>
                          <option value="web_development">Веб-разработка</option>
                          <option value="mobile_apps">Мобильные приложения</option>
                          <option value="ai_integration">AI интеграции</option>
                          <option value="automation">Автоматизация</option>
                          <option value="ecommerce">E-commerce</option>
                          <option value="other">Другое</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Сложность
                        </label>
                        <select
                          value={formData.complexity}
                          onChange={(e) => setFormData({ ...formData, complexity: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="simple">Простой</option>
                          <option value="medium">Средний</option>
                          <option value="complex">Сложный</option>
                          <option value="premium">Премиум</option>
                        </select>
                      </div>
                    </div>

                    {/* Technologies */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Технологии
                      </label>
                      <input
                        type="text"
                        value={formData.technologies}
                        onChange={(e) =>
                          setFormData({ ...formData, technologies: e.target.value })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Python, PostgreSQL, Redis, Docker"
                      />
                    </div>

                    {/* Cost, Duration, Date */}
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Стоимость, ₽
                        </label>
                        <input
                          type="number"
                          value={formData.cost || ''}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              cost: e.target.value ? Number(e.target.value) : undefined,
                            })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="50000"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Время, дней
                        </label>
                        <input
                          type="number"
                          value={formData.development_time || ''}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              development_time: e.target.value ? Number(e.target.value) : undefined,
                            })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="14"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Дата завершения
                        </label>
                        <input
                          type="date"
                          value={formData.completed_at}
                          onChange={(e) =>
                            setFormData({ ...formData, completed_at: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                      </div>
                    </div>

                    {/* Links */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Демо-ссылка
                        </label>
                        <input
                          type="url"
                          value={formData.demo_link}
                          onChange={(e) => setFormData({ ...formData, demo_link: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="https://demo.example.com"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Репозиторий
                        </label>
                        <input
                          type="url"
                          value={formData.repository_link}
                          onChange={(e) =>
                            setFormData({ ...formData, repository_link: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="https://github.com/username/repo"
                        />
                      </div>
                    </div>

                    {/* Client and Status */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Клиент
                        </label>
                        <input
                          type="text"
                          value={formData.client_name}
                          onChange={(e) =>
                            setFormData({ ...formData, client_name: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="Название компании"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Статус проекта
                        </label>
                        <select
                          value={formData.project_status}
                          onChange={(e) =>
                            setFormData({ ...formData, project_status: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="completed">Завершен</option>
                          <option value="in_progress">В разработке</option>
                          <option value="demo">Демо-версия</option>
                        </select>
                      </div>
                    </div>

                    {/* Tags */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Теги для поиска
                      </label>
                      <input
                        type="text"
                        value={formData.tags}
                        onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="бот, автоматизация, продажи"
                      />
                    </div>
                  </div>

                  {/* Right Column - Image and Settings */}
                  <div className="space-y-4">
                    {/* Main Image */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Главное изображение
                      </label>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-purple-500 transition-all">
                        {mainImagePreview ? (
                          <div className="relative">
                            <img
                              src={mainImagePreview}
                              alt="Preview"
                              className="w-full h-40 object-cover rounded-lg"
                            />
                            <button
                              type="button"
                              onClick={handleRemoveImage}
                              className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <label className="cursor-pointer block">
                            <input
                              type="file"
                              accept="image/*"
                              onChange={handleImageChange}
                              className="hidden"
                            />
                            <div className="flex flex-col items-center gap-2">
                              <Upload className="w-8 h-8 text-gray-400" />
                              <p className="text-sm text-gray-600">Загрузить изображение</p>
                              <p className="text-xs text-gray-500">PNG, JPG до 10MB</p>
                            </div>
                          </label>
                        )}
                      </div>
                    </div>

                    {/* Settings */}
                    <div className="space-y-3">
                      <label className="block text-sm font-semibold text-gray-700">
                        Настройки отображения
                      </label>

                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.is_featured}
                          onChange={(e) =>
                            setFormData({ ...formData, is_featured: e.target.checked })
                          }
                          className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                        />
                        <span className="text-sm text-gray-700">Рекомендуемый проект</span>
                      </label>

                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.is_visible}
                          onChange={(e) =>
                            setFormData({ ...formData, is_visible: e.target.checked })
                          }
                          className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                        />
                        <span className="text-sm text-gray-700">Показывать в портфолио</span>
                      </label>

                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.show_cost}
                          onChange={(e) =>
                            setFormData({ ...formData, show_cost: e.target.checked })
                          }
                          className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                        />
                        <span className="text-sm text-gray-700">Показывать стоимость</span>
                      </label>
                    </div>

                    {/* Sort Order */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Порядок отображения
                      </label>
                      <input
                        type="number"
                        value={formData.sort_order}
                        onChange={(e) =>
                          setFormData({ ...formData, sort_order: Number(e.target.value) })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="0"
                      />
                      <p className="text-xs text-gray-500 mt-1">Меньшее число = выше в списке</p>
                    </div>

                    {/* Complexity Level */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Уровень сложности (1-10)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        value={formData.complexity_level}
                        onChange={(e) =>
                          setFormData({ ...formData, complexity_level: Number(e.target.value) })
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                </div>
              </form>
            </div>

            {/* Modal Footer - Sticky */}
            <div className="sticky bottom-0 bg-gray-50 px-6 py-4 rounded-b-2xl flex items-center justify-end gap-3 border-t border-gray-200">
              <button
                type="button"
                onClick={handleCloseModal}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all font-semibold"
              >
                Отмена
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Сохранение...
                  </>
                ) : (
                  <>Сохранить</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-3 rounded-lg shadow-lg text-white ${
              toast.type === 'success'
                ? 'bg-green-500'
                : toast.type === 'error'
                ? 'bg-red-500'
                : 'bg-blue-500'
            } animate-slide-in`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  )
}
