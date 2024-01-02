import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Connect to SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()


def search(query, search_algorithm):
    """
    Executes the search based on the chosen search algorithm.

    Args:
    - query: The search query
    - search_algorithm: The algorithm chosen for search

    Returns:
    - list: List of search results
    """
    try:
        if search_algorithm == 'boolean':
            results = boolean_search(query)
        elif search_algorithm == 'extended_boolean':
            results = extended_boolean_search(query)
        elif search_algorithm == 'vector':
            results = vector_search(query)
        else:
            raise ValueError("Invalid search algorithm")

        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []


def boolean_search(query):
    try:
        query = query.lower()  # Convert query to lowercase for case-insensitive search
        terms = query.split()

        results = None  # Initialize results as None

        for term in terms:
            cursor.execute('''
                SELECT file_path FROM indexed_documents
                WHERE lower(indexed_content) LIKE ?
            ''', ('%' + term + '%',))
            matching_documents = cursor.fetchall()
            matching_paths = {doc[0] for doc in matching_documents}

            if results is None:
                results = matching_paths
            else:
                results &= matching_paths

        return list(results) if results is not None else []
    except sqlite3.Error as e:
        print(f"Boolean search error: {e}")
        return []


def extended_boolean_search(query):
    try:
        query = query.lower()
        query_parts = query.split()

        results = None  # Initialize results as None
        operator = None

        for part in query_parts:
            if part in ('and', 'or', 'not'):
                operator = part
            else:
                cursor.execute('''
                    SELECT file_path FROM indexed_documents
                    WHERE lower(indexed_content) LIKE ?
                ''', ('%' + part + '%',))
                matching_documents = cursor.fetchall()
                matching_paths = {doc[0] for doc in matching_documents}

                if operator is None or operator == 'and':
                    if results is None:
                        results = matching_paths
                    else:
                        results &= matching_paths
                elif operator == 'or':
                    results |= matching_paths
                elif operator == 'not':
                    results -= matching_paths

        return list(results) if results is not None else []
    except sqlite3.Error as e:
        print(f"Extended Boolean search error: {e}")
        return []


def vector_search(query):
    SIMILARITY_THRESHOLD = 0.2  # Define your threshold here
    try:
        cursor.execute('SELECT file_path, indexed_content FROM indexed_documents')
        documents = cursor.fetchall()

        if not documents:
            print("No documents found in the database.")
            return []

        document_contents = [doc[1] for doc in documents]
        file_paths = [doc[0] for doc in documents]
        document_contents.append(query)

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(document_contents)

        query_vector = tfidf_matrix[-1]
        tfidf_matrix_for_query = tfidf_matrix[:-1]

        similarities = cosine_similarity(query_vector, tfidf_matrix_for_query)

        results = []
        for index, similarity_score in enumerate(similarities[0]):
            if similarity_score > SIMILARITY_THRESHOLD:
                results.append(file_paths[index])

        return results
    except Exception as e:
        print(f"Vector search error: {e}")
        return []