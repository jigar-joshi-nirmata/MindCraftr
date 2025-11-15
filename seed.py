import sqlite3
from database import DATABASE_NAME, create_tables, seed_data

def initialize_database():
    """
    Initializes the database by dropping existing tables, creating new ones,
    and seeding with initial data. This script is re-runnable.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Drop all tables if they exist to ensure script is re-runnable
    print("Dropping existing tables...")
    cursor.execute('DROP TABLE IF EXISTS generated_tests')
    cursor.execute('DROP TABLE IF EXISTS topic_mastery')
    cursor.execute('DROP TABLE IF EXISTS flashcards')
    cursor.execute('DROP TABLE IF EXISTS recommended_topics')
    cursor.execute('DROP TABLE IF EXISTS test_results')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    conn.commit()
    
    # Create tables
    print("Creating tables...")
    create_tables(conn)
    
    # Seed data
    print("Seeding data...")
    seed_data(conn)
    
    # Close connection
    conn.close()
    
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    initialize_database()

