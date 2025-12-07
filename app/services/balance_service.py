"""
Balance Service - Управление балансами клиентов
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.models import (
    ClientBalance,
    BalanceTransaction,
    HostingServer
)

logger = logging.getLogger(__name__)


class BalanceService:
    """Сервис для управления балансами клиентов"""

    def get_or_create_balance(
        self,
        db: Session,
        client_id: int,
        client_name: str,
        client_telegram_id: Optional[int] = None
    ) -> ClientBalance:
        """
        Получить или создать баланс клиента

        Args:
            db: Сессия БД
            client_id: ID клиента
            client_name: Имя клиента
            client_telegram_id: Telegram ID клиента

        Returns:
            Объект ClientBalance
        """
        balance = db.query(ClientBalance).filter(
            ClientBalance.client_id == client_id
        ).first()

        if not balance:
            balance = ClientBalance(
                client_id=client_id,
                client_name=client_name,
                client_telegram_id=client_telegram_id,
                balance=0.0,
                total_monthly_cost=0.0,
                days_remaining=0
            )
            db.add(balance)
            db.commit()
            db.refresh(balance)
            logger.info(f"Created new balance for client {client_id} ({client_name})")

        return balance

    def add_balance(
        self,
        db: Session,
        client_id: int,
        client_name: str,
        amount: float,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
        client_telegram_id: Optional[int] = None
    ) -> Tuple[ClientBalance, BalanceTransaction]:
        """
        Пополнить баланс клиента

        Args:
            db: Сессия БД
            client_id: ID клиента
            client_name: Имя клиента
            amount: Сумма пополнения
            description: Описание
            created_by: Кто создал транзакцию
            client_telegram_id: Telegram ID клиента

        Returns:
            Кортеж (ClientBalance, BalanceTransaction)
        """
        # Получаем или создаем баланс
        balance = self.get_or_create_balance(db, client_id, client_name, client_telegram_id)

        # ВАЖНО: Пересчитываем затраты перед пополнением (могли измениться цены серверов)
        self.update_client_costs(db, client_id, client_name)
        db.refresh(balance)

        # Сохраняем старый баланс
        old_balance = balance.balance

        # Обновляем баланс
        balance.balance += amount
        balance.updated_at = datetime.utcnow()

        # Пересчитываем дни
        balance.days_remaining = balance.calculate_days_remaining()

        # Обновляем дату следующего списания
        if balance.total_monthly_cost > 0 and balance.days_remaining > 0:
            # Дата следующего списания = сегодня + days_remaining
            balance.next_charge_date = datetime.utcnow() + timedelta(days=balance.days_remaining)

        # Сбрасываем флаг уведомления если баланс пополнен
        if balance.days_remaining > 5:
            balance.low_balance_notified = False

        # Создаем транзакцию
        transaction = BalanceTransaction(
            client_id=client_id,
            client_name=client_name,
            type="replenish",
            amount=amount,
            balance_before=old_balance,
            balance_after=balance.balance,
            description=description or f"Пополнение баланса на {amount}₽",
            created_by=created_by
        )

        db.add(transaction)
        db.commit()
        db.refresh(balance)
        db.refresh(transaction)

        logger.info(f"Added {amount}₽ to client {client_id} balance: {old_balance}₽ → {balance.balance}₽")

        return balance, transaction

    def charge_balance(
        self,
        db: Session,
        client_id: int,
        client_name: str,
        amount: float,
        server_id: Optional[int] = None,
        server_name: Optional[str] = None,
        description: Optional[str] = None,
        created_by: Optional[str] = "system"
    ) -> Tuple[ClientBalance, BalanceTransaction]:
        """
        Списать средства с баланса клиента

        Args:
            db: Сессия БД
            client_id: ID клиента
            client_name: Имя клиента
            amount: Сумма списания
            server_id: ID сервера
            server_name: Название сервера
            description: Описание
            created_by: Кто создал транзакцию

        Returns:
            Кортеж (ClientBalance, BalanceTransaction)

        Raises:
            ValueError: Если недостаточно средств
        """
        balance = self.get_or_create_balance(db, client_id, client_name)

        # Проверяем достаточность средств
        if balance.balance < amount:
            raise ValueError(
                f"Недостаточно средств на балансе клиента {client_name}. "
                f"Баланс: {balance.balance}₽, требуется: {amount}₽"
            )

        # Сохраняем старый баланс
        old_balance = balance.balance

        # Списываем средства
        balance.balance -= amount
        balance.last_charge_date = datetime.utcnow()
        balance.updated_at = datetime.utcnow()

        # Пересчитываем дни
        balance.days_remaining = balance.calculate_days_remaining()

        # Создаем транзакцию
        transaction = BalanceTransaction(
            client_id=client_id,
            client_name=client_name,
            type="charge",
            amount=amount,
            balance_before=old_balance,
            balance_after=balance.balance,
            description=description or f"Списание за сервер {server_name}",
            server_id=server_id,
            server_name=server_name,
            created_by=created_by
        )

        db.add(transaction)
        db.commit()
        db.refresh(balance)
        db.refresh(transaction)

        logger.info(f"Charged {amount}₽ from client {client_id}: {old_balance}₽ → {balance.balance}₽")

        return balance, transaction

    def update_client_costs(
        self,
        db: Session,
        client_id: int,
        client_name: str
    ) -> ClientBalance:
        """
        Обновить общую стоимость серверов клиента

        Args:
            db: Сессия БД
            client_id: ID клиента
            client_name: Имя клиента

        Returns:
            Обновленный ClientBalance
        """
        balance = self.get_or_create_balance(db, client_id, client_name)

        # Получаем все активные серверы клиента
        servers = db.query(HostingServer).filter(
            and_(
                HostingServer.client_id == client_id,
                HostingServer.status.in_(["active", "overdue"])
            )
        ).all()

        # Считаем общую месячную стоимость
        total_cost = sum(server.client_price for server in servers)

        balance.total_monthly_cost = total_cost
        balance.days_remaining = balance.calculate_days_remaining()
        balance.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(balance)

        logger.info(f"Updated costs for client {client_id}: {len(servers)} servers, total {total_cost}₽/month")

        return balance

    def get_clients_with_low_balance(
        self,
        db: Session,
        days_threshold: int = 5
    ) -> List[ClientBalance]:
        """
        Получить клиентов с низким балансом

        Args:
            db: Сессия БД
            days_threshold: Порог дней (по умолчанию 5)

        Returns:
            Список ClientBalance с низким балансом
        """
        return db.query(ClientBalance).filter(
            and_(
                ClientBalance.days_remaining <= days_threshold,
                ClientBalance.days_remaining >= 0,
                ClientBalance.total_monthly_cost > 0
            )
        ).all()

    def get_transactions(
        self,
        db: Session,
        client_id: int,
        limit: int = 50
    ) -> List[BalanceTransaction]:
        """
        Получить историю транзакций клиента

        Args:
            db: Сессия БД
            client_id: ID клиента
            limit: Максимальное количество транзакций

        Returns:
            Список транзакций
        """
        return db.query(BalanceTransaction).filter(
            BalanceTransaction.client_id == client_id
        ).order_by(
            BalanceTransaction.created_at.desc()
        ).limit(limit).all()

    def get_balance_summary(
        self,
        db: Session
    ) -> Dict:
        """
        Получить общую статистику по балансам

        Returns:
            Словарь со статистикой
        """
        balances = db.query(ClientBalance).all()

        total_balance = sum(b.balance for b in balances)
        total_monthly_revenue = sum(b.total_monthly_cost for b in balances)

        low_balance_clients = [b for b in balances if 0 <= b.days_remaining <= 5]
        negative_balance_clients = [b for b in balances if b.balance < 0]

        return {
            "total_clients": len(balances),
            "total_balance": total_balance,
            "total_monthly_revenue": total_monthly_revenue,
            "low_balance_count": len(low_balance_clients),
            "negative_balance_count": len(negative_balance_clients),
            "low_balance_clients": [b.to_dict() for b in low_balance_clients]
        }


# Global instance
balance_service = BalanceService()
