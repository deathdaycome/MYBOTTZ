import { useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';

export const TestRevisions = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <h1 className="text-2xl font-bold mb-6">Тестирование системы правок</h1>
      
      <div className="space-y-3">
        <Button 
          onClick={() => navigate('/projects/1/revisions')}
          fullWidth
        >
          📋 Список правок проекта #1
        </Button>
        
        <Button 
          onClick={() => navigate('/projects/1/revisions/new')}
          fullWidth
        >
          ➕ Создать новую правку
        </Button>
        
        <Button 
          onClick={() => navigate('/revisions/1')}
          fullWidth
        >
          💬 Чат правки #1
        </Button>

        <Button 
          onClick={() => navigate('/')}
          fullWidth
          variant="secondary"
        >
          🏠 На главную
        </Button>
      </div>

      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold mb-2">💡 Инструкция:</h3>
        <ol className="list-decimal list-inside space-y-1 text-sm">
          <li>Кликни "Список правок" чтобы увидеть все правки</li>
          <li>Кликни "Создать правку" для создания новой (4 шага)</li>
          <li>Кликни "Чат правки" чтобы увидеть детали и чат</li>
        </ol>
      </div>
    </div>
  );
};
