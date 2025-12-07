import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  Send,
  Paperclip,
  User,
  X,
  FileText,
  Video,
  Download,
  Eye
} from 'lucide-react';
import { useTelegram } from '../hooks/useTelegram';
import { chatsApi } from '../api/chats';

export const ChatDetail: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const { hapticFeedback } = useTelegram();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messageText, setMessageText] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState<'messages' | 'attachments'>('messages');
  const [lightboxImage, setLightboxImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Загружаем сообщения чата
  const { data: chatData, isLoading } = useQuery({
    queryKey: ['chat-messages', chatId],
    queryFn: () => chatsApi.getChatMessages(Number(chatId)),
    refetchInterval: 3000, // Обновляем каждые 3 секунды
  });

  const messages = chatData?.messages || [];
  const projectTitle = chatData?.project_title || 'Чат';
  const clientName = chatData?.client_name;

  // Мутация для отправки сообщения
  const sendMessageMutation = useMutation({
    mutationFn: (data: { message_text?: string; attachments?: File[] }) => {
      console.log('📤 Отправка сообщения:', {
        text: data.message_text,
        filesCount: data.attachments?.length || 0
      });
      return chatsApi.sendMessage(Number(chatId), data);
    },
    onSuccess: () => {
      console.log('✅ Сообщение успешно отправлено');
      queryClient.invalidateQueries({ queryKey: ['chat-messages', chatId] });
      queryClient.invalidateQueries({ queryKey: ['chats'] });
      setMessageText('');
      setSelectedFiles([]);
      setIsUploading(false);
      hapticFeedback('success');
    },
    onError: (error: any) => {
      console.error('❌ Ошибка отправки сообщения:', error);
      console.error('Детали ошибки:', error?.response?.data || error.message);
      setIsUploading(false);
      hapticFeedback('error');
    },
  });

  // Автоскролл к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!messageText.trim() && selectedFiles.length === 0) return;

    console.log('🎯 Начинаем отправку сообщения');
    console.log('Текст:', messageText.trim());
    console.log('Файлов:', selectedFiles.length);

    setIsUploading(true);
    sendMessageMutation.mutate({
      message_text: messageText.trim() || undefined,
      attachments: selectedFiles.length > 0 ? selectedFiles : undefined,
    });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setSelectedFiles((prev) => [...prev, ...newFiles]);
      hapticFeedback('light');
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    hapticFeedback('light');
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Вчера';
    } else {
      return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
    }
  };

  // Группируем сообщения по датам
  const groupedMessages = messages.reduce((acc: any, message: any) => {
    const dateKey = new Date(message.created_at).toDateString();
    if (!acc[dateKey]) {
      acc[dateKey] = [];
    }
    acc[dateKey].push(message);
    return acc;
  }, {});

  // Собираем все вложения
  const allAttachments = messages.flatMap((msg: any) =>
    (msg.attachments || []).map((att: any) => ({
      ...att,
      messageId: msg.id,
      createdAt: msg.created_at,
      senderName: msg.sender_name
    }))
  );

  // Определяем тип файла
  const getFileType = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext || '')) return 'image';
    if (['mp4', 'webm', 'ogg', 'mov'].includes(ext || '')) return 'video';
    if (['pdf'].includes(ext || '')) return 'pdf';
    return 'document';
  };

  // Рендер вложения в сообщении
  const renderAttachment = (attachment: any) => {
    const fileType = getFileType(attachment.filename);

    if (fileType === 'image') {
      return (
        <div
          onClick={() => setLightboxImage(attachment.url)}
          className="cursor-pointer rounded-lg overflow-hidden max-w-xs mb-2"
        >
          <img
            src={attachment.url}
            alt={attachment.filename}
            className="w-full h-auto rounded-lg hover:opacity-90 transition-opacity"
          />
        </div>
      );
    }

    if (fileType === 'video') {
      return (
        <video
          controls
          className="rounded-lg max-w-xs mb-2"
          src={attachment.url}
        >
          Ваш браузер не поддерживает видео.
        </video>
      );
    }

    if (fileType === 'pdf') {
      return (
        <a
          href={attachment.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-lg mb-2 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          <FileText className="w-5 h-5 text-red-500" />
          <span className="text-sm font-medium truncate max-w-[200px]">{attachment.filename}</span>
          <Eye className="w-4 h-4 ml-auto" />
        </a>
      );
    }

    return (
      <a
        href={attachment.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-lg mb-2 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      >
        <Paperclip className="w-4 h-4 text-gray-600 dark:text-gray-400" />
        <span className="text-sm font-medium truncate max-w-[200px]">{attachment.filename}</span>
        <Download className="w-4 h-4 ml-auto" />
      </a>
    );
  };

  return (
    <div className="h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white dark:bg-gray-800 shadow-sm"
      >
        <div className="px-4 py-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                hapticFeedback('light');
                navigate('/chats');
              }}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>
            <div className="flex-1">
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                {projectTitle}
              </h1>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Чат с исполнителем
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={() => {
              setActiveTab('messages');
              hapticFeedback('light');
            }}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'messages'
                ? 'text-emerald-600 border-b-2 border-emerald-600'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            Сообщения
          </button>
          <button
            onClick={() => {
              setActiveTab('attachments');
              hapticFeedback('light');
            }}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'attachments'
                ? 'text-emerald-600 border-b-2 border-emerald-600'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            Вложения ({allAttachments.length})
          </button>
        </div>
      </motion.div>

      {/* Content Area */}
      {activeTab === 'messages' ? (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
              </div>
            ) : Object.keys(groupedMessages).length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <User className="w-16 h-16 text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Нет сообщений
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Начните диалог с исполнителем
                </p>
              </div>
            ) : (
              Object.entries(groupedMessages).map(([dateKey, dateMessages]: [string, any]) => (
                <div key={dateKey}>
                  {/* Разделитель по датам */}
                  <div className="flex items-center justify-center my-4">
                    <div className="bg-gray-200 dark:bg-gray-700 px-3 py-1 rounded-full text-xs text-gray-600 dark:text-gray-400">
                      {formatDate(dateMessages[0].created_at)}
                    </div>
                  </div>

                  {/* Сообщения за дату */}
                  {dateMessages.map((message: any) => {
                    const isClient = message.sender_type === 'client';

                    return (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex ${isClient ? 'justify-end' : 'justify-start'} mb-3`}
                      >
                        <div className={`max-w-[75%] ${isClient ? 'order-2' : 'order-1'}`}>
                          {/* Имя отправителя */}
                          <div className={`text-xs mb-1 px-3 ${
                            isClient
                              ? 'text-gray-600 dark:text-gray-400 text-right'
                              : 'text-gray-600 dark:text-gray-400'
                          }`}>
                            {message.sender_name || (isClient ? clientName || 'Вы' : 'Исполнитель')}
                          </div>

                          {/* Bubble сообщения */}
                          <div
                            className={`px-4 py-2 rounded-2xl ${
                              isClient
                                ? 'bg-emerald-500 text-white rounded-br-sm'
                                : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-sm'
                            }`}
                          >
                            {/* Вложения */}
                            {message.attachments && message.attachments.length > 0 && (
                              <div className="mb-2">
                                {message.attachments.map((attachment: any, idx: number) => (
                                  <div key={idx}>
                                    {renderAttachment(attachment)}
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Текст сообщения */}
                            {message.message_text && (
                              <p className="text-sm break-words whitespace-pre-wrap">
                                {message.message_text}
                              </p>
                            )}

                            {/* Время */}
                            <div
                              className={`text-xs mt-1 ${
                                isClient ? 'text-emerald-100' : 'text-gray-500 dark:text-gray-400'
                              }`}
                            >
                              {formatTime(message.created_at)}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Selected Files Preview */}
          {selectedFiles.length > 0 && (
            <div className="px-4 py-2 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
              <div className="flex flex-wrap gap-2">
                {selectedFiles.map((file, index) => (
                  <motion.div
                    key={index}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="flex items-center gap-2 bg-white dark:bg-gray-700 px-3 py-1 rounded-lg text-sm shadow-sm"
                  >
                    <Paperclip className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    <span className="text-gray-900 dark:text-white truncate max-w-[150px]">
                      {file.name}
                    </span>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-3">
            <div className="flex items-end gap-2">
              {/* File Attach Button */}
              <button
                onClick={() => {
                  hapticFeedback('light');
                  fileInputRef.current?.click();
                }}
                disabled={isUploading}
                className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
              />

              {/* Text Input */}
              <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-2xl px-4 py-2">
                <textarea
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder="Напишите сообщение..."
                  disabled={isUploading}
                  className="w-full bg-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none outline-none text-sm disabled:opacity-50"
                  rows={1}
                  style={{
                    maxHeight: '120px',
                    minHeight: '24px',
                  }}
                />
              </div>

              {/* Send Button */}
              <button
                onClick={handleSendMessage}
                disabled={(!messageText.trim() && selectedFiles.length === 0) || isUploading}
                className={`p-2 rounded-lg transition-colors ${
                  (messageText.trim() || selectedFiles.length > 0) && !isUploading
                    ? 'bg-emerald-500 text-white hover:bg-emerald-600'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                }`}
              >
                {isUploading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </>
      ) : (
        /* Attachments Tab */
        <div className="flex-1 overflow-y-auto p-4">
          {allAttachments.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Paperclip className="w-16 h-16 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Нет вложений
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Вложенные файлы появятся здесь
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {allAttachments.map((attachment: any, idx: number) => {
                const fileType = getFileType(attachment.filename);

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-sm"
                  >
                    {fileType === 'image' ? (
                      <div
                        onClick={() => setLightboxImage(attachment.url)}
                        className="cursor-pointer"
                      >
                        <img
                          src={attachment.url}
                          alt={attachment.filename}
                          className="w-full h-32 object-cover"
                        />
                        <div className="p-2">
                          <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                            {attachment.filename}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            {attachment.senderName}
                          </p>
                        </div>
                      </div>
                    ) : fileType === 'video' ? (
                      <div>
                        <div className="relative h-32 bg-gray-900 flex items-center justify-center">
                          <Video className="w-12 h-12 text-white" />
                        </div>
                        <div className="p-2">
                          <a
                            href={attachment.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-emerald-600 dark:text-emerald-400 truncate block hover:underline"
                          >
                            {attachment.filename}
                          </a>
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            {attachment.senderName}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="h-32 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                          <FileText className="w-12 h-12 text-gray-400" />
                        </div>
                        <div className="p-2">
                          <a
                            href={attachment.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-emerald-600 dark:text-emerald-400 truncate block hover:underline"
                          >
                            {attachment.filename}
                          </a>
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            {attachment.senderName}
                          </p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Image Lightbox */}
      <AnimatePresence>
        {lightboxImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setLightboxImage(null)}
            className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          >
            <button
              onClick={() => setLightboxImage(null)}
              className="absolute top-4 right-4 text-white p-2 hover:bg-white/10 rounded-lg"
            >
              <X className="w-6 h-6" />
            </button>
            <img
              src={lightboxImage}
              alt="Preview"
              className="max-w-full max-h-full object-contain"
              onClick={(e) => e.stopPropagation()}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
