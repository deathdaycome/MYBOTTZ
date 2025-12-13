# Система Балансов для Хостинг-Серверов

## ✅ Что было реализовано

### 1. База Данных

#### Модель HostingServer (обновлена)
Добавлены новые поля:
- `balance` (Float) - текущий баланс клиента в рублях
- `balance_last_updated` (DateTime) - дата последнего изменения баланса

Добавлены методы:
- `calculate_days_remaining()` - рассчитывает количество дней, на которые хватит баланса
- `get_payment_calendar(months_ahead=6)` - генерирует календарь платежей на N месяцев вперед

#### Модель BalanceTransaction (новая)
Таблица для хранения истории всех операций с балансом:
- `server_id` - ID сервера
- `amount` - сумма (положительная - пополнение, отрицательная - списание)
- `transaction_type` - тип транзакции (deposit, withdrawal, refund, adjustment)
- `balance_before` - баланс до операции
- `balance_after` - баланс после операции
- `description` - описание
- `payment_method` - способ оплаты
- `receipt_url` - ссылка на чек
- `admin_user_id`, `admin_user_name` - кто провел операцию
- `created_at` - дата и время

### 2. Миграции

Созданы и выполнены:
- `migrations/add_balance_to_hosting_servers.py` - добавляет поля balance
- `migrations/add_balance_transactions_table.py` - создает таблицу транзакций

Запустить миграции:
```bash
python3 migrations/add_balance_to_hosting_servers.py
python3 migrations/add_balance_transactions_table.py
```

## 📋 Как Работает Система

### Пример расчета:

Допустим у клиента:
- Месячная стоимость: 3000₽ (client_price + service_fee)
- Текущий баланс: 6000₽

Расчет:
```python
# Стоимость за день
daily_cost = 3000 / 30 = 100₽/день

# Количество дней
days_remaining = 6000 / 100 = 60 дней
```

### Календарь Платежей:

Система автоматически генерирует календарь на 6 месяцев вперед, показывая:
- Какие месяцы уже оплачены (статус: `paid`)
- Где баланса хватит частично (статус: `partial`)
- Какие месяцы не оплачены (статус: `unpaid`)
- Сколько не хватает для оплаты

## 🔧 API Endpoints (необходимо добавить)

### 1. Пополнение баланса
```python
@router.post("/api/servers/{server_id}/balance/deposit")
async def deposit_balance(
    server_id: int,
    amount: float,
    description: str = None,
    payment_method: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Пополнить баланс сервера"""
    # 1. Получить сервер
    # 2. Создать транзакцию
    # 3. Обновить balance сервера
    # 4. Обновить balance_last_updated
    pass
```

### 2. Списание с баланса
```python
@router.post("/api/servers/{server_id}/balance/withdraw")
async def withdraw_balance(
    server_id: int,
    amount: float,
    description: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Списать средства с баланса"""
    pass
```

### 3. История транзакций
```python
@router.get("/api/servers/{server_id}/balance/transactions")
async def get_balance_transactions(
    server_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_current_admin_user)
):
    """Получить историю транзакций"""
    pass
```

### 4. Календарь платежей
```python
@router.get("/api/servers/{server_id}/payment-calendar")
async def get_payment_calendar(
    server_id: int,
    months: int = 6,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить календарь платежей"""
    result = await db.execute(select(HostingServer).where(HostingServer.id == server_id))
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    calendar = server.get_payment_calendar(months_ahead=months)
    return {"calendar": calendar}
```

## 🎨 Frontend (изменения необходимы)

### 1. Отображение Баланса в Таблице

В таблице серверов добавить колонки:
```tsx
<th>Баланс</th>
<th>Осталось дней</th>
```

```tsx
<td>{server.balance?.toLocaleString('ru-RU')} ₽</td>
<td>
  {server.days_remaining > 0 ? (
    <span className={server.days_remaining < 30 ? 'text-warning' : 'text-success'}>
      {server.days_remaining} дней
    </span>
  ) : (
    <span className="text-danger">Баланс исчерпан</span>
  )}
</td>
```

### 2. Модальное Окно Пополнения Баланса

```tsx
function BalanceDepositModal({ server, onClose, onSuccess }) {
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('transfer');
  const [description, setDescription] = useState('');

  const handleSubmit = async () => {
    await fetch(`/admin/hosting/api/servers/${server.id}/balance/deposit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, payment_method: paymentMethod, description })
    });
    onSuccess();
  };

  return (
    <div className="modal">
      <h3>Пополнить баланс сервера {server.server_name}</h3>
      <div>
        <label>Сумма (₽)</label>
        <input
          type="number"
          value={amount}
          onChange={e => setAmount(e.target.value)}
        />
      </div>
      <div>
        <label>Способ оплаты</label>
        <select value={paymentMethod} onChange={e => setPaymentMethod(e.target.value)}>
          <option value="transfer">Перевод</option>
          <option value="card">Карта</option>
          <option value="cash">Наличные</option>
        </select>
      </div>
      <div>
        <label>Комментарий</label>
        <textarea value={description} onChange={e => setDescription(e.target.value)} />
      </div>
      <button onClick={handleSubmit}>Пополнить</button>
    </div>
  );
}
```

### 3. Календарь Платежей

```tsx
function PaymentCalendar({ serverId }) {
  const [calendar, setCalendar] = useState([]);

  useEffect(() => {
    fetch(`/admin/hosting/api/servers/${serverId}/payment-calendar`)
      .then(res => res.json())
      .then(data => setCalendar(data.calendar));
  }, [serverId]);

  return (
    <div className="payment-calendar">
      <h4>Календарь платежей</h4>
      <table>
        <thead>
          <tr>
            <th>Месяц</th>
            <th>Стоимость</th>
            <th>Статус</th>
            <th>Недостаток</th>
          </tr>
        </thead>
        <tbody>
          {calendar.map((month, idx) => (
            <tr key={idx} className={`status-${month.status}`}>
              <td>{month.month}</td>
              <td>{month.amount} ₽</td>
              <td>
                {month.status === 'paid' && '✅ Оплачено'}
                {month.status === 'partial' && '⚠️ Частично'}
                {month.status === 'unpaid' && '❌ Не оплачено'}
              </td>
              <td>{month.shortage > 0 ? `${month.shortage} ₽` : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## 📊 Пример использования

### Добавить баланс через Python:

```python
from app.database.models import HostingServer, BalanceTransaction
from datetime import datetime

# Получить сервер
server = db.query(HostingServer).filter(HostingServer.id == 1).first()

# Пополнить баланс
amount = 6000.0
balance_before = server.balance or 0
balance_after = balance_before + amount

# Создать транзакцию
transaction = BalanceTransaction(
    server_id=server.id,
    amount=amount,
    transaction_type="deposit",
    balance_before=balance_before,
    balance_after=balance_after,
    description="Пополнение баланса от клиента",
    payment_method="transfer",
    admin_user_id=current_user.id,
    admin_user_name=current_user.username
)

# Обновить сервер
server.balance = balance_after
server.balance_last_updated = datetime.utcnow()

db.add(transaction)
db.commit()

# Проверить сколько дней осталось
days = server.calculate_days_remaining()
print(f"Осталось дней: {days}")

# Получить календарь
calendar = server.get_payment_calendar()
for month in calendar:
    print(f"{month['month']}: {month['status']}")
```

## 🚀 Следующие Шаги

1. **Добавить API endpoints** в [app/admin/routers/hosting.py](app/admin/routers/hosting.py:1)
2. **Обновить фронтенд** для отображения баланса и календаря
3. **Настроить уведомления** когда баланс заканчивается (осталось < 7 дней)
4. **Добавить автоматическое списание** - ежедневно списывать стоимость за день
5. **Создать отчеты** по балансам всех клиентов

## 💡 Дополнительные Функции

### Автоматическое Списание (Cronjob)

Создать задачу которая каждый день:
1. Проходит по всем активным серверам
2. Рассчитывает дневную стоимость (monthly_cost / 30)
3. Списывает со баланса
4. Создает транзакцию типа "withdrawal"
5. Отправляет уведомление если баланс < 1000₽

### Уведомления

- Баланс < 7 дней - предупреждение
- Баланс < 3 дней - срочное предупреждение
- Баланс = 0 - сервер приостановлен

## 📝 Заметки

- Все расчеты в рублях (₽)
- Месяц считается как 30 дней для упрощения
- История транзакций хранится бессрочно
- При удалении сервера все транзакции также удаляются (CASCADE)
