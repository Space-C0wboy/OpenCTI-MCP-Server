import pytest
from opencti_mcp import server, config, client
from opencti_mcp.errors import ConfigError


@pytest.fixture(autouse=True)
def _reset():
    config.reset_config_cache()
    client.reset_client_cache()
    yield
    config.reset_config_cache()
    client.reset_client_cache()


@pytest.mark.asyncio
async def test_build_server_registers_tools(monkeypatch):
    monkeypatch.setenv("OPENCTI_URL", "https://x/")
    monkeypatch.setenv("OPENCTI_TOKEN", "t")
    monkeypatch.setenv("OPENCTI_READ_ONLY", "true")

    class F:
        def list(self, **kw): return []
        def read(self, **kw): return {}
    fake = type("C", (), {})()
    for attr in [
        "indicator", "stix_cyber_observable", "report", "malware",
        "threat_actor_group", "intrusion_set", "campaign", "attack_pattern",
        "tool", "vulnerability", "incident", "case_incident",
        "stix_core_relationship", "label", "marking_definition",
    ]:
        setattr(fake, attr, F())
    monkeypatch.setattr(client, "get_client", lambda: fake)

    mcp = server.build_server()
    names = set((await mcp.get_tools()).keys())
    assert "indicators_list" in names
    assert not any(n.endswith("_create") for n in names)


def test_main_exits_2_on_missing_config(monkeypatch):
    def _raise():
        raise ConfigError("missing")
    monkeypatch.setattr(server, "get_config", _raise)
    with pytest.raises(SystemExit) as exc:
        server.main(["--transport", "stdio"])
    assert exc.value.code == 2
