import logging
from enum import Enum

from src.parser.parser_interface import IParser as _IParser
from src.parser.parser_types.dash import DashParser as _DashParser


logger = logging.getLogger(__name__)


def detect_format(uri: str) -> str:
    """Detect manifest format based on file extension."""
    if uri.endswith(".mpd"):
        return "DASH"
    elif uri.endswith(".m3u8"):
        return "HLS"
    return "Unknown"


class ParserTypes(Enum):
    DASH = "DASH"
    HLS = "HLS"


class ParserFactory:
    """Factory class for creating manifest parsers."""

    _parsers = {
        ParserTypes.DASH: _DashParser,
        # ParserTypes.HLS: HlsParser,
    }

    @staticmethod
    def create(parser_type: ParserTypes) -> _IParser:
        parser_class = ParserFactory._parsers.get(parser_type)
        if not parser_class:
            logger.error(f"Parser type '{parser_type}' is not supported")
            raise ValueError(f"Unsupported parser type: {parser_type}")

        logger.debug(f"Creating parser for type: {parser_type.value}")
        return parser_class()
