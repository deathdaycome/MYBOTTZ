import React, { useEffect, useState } from 'react';
import { Bell, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { notificationsApi, Notification } from '../api/notifications';

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const data = await notificationsApi.getNotifications(50);
      setNotifications(data);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки уведомлений');
    } finally {
      setLoading(false);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
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
          <Bell className="w-8 h-8" />
          <h1 className="text-2xl font-bold">Уведомления</h1>
        </div>
        <p className="text-purple-100">Все важные обновления</p>
      </div>

      <div className="p-4 space-y-3">
        {notifications.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Уведомлений пока нет</p>
          </div>
        ) : (
          notifications.map((notif) => (
            <div
              key={notif.id}
              className="bg-white rounded-2xl shadow-md p-4 hover:shadow-lg transition-shadow"
            >
              <div className="flex gap-3">
                <div className="flex-shrink-0 mt-1">
                  {getNotificationIcon(notif.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {notif.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-2 whitespace-pre-wrap">
                    {notif.message}
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(notif.sent_at).toLocaleString('ru-RU')}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notifications;
