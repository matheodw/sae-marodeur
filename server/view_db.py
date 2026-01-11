import sys
import os

# Path configuration for imports
# Ensures that the 'database' module can be found regardless of execution context.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

def run_visualization(db_name="marodeur.db"):
    """
    Connects to the database and prints all tables, columns, and rows.

    :param db_name: Name of the database file to visualize.
    :type db_name: str
    """
    db = Database(db_name)

    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        for table_row in tables:
            table_name = table_row[0]
            print(f"\n Table: {table_name}")
            print("-" * 50)
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if rows:
                print(" | ".join(columns))
                print("-" * 50)
                
                for row in rows:
                    print(" | ".join(str(val) if val is not None else "NULL" for val in list(row)))
            else:
                print("(empty)")
            
            print()

    finally:
        cursor.close()
        conn.close()
        print("Visualization complete, database disconnected.")

if __name__ == "__main__":
    run_visualization()
