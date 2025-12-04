# src/database_manager.py
import sqlite3
import os

PROFILES_DIR = os.path.join(os.path.dirname(__file__), '..', 'profiles')

def get_db_connection(profile_name="default"):
    os.makedirs(PROFILES_DIR, exist_ok=True)
    db_path = os.path.join(PROFILES_DIR, f"{profile_name}.db")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"DB Error ({profile_name}): {e}")
        return None

def create_tables(profile_name="default"):
    conn = get_db_connection(profile_name)
    if conn is None: return

    with conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS digimon_collection (id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE, hatch_status INTEGER DEFAULT 0, cloned_status INTEGER DEFAULT 0, fonte TEXT);")
        cursor.execute("CREATE TABLE IF NOT EXISTS seal_tracker (id INTEGER PRIMARY KEY, digimon_nome TEXT NOT NULL, stat_type TEXT NOT NULL, count INTEGER DEFAULT 0, UNIQUE(digimon_nome, stat_type));")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dungeons (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, difficulty TEXT NOT NULL, 
                base_points INTEGER DEFAULT 0, run_count INTEGER DEFAULT 0, UNIQUE(name, difficulty)
            );
        """)
        cursor.execute("CREATE TABLE IF NOT EXISTS run_history (id INTEGER PRIMARY KEY, description TEXT, points_change TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_wallet (
                id INTEGER PRIMARY KEY CHECK (id = 1), vip_level INTEGER DEFAULT 0,
                points_easy INTEGER DEFAULT 0, points_normal INTEGER DEFAULT 0, points_hard INTEGER DEFAULT 0
            );
        """)
        cursor.execute("INSERT OR IGNORE INTO player_wallet (id, vip_level) VALUES (1, 0)")
        cursor.execute("CREATE TABLE IF NOT EXISTS shop_items (id INTEGER PRIMARY KEY, npc_type TEXT NOT NULL, item_name TEXT NOT NULL, cost INTEGER NOT NULL, image_path TEXT);")
        # Daily Tasks Table (Prepared for future)
        cursor.execute("CREATE TABLE IF NOT EXISTS daily_tasks (id INTEGER PRIMARY KEY, name TEXT NOT NULL, reset_type TEXT NOT NULL, is_done INTEGER DEFAULT 0);")

    print(f"--- 💾 Profile '{profile_name}' Loaded/Created ---")
    conn.close()
    return True