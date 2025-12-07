-- ============================================================================
-- Configure PostgreSQL Extensions
-- Created: 2025-11-12
-- Description: Enable required PostgreSQL extensions for monitoring
-- ============================================================================

-- Enable pg_stat_statements for query performance tracking
-- This is required for Phase 11 (Performance & Optimization)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify extension is enabled
SELECT
    extname as extension_name,
    extversion as version,
    extnamespace::regnamespace as schema
FROM pg_extension
WHERE extname = 'pg_stat_statements';

-- Show current pg_stat_statements settings
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name LIKE 'pg_stat_statements%'
ORDER BY name;

-- ============================================================================
-- IMPORTANT NOTES
-- ============================================================================
--
-- After enabling pg_stat_statements, you need to add it to postgresql.conf:
--
-- 1. Edit postgresql.conf (usually in /etc/postgresql/16/main/postgresql.conf)
-- 2. Add or update:
--    shared_preload_libraries = 'pg_stat_statements'
--    pg_stat_statements.max = 10000
--    pg_stat_statements.track = all
--
-- 3. Restart PostgreSQL:
--    sudo systemctl restart postgresql
--
-- Or for Docker:
--    docker-compose restart postgres
--
-- ============================================================================

-- Test query (optional - uncomment to test)
/*
-- This should show tracked queries after some activity
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
*/
