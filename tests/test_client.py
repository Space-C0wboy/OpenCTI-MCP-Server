from opencti_mcp import client


def test_is_mutation_document_detects_mutation():
    assert client.is_mutation_document("mutation Foo { x }") is True
    assert client.is_mutation_document("  \n  mutation { x }") is True
    assert client.is_mutation_document("query Foo { x }") is False
    assert client.is_mutation_document("{ x }") is False


def test_get_client_is_cached(monkeypatch):
    client.reset_client_cache()
    calls = []

    class FakeApi:
        def __init__(self, url, token, ssl_verify=True, **kw):
            calls.append((url, token, ssl_verify))

    monkeypatch.setattr(client, "OpenCTIApiClient", FakeApi)
    monkeypatch.setattr(
        client, "get_config",
        lambda: client_config_stub(),
    )
    c1 = client.get_client()
    c2 = client.get_client()
    assert c1 is c2
    assert len(calls) == 1


def client_config_stub():
    from opencti_mcp.config import Config
    return Config(
        url="https://x/", token="t", read_only=True, timeout=30,
        ssl_verify=True, log_level="INFO", http_host="127.0.0.1", http_port=8765,
    )
