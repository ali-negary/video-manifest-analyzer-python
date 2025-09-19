import logging
import pytest

from src.configuration import log_config


def test_get_log_level_local(monkeypatch):
    monkeypatch.setattr(log_config.settings, "app_env", "local")
    assert log_config.get_log_level() == logging.DEBUG


def test_get_log_level_dev(monkeypatch):
    monkeypatch.setattr(log_config.settings, "app_env", "dev")
    assert log_config.get_log_level() == logging.INFO


def test_get_log_level_prod(monkeypatch):
    monkeypatch.setattr(log_config.settings, "app_env", "prod")
    assert log_config.get_log_level() == logging.INFO


def test_get_log_level_invalid(monkeypatch):
    monkeypatch.setattr(log_config.settings, "app_env", "staging")
    with pytest.raises(ValueError, match="Invalid environment"):
        log_config.get_log_level()


def test_setup_logging_writes_file(tmp_path, monkeypatch):
    """Ensure setup_logging configures handlers and writes to file."""
    log_file = tmp_path / "app.log"

    # Patch FileHandler to use tmp_path instead of fixed "app.log"
    monkeypatch.setattr(log_config, "logging", logging)
    monkeypatch.setattr(log_config, "sys", __import__("sys"))

    # Temporarily override FileHandler
    original_file_handler = logging.FileHandler
    logging.FileHandler = lambda filename: original_file_handler(log_file)

    try:
        log_config.setup_logging()
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        logger.debug("hello log")

        # Verify file got created and contains log
        assert log_file.exists()
        content = log_file.read_text()
        assert "hello log" in content
    finally:
        logging.FileHandler = original_file_handler
