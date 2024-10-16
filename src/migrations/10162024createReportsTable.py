import sqlite3
import sys
from migration_utils import run_migration

def up():
    conn: sqlite3.Connection = sqlite3.connect("database/reports.db")
    """Create the Report table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Report (
        UserID TEXT NOT NULL,  -- Store UUID as text
        Severity INTEGER NOT NULL,
        Status TEXT CHECK(Status IN ('Pending', 'In Progress', 'Resolved')),  -- Assuming status values are predefined
        ReportID TEXT PRIMARY KEY,  -- Store UUID as text
        Description TEXT,
        imagePath TEXT,
        assignedAuthorityUEN TEXT,
        title TEXT,
        UEN TEXT,
        FOREIGN KEY (assignedAuthorityUEN) REFERENCES Authority(UEN)  -- Assuming Authority table exists with UEN as the key
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        print("Report table created successfully.")
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()

def down():
    conn: sqlite3.Connection = sqlite3.connect("database/reports.db")

    """Delete the Report table if it exists."""
    drop_table_query = "DROP TABLE IF EXISTS Report;"
    try:
        cursor = conn.cursor()
        cursor.execute(drop_table_query)
        conn.commit()
        print("Report table deleted successfully.")
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration(up, down)
