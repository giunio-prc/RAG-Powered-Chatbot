from app.databases.chroma_database import ChromaDatabase


def test_chroma_db__returns_zero_length_of_longest_vector_when_empty(): # bugfix
    chroma_db = ChromaDatabase()

    assert chroma_db.get_length_of_longest_vector() == 0
