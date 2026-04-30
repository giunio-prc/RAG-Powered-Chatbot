from fastapi.testclient import TestClient


def test_query_stream_endpoint_returns_sse_response(client: TestClient):
    response = client.post(
        "/query-stream",
        content='"What is the return policy?"',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    content = response.text
    assert "data:" in content

    # Verify SSE data contains expected words
    assert 'data: "You "' in content
    assert 'data: "asked "' in content
    assert 'data: "following "' in content
    assert 'data: "question:\\n "' in content
    assert 'data: "context\\nUnfortunately "' in content
    assert 'data: "fake "' in content
    assert 'data: "agent "' in content
