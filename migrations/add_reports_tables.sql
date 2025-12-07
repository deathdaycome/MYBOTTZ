-- ============================================================================
-- Migration: Add Reports Tables
-- Created: 2025-11-12
-- Description: Creates tables for Reports module (Phase 12)
-- ============================================================================

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    requested_by INTEGER NOT NULL,
    parameters JSONB,
    file_path VARCHAR(500),
    file_size INTEGER,
    error_message TEXT,
    generation_time_seconds FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Create indexes for reports table
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_user ON reports(requested_by);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_expires ON reports(expires_at);

-- Create scheduled_reports table
CREATE TABLE IF NOT EXISTS scheduled_reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    parameters JSONB,
    cron_expression VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    email_recipients JSONB,
    user_recipients JSONB,
    created_by INTEGER NOT NULL,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for scheduled_reports table
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_active ON scheduled_reports(is_active);
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_next_run ON scheduled_reports(next_run_at);

-- Create updated_at trigger for scheduled_reports
CREATE OR REPLACE FUNCTION update_scheduled_reports_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_scheduled_reports_updated_at ON scheduled_reports;
CREATE TRIGGER trigger_scheduled_reports_updated_at
    BEFORE UPDATE ON scheduled_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_scheduled_reports_updated_at();

-- Add comments for documentation
COMMENT ON TABLE reports IS 'Tracks report generation tasks and their results';
COMMENT ON TABLE scheduled_reports IS 'Stores scheduled periodic reports configuration';

COMMENT ON COLUMN reports.status IS 'Status: pending, processing, completed, failed';
COMMENT ON COLUMN reports.report_type IS 'Type: projects_summary, tasks_summary, users_activity, deliveries_report, vehicles_utilization, financial_summary, wb_products, wb_orders, custom';
COMMENT ON COLUMN reports.format IS 'Format: pdf, excel, csv, json';
COMMENT ON COLUMN reports.parameters IS 'JSON parameters for report generation (date ranges, filters, etc)';
COMMENT ON COLUMN reports.expires_at IS 'Report files are automatically cleaned after this date';

COMMENT ON COLUMN scheduled_reports.cron_expression IS 'Cron expression for scheduling (e.g., "0 9 * * MON" for weekly Monday 9am)';
COMMENT ON COLUMN scheduled_reports.email_recipients IS 'JSON array of email addresses to send report to';
COMMENT ON COLUMN scheduled_reports.user_recipients IS 'JSON array of user IDs to notify';

-- ============================================================================
-- Verification queries
-- ============================================================================

-- Check if tables were created
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_name IN ('reports', 'scheduled_reports')
ORDER BY table_name;

-- Check indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('reports', 'scheduled_reports')
ORDER BY tablename, indexname;

-- ============================================================================
-- Sample data (optional - uncomment to insert test data)
-- ============================================================================

/*
-- Insert sample report
INSERT INTO reports (
    title,
    report_type,
    format,
    status,
    requested_by,
    parameters,
    expires_at
) VALUES (
    'Monthly Projects Report',
    'projects_summary',
    'pdf',
    'pending',
    1,
    '{"start_date": "2025-01-01", "end_date": "2025-01-31"}'::jsonb,
    CURRENT_TIMESTAMP + INTERVAL '7 days'
);

-- Insert sample scheduled report
INSERT INTO scheduled_reports (
    title,
    report_type,
    format,
    parameters,
    cron_expression,
    is_active,
    created_by,
    next_run_at
) VALUES (
    'Weekly Tasks Summary',
    'tasks_summary',
    'excel',
    '{"status": "all", "priority": "all"}'::jsonb,
    '0 9 * * MON',
    true,
    1,
    CURRENT_TIMESTAMP + INTERVAL '1 week'
);
*/

-- ============================================================================
-- Migration complete!
-- ============================================================================
