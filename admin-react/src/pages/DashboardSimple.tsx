export const DashboardSimple = () => {
  return (
    <div className="p-8">
      <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 rounded-3xl p-8 text-white shadow-2xl">
        <h1 className="text-3xl font-bold mb-2">Тестовый Dashboard работает! 👋</h1>
        <p className="text-purple-100">Если вы видите это сообщение, значит React работает корректно.</p>
      </div>

      <div className="mt-8 bg-white rounded-2xl p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Проверка базового функционала</h2>
        <ul className="space-y-2 text-gray-700">
          <li>✅ React загрузился</li>
          <li>✅ Tailwind CSS работает</li>
          <li>✅ Градиенты отображаются</li>
          <li>✅ Шрифт Manrope применён</li>
        </ul>
      </div>
    </div>
  )
}
