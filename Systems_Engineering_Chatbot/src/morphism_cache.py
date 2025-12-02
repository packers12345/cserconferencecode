import json
import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List, Any


class MorphismCache:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'morphism_cache.db')
        
        self.db_path = db_path
        self.db = None
        self._init_db()

    def _init_db(self):
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_schema()

    def _create_schema(self):
        cursor = self.db.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_specs (
                system_name TEXT PRIMARY KEY,
                specification JSON,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS morphism_pairs (
                system1_name TEXT,
                system2_name TEXT,
                morphisms JSON,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (system1_name, system2_name)
            )
        """)
        
        self.db.commit()

    def get_cached_system(self, system_name: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT specification FROM system_specs WHERE system_name = ?",
            (system_name,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

    def cache_system(self, system_name: str, spec: Dict[str, Any]) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            """REPLACE INTO system_specs (system_name, specification, timestamp) 
               VALUES (?, ?, ?)""",
            (system_name, json.dumps(spec), datetime.now().isoformat())
        )
        self.db.commit()

    def get_cached_morphisms(self, system1: str, system2: str) -> Optional[List[Dict[str, Any]]]:
        cursor = self.db.cursor()
        cursor.execute(
            """SELECT morphisms FROM morphism_pairs 
               WHERE (system1_name = ? AND system2_name = ?)
               OR (system1_name = ? AND system2_name = ?)""",
            (system1, system2, system2, system1)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

    def cache_morphisms(self, system1: str, system2: str, morphisms: List[Dict[str, Any]]) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            """REPLACE INTO morphism_pairs (system1_name, system2_name, morphisms, timestamp)
               VALUES (?, ?, ?, ?)""",
            (system1, system2, json.dumps(morphisms), datetime.now().isoformat())
        )
        self.db.commit()

    def clear_all(self) -> None:
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM system_specs")
        cursor.execute("DELETE FROM morphism_pairs")
        self.db.commit()

    def close(self) -> None:
        if self.db:
            self.db.close()

    def __del__(self):
        self.close()
