"""Database operations for WizardLightYearsCalculator."""

import sqlite3
from datetime import datetime
from typing import Optional, Dict
from config import DATABASE_PATH


class Database:
    """Handles all database operations."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize the database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS systems (
                system_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                added TIMESTAMP NOT NULL,
                last_update TIMESTAMP NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_system(self, system_id: int) -> Optional[Dict]:
        """
        Retrieve system information from database.
        
        Security: Uses parameterized queries to prevent SQL injection.
        
        Args:
            system_id: The EVE Online system ID
            
        Returns:
            Dictionary with system information or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Parameterized query prevents SQL injection
        cursor.execute("""
            SELECT system_id, name, x, y, z, added, last_update
            FROM systems
            WHERE system_id = ?
        """, (system_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "system_id": row["system_id"],
                "name": row["name"],
                "x": row["x"],
                "y": row["y"],
                "z": row["z"],
                "added": row["added"],
                "last_update": row["last_update"]
            }
        return None
    
    def insert_system(self, system_id: int, name: str, x: float, y: float, z: float):
        """
        Insert a new system into the database.
        
        Args:
            system_id: The EVE Online system ID
            name: System name
            x, y, z: Position coordinates
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO systems (system_id, name, x, y, z, added, last_update)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (system_id, name, x, y, z, now, now))
        
        conn.commit()
        conn.close()
    
    def update_system_timestamp(self, system_id: int):
        """
        Update the last_update timestamp for a system.
        
        Args:
            system_id: The EVE Online system ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            UPDATE systems
            SET last_update = ?
            WHERE system_id = ?
        """, (now, system_id))
        
        conn.commit()
        conn.close()
