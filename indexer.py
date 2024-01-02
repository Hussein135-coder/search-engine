import os
import sqlite3
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from docx import Document

nltk.download('punkt')
nltk.download('stopwords')


def create_table(connection):
    """
    Creates a table in the database if it doesn't exist.

    Args:
    - connection: SQLite connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indexed_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                indexed_content TEXT,
                language TEXT,
                tokenization_algorithm TEXT
            )
        ''')
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")


def connect_to_database():
    """
    Connects to the SQLite database.

    Returns:
    - SQLite connection object
    """
    return sqlite3.connect('database.db')


def insert_indexed_data(connection, file_path, indexed_content, language, tokenization_algorithm):
    """
    Inserts indexed data into the database.

    Args:
    - connection: SQLite connection object
    - file_path: Path of the indexed file
    - indexed_content: Tokenized content of the file
    - language: Language used for tokenization
    - tokenization_algorithm: Algorithm used for tokenization
    """
    try:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO indexed_documents (file_path, indexed_content, language, tokenization_algorithm)
            VALUES (?, ?, ?, ?)
        ''', (file_path, ' '.join(indexed_content), language, tokenization_algorithm))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error inserting indexed data: {e}")


def search_in_database(connection, query):
    """
    Searches for a query in the indexed content stored in the database.

    Args:
    - connection: SQLite connection object
    - query: Search query

    Returns:
    - list: List of file paths containing the query
    """
    try:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT file_path FROM indexed_documents
            WHERE lower(indexed_content) LIKE ?
        ''', ('%' + query.lower() + '%',))
        results = cursor.fetchall()
        return [result[0] for result in results]
    except sqlite3.Error as e:
        print(f"Error searching in database: {e}")
        return []


def tokenize(content, language, tokenization_algorithm):
    """
    Tokenizes content based on language and tokenization algorithm.

    Args:
    - content: Text content to tokenize
    - language: Language used for tokenization
    - tokenization_algorithm: Algorithm used for tokenization

    Returns:
    - list: List of tokens
    """
    tokens = []
    if tokenization_algorithm == 'Whitespace':
        tokens = content.split()
    elif tokenization_algorithm == 'Word':
        tokens = word_tokenize(content)

    if language == 'english':
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token.lower() not in stop_words]
    elif language == 'arabic':
        tokenizer = RegexpTokenizer(r'\b\w+\b')
        tokens = tokenizer.tokenize(content)

    return tokens


def read_docx_content(file_path):
    try:
        doc = Document(file_path)
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return content
    except Exception as e:
        print(f"Error reading .docx file '{file_path}': {e}")
        return ""


def tokenize_and_index(file_paths, language, tokenization_algorithm):
    try:
        conn = connect_to_database()
        create_table(conn)
        for file_path in file_paths:
            content = read_docx_content(os.path.abspath(file_path))  # Ensure correct path formatting
            indexed_content = tokenize(content, language, tokenization_algorithm)
            insert_indexed_data(conn, file_path, indexed_content, language, tokenization_algorithm)
        conn.close()
    except Exception as e:
        print(f"Error tokenizing and indexing: {e}")
        # Handle error as needed
