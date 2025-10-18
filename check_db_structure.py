#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/app/data/bot.db')
cursor = conn.cursor()

print('=== Check Database Structure ===')
print()

# Check users table
print('Table: users')
users = cursor.execute('SELECT id, telegram_id, username, first_name FROM users LIMIT 3').fetchall()
for u in users:
    print(f'  ID: {u[0]}, TG_ID: {u[1]}, Username: {u[2]}, Name: {u[3]}')

print()
print('Table: clients')
info = cursor.execute('PRAGMA table_info(clients)').fetchall()
print(f'  Columns: {[col[1] for col in info]}')
clients = cursor.execute('SELECT id, name, email, user_id FROM clients LIMIT 3').fetchall()
for c in clients:
    print(f'  ID: {c[0]}, Name: {c[1]}, Email: {c[2]}, User_ID: {c[3]}')

print()
print('Table: projects')
info = cursor.execute('PRAGMA table_info(projects)').fetchall()
print(f'  Columns: {[col[1] for col in info]}')
projects = cursor.execute('SELECT id, name, client_id, user_id FROM projects LIMIT 3').fetchall()
for p in projects:
    print(f'  ID: {p[0]}, Name: {p[1]}, Client_ID: {p[2]}, User_ID: {p[3]}')

print()
print('Table: documents')
info = cursor.execute('PRAGMA table_info(documents)').fetchall()
print(f'  Columns: {[col[1] for col in info]}')
docs_count = cursor.execute('SELECT COUNT(*) FROM documents').fetchone()
print(f'  Total documents: {docs_count[0]}')

print()
print('Table: deals')
info = cursor.execute('PRAGMA table_info(deals)').fetchall()
print(f'  Columns: {[col[1] for col in info]}')
deals_count = cursor.execute('SELECT COUNT(*) FROM deals').fetchone()
print(f'  Total deals: {deals_count[0]}')

print()
print('Table: transactions')
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%transact%'").fetchall()
print(f'  Transaction tables: {[t[0] for t in tables]}')

print()
print('All tables in database:')
all_tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
for t in all_tables:
    print(f'  - {t[0]}')

conn.close()
