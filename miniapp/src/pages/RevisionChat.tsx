import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { revisionsApi } from '../api/revisions';
import { RevisionBadge } from '../components/revisions/RevisionBadge';
import { ProgressBar } from '../components/revisions/ProgressBar';
import { ChatMessage } from '../components/revisions/ChatMessage';


import { useTelegram } from '../hooks/useTelegram';

export const RevisionChat = () => {
  const { revisionId } = useParams<{ revisionId: string }>();
  const navigate = useNavigate();
  const { BackButton, user } = useTelegram();
  const queryClient = useQueryClient();
  
  const [newMessage, setNewMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Получаем детали правки
  const { data: revision, isLoading: revisionLoading } = useQuery({
    queryKey: ['revision', revisionId],
    queryFn: () => revisionsApi.getRevisionDetails(Number(revisionId)),
    enabled: !!revisionId,
  });

  // Получаем сообщения
  const { data: messages = [], isLoading: messagesLoading } = useQuery({
    queryKey: ['revision-messages', revisionId],
    queryFn: () => revisionsApi.getRevisionMessages(Number(revisionId)),
    enabled: !!revisionId,
    refetchInterval: 5000, // Обновляем каждые 5 секунд
  });

  // Мутация для отправки сообщения
  const sendMessageMutation = useMutation({
    mutationFn: ({ message, files }: { message: string; files?: File[] }) =>
      revisionsApi.sendRevisionMessage(Number(revisionId), message, files),
    onSuccess: () => {
      setNewMessage('');
      setSelectedFiles([]);
      queryClient.invalidateQueries({ queryKey: ['revision-messages', revisionId] });
      scrollToBottom();
    },
    onError: (error) => {
      console.error('Ошибка отправки сообщения:', error);
      alert('Не удалось отправить сообщение. Попробуйте еще раз.');
    },
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    BackButton.show();
    BackButton.onClick(() => navigate(`/projects/${revision?.project_id}/revisions`));
    
    return () => {
      BackButton.hide();
    };
  }, [BackButton, navigate, revision]);

  const handleSendMessage = () => {
    if (!newMessage.trim() && selectedFiles.length === 0) return;
    sendMessageMutation.mutate({
      message: newMessage.trim() || 'Файлы',
      files: selectedFiles.length > 0 ? selectedFiles : undefined,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    // Фильтруем только изображения и видео
    const validFiles = files.filter(file =>
      file.type.startsWith('image/') || file.type.startsWith('video/')
    );

    if (validFiles.length < files.length) {
      alert('Можно прикреплять только фото и видео');
    }

    setSelectedFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  if (revisionLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка правки...</p>
        </div>
      </div>
    );
  }

  if (!revision) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Правка не найдена</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Шапка с деталями правки */}
      <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10 shadow-sm">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h1 className="text-lg font-bold text-gray-900">
              #{revision.revision_number} - {revision.title}
            </h1>
            <p className="text-sm text-gray-600 mt-1">{revision.description}</p>
          </div>
        </div>

        {/* Статус и приоритет */}
        <div className="flex items-center gap-2 mb-3">
          <RevisionBadge type="status" value={revision.status} />
          <RevisionBadge type="priority" value={revision.priority} />
        </div>

        {/* Прогресс-бар (только для статуса in_progress) */}
        {revision.status === 'in_progress' && (
          <ProgressBar 
            progress={revision.progress} 
            timeSpentSeconds={revision.time_spent_seconds}
          />
        )}
      </div>

      {/* Область сообщений */}
      <div
        className="flex-1 overflow-y-auto p-4 pb-24"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23e5e7eb' fill-opacity='0.15'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          backgroundColor: '#f9fafb'
        }}
      >
        {messagesLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-12 bg-white/50 backdrop-blur-sm rounded-2xl mx-4 shadow-sm">
            <div className="text-5xl mb-3">💬</div>
            <p className="text-gray-700 font-medium">Сообщений пока нет</p>
            <p className="text-sm text-gray-500 mt-1">Напишите первое сообщение исполнителю</p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              isOwn={message.sender_user_id === user?.id}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Поле ввода сообщения */}
      <div className="bg-white border-t border-gray-200 p-3 fixed bottom-0 left-0 right-0 shadow-lg">
        <div className="max-w-4xl mx-auto">
          {/* Превью прикрепленных файлов */}
          {selectedFiles.length > 0 && (
            <div className="mb-3 flex gap-2 overflow-x-auto pb-2">
              {selectedFiles.map((file, index) => (
                <div key={index} className="relative flex-shrink-0">
                  <div className="w-20 h-20 rounded-lg overflow-hidden bg-gray-100 border border-gray-300">
                    {file.type.startsWith('image/') ? (
                      <img
                        src={URL.createObjectURL(file)}
                        alt={file.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-2xl">
                        🎥
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 active:scale-90 transition-all shadow-md"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Панель ввода */}
          <div className="flex items-end gap-2">
            {/* Кнопка прикрепления */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={sendMessageMutation.isPending}
              className="bg-gray-100 text-gray-700 rounded-full w-12 h-12 flex items-center justify-center hover:bg-gray-200 active:scale-95 transition-all disabled:opacity-50"
              title="Прикрепить фото или видео"
            >
              <span className="text-2xl">📎</span>
            </button>

            {/* Поле ввода */}
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Сообщение..."
              className="flex-1 resize-none rounded-2xl border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32 bg-gray-50 text-gray-900 placeholder:text-gray-400 transition-all"
              rows={1}
              disabled={sendMessageMutation.isPending}
            />

            {/* Кнопка отправки */}
            <button
              onClick={handleSendMessage}
              disabled={(!newMessage.trim() && selectedFiles.length === 0) || sendMessageMutation.isPending}
              className="bg-blue-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600 active:scale-95 transition-all shadow-md disabled:shadow-none"
            >
              {sendMessageMutation.isPending ? (
                <div className="animate-spin">⏳</div>
              ) : (
                <span className="text-xl">➤</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
