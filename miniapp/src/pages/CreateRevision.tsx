import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { revisionsApi } from '../api/revisions';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Textarea } from '../components/common/Textarea';
import { useTelegram } from '../hooks/useTelegram';
import type { RevisionPriority } from '../types/revision';

const STEPS = [
  { id: 1, title: 'Заголовок', description: 'Краткое описание правки' },
  { id: 2, title: 'Описание', description: 'Подробное описание правки' },
  { id: 3, title: 'Файлы', description: 'Прикрепите файлы (опционально)' },
  { id: 4, title: 'Приоритет', description: 'Выберите приоритет правки' },
];

export const CreateRevision = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { BackButton, showAlert } = useTelegram();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'normal' as RevisionPriority,
    files: [] as File[],
  });

  // Мутация для создания правки
  const createMutation = useMutation({
    mutationFn: () => revisionsApi.createRevision({
      project_id: Number(projectId),
      title: formData.title,
      description: formData.description,
      priority: formData.priority,
      files: formData.files,
    }),
    onSuccess: (data) => {
      showAlert('Правка успешно создана!');
      navigate(`/revisions/${data.id}`);
    },
    onError: () => {
      showAlert('Ошибка при создании правки');
    },
  });

  useEffect(() => {
    BackButton.show();
    BackButton.onClick(() => {
      if (currentStep > 1) {
        setCurrentStep(currentStep - 1);
      } else {
        navigate(`/projects/${projectId}/revisions`);
      }
    });
    
    return () => {
      BackButton.hide();
    };
  }, [BackButton, navigate, currentStep, projectId]);

  const handleNext = () => {
    // Валидация
    if (currentStep === 1 && (formData.title.length < 5 || formData.title.length > 200)) {
      showAlert('Заголовок должен быть от 5 до 200 символов');
      return;
    }
    
    if (currentStep === 2 && formData.description.length < 10) {
      showAlert('Описание должно содержать минимум 10 символов');
      return;
    }

    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    } else {
      createMutation.mutate();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFormData({ ...formData, files: Array.from(e.target.files) });
    }
  };

  const removeFile = (index: number) => {
    const newFiles = [...formData.files];
    newFiles.splice(index, 1);
    setFormData({ ...formData, files: newFiles });
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Прогресс */}
      <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10">
        <h1 className="text-xl font-bold text-gray-900 mb-4">Создание правки</h1>
        
        {/* Индикатор шагов */}
        <div className="flex items-center justify-between mb-2">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center flex-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                  currentStep >= step.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step.id}
              </div>
              {index < STEPS.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-2 rounded transition-colors ${
                    currentStep > step.id ? 'bg-primary-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-2">
          <p className="font-medium text-gray-900">{STEPS[currentStep - 1].title}</p>
          <p className="text-sm text-gray-600">{STEPS[currentStep - 1].description}</p>
        </div>
      </div>

      {/* Контент шага */}
      <div className="p-4">
        <AnimatePresence mode="wait">
          {/* Шаг 1: Заголовок */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <Input
                label="Заголовок правки"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Например: Исправить ошибку авторизации"
                
              />
              <p className="text-sm text-gray-600">
                {formData.title.length}/200 символов
              </p>
            </motion.div>
          )}

          {/* Шаг 2: Описание */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <Textarea
                label="Подробное описание"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Опишите подробно, что нужно исправить или добавить..."
                rows={8}
              />
              <p className="text-sm text-gray-600">
                Минимум 10 символов ({formData.description.length})
              </p>
            </motion.div>
          )}

          {/* Шаг 3: Файлы */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <div className="text-4xl mb-4">📎</div>
                <label className="cursor-pointer">
                  <span className="text-primary-600 hover:text-primary-700 font-medium">
                    Выберите файлы
                  </span>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                    accept="image/*,.pdf,.doc,.docx"
                  />
                </label>
                <p className="text-sm text-gray-500 mt-2">
                  Изображения, PDF, документы (необязательно)
                </p>
              </div>

              {/* Список прикрепленных файлов */}
              {formData.files.length > 0 && (
                <div className="space-y-2">
                  {formData.files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-white rounded-lg p-3 border border-gray-200"
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <span className="text-2xl">📄</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(file.size / 1024).toFixed(1)} KB
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-600 hover:text-red-700 ml-2"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* Шаг 4: Приоритет */}
          {currentStep === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-3"
            >
              {[
                { value: 'low', label: 'Низкий', emoji: '🟢', desc: 'Не срочно, можно сделать позже' },
                { value: 'normal', label: 'Обычный', emoji: '🔵', desc: 'Стандартный приоритет' },
                { value: 'high', label: 'Высокий', emoji: '🟡', desc: 'Важная правка, нужно сделать быстрее' },
                { value: 'urgent', label: 'Срочный', emoji: '🔴', desc: 'Критично, требует немедленного внимания' },
              ].map((priority) => (
                <button
                  key={priority.value}
                  onClick={() => setFormData({ ...formData, priority: priority.value as RevisionPriority })}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                    formData.priority === priority.value
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{priority.emoji}</span>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{priority.label}</p>
                      <p className="text-sm text-gray-600">{priority.desc}</p>
                    </div>
                    {formData.priority === priority.value && (
                      <span className="text-primary-600">✓</span>
                    )}
                  </div>
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Кнопки навигации */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
        <Button
          onClick={handleNext}
          disabled={createMutation.isPending}
          fullWidth
        >
          {currentStep === 4 
            ? (createMutation.isPending ? 'Создание...' : 'Создать правку')
            : 'Далее'
          }
        </Button>
      </div>
    </div>
  );
};
