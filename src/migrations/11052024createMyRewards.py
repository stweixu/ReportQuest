import sqlite3
import sys
from migration_utils import run_migration


def up():
    conn: sqlite3.Connection = sqlite3.connect("database/myRewards.db")
    """Create the Report and MyRewards tables if they don't exist."""
    
    # Create Report table
    create_report_table_query = """
    CREATE TABLE IF NOT EXISTS Report (
        UserID TEXT NOT NULL,  -- Store UUID as text
        Severity INTEGER NOT NULL,
        Status TEXT CHECK(Status IN ('Pending', 'In Progress', 'Resolved')),  -- Assuming status values are predefined
        ReportID TEXT PRIMARY KEY,  -- Store UUID as text
        Description TEXT,
        imagePath TEXT,
        title TEXT,
        Datetime INTEGER NOT NULL,  -- Unix timestamp
        Location TEXT NOT NULL  -- Store location as text
    );
    """

    # Create MyRewards table
    create_myrewards_table_query = """
    CREATE TABLE IF NOT EXISTS MyRewards (
        rewardId TEXT PRIMARY KEY,  -- Store UUID as text
        userId TEXT NOT NULL,  -- Store UUID as text
        expiry INTEGER NOT NULL,  -- Unix timestamp
        giftcode TEXT  -- Store gift code as text
    );
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(create_report_table_query)
        cursor.execute(create_myrewards_table_query)
        conn.commit()
        print("MyRewards tables created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
    finally:
        conn.close()


def down():
    conn: sqlite3.Connection = sqlite3.connect("database/myRewards.db")
    """Delete the Report and MyRewards tables if they exist."""
    
    drop_myrewards_table_query = "DROP TABLE IF EXISTS MyRewards;"
    
    try:
        cursor = conn.cursor()
        cursor.execute(drop_myrewards_table_query)
        conn.commit()
        print("MyRewards tables deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting tables: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration(up, down)
