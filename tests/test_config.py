import pytest
from opencti_mcp import config
from opencti_mcp.errors import ConfigError


@pytest.fixture(autouse=True)
def _reset():
    config.reset_config_cache()
    yield
    config.reset_config_cache()


def test_parses_json_style_env_file(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        '"OPENCTI_URL": "https://cti.example.com/",\n'
        '"OPENCTI_TOKEN": "abc123"\n'
    )
    monkeypatch.delenv("OPENCTI_URL", raising=False)
    monkeypatch.delenv("OPENCTI_TOKEN", raising=False)
    cfg = config.get_config(env_path=env)
    assert cfg.url == "https://cti.example.com/"
    assert cfg.token == "abc123"
    assert cfg.read_only is True  # default


def test_parses_standard_dotenv_file(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("OPENCTI_URL=https://x/\nOPENCTI_TOKEN=t\nOPENCTI_READ_ONLY=false\n")
    monkeypatch.delenv("OPENCTI_URL", raising=False)
    monkeypatch.delenv("OPENCTI_TOKEN", raising=False)
    cfg = config.get_config(env_path=env)
    assert cfg.url == "https://x/"
    assert cfg.read_only is False


def test_os_env_overrides_file(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('"OPENCTI_URL": "https://file/",\n"OPENCTI_TOKEN": "filetok"\n')
    monkeypatch.setenv("OPENCTI_TOKEN", "envtok")
    cfg = config.get_config(env_path=env)
    assert cfg.token == "envtok"


def test_missing_required_raises(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('"OPENCTI_URL": "https://x/"\n')  # no token
    monkeypatch.delenv("OPENCTI_TOKEN", raising=False)
    with pytest.raises(ConfigError):
        config.get_config(env_path=env)
