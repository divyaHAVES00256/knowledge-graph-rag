import app


def test_parse_graph_elements_returns_empty_when_llm_fails(monkeypatch):
    # Fake Ollama call that crashes, like Ollama being offline
    def fake_chat(**kwargs):
        raise ConnectionError("Ollama is not running")

    # Record warnings instead of calling the real Streamlit UI
    warnings = []

    monkeypatch.setattr(app.inference_client, "chat", fake_chat)
    monkeypatch.setattr(app.st, "warning", lambda msg: warnings.append(msg))

    nodes, edges = app.parse_graph_elements_via_llm(
        "Ada is a researcher.", "sample.txt"
    )

    # The function should not crash, it returns empty lists instead
    assert nodes == []
    assert edges == []

    # The user should be warned, and the warning should include the error
    assert len(warnings) == 1
    assert "Ollama is not running" in warnings[0]