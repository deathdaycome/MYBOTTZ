import { motion } from 'framer-motion';
import type { RevisionMessage } from '../../types/revision';

interface ChatMessageProps {
  message: RevisionMessage;
  isOwn: boolean;
}

export const ChatMessage = ({ message, isOwn }: ChatMessageProps) => {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  const getSenderInfo = () => {
    if (message.sender_type === 'client') {
      return {
        name: 'Вы',
        color: 'bg-blue-500',
        textColor: 'text-white',
        avatar: '👤',
        bubbleColor: 'bg-blue-500',
        bubbleText: 'text-white'
      };
    }
    if (message.sender_type === 'executor') {
      return {
        name: 'Исполнитель',
        color: 'bg-purple-500',
        textColor: 'text-white',
        avatar: '👨‍💼',
        bubbleColor: 'bg-white',
        bubbleText: 'text-gray-900'
      };
    }
    return {
      name: 'Админ',
      color: 'bg-green-500',
      textColor: 'text-white',
      avatar: '⭐',
      bubbleColor: 'bg-white',
      bubbleText: 'text-gray-900'
    };
  };

  const sender = getSenderInfo();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={'flex mb-4 gap-2 ' + (isOwn ? 'justify-end' : 'justify-start')}
    >
      {/* Аватар слева для чужих сообщений */}
      {!isOwn && (
        <div className={`flex-shrink-0 w-10 h-10 rounded-full ${sender.color} flex items-center justify-center text-xl`}>
          {sender.avatar}
        </div>
      )}

      <div className={'max-w-[70%] flex flex-col gap-1 ' + (isOwn ? 'items-end' : 'items-start')}>
        {/* Имя отправителя */}
        {!isOwn && (
          <span className="text-xs font-semibold text-gray-700 px-2">
            {sender.name}
          </span>
        )}

        {/* Пузырь сообщения */}
        <div
          className={`rounded-2xl px-4 py-3 shadow-sm ${
            isOwn
              ? 'bg-blue-500 text-white rounded-br-none'
              : 'bg-white text-gray-900 border border-gray-200 rounded-bl-none'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{message.message}</p>

          {message.files && message.files.length > 0 && (
            <div className="mt-3 space-y-2">
              {message.files.map((file) => (
                <div key={file.id}>
                  {file.file_type === 'image' ? (
                    <a
                      href={file.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block"
                    >
                      <img
                        src={file.file_url}
                        alt={file.original_filename}
                        className="max-w-full rounded-lg cursor-pointer hover:opacity-90 transition-opacity border-2 border-white/20"
                        style={{ maxHeight: '300px', objectFit: 'cover' }}
                      />
                      <div className={`text-xs mt-1 ${isOwn ? 'text-blue-100' : 'text-gray-600'}`}>
                        📷 {file.original_filename} ({(file.file_size / 1024).toFixed(1)} KB)
                      </div>
                    </a>
                  ) : (
                    <a
                      href={file.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`flex items-center gap-2 text-xs p-2 rounded-lg ${
                        isOwn ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-100 hover:bg-gray-200'
                      } transition-colors`}
                    >
                      <span>📎</span>
                      <span className="truncate flex-1">{file.original_filename}</span>
                      <span className="text-xs opacity-75">({(file.file_size / 1024).toFixed(1)} KB)</span>
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Время внутри пузыря */}
          <div className={`text-xs mt-2 ${isOwn ? 'text-blue-100' : 'text-gray-500'} text-right`}>
            {formatTime(message.created_at)}
          </div>
        </div>
      </div>

      {/* Аватар справа для своих сообщений */}
      {isOwn && (
        <div className={`flex-shrink-0 w-10 h-10 rounded-full ${sender.color} flex items-center justify-center text-xl`}>
          {sender.avatar}
        </div>
      )}
    </motion.div>
  );
};
