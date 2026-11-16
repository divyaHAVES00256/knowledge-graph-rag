import app


def test_parse_graph_elements_uses_llm_response(monkeypatch):
    def fake_chat(**kwargs):
        return {
            "message": {
                "content": (
                    '{"nodes":[{"name":"Ada","type":"PERSON",'
                    '"summary":"A researcher"}],"edges":[]}'
                )
            }
        }

    monkeypatch.setattr(app.inference_client, "chat", fake_chat)

    nodes, edges = app.parse_graph_elements_via_llm(
        "Ada is a researcher.", "sample.txt"
    )

    assert len(nodes) == 1
    assert nodes[0].display_name == "Ada"
    assert nodes[0].origin_document == "sample.txt"
    assert edges == []