import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { projectsApi } from '../api/projects';
import { useTelegram } from '../hooks/useTelegram';

type ProjectType = 'telegram_bot' | 'telegram_miniapp' | 'whatsapp_bot' | 'android_app' | 'ios_app';
type Step = 'type' | 'name' | 'description' | 'deadline';

interface ProjectTypeInfo {
  name: string;
  type: ProjectType;
  emoji: string;
}

const projectTypes: Record<string, ProjectTypeInfo> = {
  telegram_bot: { name: 'Telegram бот', type: 'telegram_bot', emoji: '🤖' },
  telegram_miniapp: { name: 'Telegram Mini App', type: 'telegram_miniapp', emoji: '✨' },
  whatsapp_bot: { name: 'WhatsApp бот', type: 'whatsapp_bot', emoji: '💬' },
  android_app: { name: 'Android приложение', type: 'android_app', emoji: '🤖' },
  ios_app: { name: 'iOS приложение', type: 'ios_app', emoji: '📱' },
};

const deadlineOptions = [
  { value: 'Как можно быстрее', label: 'Как можно быстрее' },
  { value: 'В течение месяца', label: 'В течение месяца' },
  { value: '1-3 месяца', label: '1-3 месяца' },
  { value: '3-6 месяцев', label: '3-6 месяцев' },
  { value: 'Более 6 месяцев', label: 'Более 6 месяцев' },
  { value: 'Не критично', label: 'Не критично' },
];

export const QuickProjectCreate = () => {
  const navigate = useNavigate();
  const { BackButton } = useTelegram();

  const [currentStep, setCurrentStep] = useState<Step>('type');
  const [selectedType, setSelectedType] = useState<ProjectTypeInfo | null>(null);
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [deadline, setDeadline] = useState('');

  const createProjectMutation = useMutation({
    mutationFn: () =>
      projectsApi.createQuickProject({
        title: projectName,
        description: description,
        project_type: selectedType!.type,
        budget: 'Не указан',
        deadline: deadline,
      }),
    onSuccess: () => {
      alert('✅ Проект успешно создан! Мы свяжемся с вами в ближайшее время.');
      navigate('/projects');
    },
    onError: (error) => {
      console.error('Ошибка создания проекта:', error);
      alert('Не удалось создать проект. Попробуйте еще раз.');
    },
  });

  useEffect(() => {
    BackButton.show();
    BackButton.onClick(() => {
      if (currentStep === 'type') {
        navigate('/');
      } else {
        // Возврат на предыдущий шаг
        const steps: Step[] = ['type', 'name', 'description', 'deadline'];
        const currentIndex = steps.indexOf(currentStep);
        if (currentIndex > 0) {
          setCurrentStep(steps[currentIndex - 1]);
        }
      }
    });

    return () => {
      BackButton.hide();
    };
  }, [BackButton, navigate, currentStep]);

  const handleTypeSelect = (type: ProjectTypeInfo) => {
    setSelectedType(type);
    setCurrentStep('name');
  };

  const handleNameSubmit = () => {
    if (projectName.trim().length < 3) {
      alert('Название слишком короткое. Минимум 3 символа.');
      return;
    }
    setCurrentStep('description');
  };

  const handleDescriptionSubmit = () => {
    if (description.trim().length < 10) {
      alert('Описание слишком короткое. Минимум 10 символов.');
      return;
    }
    setCurrentStep('deadline');
  };

  const handleDeadlineSelect = (value: string) => {
    setDeadline(value);
    createProjectMutation.mutate();
  };

  const getStepNumber = () => {
    const steps: Record<Step, number> = {
      type: 0,
      name: 1,
      description: 2,
      deadline: 3,
    };
    return steps[currentStep];
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-20">
      {/* Прогресс */}
      {currentStep !== 'type' && (
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {selectedType?.emoji} {selectedType?.name}
            </span>
            <span className="text-sm text-gray-500">
              Шаг {getStepNumber()} из 3
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(getStepNumber() / 3) * 100}%` }}
            />
          </div>
        </div>
      )}

      <div className="p-4">
        <AnimatePresence mode="wait">
          {/* Шаг 1: Выбор типа проекта */}
          {currentStep === 'type' && (
            <motion.div
              key="type"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                ⚡ Быстрое создание проекта
              </h1>
              <p className="text-gray-600 mb-6">
                Создайте заявку за 2 минуты! Ответьте на 3 простых вопроса.
              </p>

              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
                <p className="text-sm text-blue-900 font-medium mb-2">💡 Что дальше:</p>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Изучим вашу заявку</li>
                  <li>• Свяжемся в течение 2 часов</li>
                  <li>• Обсудим детали и подготовим предложение</li>
                </ul>
              </div>

              <p className="text-sm font-medium text-gray-700 mb-3">Выберите тип проекта:</p>

              <div className="space-y-3">
                {Object.values(projectTypes).map((type) => (
                  <motion.button
                    key={type.type}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleTypeSelect(type)}
                    className="w-full bg-white border-2 border-gray-200 rounded-xl p-4 text-left hover:border-blue-500 hover:shadow-md transition-all"
                  >
                    <span className="text-2xl mr-3">{type.emoji}</span>
                    <span className="text-lg font-medium text-gray-900">{type.name}</span>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Шаг 2: Название */}
          {currentStep === 'name' && (
            <motion.div
              key="name"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Шаг 1 из 4: Название
              </h2>
              <p className="text-gray-600 mb-6">
                Как назовем ваш проект? Придумайте короткое и понятное название.
              </p>

              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-6">
                <p className="text-sm text-gray-700 font-medium mb-2">Примеры:</p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• "Магазин одежды"</li>
                  <li>• "Бот для записи на услуги"</li>
                  <li>• "Мини-игра для Telegram"</li>
                </ul>
              </div>

              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Введите название проекта"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
                autoFocus
              />

              <button
                onClick={handleNameSubmit}
                disabled={projectName.trim().length < 3}
                className="w-full bg-blue-500 text-white py-3 rounded-xl font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Продолжить →
              </button>
            </motion.div>
          )}

          {/* Шаг 3: Описание */}
          {currentStep === 'description' && (
            <motion.div
              key="description"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Шаг 2 из 3: Описание задачи
              </h2>
              <p className="text-gray-600 mb-2">✅ Название: <i>{projectName}</i></p>
              <p className="text-gray-600 mb-6">
                Опишите что должно делать приложение. Напишите 2-3 предложения о главных функциях.
              </p>

              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-6">
                <p className="text-sm text-gray-700 font-medium mb-2">Примеры:</p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• "Бот для продажи товаров с каталогом, корзиной и оплатой"</li>
                  <li>• "Игра в Telegram с рейтингом игроков и призами"</li>
                  <li>• "Приложение для доставки еды с картой и трекингом"</li>
                </ul>
              </div>

              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Опишите задачу..."
                rows={5}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4 resize-none"
                autoFocus
              />

              <button
                onClick={handleDescriptionSubmit}
                disabled={description.trim().length < 10}
                className="w-full bg-blue-500 text-white py-3 rounded-xl font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Продолжить →
              </button>
            </motion.div>
          )}

          {/* Шаг 3: Сроки */}
          {currentStep === 'deadline' && (
            <motion.div
              key="deadline"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Шаг 3 из 3: Сроки
              </h2>
              <p className="text-gray-600 mb-2">✅ Название: <i>{projectName}</i></p>
              <p className="text-gray-600 mb-2">✅ Описание: <i>{description.slice(0, 50)}...</i></p>
              <p className="text-gray-600 mb-6">
                Когда нужно завершить проект? Выберите желаемый срок.
              </p>

              {createProjectMutation.isPending ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  {deadlineOptions.map((option) => (
                    <motion.button
                      key={option.value}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleDeadlineSelect(option.value)}
                      className="bg-white border-2 border-gray-200 rounded-xl p-4 text-center hover:border-blue-500 hover:shadow-md transition-all"
                    >
                      <span className="text-sm font-medium text-gray-900">{option.label}</span>
                    </motion.button>
                  ))}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
