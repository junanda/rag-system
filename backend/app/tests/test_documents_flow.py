import io
from datetime import datetime

from app.models.document import Document


def _fake_delay(db_session):
    """Return a fake celery delay() that marks document as completed immediately."""
    def _delay(document_id: int, file_path: str, fund_id: int):
        doc = db_session.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.parsing_status = "completed"
            doc.error_message = None
            db_session.commit()
        class _Task:
            id = "fake-task-id"
        return _Task()
    return _delay


def _pdf_bytes():
    # Minimal bytes; endpoint only checks filename extension and size
    return b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


def test_document_upload_and_status_flow(client, db_session, monkeypatch):
    # Monkeypatch the celery delay to be synchronous and mark completed
    import app.tasks.document_task as document_task
    monkeypatch.setattr(document_task.task_document_process, "delay", _fake_delay(db_session))

    files = {
        "file": ("sample.pdf", io.BytesIO(_pdf_bytes()), "application/pdf"),
    }
    r = client.post("/api/documents/upload", files=files, data={"fund_id": 1})
    assert r.status_code == 200
    body = r.json()
    doc_id = body["document_id"]
    assert body["status"] in ("pending", "processing", "completed")
    assert body["task_id"] == "fake-task-id"

    # Status should be completed due to fake delay
    rs = client.get(f"/api/documents/{doc_id}/status")
    assert rs.status_code == 200
    status = rs.json()
    assert status["document_id"] == doc_id
    assert status["status"] == "completed"

    # Get document detail
    rg = client.get(f"/api/documents/{doc_id}")
    assert rg.status_code == 200
    detail = rg.json()
    assert detail["id"] == doc_id
    assert detail["file_name"] == "sample.pdf"

    # List documents
    rl = client.get("/api/documents?limit=10")
    assert rl.status_code == 200
    docs = rl.json()
    assert any(d["id"] == doc_id for d in docs)

    # Delete document
    rd = client.delete(f"/api/documents/{doc_id}")
    assert rd.status_code == 200
    assert rd.json()["message"] == "Document deleted successfully"

    # Status after delete should 404
    rs2 = client.get(f"/api/documents/{doc_id}/status")
    assert rs2.status_code == 404
