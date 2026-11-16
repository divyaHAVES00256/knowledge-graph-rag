import app


def test_parse_graph_elements_returns_nodes_and_edges(monkeypatch):
    # Fake Ollama reply: 2 nodes and 1 relationship between them.
    # This replaces the real LLM, so the test is fast and needs no services.
    def fake_chat(**kwargs):
        return {
            "message": {
                "content": (
                    '{"nodes":['
                    '{"name":"Ada","type":"PERSON","summary":"A researcher"},'
                    '{"name":"Acme","type":"ORGANIZATION","summary":"A company"}'
                    '],"edges":['
                    '{"source":"Ada","target":"Acme","type":"WORKS_FOR",'
                    '"context":"Ada works at Acme"}'
                    ']}'
                )
            }
        }

    # Swap the real Ollama client's chat method with our fake one
    monkeypatch.setattr(app.inference_client, "chat", fake_chat)

    nodes, edges = app.parse_graph_elements_via_llm(
        "Ada works at Acme.", "sample.txt"
    )

    # Both nodes should be parsed into GraphNode objects
    assert len(nodes) == 2
    assert nodes[0].display_name == "Ada"
    assert nodes[1].display_name == "Acme"

    # The edge should be parsed into a GraphEdge with the right fields
    assert len(edges) == 1
    assert edges[0].source_node == "Ada"
    assert edges[0].target_node == "Acme"
    assert edges[0].edge_type == "WORKS_FOR"
    assert edges[0].origin_document == "sample.txt"