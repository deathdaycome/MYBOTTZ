"""
Database Optimization Utilities
Provides tools for query optimization, indexing, and performance analysis
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool, QueuePool, StaticPool
import time
from contextlib import asynccontextmanager

from app.core.logging import logger
from app.core.metrics import db_query_duration_seconds, db_queries_total


# ============================================
# QUERY OPTIMIZATION
# ============================================

class QueryOptimizer:
    """Helper class for query optimization"""

    @staticmethod
    async def analyze_query(db: AsyncSession, query: str) -> Dict[str, Any]:
        """
        Analyze a query using EXPLAIN ANALYZE
        Returns query execution plan and statistics
        """
        try:
            # Use EXPLAIN ANALYZE to get query plan and actual execution stats
            result = await db.execute(text(f"EXPLAIN ANALYZE {query}"))
            plan = result.fetchall()

            return {
                "query": query,
                "plan": [str(row[0]) for row in plan],
                "analyzed": True,
            }
        except Exception as e:
            logger.error("query_analyze_failed", error=str(e), query=query)
            return {
                "query": query,
                "error": str(e),
                "analyzed": False,
            }

    @staticmethod
    async def get_slow_queries(
        db: AsyncSession, min_duration_ms: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get list of slow queries from pg_stat_statements
        Requires pg_stat_statements extension to be enabled
        """
        query = text("""
            SELECT
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                max_exec_time,
                stddev_exec_time,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time > :min_duration
            ORDER BY mean_exec_time DESC
            LIMIT 50
        """)

        try:
            result = await db.execute(query, {"min_duration": min_duration_ms})
            rows = result.fetchall()

            return [
                {
                    "query": row[0],
                    "calls": row[1],
                    "total_time_ms": row[2],
                    "mean_time_ms": row[3],
                    "max_time_ms": row[4],
                    "stddev_time_ms": row[5],
                    "rows": row[6],
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning("slow_queries_fetch_failed", error=str(e))
            return []

    @staticmethod
    async def get_missing_indexes(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Identify potentially missing indexes based on sequential scans
        """
        query = text("""
            SELECT
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                seq_tup_read / seq_scan as avg_seq_tup_read
            FROM pg_stat_user_tables
            WHERE seq_scan > 0
            ORDER BY seq_tup_read DESC
            LIMIT 25
        """)

        try:
            result = await db.execute(query)
            rows = result.fetchall()

            return [
                {
                    "schema": row[0],
                    "table": row[1],
                    "seq_scans": row[2],
                    "seq_tuples_read": row[3],
                    "index_scans": row[4] or 0,
                    "avg_tuples_per_scan": float(row[5]) if row[5] else 0,
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning("missing_indexes_check_failed", error=str(e))
            return []


# ============================================
# INDEX MANAGEMENT
# ============================================

class IndexManager:
    """Helper class for index management"""

    @staticmethod
    async def get_index_usage(db: AsyncSession) -> List[Dict[str, Any]]:
        """Get index usage statistics"""
        query = text("""
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan ASC
        """)

        try:
            result = await db.execute(query)
            rows = result.fetchall()

            return [
                {
                    "schema": row[0],
                    "table": row[1],
                    "index": row[2],
                    "scans": row[3],
                    "tuples_read": row[4],
                    "tuples_fetched": row[5],
                    "size": row[6],
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning("index_usage_fetch_failed", error=str(e))
            return []

    @staticmethod
    async def get_duplicate_indexes(db: AsyncSession) -> List[Dict[str, Any]]:
        """Identify duplicate or redundant indexes"""
        query = text("""
            SELECT
                pg_size_pretty(sum(pg_relation_size(idx))::bigint) as size,
                (array_agg(idx))[1] as idx1,
                (array_agg(idx))[2] as idx2,
                (array_agg(idx))[3] as idx3,
                (array_agg(idx))[4] as idx4
            FROM (
                SELECT
                    indexrelid::regclass as idx,
                    (indrelid::text || E'\\n' || indclass::text || E'\\n' ||
                     indkey::text || E'\\n' || coalesce(indexprs::text, '') ||
                     E'\\n' || coalesce(indpred::text, '')) as key
                FROM pg_index
            ) sub
            GROUP BY key
            HAVING count(*) > 1
            ORDER BY sum(pg_relation_size(idx)) DESC
        """)

        try:
            result = await db.execute(query)
            rows = result.fetchall()

            return [
                {
                    "total_size": row[0],
                    "indexes": [idx for idx in row[1:] if idx is not None],
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning("duplicate_indexes_check_failed", error=str(e))
            return []


# ============================================
# PERFORMANCE MONITORING
# ============================================

@asynccontextmanager
async def track_query_performance(
    operation: str, table: str = "unknown", threshold_ms: float = 100.0
):
    """
    Context manager to track query performance

    Usage:
        async with track_query_performance("select", "users"):
            result = await db.execute(query)
    """
    start_time = time.time()
    error = None

    try:
        yield
    except Exception as e:
        error = e
        raise
    finally:
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Track metrics
        db_queries_total.labels(operation=operation).inc()
        db_query_duration_seconds.labels(operation=operation, table=table).observe(
            duration
        )

        # Log slow queries
        if duration_ms > threshold_ms:
            logger.warning(
                "slow_query_detected",
                operation=operation,
                table=table,
                duration_ms=duration_ms,
                error=str(error) if error else None,
            )


# ============================================
# DATABASE STATISTICS
# ============================================

class DatabaseStats:
    """Helper class for database statistics"""

    @staticmethod
    async def get_table_sizes(db: AsyncSession) -> List[Dict[str, Any]]:
        """Get table sizes"""
        query = text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                               pg_relation_size(schemaname||'.'||tablename)) as indexes_size
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)

        try:
            result = await db.execute(query)
            rows = result.fetchall()

            return [
                {
                    "schema": row[0],
                    "table": row[1],
                    "total_size": row[2],
                    "table_size": row[3],
                    "indexes_size": row[4],
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning("table_sizes_fetch_failed", error=str(e))
            return []

    @staticmethod
    async def get_cache_hit_ratio(db: AsyncSession) -> Dict[str, Any]:
        """Get cache hit ratio for the database"""
        query = text("""
            SELECT
                sum(heap_blks_read) as heap_read,
                sum(heap_blks_hit) as heap_hit,
                sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
            FROM pg_statio_user_tables
        """)

        try:
            result = await db.execute(query)
            row = result.fetchone()

            if row and row[2]:
                return {
                    "heap_blocks_read": row[0],
                    "heap_blocks_hit": row[1],
                    "cache_hit_ratio": float(row[2]),
                }
            else:
                return {
                    "heap_blocks_read": 0,
                    "heap_blocks_hit": 0,
                    "cache_hit_ratio": 0.0,
                }
        except Exception as e:
            logger.warning("cache_hit_ratio_fetch_failed", error=str(e))
            return {"error": str(e)}


# ============================================
# RECOMMENDED INDEXES
# ============================================

RECOMMENDED_INDEXES = {
    "users": [
        {"columns": ["email"], "unique": True},
        {"columns": ["username"], "unique": True},
        {"columns": ["is_active", "created_at"]},
        {"columns": ["role"]},
    ],
    "projects": [
        {"columns": ["status", "created_at"]},
        {"columns": ["client_id"]},
        {"columns": ["created_at"]},
    ],
    "tasks": [
        {"columns": ["project_id", "status"]},
        {"columns": ["assigned_to", "status"]},
        {"columns": ["deadline"]},
        {"columns": ["status", "priority"]},
        {"columns": ["created_at"]},
    ],
    "wb_products": [
        {"columns": ["wb_article"], "unique": True},
        {"columns": ["last_sync"]},
    ],
    "wb_orders": [
        {"columns": ["wb_order_id"], "unique": True},
        {"columns": ["status"]},
        {"columns": ["order_date"]},
    ],
    "wb_webhook_logs": [
        {"columns": ["event_type", "created_at"]},
        {"columns": ["processed"]},
    ],
}


async def create_recommended_indexes(db: AsyncSession) -> Dict[str, Any]:
    """
    Create recommended indexes for all tables
    This is a helper function - actual indexes should be created via migrations
    """
    results = {
        "created": [],
        "already_exists": [],
        "errors": [],
    }

    for table_name, indexes in RECOMMENDED_INDEXES.items():
        for index_config in indexes:
            columns = index_config["columns"]
            unique = index_config.get("unique", False)
            index_name = f"idx_{table_name}_{'_'.join(columns)}"

            try:
                # Check if index exists
                check_query = text("""
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = :table_name AND indexname = :index_name
                """)
                result = await db.execute(
                    check_query, {"table_name": table_name, "index_name": index_name}
                )

                if result.fetchone():
                    results["already_exists"].append(index_name)
                    continue

                # Create index
                unique_str = "UNIQUE" if unique else ""
                columns_str = ", ".join(columns)
                create_query = text(
                    f"CREATE {unique_str} INDEX CONCURRENTLY {index_name} "
                    f"ON {table_name} ({columns_str})"
                )

                await db.execute(create_query)
                await db.commit()
                results["created"].append(index_name)

                logger.info("index_created", index_name=index_name, table=table_name)

            except Exception as e:
                results["errors"].append(
                    {"index": index_name, "table": table_name, "error": str(e)}
                )
                logger.error(
                    "index_creation_failed",
                    index_name=index_name,
                    table=table_name,
                    error=str(e),
                )

    return results


# ============================================
# EXPORT
# ============================================

__all__ = [
    "QueryOptimizer",
    "IndexManager",
    "DatabaseStats",
    "track_query_performance",
    "create_recommended_indexes",
    "RECOMMENDED_INDEXES",
]
