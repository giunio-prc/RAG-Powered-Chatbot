import io

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.databases import FakeDatabase


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
        assert "cannot be uploaded" in response.json()["detail"]

    def test_add_document_stores_content_in_database(
        self, client: TestClient, fake_database: FakeDatabase
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

        assert fake_database.get_number_of_vectors("test-session") > 0


class TestGetVectorsDataEndpoint:
    def test_get_vectors_data_returns_empty_database_stats(self, client: TestClient):
        response = client.get("/get-vectors-data")

        assert response.status_code == 200
        data = response.json()
        assert data["number_of_vectors"] == 0
        assert data["longest_vector"] == 0

    def test_get_vectors_data_returns_correct_stats_after_adding_content(
        self, client: TestClient, fake_database: FakeDatabase
    ):
        # Add some content to the database
        fake_database.db["test-session"] = ["short", "a longer text chunk here"]

        response = client.get("/get-vectors-data")

        assert response.status_code == 200
        data = response.json()
        assert data["number_of_vectors"] == 2
        assert data["longest_vector"] == len("a longer text chunk here")

    def test_get_vectors_data_isolates_sessions(
        self, client: TestClient, fake_database: FakeDatabase
    ):
        # Add content to a different session
        fake_database.db["other-session"] = ["content from other session"]

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
        self, client: TestClient, fake_database: FakeDatabase
    ):
        # Add content first
        fake_database.db["test-session"] = ["chunk1", "chunk2", "chunk3"]
        assert fake_database.get_number_of_vectors("test-session") == 3

        response = client.delete("/empty-database")

        assert response.status_code == 200
        assert fake_database.get_number_of_vectors("test-session") == 0

    def test_empty_database_does_not_affect_other_sessions(
        self, client: TestClient, fake_database: FakeDatabase
    ):
        # Add content to both sessions
        fake_database.db["test-session"] = ["test session content"]
        fake_database.db["other-session"] = ["other session content"]

        client.delete("/empty-database")

        assert fake_database.get_number_of_vectors("test-session") == 0
        assert fake_database.get_number_of_vectors("other-session") == 1


class TestSessionCookieHandling:
    def test_endpoints_use_default_session_without_cookie(
        self, app_with_mocks: FastAPI, fake_database: FakeDatabase
    ):
        # Client without SESSION cookie
        client = TestClient(app_with_mocks)
        fake_database.db["default"] = ["default session content"]

        response = client.get("/get-vectors-data")

        assert response.status_code == 200
        data = response.json()
        assert data["number_of_vectors"] == 1

    def test_endpoints_use_custom_session_with_cookie(
        self, app_with_mocks: FastAPI, fake_database: FakeDatabase
    ):
        client = TestClient(app_with_mocks, cookies={"SESSION": "custom-session"})
        fake_database.db["custom-session"] = ["custom content", "more content"]

        response = client.get("/get-vectors-data")

        assert response.status_code == 200
        data = response.json()
        assert data["number_of_vectors"] == 2
