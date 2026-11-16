import app


# Fake graph store: pretends the database found nothing.
# No real Neo4j connection is needed.
class FakeEmptyStore:
    def query_nodes_by_text(self, text_query):
        return []


def test_no_matching_nodes_returns_message_and_skips_ollama(monkeypatch):
    # If Ollama is called, record it so we can check later
    ollama_calls = []

    def fake_chat(**kwargs):
        ollama_calls.append(kwargs)
        return {"message": {"content": "should never be used"}}

    monkeypatch.setattr(app.inference_client, "chat", fake_chat)

    result = app.run_attributed_graph_rag("Who is Ada?", FakeEmptyStore())

    # The assistant should return its no-match message
    assert "No matching nodes found" in result.content

    # No sources, since nothing was retrieved
    assert result.sources == []

    # Ollama must NOT be called when there is nothing to answer from
    assert ollama_calls == []