import React, { useState, useEffect } from 'react'
import { FileText, X, Plus, Download, Send, Eye, Edit2, Trash2, DollarSign, Calendar, User, CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface InvoicingProps {
  projectId: number
  onClose: () => void
}

interface Invoice {
  id: number
  invoiceNumber: string
  clientName: string
  clientEmail: string
  clientAddress: string
  issueDate: string
  dueDate: string
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled'
  items: InvoiceItem[]
  subtotal: number
  tax: number
  taxRate: number
  discount: number
  total: number
  notes: string
  paymentMethod?: string
  paidDate?: string
}

interface InvoiceItem {
  id: number
  description: string
  quantity: number
  unitPrice: number
  amount: number
}

const Invoicing: React.FC<InvoicingProps> = ({ projectId, onClose }) => {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [filterStatus, setFilterStatus] = useState<string>('all')

  const [newInvoice, setNewInvoice] = useState({
    clientName: '',
    clientEmail: '',
    clientAddress: '',
    issueDate: new Date().toISOString().slice(0, 10),
    dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
    items: [] as InvoiceItem[],
    taxRate: 20,
    discount: 0,
    notes: '',
  })

  const [newItem, setNewItem] = useState({
    description: '',
    quantity: 1,
    unitPrice: 0,
  })

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = 'unset' }
  }, [])

  useEffect(() => {
    fetchInvoices()
  }, [projectId])

  const fetchInvoices = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://147.45.215.199:8001/api/projects/${projectId}/invoices`,
        {
          headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setInvoices(data)
      } else {
        setInvoices([
          {
            id: 1,
            invoiceNumber: 'INV-2024-001',
            clientName: 'ООО "ТехноКом"',
            clientEmail: 'client@technocom.ru',
            clientAddress: 'г. Москва, ул. Ленина, д. 10',
            issueDate: '2024-03-01',
            dueDate: '2024-03-31',
            status: 'paid',
            items: [
              { id: 1, description: 'Разработка сайта', quantity: 1, unitPrice: 150000, amount: 150000 },
              { id: 2, description: 'Поддержка (1 месяц)', quantity: 1, unitPrice: 20000, amount: 20000 },
            ],
            subtotal: 170000,
            tax: 34000,
            taxRate: 20,
            discount: 5000,
            total: 199000,
            notes: 'Оплата в течение 30 дней',
            paymentMethod: 'Безналичный расчет',
            paidDate: '2024-03-15',
          },
          {
            id: 2,
            invoiceNumber: 'INV-2024-002',
            clientName: 'ИП Иванов И.И.',
            clientEmail: 'ivanov@example.com',
            clientAddress: 'г. Санкт-Петербург, пр. Невский, д. 25',
            issueDate: '2024-03-15',
            dueDate: '2024-04-15',
            status: 'sent',
            items: [
              { id: 1, description: 'Консультация', quantity: 5, unitPrice: 5000, amount: 25000 },
              { id: 2, description: 'Доработка функционала', quantity: 1, unitPrice: 45000, amount: 45000 },
            ],
            subtotal: 70000,
            tax: 14000,
            taxRate: 20,
            discount: 0,
            total: 84000,
            notes: 'Срок оплаты — 30 дней с даты выставления',
          },
          {
            id: 3,
            invoiceNumber: 'INV-2024-003',
            clientName: 'АО "БизнесГруп"',
            clientEmail: 'info@bizgroup.ru',
            clientAddress: 'г. Екатеринбург, ул. Малышева, д. 5',
            issueDate: '2024-02-01',
            dueDate: '2024-02-28',
            status: 'overdue',
            items: [
              { id: 1, description: 'Интеграция с CRM', quantity: 1, unitPrice: 80000, amount: 80000 },
            ],
            subtotal: 80000,
            tax: 16000,
            taxRate: 20,
            discount: 0,
            total: 96000,
            notes: 'Внимание: просрочен платеж',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching invoices:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateInvoiceTotal = () => {
    const subtotal = newInvoice.items.reduce((sum, item) => sum + item.amount, 0)
    const tax = (subtotal * newInvoice.taxRate) / 100
    const total = subtotal + tax - newInvoice.discount
    return { subtotal, tax, total }
  }

  const handleAddItem = () => {
    if (!newItem.description || newItem.quantity <= 0 || newItem.unitPrice <= 0) {
      alert('Заполните все поля товара/услуги')
      return
    }

    const item: InvoiceItem = {
      id: Date.now(),
      description: newItem.description,
      quantity: newItem.quantity,
      unitPrice: newItem.unitPrice,
      amount: newItem.quantity * newItem.unitPrice,
    }

    setNewInvoice({
      ...newInvoice,
      items: [...newInvoice.items, item],
    })

    setNewItem({ description: '', quantity: 1, unitPrice: 0 })
  }

  const handleRemoveItem = (itemId: number) => {
    setNewInvoice({
      ...newInvoice,
      items: newInvoice.items.filter((item) => item.id !== itemId),
    })
  }

  const handleCreateInvoice = () => {
    if (!newInvoice.clientName || !newInvoice.clientEmail || newInvoice.items.length === 0) {
      alert('Заполните обязательные поля и добавьте минимум 1 товар/услугу')
      return
    }

    const { subtotal, tax, total } = calculateInvoiceTotal()

    const invoice: Invoice = {
      id: Date.now(),
      invoiceNumber: `INV-${new Date().getFullYear()}-${String(invoices.length + 1).padStart(3, '0')}`,
      clientName: newInvoice.clientName,
      clientEmail: newInvoice.clientEmail,
      clientAddress: newInvoice.clientAddress,
      issueDate: newInvoice.issueDate,
      dueDate: newInvoice.dueDate,
      status: 'draft',
      items: newInvoice.items,
      subtotal,
      tax,
      taxRate: newInvoice.taxRate,
      discount: newInvoice.discount,
      total,
      notes: newInvoice.notes,
    }

    setInvoices([invoice, ...invoices])
    setShowCreateModal(false)
    setNewInvoice({
      clientName: '',
      clientEmail: '',
      clientAddress: '',
      issueDate: new Date().toISOString().slice(0, 10),
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      items: [],
      taxRate: 20,
      discount: 0,
      notes: '',
    })
  }

  const handleDeleteInvoice = (invoiceId: number) => {
    if (!confirm('Удалить счет?')) return
    setInvoices(invoices.filter((inv) => inv.id !== invoiceId))
  }

  const handleSendInvoice = (invoiceId: number) => {
    const invoice = invoices.find((inv) => inv.id === invoiceId)
    if (!invoice) return

    if (invoice.status === 'draft') {
      setInvoices(
        invoices.map((inv) =>
          inv.id === invoiceId ? { ...inv, status: 'sent' as const } : inv
        )
      )
      alert('Счет отправлен клиенту')
    }
  }

  const handleMarkAsPaid = (invoiceId: number) => {
    setInvoices(
      invoices.map((inv) =>
        inv.id === invoiceId
          ? { ...inv, status: 'paid' as const, paidDate: new Date().toISOString().slice(0, 10) }
          : inv
      )
    )
    alert('Счет отмечен как оплаченный')
  }

  const getStatusIcon = (status: string) => {
    const icons = {
      draft: <Edit2 className="w-5 h-5" />,
      sent: <Send className="w-5 h-5" />,
      paid: <CheckCircle className="w-5 h-5" />,
      overdue: <AlertCircle className="w-5 h-5" />,
      cancelled: <X className="w-5 h-5" />,
    }
    return icons[status as keyof typeof icons] || <FileText className="w-5 h-5" />
  }

  const getStatusColor = (status: string) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-700',
      sent: 'bg-blue-100 text-blue-700',
      paid: 'bg-green-100 text-green-700',
      overdue: 'bg-red-100 text-red-700',
      cancelled: 'bg-orange-100 text-orange-700',
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  const getStatusLabel = (status: string) => {
    const labels = {
      draft: 'Черновик',
      sent: 'Отправлен',
      paid: 'Оплачен',
      overdue: 'Просрочен',
      cancelled: 'Отменен',
    }
    return labels[status as keyof typeof labels] || status
  }

  const filteredInvoices = invoices.filter((invoice) => {
    if (filterStatus === 'all') return true
    return invoice.status === filterStatus
  })

  const totalStats = {
    total: invoices.reduce((sum, inv) => sum + inv.total, 0),
    paid: invoices.filter((inv) => inv.status === 'paid').reduce((sum, inv) => sum + inv.total, 0),
    pending: invoices
      .filter((inv) => inv.status === 'sent' || inv.status === 'overdue')
      .reduce((sum, inv) => sum + inv.total, 0),
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка счетов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <FileText className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Выставление счетов</h2>
              <p className="text-green-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 border-b bg-gray-50">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <DollarSign className="w-8 h-8 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-500">Всего выставлено</p>
                  <p className="text-xl font-bold text-gray-900">{totalStats.total.toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-8 h-8 text-green-600" />
                <div>
                  <p className="text-sm text-gray-500">Оплачено</p>
                  <p className="text-xl font-bold text-green-700">{totalStats.paid.toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <Clock className="w-8 h-8 text-orange-600" />
                <div>
                  <p className="text-sm text-gray-500">Ожидается</p>
                  <p className="text-xl font-bold text-orange-700">{totalStats.pending.toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2 font-medium"
            >
              <Plus className="w-5 h-5" />
              Создать счет
            </button>
          </div>

          <div className="flex gap-2">
            {['all', 'draft', 'sent', 'paid', 'overdue'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  filterStatus === status
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
                }`}
              >
                {status === 'all' ? 'Все' : getStatusLabel(status)}
                <span className="ml-2 text-xs">
                  ({status === 'all' ? invoices.length : invoices.filter((inv) => inv.status === status).length})
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {filteredInvoices.map((invoice) => (
              <div
                key={invoice.id}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-4 flex-1">
                    <div className={`p-3 rounded-lg ${getStatusColor(invoice.status)}`}>
                      {getStatusIcon(invoice.status)}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-900">{invoice.invoiceNumber}</h3>
                        <span className={`text-xs px-3 py-1 rounded-full ${getStatusColor(invoice.status)}`}>
                          {getStatusLabel(invoice.status)}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="font-medium text-gray-900">{invoice.clientName}</p>
                            <p className="text-xs text-gray-500">{invoice.clientEmail}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="text-gray-900">Выставлен: {new Date(invoice.issueDate).toLocaleDateString('ru-RU')}</p>
                            <p className="text-xs text-gray-500">Оплатить до: {new Date(invoice.dueDate).toLocaleDateString('ru-RU')}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4 text-gray-400" />
                          <div>
                            <p className="text-lg font-bold text-gray-900">{invoice.total.toLocaleString('ru-RU')} ₽</p>
                            <p className="text-xs text-gray-500">{invoice.items.length} позиций</p>
                          </div>
                        </div>

                        {invoice.paidDate && (
                          <div className="flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-green-600" />
                            <div>
                              <p className="text-gray-900">Оплачен</p>
                              <p className="text-xs text-gray-500">{new Date(invoice.paidDate).toLocaleDateString('ru-RU')}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedInvoice(invoice)}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Просмотр"
                    >
                      <Eye className="w-5 h-5" />
                    </button>

                    {invoice.status === 'draft' && (
                      <button
                        onClick={() => handleSendInvoice(invoice.id)}
                        className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="Отправить"
                      >
                        <Send className="w-5 h-5" />
                      </button>
                    )}

                    {(invoice.status === 'sent' || invoice.status === 'overdue') && (
                      <button
                        onClick={() => handleMarkAsPaid(invoice.id)}
                        className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="Отметить как оплаченный"
                      >
                        <CheckCircle className="w-5 h-5" />
                      </button>
                    )}

                    <button
                      onClick={() => handleDeleteInvoice(invoice.id)}
                      className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Удалить"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {invoice.notes && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-600">{invoice.notes}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {filteredInvoices.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Счета не найдены</p>
            </div>
          )}
        </div>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-6 flex justify-between items-center">
              <h3 className="text-2xl font-bold">Создать счет</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Клиент *</label>
                    <input
                      type="text"
                      value={newInvoice.clientName}
                      onChange={(e) => setNewInvoice({ ...newInvoice, clientName: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                    <input
                      type="email"
                      value={newInvoice.clientEmail}
                      onChange={(e) => setNewInvoice({ ...newInvoice, clientEmail: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Адрес клиента</label>
                  <textarea
                    value={newInvoice.clientAddress}
                    onChange={(e) => setNewInvoice({ ...newInvoice, clientAddress: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Дата выставления</label>
                    <input
                      type="date"
                      value={newInvoice.issueDate}
                      onChange={(e) => setNewInvoice({ ...newInvoice, issueDate: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Срок оплаты</label>
                    <input
                      type="date"
                      value={newInvoice.dueDate}
                      onChange={(e) => setNewInvoice({ ...newInvoice, dueDate: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold mb-3">Товары/Услуги</h4>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
                      <div className="md:col-span-5">
                        <input
                          type="text"
                          value={newItem.description}
                          onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                          placeholder="Описание"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <input
                          type="number"
                          value={newItem.quantity}
                          onChange={(e) => setNewItem({ ...newItem, quantity: parseFloat(e.target.value) || 0 })}
                          placeholder="Кол-во"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        />
                      </div>
                      <div className="md:col-span-3">
                        <input
                          type="number"
                          value={newItem.unitPrice}
                          onChange={(e) => setNewItem({ ...newItem, unitPrice: parseFloat(e.target.value) || 0 })}
                          placeholder="Цена"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <button
                          onClick={handleAddItem}
                          className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <Plus className="w-5 h-5 mx-auto" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {newInvoice.items.length > 0 && (
                    <div className="space-y-2">
                      {newInvoice.items.map((item) => (
                        <div
                          key={item.id}
                          className="bg-white border border-gray-200 rounded-lg p-3 flex items-center justify-between"
                        >
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{item.description}</p>
                            <p className="text-sm text-gray-500">
                              {item.quantity} × {item.unitPrice.toLocaleString('ru-RU')} ₽
                            </p>
                          </div>
                          <div className="flex items-center gap-4">
                            <p className="text-lg font-bold text-gray-900">{item.amount.toLocaleString('ru-RU')} ₽</p>
                            <button
                              onClick={() => handleRemoveItem(item.id)}
                              className="p-1 text-red-600 hover:bg-red-50 rounded"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">НДС (%)</label>
                    <input
                      type="number"
                      value={newInvoice.taxRate}
                      onChange={(e) => setNewInvoice({ ...newInvoice, taxRate: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Скидка (₽)</label>
                    <input
                      type="number"
                      value={newInvoice.discount}
                      onChange={(e) => setNewInvoice({ ...newInvoice, discount: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {newInvoice.items.length > 0 && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Подытог:</span>
                        <span className="font-medium">{calculateInvoiceTotal().subtotal.toLocaleString('ru-RU')} ₽</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">НДС ({newInvoice.taxRate}%):</span>
                        <span className="font-medium">{calculateInvoiceTotal().tax.toLocaleString('ru-RU')} ₽</span>
                      </div>
                      {newInvoice.discount > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Скидка:</span>
                          <span className="font-medium text-red-600">-{newInvoice.discount.toLocaleString('ru-RU')} ₽</span>
                        </div>
                      )}
                      <div className="flex justify-between text-lg font-bold text-gray-900 pt-2 border-t border-green-300">
                        <span>Итого:</span>
                        <span>{calculateInvoiceTotal().total.toLocaleString('ru-RU')} ₽</span>
                      </div>
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Примечания</label>
                  <textarea
                    value={newInvoice.notes}
                    onChange={(e) => setNewInvoice({ ...newInvoice, notes: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t flex gap-3 justify-end">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateInvoice}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Создать счет
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-6 flex justify-between items-center">
              <h3 className="text-2xl font-bold">{selectedInvoice.invoiceNumber}</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => alert('Функция экспорта в PDF будет реализована')}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                  title="Скачать PDF"
                >
                  <Download className="w-6 h-6" />
                </button>
                <button
                  onClick={() => setSelectedInvoice(null)}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-8">
              <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center justify-between pb-6 border-b">
                  <div>
                    <h4 className="text-2xl font-bold text-gray-900">СЧЕТ</h4>
                    <p className="text-lg text-gray-600">{selectedInvoice.invoiceNumber}</p>
                  </div>
                  <span className={`px-4 py-2 rounded-lg ${getStatusColor(selectedInvoice.status)}`}>
                    {getStatusLabel(selectedInvoice.status)}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-8">
                  <div>
                    <h5 className="text-sm font-medium text-gray-500 mb-2">Клиент</h5>
                    <p className="text-lg font-semibold text-gray-900">{selectedInvoice.clientName}</p>
                    <p className="text-sm text-gray-600">{selectedInvoice.clientEmail}</p>
                    {selectedInvoice.clientAddress && (
                      <p className="text-sm text-gray-600 mt-1">{selectedInvoice.clientAddress}</p>
                    )}
                  </div>

                  <div>
                    <div className="mb-3">
                      <h5 className="text-sm font-medium text-gray-500">Дата выставления</h5>
                      <p className="text-gray-900">{new Date(selectedInvoice.issueDate).toLocaleDateString('ru-RU')}</p>
                    </div>
                    <div>
                      <h5 className="text-sm font-medium text-gray-500">Срок оплаты</h5>
                      <p className="text-gray-900">{new Date(selectedInvoice.dueDate).toLocaleDateString('ru-RU')}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-gray-300">
                        <th className="text-left py-3 text-sm font-medium text-gray-500">Описание</th>
                        <th className="text-center py-3 text-sm font-medium text-gray-500">Кол-во</th>
                        <th className="text-right py-3 text-sm font-medium text-gray-500">Цена</th>
                        <th className="text-right py-3 text-sm font-medium text-gray-500">Сумма</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedInvoice.items.map((item) => (
                        <tr key={item.id} className="border-b border-gray-200">
                          <td className="py-3 text-gray-900">{item.description}</td>
                          <td className="py-3 text-center text-gray-900">{item.quantity}</td>
                          <td className="py-3 text-right text-gray-900">{item.unitPrice.toLocaleString('ru-RU')} ₽</td>
                          <td className="py-3 text-right font-medium text-gray-900">{item.amount.toLocaleString('ru-RU')} ₽</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="flex justify-end">
                  <div className="w-64 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Подытог:</span>
                      <span className="font-medium text-gray-900">{selectedInvoice.subtotal.toLocaleString('ru-RU')} ₽</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">НДС ({selectedInvoice.taxRate}%):</span>
                      <span className="font-medium text-gray-900">{selectedInvoice.tax.toLocaleString('ru-RU')} ₽</span>
                    </div>
                    {selectedInvoice.discount > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Скидка:</span>
                        <span className="font-medium text-red-600">-{selectedInvoice.discount.toLocaleString('ru-RU')} ₽</span>
                      </div>
                    )}
                    <div className="flex justify-between text-lg font-bold text-gray-900 pt-2 border-t-2 border-gray-300">
                      <span>Итого:</span>
                      <span>{selectedInvoice.total.toLocaleString('ru-RU')} ₽</span>
                    </div>
                  </div>
                </div>

                {selectedInvoice.notes && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Примечания</h5>
                    <p className="text-sm text-gray-600">{selectedInvoice.notes}</p>
                  </div>
                )}

                {selectedInvoice.paidDate && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-sm text-green-800">
                      <CheckCircle className="w-4 h-4 inline mr-2" />
                      Оплачено {new Date(selectedInvoice.paidDate).toLocaleDateString('ru-RU')}
                      {selectedInvoice.paymentMethod && ` - ${selectedInvoice.paymentMethod}`}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Invoicing
