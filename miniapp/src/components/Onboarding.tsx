import { useState } from 'react';
import { useTelegram } from '../hooks/useTelegram';

interface OnboardingProps {
  onComplete: () => void;
}

export function Onboarding({ onComplete }: OnboardingProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const { webApp } = useTelegram();

  const slides = [
    {
      emoji: '👋',
      title: 'Добро пожаловать!',
      description: 'Управляйте проектами и правками прямо из Telegram',
      features: [
        { icon: '📱', text: 'Просматривайте проекты' },
        { icon: '✏️', text: 'Создавайте правки' },
        { icon: '💬', text: 'Общайтесь в чате' },
      ],
    },
    {
      emoji: '🆔',
      title: 'Ваш Telegram ID',
      description: 'Уникальный номер для связи с проектами',
      steps: [
        { number: '1', text: 'Нажмите на кнопку ниже' },
        { number: '2', text: 'Скопируйте ваш ID' },
        { number: '3', text: 'Отправьте администратору' },
      ],
      showId: true,
    },
    {
      emoji: '🚀',
      title: 'Всё готово!',
      description: 'Начните работать с вашими проектами',
      highlights: [
        { icon: '📊', title: 'Дашборд', text: 'Все проекты в одном месте' },
        { icon: '📝', title: 'Правки', text: 'Быстрое создание и отслеживание' },
        { icon: '🔔', title: 'Уведомления', text: 'Будьте в курсе изменений' },
      ],
    },
  ];

  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    } else {
      onComplete();
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  const copyTelegramId = () => {
    if (webApp?.initDataUnsafe?.user?.id) {
      navigator.clipboard.writeText(String(webApp.initDataUnsafe.user.id));
      webApp.showPopup({
        title: '✅ Скопировано!',
        message: 'ID скопирован в буфер обмена',
        buttons: [{ type: 'ok' }],
      });
    }
  };

  const slide = slides[currentSlide];

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Skip button */}
      <button
        onClick={handleSkip}
        className="absolute top-6 right-6 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 font-medium z-10"
      >
        Пропустить
      </button>

      <div className="flex flex-col items-center justify-between h-full px-6 py-12">
        {/* Content */}
        <div className="flex-1 flex flex-col items-center justify-center w-full max-w-md">
          {/* Emoji Icon */}
          <div className="text-8xl mb-6 animate-bounce-slow">
            {slide.emoji}
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-center mb-3 text-gray-900 dark:text-white">
            {slide.title}
          </h1>

          {/* Description */}
          <p className="text-center text-gray-600 dark:text-gray-300 mb-8 text-lg">
            {slide.description}
          </p>

          {/* Slide-specific content */}
          <div className="w-full">
            {/* Slide 1: Features */}
            {currentSlide === 0 && (
              <div className="space-y-4">
                {slide.features?.map((feature, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-4 bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-md transform transition-all hover:scale-105"
                    style={{
                      animation: `slideInRight 0.5s ease-out ${index * 0.1}s both`,
                    }}
                  >
                    <div className="text-3xl">{feature.icon}</div>
                    <p className="text-gray-700 dark:text-gray-200 font-medium">
                      {feature.text}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Slide 2: Steps + Telegram ID */}
            {currentSlide === 1 && (
              <div className="space-y-6">
                {/* Telegram ID Card */}
                {slide.showId && webApp?.initDataUnsafe?.user?.id && (
                  <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 shadow-xl mb-6">
                    <p className="text-white text-sm font-medium mb-2 opacity-90">
                      Ваш Telegram ID
                    </p>
                    <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 mb-4">
                      <p className="text-white text-2xl font-bold text-center tracking-wider">
                        {webApp.initDataUnsafe.user.id}
                      </p>
                    </div>
                    <button
                      onClick={copyTelegramId}
                      className="w-full bg-white text-blue-600 font-semibold py-3 rounded-xl hover:bg-blue-50 transition-colors flex items-center justify-center space-x-2"
                    >
                      <span>📋</span>
                      <span>Скопировать ID</span>
                    </button>
                  </div>
                )}

                {/* Steps */}
                <div className="space-y-3">
                  {slide.steps?.map((step, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-4"
                      style={{
                        animation: `fadeIn 0.5s ease-out ${index * 0.15}s both`,
                      }}
                    >
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-lg">
                        {step.number}
                      </div>
                      <p className="text-gray-700 dark:text-gray-200 font-medium">
                        {step.text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Slide 3: Highlights */}
            {currentSlide === 2 && (
              <div className="space-y-4">
                {slide.highlights?.map((item, index) => (
                  <div
                    key={index}
                    className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-md"
                    style={{
                      animation: `slideInUp 0.5s ease-out ${index * 0.1}s both`,
                    }}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="text-4xl">{item.icon}</div>
                      <div>
                        <h3 className="font-bold text-gray-900 dark:text-white mb-1">
                          {item.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {item.text}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Bottom section */}
        <div className="w-full max-w-md">
          {/* Dots indicator */}
          <div className="flex justify-center space-x-2 mb-6">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`h-2 rounded-full transition-all ${
                  index === currentSlide
                    ? 'w-8 bg-gradient-to-r from-blue-500 to-purple-600'
                    : 'w-2 bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>

          {/* Next button */}
          <button
            onClick={handleNext}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-4 rounded-2xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98] transition-all"
          >
            {currentSlide === slides.length - 1 ? '🎉 Начать работу' : 'Далее →'}
          </button>
        </div>
      </div>

      <style>{`
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-20px);
          }
        }

        .animate-bounce-slow {
          animation: bounce-slow 2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
