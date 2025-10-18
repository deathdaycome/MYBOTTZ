import React, { useEffect, useState } from 'react';
import { FileText, Download, AlertCircle } from 'lucide-react';
import { documentsApi, Document } from '../api/documents';

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const data = await documentsApi.getDocuments();
      setDocuments(data);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки документов');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'signed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'signed':
        return 'Подписан';
      case 'pending':
        return 'Ожидает подписи';
      case 'draft':
        return 'Черновик';
      default:
        return status;
    }
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
          <FileText className="w-8 h-8" />
          <h1 className="text-2xl font-bold">Документы</h1>
        </div>
        <p className="text-purple-100">Договоры, акты и счета</p>
      </div>

      <div className="p-4 space-y-3">
        {documents.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Документов пока нет</p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-2xl shadow-md p-4 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-3">
                <FileText className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 mb-1">{doc.name}</h3>
                  {doc.description && (
                    <p className="text-sm text-gray-600 mb-2">{doc.description}</p>
                  )}
                  <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                    <span className={`px-2 py-1 rounded-full ${getStatusColor(doc.status)}`}>
                      {getStatusText(doc.status)}
                    </span>
                    {doc.number && <span>№ {doc.number}</span>}
                    {doc.date && <span>{new Date(doc.date).toLocaleDateString('ru-RU')}</span>}
                  </div>
                </div>
                {doc.file_url && (
                  <a
                    href={doc.file_url}
                    download
                    className="flex-shrink-0 p-2 bg-purple-100 text-purple-600 rounded-full hover:bg-purple-200 transition-colors"
                  >
                    <Download className="w-5 h-5" />
                  </a>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Documents;
