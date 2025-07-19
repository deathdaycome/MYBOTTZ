"""
Миграция для обновления таблицы portfolio
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

def upgrade():
    """Обновление схемы базы данных"""
    
    # Проверяем существует ли таблица portfolio
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'portfolio' not in inspector.get_table_names():
        # Создаем таблицу portfolio полностью
        op.create_table(
            'portfolio',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('title', sa.String(300), nullable=False),
            sa.Column('subtitle', sa.String(500), nullable=True),
            sa.Column('description', sa.Text, nullable=False),
            sa.Column('category', sa.String(100), nullable=False),
            sa.Column('main_image', sa.String(500), nullable=True),
            sa.Column('image_paths', sa.JSON, nullable=True),
            sa.Column('technologies', sa.Text, nullable=True),
            sa.Column('complexity', sa.String(20), default='medium'),
            sa.Column('complexity_level', sa.Integer, default=5),
            sa.Column('development_time', sa.Integer, nullable=True),
            sa.Column('cost', sa.Float, nullable=True),
            sa.Column('cost_range', sa.String(100), nullable=True),
            sa.Column('show_cost', sa.Boolean, default=False),
            sa.Column('demo_link', sa.String(500), nullable=True),
            sa.Column('repository_link', sa.String(500), nullable=True),
            sa.Column('external_links', sa.JSON, nullable=True),
            sa.Column('is_featured', sa.Boolean, default=False),
            sa.Column('is_visible', sa.Boolean, default=True),
            sa.Column('sort_order', sa.Integer, default=0),
            sa.Column('views_count', sa.Integer, default=0),
            sa.Column('likes_count', sa.Integer, default=0),
            sa.Column('tags', sa.Text, nullable=True),
            sa.Column('client_name', sa.String(200), nullable=True),
            sa.Column('project_status', sa.String(50), default='completed'),
            sa.Column('completed_at', sa.DateTime, nullable=True),
            sa.Column('created_at', sa.DateTime, default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('created_by', sa.Integer, nullable=True),
        )
        print("✅ Таблица portfolio создана")
    else:
        print("✅ Таблица portfolio уже существует")
        
        # Получаем существующие колонки
        columns = [col['name'] for col in inspector.get_columns('portfolio')]
        
        # Добавляем недостающие колонки
        new_columns = [
            ('subtitle', sa.String(500)),
            ('complexity_level', sa.Integer),
            ('cost', sa.Float),
            ('cost_range', sa.String(100)),
            ('show_cost', sa.Boolean),
            ('external_links', sa.JSON),
            ('views_count', sa.Integer),
            ('likes_count', sa.Integer),
            ('tags', sa.Text),
            ('client_name', sa.String(200)),
            ('project_status', sa.String(50)),
            ('completed_at', sa.DateTime),
            ('created_by', sa.Integer),
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                try:
                    op.add_column('portfolio', sa.Column(col_name, col_type))
                    print(f"✅ Добавлена колонка: {col_name}")
                except Exception as e:
                    print(f"⚠️ Ошибка добавления колонки {col_name}: {e}")

def downgrade():
    """Откат изменений"""
    # В случае необходимости отката
    pass
