import React, { useState, useEffect } from 'react'
import {
  BookOpen,
  Search,
  Plus,
  X,
  Edit2,
  Trash2,
  Folder,
  File,
  ChevronRight,
  Star,
  Eye,
  ThumbsUp,
  MessageSquare,
  Tag,
  Clock,
  User,
  Download,
  Share2,
  BookMarked,
} from 'lucide-react'

interface KnowledgeBaseProps {
  projectId: number
  onClose: () => void
}

interface Article {
  id: number
  title: string
  content: string
  categoryId: number
  author: string
  createdAt: string
  updatedAt: string
  views: number
  likes: number
  commentsCount: number
  tags: string[]
  favorite: boolean
  attachments: string[]
}

interface Category {
  id: number
  name: string
  description: string
  parentId: number | null
  articlesCount: number
  icon: string
}

const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({ projectId, onClose }) => {
  const [articles, setArticles] = useState<Article[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [currentCategoryId, setCurrentCategoryId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)
  const [showAddArticle, setShowAddArticle] = useState(false)
  const [showAddCategory, setShowAddCategory] = useState(false)
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)

  const [newArticle, setNewArticle] = useState({
    title: '',
    content: '',
    categoryId: 0,
    tags: [] as string[],
  })

  const [newCategory, setNewCategory] = useState({
    name: '',
    description: '',
    icon: '📁',
  })

  const [newTag, setNewTag] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [projectId])

  const fetchData = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/knowledge-base`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setArticles(data.articles || [])
        setCategories(data.categories || [])
      } else {
        // Mock data
        setCategories([
          { id: 1, name: 'Руководства', description: 'Пошаговые инструкции', parentId: null, articlesCount: 5, icon: '📖' },
          { id: 2, name: 'FAQ', description: 'Часто задаваемые вопросы', parentId: null, articlesCount: 8, icon: '❓' },
          { id: 3, name: 'API', description: 'Документация API', parentId: null, articlesCount: 12, icon: '⚙️' },
          { id: 4, name: 'Best Practices', description: 'Лучшие практики', parentId: null, articlesCount: 6, icon: '⭐' },
          { id: 5, name: 'Troubleshooting', description: 'Решение проблем', parentId: null, articlesCount: 10, icon: '🔧' },
        ])

        setArticles([
          {
            id: 1,
            title: 'Как начать работу с проектом',
            content: 'Подробное руководство по началу работы...',
            categoryId: 1,
            author: 'Алексей Иванов',
            createdAt: '2024-03-01T10:00:00',
            updatedAt: '2024-03-10T14:30:00',
            views: 245,
            likes: 18,
            commentsCount: 5,
            tags: ['начало работы', 'руководство'],
            favorite: true,
            attachments: ['setup-guide.pdf'],
          },
          {
            id: 2,
            title: 'Настройка окружения разработки',
            content: 'Инструкция по настройке локального окружения...',
            categoryId: 1,
            author: 'Дмитрий Смирнов',
            createdAt: '2024-02-15T09:00:00',
            updatedAt: '2024-03-05T11:20:00',
            views: 189,
            likes: 22,
            commentsCount: 8,
            tags: ['setup', 'dev environment'],
            favorite: false,
            attachments: [],
          },
          {
            id: 3,
            title: 'Как создать новую задачу?',
            content: 'FAQ: процесс создания задачи в системе...',
            categoryId: 2,
            author: 'Мария Петрова',
            createdAt: '2024-03-08T15:30:00',
            updatedAt: '2024-03-08T15:30:00',
            views: 156,
            likes: 12,
            commentsCount: 3,
            tags: ['faq', 'задачи'],
            favorite: false,
            attachments: [],
          },
          {
            id: 4,
            title: 'REST API: Аутентификация',
            content: 'Описание процесса аутентификации через API...',
            categoryId: 3,
            author: 'Дмитрий Смирнов',
            createdAt: '2024-02-20T16:00:00',
            updatedAt: '2024-03-12T10:45:00',
            views: 312,
            likes: 35,
            commentsCount: 12,
            tags: ['api', 'auth', 'security'],
            favorite: true,
            attachments: ['api-examples.json'],
          },
          {
            id: 5,
            title: 'Код-ревью: лучшие практики',
            content: 'Рекомендации по проведению код-ревью...',
            categoryId: 4,
            author: 'Алексей Иванов',
            createdAt: '2024-03-05T13:00:00',
            updatedAt: '2024-03-05T13:00:00',
            views: 98,
            likes: 15,
            commentsCount: 4,
            tags: ['code review', 'best practices'],
            favorite: false,
            attachments: [],
          },
          {
            id: 6,
            title: 'Решение проблем с производительностью',
            content: 'Типичные проблемы и их решения...',
            categoryId: 5,
            author: 'Елена Козлова',
            createdAt: '2024-03-14T11:00:00',
            updatedAt: '2024-03-14T11:00:00',
            views: 67,
            likes: 8,
            commentsCount: 2,
            tags: ['performance', 'troubleshooting'],
            favorite: false,
            attachments: ['performance-tips.pdf'],
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching knowledge base:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddArticle = async () => {
    if (!newArticle.title || !newArticle.content) {
      alert('Заполните название и содержание')
      return
    }

    const articleData: Article = {
      ...newArticle,
      id: Date.now(),
      author: 'Текущий пользователь',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      views: 0,
      likes: 0,
      commentsCount: 0,
      favorite: false,
      attachments: [],
    }

    setArticles([...articles, articleData])
    setShowAddArticle(false)
    setNewArticle({ title: '', content: '', categoryId: 0, tags: [] })
  }

  const handleAddCategory = () => {
    if (!newCategory.name) {
      alert('Введите название категории')
      return
    }

    const categoryData: Category = {
      ...newCategory,
      id: Date.now(),
      parentId: currentCategoryId,
      articlesCount: 0,
    }

    setCategories([...categories, categoryData])
    setShowAddCategory(false)
    setNewCategory({ name: '', description: '', icon: '📁' })
  }

  const handleDeleteArticle = (articleId: number) => {
    if (!confirm('Удалить статью?')) return
    setArticles(articles.filter((a) => a.id !== articleId))
  }

  const handleToggleFavorite = (article: Article) => {
    setArticles(articles.map((a) => (a.id === article.id ? { ...a, favorite: !a.favorite } : a)))
  }

  const getCurrentCategory = () => {
    return categories.find((c) => c.id === currentCategoryId)
  }

  const getCategoryPath = (): Category[] => {
    const path: Category[] = []
    let current = getCurrentCategory()
    while (current) {
      path.unshift(current)
      current = categories.find((c) => c.id === current!.parentId)
    }
    return path
  }

  const filteredArticles = articles.filter((article) => {
    const matchesCategory = article.categoryId === currentCategoryId
    const matchesSearch =
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesFavorites = !showFavoritesOnly || article.favorite
    return matchesCategory && matchesSearch && matchesFavorites
  })

  const currentCategories = categories.filter((c) => c.parentId === currentCategoryId)

  const stats = {
    totalArticles: articles.length,
    totalViews: articles.reduce((sum, a) => sum + a.views, 0),
    totalLikes: articles.reduce((sum, a) => sum + a.likes, 0),
    favorites: articles.filter((a) => a.favorite).length,
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка базы знаний...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-cyan-600 to-blue-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">База знаний</h2>
              <p className="text-cyan-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <BookMarked className="w-4 h-4" />
              <span>Статей</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalArticles}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Eye className="w-4 h-4" />
              <span>Просмотров</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.totalViews}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <ThumbsUp className="w-4 h-4" />
              <span>Лайков</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.totalLikes}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Star className="w-4 h-4" />
              <span>Избранное</span>
            </div>
            <div className="text-2xl font-bold text-yellow-600">{stats.favorites}</div>
          </div>
        </div>

        {/* Breadcrumb */}
        <div className="px-6 py-3 bg-white border-b">
          <div className="flex items-center gap-2 text-sm">
            <button onClick={() => setCurrentCategoryId(null)} className="text-cyan-600 hover:text-cyan-700 font-medium">
              Все категории
            </button>
            {getCategoryPath().map((cat) => (
              <React.Fragment key={cat.id}>
                <ChevronRight className="w-4 h-4 text-gray-400" />
                <button onClick={() => setCurrentCategoryId(cat.id)} className="text-cyan-600 hover:text-cyan-700 font-medium">
                  {cat.name}
                </button>
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex flex-wrap justify-between items-center gap-4 p-6 bg-white border-b">
          <div className="flex flex-wrap gap-3 flex-1">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Поиск в базе знаний..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                />
              </div>
            </div>
            <button
              onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
              className={`px-4 py-2 rounded-lg border transition-colors ${
                showFavoritesOnly
                  ? 'bg-yellow-100 border-yellow-300 text-yellow-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Star className={`w-5 h-5 ${showFavoritesOnly ? 'fill-current' : ''}`} />
            </button>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowAddCategory(true)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
            >
              <Folder className="w-5 h-5" />
              Категория
            </button>
            <button
              onClick={() => setShowAddArticle(true)}
              className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Статья
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Categories */}
          {currentCategories.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Категории</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {currentCategories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setCurrentCategoryId(category.id)}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow text-left"
                  >
                    <div className="text-3xl mb-2">{category.icon}</div>
                    <p className="font-medium text-gray-900">{category.name}</p>
                    <p className="text-xs text-gray-500 mt-1">{category.articlesCount} статей</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Articles */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Статьи</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredArticles.map((article) => (
                <div key={article.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3 flex-1">
                      <File className="w-6 h-6 text-cyan-600 flex-shrink-0 mt-1" />
                      <div className="flex-1">
                        <h3 className="font-bold text-lg text-gray-900 mb-2">{article.title}</h3>
                        <p className="text-sm text-gray-600 line-clamp-2">{article.content}</p>
                      </div>
                    </div>
                    <button onClick={() => handleToggleFavorite(article)} className="p-1">
                      <Star className={`w-5 h-5 ${article.favorite ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400'}`} />
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    {article.tags.map((tag, idx) => (
                      <span key={idx} className="text-xs px-2 py-1 bg-cyan-100 text-cyan-700 rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        <span>{article.views}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <ThumbsUp className="w-4 h-4" />
                        <span>{article.likes}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageSquare className="w-4 h-4" />
                        <span>{article.commentsCount}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedArticle(article)}
                      className="text-cyan-600 hover:text-cyan-700 font-medium text-sm"
                    >
                      Читать →
                    </button>
                  </div>

                  <div className="flex items-center gap-2 mt-3 pt-3 border-t text-xs text-gray-500">
                    <User className="w-3 h-3" />
                    <span>{article.author}</span>
                    <span>•</span>
                    <Clock className="w-3 h-3" />
                    <span>{new Date(article.updatedAt).toLocaleDateString('ru-RU')}</span>
                  </div>
                </div>
              ))}
            </div>

            {filteredArticles.length === 0 && currentCategories.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Нет статей в этой категории</p>
              </div>
            )}
          </div>
        </div>

        {/* Add Article Modal */}
        {showAddArticle && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[80vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">Создать статью</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название *</label>
                  <input
                    type="text"
                    value={newArticle.title}
                    onChange={(e) => setNewArticle({ ...newArticle, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Категория</label>
                  <select
                    value={newArticle.categoryId}
                    onChange={(e) => setNewArticle({ ...newArticle, categoryId: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                  >
                    <option value={0}>Без категории</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.icon} {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Содержание *</label>
                  <textarea
                    value={newArticle.content}
                    onChange={(e) => setNewArticle({ ...newArticle, content: e.target.value })}
                    rows={10}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent font-mono text-sm"
                    placeholder="Markdown поддерживается..."
                  />
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
                          setNewArticle({ ...newArticle, tags: [...newArticle.tags, newTag] })
                          setNewTag('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                      placeholder="Добавить тег (Enter)"
                    />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {newArticle.tags.map((tag, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 text-sm px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full">
                        {tag}
                        <button
                          onClick={() => setNewArticle({ ...newArticle, tags: newArticle.tags.filter((_, i) => i !== idx) })}
                          className="hover:text-cyan-900"
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
                  onClick={() => setShowAddArticle(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddArticle}
                  className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors"
                >
                  Создать
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Add Category Modal */}
        {showAddCategory && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-xl font-bold mb-4">Создать категорию</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название *</label>
                  <input
                    type="text"
                    value={newCategory.name}
                    onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Иконка</label>
                  <input
                    type="text"
                    value={newCategory.icon}
                    onChange={(e) => setNewCategory({ ...newCategory, icon: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                    placeholder="📁"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                  <textarea
                    value={newCategory.description}
                    onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddCategory(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddCategory}
                  className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors"
                >
                  Создать
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Article Detail Modal */}
        {selectedArticle && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-6">
                <div className="flex-1">
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">{selectedArticle.title}</h2>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      <span>{selectedArticle.author}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      <span>{new Date(selectedArticle.updatedAt).toLocaleString('ru-RU')}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      <span>{selectedArticle.views} просмотров</span>
                    </div>
                  </div>
                </div>
                <button onClick={() => setSelectedArticle(null)} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="prose max-w-none mb-6">
                <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">{selectedArticle.content}</div>
              </div>

              <div className="flex flex-wrap gap-2 mb-6">
                {selectedArticle.tags.map((tag, idx) => (
                  <span key={idx} className="text-sm px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full">
                    #{tag}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between pt-6 border-t">
                <div className="flex items-center gap-4">
                  <button className="flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
                    <ThumbsUp className="w-5 h-5" />
                    <span>{selectedArticle.likes}</span>
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                    <MessageSquare className="w-5 h-5" />
                    <span>{selectedArticle.commentsCount}</span>
                  </button>
                </div>
                <div className="flex gap-2">
                  <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2">
                    <Share2 className="w-5 h-5" />
                    Поделиться
                  </button>
                  <button
                    onClick={() => handleDeleteArticle(selectedArticle.id)}
                    className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors flex items-center gap-2"
                  >
                    <Trash2 className="w-5 h-5" />
                    Удалить
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default KnowledgeBase
