from rag_powered_chatbot.main import hello_world


def test_hello_world():
    result = hello_world()
    assert result == "Hello world!"
