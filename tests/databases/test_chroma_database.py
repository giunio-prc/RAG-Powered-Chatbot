def test_chroma_db__returns_zero_length_of_longest_vector_when_empty(vector_database): # bugfix

    assert vector_database.get_length_of_longest_vector() == 0
