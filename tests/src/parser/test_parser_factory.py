import pytest
import logging

from src.parser.parser_factory import ParserFactory, ParserTypes, detect_format
from src.parser.parser_types.dash import DashParser


def test_detect_format_dash():
    assert detect_format("video.mpd") == "DASH"


def test_detect_format_hls():
    assert detect_format("playlist.m3u8") == "HLS"


def test_detect_format_unknown():
    assert detect_format("file.txt") == "Unknown"


def test_create_dash_parser(caplog):
    caplog.set_level(logging.DEBUG)
    parser = ParserFactory.create(ParserTypes.DASH)
    assert isinstance(parser, DashParser)
    assert any(
        "Creating parser for type: DASH" in rec.message for rec in caplog.records
    )


def test_create_invalid_parser_type(caplog):
    caplog.set_level(logging.ERROR)

    class FakeParserType:
        value = "FAKE"

    with pytest.raises(ValueError, match="Unsupported parser type"):
        ParserFactory.create(FakeParserType)  # not in mapping

    assert any("not supported" in rec.message for rec in caplog.records)
