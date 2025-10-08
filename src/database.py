
import sqlite3

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('src/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    """Creates the 'settings' table if it doesn't already exist."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id TEXT PRIMARY KEY,
            bg_image_url TEXT,
            frame_image_url TEXT,
            video_url TEXT,
            timezone TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_settings_by_id(display_id: str) -> dict:
    """Retrieves settings from the database by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings WHERE id = ?", (display_id,))
    settings = cursor.fetchone()
    conn.close()
    if settings:
        return dict(settings)
    return {}

def update_or_create_settings(display_id: str, settings: dict):
    """Updates existing settings or creates a new entry if the ID doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use INSERT OR REPLACE to simplify the logic
    columns = ['id'] + list(settings.keys())
    values = [display_id] + list(settings.values())
    placeholders = ', '.join(['?'] * len(columns))
    query = f"INSERT OR REPLACE INTO settings ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()

def insert_initial_data():
    """Inserts initial data into the settings table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    initial_data = [
        ('1', 'autumn-7531034_960_720.jpg', 'border-318820_1920.png', '217932.mp4', 'Europe/Kiev'),
        ('2', 'abstract-8147579_1920.jpg', 'border-318820_1920.png', '141309.mp4', 'Europe/London')
    ]
    cursor.executemany("INSERT OR IGNORE INTO settings VALUES (?, ?, ?, ?, ?)", initial_data)
    conn.commit()
    conn.close()

# Create the table and insert initial data when the module is first imported.
create_table()
insert_initial_data()
