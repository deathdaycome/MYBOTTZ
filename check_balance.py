#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.database.models import ClientBalance, BalanceTransaction, HostingServer

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=== HOSTING SERVERS ===")
servers = db.query(HostingServer).all()
for server in servers:
    print(f"ID: {server.id}, Name: {server.server_name}, client_id: {server.client_id}, "
          f"client_name: {server.client_name}, client_price: {server.client_price}₽/мес")

print("\n=== CLIENT BALANCES ===")
balances = db.query(ClientBalance).all()
for balance in balances:
    print(f"ID: {balance.id}, client_id: {balance.client_id}, client_name: {balance.client_name}")
    print(f"  Balance: {balance.balance}₽, Monthly Cost: {balance.total_monthly_cost}₽/мес")
    print(f"  Days Remaining: {balance.days_remaining}")

print("\n=== TRANSACTIONS ===")
transactions = db.query(BalanceTransaction).all()
for tx in transactions:
    print(f"ID: {tx.id}, Type: {tx.type}, Amount: {tx.amount}₽")
    print(f"  Before: {tx.balance_before}₽ → After: {tx.balance_after}₽")
    print(f"  Description: {tx.description}")

db.close()
