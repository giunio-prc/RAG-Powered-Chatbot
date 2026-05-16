import io

from fastapi.testclient import TestClient

from app.databases import FakeDatabaseManager


class TestAddDocumentEndpoint:
    def test_add_document_returns_streaming_response(self, client: TestClient):
        file_content = b"This is a test document with some content."
        file = io.BytesIO(file_content)

        response = client.post(
            "/add-document",
            files={"file": ("test.txt", file, "text/plain")},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_add_document_returns_progress_events(self, client: TestClient):
        file_content = b"This is a test document with some content."
        file = io.BytesIO(file_content)

        response = client.post(
            "/add-document",
            files={"file": ("test.txt", file, "text/plain")},
        )

        content = response.text
        # Controller yields progress percentage values
        assert "100.0" in content

    def test_add_document_rejects_non_text_files(self, client: TestClient):
        file_content = b"fake pdf content"
        file = io.BytesIO(file_content)

        response = client.post(
            "/add-document",
            files={"file": ("test.pdf", file, "application/pdf")},
        )

        assert response.status_code == 415
        assert "Invalid file" in response.json()["detail"]

    def test_add_document_rejects_image_files(self, client: TestClient):
        file_content = b"\x89PNG\r\n\x1a\n"
        file = io.BytesIO(file_content)

        response = client.post(
            "/add-document",
            files={"file": ("image.png", file, "image/png")},
        )

        assert response.status_code == 415

    def test_add_document_handles_unicode_decode_error(self, client: TestClient):
        # Invalid UTF-8 sequence
        file_content = b"\x80\x81\x82\x83"
        file = io.BytesIO(file_content)

        response = client.post(
            "/add-document",
            files={"file": ("test.txt", file, "text/plain")},
        )

        assert response.status_code == 406
        detail = response.json()["detail"]
        assert "cannot be uploaded" in detail
        assert "position 0: invalid start byte" in detail

    def test_add_document_rejects_file_exceeding_size_limit(self, client: TestClient):
        file_content = b"x" * (1024 * 1024 + 1)  # 1 MB + 1 byte
        file = io.BytesIO(file_content)

        response = client.post(
            "/add-document",
            files={"file": ("large.txt", file, "text/plain")},
        )

        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]

    def test_add_document_stores_content_in_database(
        self, client: TestClient, fake_database_manager: FakeDatabaseManager
    ):
        file_content = b"Test content for database storage."
        file = io.BytesIO(file_content)

        # Consume the streaming response to trigger the generator
        response = client.post(
            "/add-document",
            files={"file": ("test.txt", file, "text/plain")},
        )
        # Read content to ensure streaming completes
        _ = response.text
        vectors = fake_database_manager.db.popitem()
        assert vectors[1] == ["Test content for database storage."]


class TestGetVectorsDataEndpoint:
    def test_get_vectors_data_returns_empty_database_stats(self, client: TestClient):
        response = client.get("/get-vectors-data")

        assert response.status_code == 200
        data = response.json()
        assert data["number_of_vectors"] == 0
        assert data["longest_vector"] == 0

    def test_get_vectors_data_returns_correct_stats(self, client: TestClient):
        # Add content via the API
        file_content = b"short\n\na much longer text chunk here for testing"
        file = io.BytesIO(file_content)

        response = client.post(
            "/add-document",
            files={"file": ("test.txt", file, "text/plain")},
        )
        _ = response.text

        response = client.get("/get-vectors-data")

        assert response.status_code == 200
        data = response.json()
        assert data["number_of_vectors"] == 1
        assert data["longest_vector"] == 47

    def test_get_vectors_data_isolates_sessions(
        self, client: TestClient, fake_database_manager: FakeDatabaseManager
    ):
        # Add content to a different session
        fake_database_manager.db["other-session"] = ["content from other session"]

        response = client.get("/get-vectors-data")

        assert response.status_code == 200
        data = response.json()
        assert data["number_of_vectors"] == 0


class TestEmptyDatabaseEndpoint:
    def test_empty_database_returns_success_message(self, client: TestClient):
        response = client.delete("/empty-database")

        assert response.status_code == 200
        assert response.json()["message"] == "Database emptied successfully"

    def test_empty_database_clears_content(
        self, client: TestClient, fake_database_manager: FakeDatabaseManager
    ):
        # Add content first
        file_content = "chunk1" * 40 + "\n" + "chunk2" * 40 + "\n" + "chunk3"
        file = io.BytesIO(file_content.encode())

        _response = client.post(
            "/add-document",
            files={"file": ("test.txt", file, "text/plain")},
        )
        # Read content to ensure streaming completes
        _ = _response.text

        cookie, chunks = fake_database_manager.db.popitem()

        assert len(chunks) == 3

        response = client.delete("/empty-database")

        assert response.status_code == 200
        assert fake_database_manager.get_number_of_vectors(cookie) == 0

    def test_empty_database_does_not_affect_other_sessions(
        self, client: TestClient, fake_database_manager: FakeDatabaseManager
    ):
        # Add content to both sessions
        cookie_session = client.get("/cookie").text
        fake_database_manager.db[cookie_session] = ["test session content"]
        fake_database_manager.db["other-session"] = ["other session content"]

        client.delete("/empty-database")

        assert fake_database_manager.get_number_of_vectors("test-session") == 0
        assert fake_database_manager.get_number_of_vectors("other-session") == 1


class TestGetAgentInfoEndpoint:
    def test_get_agent_info_returns_fake_agent_info(self, client: TestClient):
        """Test that /agent-info returns correct info for FakeAgent."""
        response = client.get("/agent-info")

        assert response.status_code == 200
        data = response.json()
        assert data["is_fake"] is True
        assert data["icon"] == "pets"
        assert data["label"] == "RAG Parrot"
        assert data["embedding_model"] == "No Embedding Model"
