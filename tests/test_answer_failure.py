import app


# Fake graph store: returns one match and one connected neighbor.
# No real Neo4j connection is needed.
class FakeStore:
    def query_nodes_by_text(self, text_query):
        return [{"name": "Ada"}]

    def fetch_hops_context(self, start_node, depth=2):
        return [
            {
                "name": "Acme",
                "summary": "A company",
                "source": "sample.txt",
                "chunk": "Ada works at Acme.",
                "path_contexts": ["Ada works at Acme"],
            }
        ]


def test_answer_generation_failure_returns_error_message(monkeypatch):
    # Fake Ollama call that crashes while generating the answer
    def fake_chat(**kwargs):
        raise ConnectionError("Ollama is not running")

    monkeypatch.setattr(app.inference_client, "chat", fake_chat)

    result = app.run_attributed_graph_rag("Where does Ada work?", FakeStore())

    # The app should not crash, it returns an error message instead
    assert "An error occurred during text generation" in result.content
    assert "Ollama is not running" in result.content

    # No sources, since no answer was generated
    assert result.sources == []

    # The trace should still show the retrieval steps that ran before the failure
    assert any("Compiled context" in step for step in result.execution_steps)