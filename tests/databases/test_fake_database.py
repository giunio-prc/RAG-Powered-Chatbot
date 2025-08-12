def test_fake_database__returns_zero_length_of_longest_vector_when_empty(fake_database): # bugfix

    assert fake_database.get_length_of_longest_vector() == 0
