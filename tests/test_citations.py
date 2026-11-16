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


def test_valid_citation_returns_matching_source(monkeypatch):
    # Fake Ollama answer that cites [1] (valid) and [9] (does not exist)
    def fake_chat(**kwargs):
        return {"message": {"content": "Ada works at Acme [1]. Extra claim [9]."}}

    monkeypatch.setattr(app.inference_client, "chat", fake_chat)

    result = app.run_attributed_graph_rag("Where does Ada work?", FakeStore())

    # The answer text should be passed through unchanged
    assert "Ada works at Acme [1]" in result.content

    # Only the valid citation [1] becomes a source, the fake [9] is ignored
    assert len(result.sources) == 1

    # The source should carry the document name and stored snippet
    source = result.sources[0]
    assert source.doc_source == "sample.txt"
    assert source.reference_text == "Ada works at Acme."
    assert source.path_trace == ["GraphNode: Acme"]