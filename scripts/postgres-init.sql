-- ============================================
-- POSTGRESQL INITIALIZATION SCRIPT
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For GIN indexes
CREATE EXTENSION IF NOT EXISTS "btree_gist"; -- For GIST indexes

-- Create schemas for modular organization (optional)
-- CREATE SCHEMA IF NOT EXISTS users;
-- CREATE SCHEMA IF NOT EXISTS vehicles;
-- CREATE SCHEMA IF NOT EXISTS drivers;
-- CREATE SCHEMA IF NOT EXISTS routes;
-- CREATE SCHEMA IF NOT EXISTS trips;
-- CREATE SCHEMA IF NOT EXISTS fuel;
-- CREATE SCHEMA IF NOT EXISTS analytics;

-- Set default search path
-- SET search_path TO public;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crm_user;

-- Set timezone
SET timezone = 'UTC';

-- Optimize PostgreSQL for performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- Log queries that take longer than 1 second
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Connection settings
ALTER SYSTEM SET max_connections = 200;

-- Memory settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET work_mem = '4MB';

-- Checkpoint settings
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Query planner settings
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Parallel query settings
ALTER SYSTEM SET max_worker_processes = 4;
ALTER SYSTEM SET max_parallel_workers_per_gather = 2;
ALTER SYSTEM SET max_parallel_workers = 4;
ALTER SYSTEM SET max_parallel_maintenance_workers = 2;

-- WAL settings
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = 'on';

-- Create initial admin user table if not exists (will be managed by Alembic)
-- This is just for reference, actual tables will be created by migrations

-- Example table structure (commented out - will be created by Alembic):
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     telegram_id BIGINT UNIQUE NOT NULL,
--     username VARCHAR(255),
--     first_name VARCHAR(255),
--     last_name VARCHAR(255),
--     role VARCHAR(50) DEFAULT 'VIEWER',
--     is_active BOOLEAN DEFAULT TRUE,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- Create indexes for common queries
-- CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
-- CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
-- CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Create audit log table (example)
-- CREATE TABLE IF NOT EXISTS audit_log (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER REFERENCES users(id),
--     action VARCHAR(100) NOT NULL,
--     entity_type VARCHAR(100),
--     entity_id INTEGER,
--     changes JSONB,
--     ip_address INET,
--     user_agent TEXT,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
-- CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
-- CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
-- CREATE INDEX IF NOT EXISTS idx_audit_log_changes ON audit_log USING GIN(changes);

COMMENT ON DATABASE crm_db IS 'Enterprise CRM System Database';
