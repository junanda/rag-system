import uuid

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_create_and_get_conversation(client):
    # Create
    r = client.post("/api/chat/conversations", json={"fund_id": 1})
    assert r.status_code == 200
    body = r.json()
    assert "conversation_id" in body
    conv_id = body["conversation_id"]
    # Ensure it's a UUID string
    uuid.UUID(conv_id)

    # Get
    r2 = client.get(f"/api/chat/conversations/{conv_id}")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["conversation_id"] == conv_id
    assert body2["messages"] == []


def test_chat_query_requires_conversation_id(client_with_fake_query):
    # Missing conversation_id should 400
    r = client_with_fake_query.post("/api/chat/query", json={"query": "Hello", "fund_id": 1})
    assert r.status_code == 400


def test_chat_query_flow(client_with_fake_query):
    # Create conversation first
    r = client_with_fake_query.post("/api/chat/conversations", json={"fund_id": 1})
    assert r.status_code == 200
    conv_id = r.json()["conversation_id"]

    # Send query
    r2 = client_with_fake_query.post(
        "/api/chat/query",
        json={
            "query": "What is NAV?",
            "fund_id": 1,
            "conversation_id": conv_id,
        },
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["answer"].startswith("Echo: ")
    assert isinstance(body["sources"], list)

    # Verify messages stored
    r3 = client_with_fake_query.get(f"/api/chat/conversations/{conv_id}")
    assert r3.status_code == 200
    hist = r3.json()["messages"]
    # Expect 2 messages: user and assistant (assistant may be empty if error; fake engine returns content)
    assert len(hist) >= 2
    roles = [m["role"] for m in hist]
    assert roles[0] == "user"
    assert roles[1] == "assistant"
