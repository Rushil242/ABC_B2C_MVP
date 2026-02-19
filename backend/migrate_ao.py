
from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN ao_details TEXT"))
            print("Successfully added ao_details column.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column ao_details already exists.")
            else:
                print(f"Error adding column: {e}")

if __name__ == "__main__":
    migrate()
