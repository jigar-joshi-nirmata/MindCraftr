import sqlite3
import os

DATABASE_NAME = 'mindcraftr.db'

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Sets row_factory to sqlite3.Row to access columns by name.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn):
    """
    Creates all necessary tables for the MindCraftr application.
    """
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Test results table
    cursor.execute('''
        CREATE TABLE test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            test_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            duration_seconds INTEGER NOT NULL,
            questions_answered INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Recommended topics table
    cursor.execute('''
        CREATE TABLE recommended_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            key_concepts TEXT NOT NULL,
            common_pitfalls TEXT NOT NULL,
            example_title TEXT,
            example_code TEXT,
            example_explanation TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Flashcards table
    cursor.execute('''
        CREATE TABLE flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            front_content TEXT NOT NULL,
            back_content TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Topic mastery table
    cursor.execute('''
        CREATE TABLE topic_mastery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_name TEXT NOT NULL,
            mastery_score REAL NOT NULL,
            UNIQUE(user_id, topic_name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()

def seed_data(conn):
    """
    Populates the database with initial test data.
    """
    cursor = conn.cursor()
    
    # Insert user
    cursor.execute('''
        INSERT INTO users (id, name, email) 
        VALUES (1, 'Jane Doe', 'jane.doe@example.com')
    ''')
    
    # Insert test results
    cursor.execute('''
        INSERT INTO test_results (user_id, test_name, score, duration_seconds, questions_answered, total_questions) 
        VALUES
        (1, 'React Fundamentals', 85, 900, 17, 20),
        (1, 'Advanced Hooks Quiz', 95, 1200, 19, 20),
        (1, 'CSS Layouts Test', 72, 750, 14, 20)
    ''')
    
    # Insert recommended topics
    cursor.execute('''
        INSERT INTO recommended_topics (user_id, title, summary, key_concepts, common_pitfalls, example_title, example_code, example_explanation) 
        VALUES
        (1, 'React Hooks', 'useState, useEffect, useContext, etc.', '["useState: For adding local state to components.", "useEffect: For handling side effects."]', '["Forgetting the dependency array in useEffect."]', 'Example: Counter', 'const [count, setCount] = useState(0);', 'This uses useState to track count.'),
        (1, 'CSS Grid Layout', 'A two-dimensional layout system.', '["Grid Container", "fr unit"]', '["Applying grid properties to items instead of the container."]', 'Example: 3-Column Layout', '.grid-container { display: grid; }', 'This creates a three-column grid.')
    ''')
    
    # Insert flashcards
    cursor.execute('''
        INSERT INTO flashcards (user_id, front_content, back_content) 
        VALUES
        (1, 'What is `useState`?', 'A React Hook that lets you add state to function components.'),
        (1, 'What is `useEffect` used for?', 'It lets you perform side effects in function components.'),
        (1, 'FIB: I am too __ for the hackathon.', 'excited')
    ''')
    
    # Insert topic mastery
    cursor.execute('''
        INSERT INTO topic_mastery (user_id, topic_name, mastery_score) 
        VALUES
        (1, 'useState', 0.95), 
        (1, 'useEffect', 0.70), 
        (1, 'Props', 1.0),
        (1, 'Context API', 0.60), 
        (1, 'CSS Grid', 0.80), 
        (1, 'Flexbox', 0.90),
        (1, 'Recursion', 0.55)
    ''')
    
    conn.commit()

