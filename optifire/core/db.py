"""
Database management with SQLite (WAL mode).
"""
import sqlite3
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
import aiosqlite

from .logger import logger
from .errors import DataError


class Database:
    """
    SQLite database manager with WAL mode for concurrency.
    Async-first design with connection pooling.
    """

    def __init__(self, db_path: Path):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize database with schema."""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            # Enable WAL mode
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA synchronous=NORMAL")
            await db.execute("PRAGMA cache_size=10000")
            await db.execute("PRAGMA temp_store=MEMORY")

            # Create tables
            await self._create_schema(db)
            await db.commit()

        self._initialized = True
        logger.info(f"Initialized database at {self.db_path} (WAL mode)")

    async def _create_schema(self, db: aiosqlite.Connection) -> None:
        """Create database schema."""

        # Positions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                qty REAL NOT NULL,
                avg_entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL,
                realized_pnl REAL DEFAULT 0,
                market_value REAL,
                cost_basis REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Orders table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                order_type TEXT NOT NULL,
                limit_price REAL,
                stop_price REAL,
                status TEXT NOT NULL,
                filled_qty REAL DEFAULT 0,
                filled_avg_price REAL,
                submitted_at TIMESTAMP,
                filled_at TIMESTAMP,
                canceled_at TIMESTAMP,
                metadata TEXT
            )
        """)

        # Trades table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL NOT NULL,
                commission REAL DEFAULT 0,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pnl REAL,
                metadata TEXT
            )
        """)

        # Signals table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                value REAL NOT NULL,
                confidence REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)

        # Features table (for ML)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS features (
                feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                feature_name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, feature_name, timestamp)
            )
        """)

        # Performance metrics
        await db.execute("""
            CREATE TABLE IF NOT EXISTS performance (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Risk metrics
        await db.execute("""
            CREATE TABLE IF NOT EXISTS risk_metrics (
                risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                symbol TEXT,
                value REAL NOT NULL,
                threshold REAL,
                breached BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Plugin execution log
        await db.execute("""
            CREATE TABLE IF NOT EXISTS plugin_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plugin_id TEXT NOT NULL,
                status TEXT NOT NULL,
                cpu_ms INTEGER,
                mem_mb INTEGER,
                error_msg TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Create indices
        await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_features_symbol ON features(symbol)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance(timestamp)")

    @asynccontextmanager
    async def connection(self):
        """Get database connection as async context manager."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            yield db

    async def execute(
        self,
        query: str,
        params: Optional[Tuple] = None,
    ) -> aiosqlite.Cursor:
        """
        Execute a query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Cursor object
        """
        async with self.connection() as db:
            cursor = await db.execute(query, params or ())
            await db.commit()
            return cursor

    async def fetch_one(
        self,
        query: str,
        params: Optional[Tuple] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch single row.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Row as dictionary or None
        """
        async with self.connection() as db:
            cursor = await db.execute(query, params or ())
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetch_all(
        self,
        query: str,
        params: Optional[Tuple] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        async with self.connection() as db:
            cursor = await db.execute(query, params or ())
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def insert_position(self, symbol: str, qty: float, avg_entry_price: float) -> None:
        """Insert or update position."""
        await self.execute(
            """
            INSERT INTO positions (symbol, qty, avg_entry_price, cost_basis)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                qty = qty + excluded.qty,
                avg_entry_price = (
                    (avg_entry_price * qty + excluded.avg_entry_price * excluded.qty) /
                    (qty + excluded.qty)
                ),
                cost_basis = cost_basis + excluded.cost_basis,
                updated_at = CURRENT_TIMESTAMP
            """,
            (symbol, qty, avg_entry_price, qty * avg_entry_price),
        )

    async def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get position for symbol."""
        return await self.fetch_one(
            "SELECT * FROM positions WHERE symbol = ?",
            (symbol,),
        )

    async def get_all_positions(self) -> List[Dict[str, Any]]:
        """Get all positions."""
        return await self.fetch_all("SELECT * FROM positions WHERE qty != 0")

    async def insert_order(self, order_data: Dict[str, Any]) -> None:
        """Insert order."""
        await self.execute(
            """
            INSERT INTO orders (
                order_id, symbol, side, qty, order_type, limit_price,
                stop_price, status, submitted_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_data["order_id"],
                order_data["symbol"],
                order_data["side"],
                order_data["qty"],
                order_data.get("order_type", "market"),
                order_data.get("limit_price"),
                order_data.get("stop_price"),
                order_data.get("status", "pending"),
                order_data.get("submitted_at"),
                order_data.get("metadata"),
            ),
        )

    async def update_order(self, order_id: str, updates: Dict[str, Any]) -> None:
        """Update order status."""
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [order_id]
        await self.execute(
            f"UPDATE orders SET {set_clause} WHERE order_id = ?",
            tuple(values),
        )

    async def insert_signal(self, signal_data: Dict[str, Any]) -> None:
        """Insert signal."""
        await self.execute(
            """
            INSERT INTO signals (
                plugin_id, symbol, signal_type, value, confidence, metadata, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal_data["plugin_id"],
                signal_data["symbol"],
                signal_data["signal_type"],
                signal_data["value"],
                signal_data.get("confidence"),
                signal_data.get("metadata"),
                signal_data.get("expires_at"),
            ),
        )

    async def get_recent_signals(
        self,
        symbol: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get recent signals."""
        if symbol:
            query = """
                SELECT * FROM signals
                WHERE symbol = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY created_at DESC LIMIT ?
            """
            return await self.fetch_all(query, (symbol, limit))
        else:
            query = """
                SELECT * FROM signals
                WHERE expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP
                ORDER BY created_at DESC LIMIT ?
            """
            return await self.fetch_all(query, (limit,))

    async def log_plugin_execution(
        self,
        plugin_id: str,
        status: str,
        cpu_ms: Optional[int] = None,
        mem_mb: Optional[int] = None,
        error_msg: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ) -> None:
        """Log plugin execution."""
        await self.execute(
            """
            INSERT INTO plugin_log (
                plugin_id, status, cpu_ms, mem_mb, error_msg, started_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (plugin_id, status, cpu_ms, mem_mb, error_msg, started_at, completed_at),
        )
