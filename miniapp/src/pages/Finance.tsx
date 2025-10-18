import React, { useEffect, useState } from 'react';
import { Wallet, TrendingUp, AlertCircle, DollarSign, CreditCard } from 'lucide-react';
import { financeApi } from '../api/finance';
import type { FinanceSummary, Transaction, Deal } from '../api/finance';

const Finance: React.FC = () => {
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [activeTab, setActiveTab] = useState<'summary' | 'deals' | 'transactions'>('summary');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFinanceData();
  }, []);

  const loadFinanceData = async () => {
    try {
      setLoading(true);
      const [summaryData, transactionsData, dealsData] = await Promise.all([
        financeApi.getSummary(),
        financeApi.getTransactions(),
        financeApi.getDeals(),
      ]);
      setSummary(summaryData);
      setTransactions(transactionsData);
      setDeals(dealsData);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки финансов');
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Ошибка</h3>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 shadow-lg">
        <div className="flex items-center gap-3 mb-2">
          <Wallet className="w-8 h-8" />
          <h1 className="text-2xl font-bold">Финансы</h1>
        </div>
        <p className="text-purple-100">Платежи и сделки</p>
      </div>

      {/* Tabs */}
      <div className="bg-white shadow-md sticky top-0 z-10">
        <div className="flex">
          <button
            onClick={() => setActiveTab('summary')}
            className={`flex-1 py-3 px-4 font-medium transition-colors ${
              activeTab === 'summary'
                ? 'text-purple-600 border-b-2 border-purple-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Обзор
          </button>
          <button
            onClick={() => setActiveTab('deals')}
            className={`flex-1 py-3 px-4 font-medium transition-colors ${
              activeTab === 'deals'
                ? 'text-purple-600 border-b-2 border-purple-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Сделки
          </button>
          <button
            onClick={() => setActiveTab('transactions')}
            className={`flex-1 py-3 px-4 font-medium transition-colors ${
              activeTab === 'transactions'
                ? 'text-purple-600 border-b-2 border-purple-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Платежи
          </button>
        </div>
      </div>

      <div className="p-4">
        {/* Summary Tab */}
        {activeTab === 'summary' && summary && (
          <div className="space-y-3">
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl shadow-lg p-6 text-white">
              <p className="text-green-100 mb-2">Оплачено</p>
              <p className="text-3xl font-bold">{formatAmount(summary.paid_amount)}</p>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-500 text-sm mb-1">Всего</p>
                  <p className="text-xl font-bold text-gray-900">
                    {formatAmount(summary.total_amount)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm mb-1">Остаток</p>
                  <p className="text-xl font-bold text-orange-600">
                    {formatAmount(summary.balance)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-8 h-8 text-purple-600" />
                <div>
                  <p className="text-gray-500 text-sm">Проектов</p>
                  <p className="text-2xl font-bold text-gray-900">{summary.projects_count}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Deals Tab */}
        {activeTab === 'deals' && (
          <div className="space-y-3">
            {deals.length === 0 ? (
              <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
                <DollarSign className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">Сделок пока нет</p>
              </div>
            ) : (
              deals.map((deal) => (
                <div key={deal.id} className="bg-white rounded-2xl shadow-md p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">{deal.title}</h3>
                  {deal.project_name && (
                    <p className="text-sm text-gray-600 mb-3">Проект: {deal.project_name}</p>
                  )}
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div>
                      <p className="text-gray-500">Сумма</p>
                      <p className="font-semibold">{formatAmount(deal.amount || 0)}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Оплачено</p>
                      <p className="font-semibold text-green-600">
                        {formatAmount(deal.paid_amount || 0)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Остаток</p>
                      <p className="font-semibold text-orange-600">
                        {formatAmount(deal.balance || 0)}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Transactions Tab */}
        {activeTab === 'transactions' && (
          <div className="space-y-3">
            {transactions.length === 0 ? (
              <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
                <CreditCard className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">Транзакций пока нет</p>
              </div>
            ) : (
              transactions.map((tr) => (
                <div key={tr.id} className="bg-white rounded-2xl shadow-md p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{tr.description}</h3>
                      <p className="text-sm text-gray-500">{tr.project_name}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg text-gray-900">
                        {formatAmount(tr.amount)}
                      </p>
                      <p className="text-xs text-gray-500">{tr.payment_method}</p>
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>{tr.type}</span>
                    <span>{new Date(tr.date).toLocaleDateString('ru-RU')}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Finance;
