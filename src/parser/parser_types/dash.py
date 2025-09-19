import logging
from typing import Dict, List

from lxml import etree

from src.parser.parser_interface import IParser as _IParser
from src.parser.util.models import VideoTrack as _VideoTrack, AudioTrack as _AudioTrack


logger = logging.getLogger(__name__)


class DashParser(_IParser):
    def analyze(self, manifest: str) -> Dict[str, List]:
        if not manifest or not manifest.strip():
            logger.error("Manifest is empty")
            raise ValueError("Manifest is empty")

        try:
            tree = etree.fromstring(manifest.encode("utf-8"))
        except etree.XMLSyntaxError as e:
            logger.error(f"Invalid XML manifest: {e}")
            raise ValueError(f"Invalid XML manifest: {e}") from e

        ns = {"mpd": tree.nsmap.get(None)} if None in tree.nsmap else {}
        videos: List[_VideoTrack] = []
        audios: List[_AudioTrack] = []

        for adaptation in tree.xpath("//mpd:AdaptationSet", namespaces=ns):
            mime_type = adaptation.attrib.get("mimeType", "").lower().strip()
            if not mime_type:
                logger.debug("Skipping AdaptationSet without mimeType")
                continue

            for rep in adaptation.xpath("mpd:Representation", namespaces=ns):
                codec = rep.attrib.get("codecs", "")
                bitrate = int(rep.attrib.get("bandwidth", 0))

                if not codec or bitrate <= 0:
                    logger.debug("Skipping Representation with missing codec/bitrate")
                    continue

                if "video" in mime_type:
                    width = int(rep.attrib.get("width", 0))
                    height = int(rep.attrib.get("height", 0))
                    if width <= 0 or height <= 0:
                        logger.debug(
                            f"Skipping video rep with invalid resolution ({width}x{height})"
                        )
                        continue
                    resolution = f"{width}x{height}"
                    videos.append(
                        _VideoTrack(codec=codec, bitrate=bitrate, resolution=resolution)
                    )
                    logger.debug(f"Added video track: {codec}, {bitrate}, {resolution}")

                elif "audio" in mime_type:
                    channels = None
                    config = rep.find(".//mpd:AudioChannelConfiguration", namespaces=ns)
                    if config is not None:
                        try:
                            channels = int(config.attrib.get("value", "0"))
                        except ValueError:
                            logger.warning(
                                f"Invalid channel value in {rep.attrib.get('id')}"
                            )
                    audios.append(
                        _AudioTrack(
                            codec=codec,
                            bitrate=bitrate,
                            channels=channels,
                            language=adaptation.attrib.get("lang"),
                        )
                    )
                    logger.debug(
                        f"Added audio track: {codec}, {bitrate}, {channels}, {adaptation.attrib.get('lang')}"
                    )

        if not videos and not audios:
            logger.error("No valid video or audio tracks found in manifest")
            raise ValueError("No valid video or audio tracks found in manifest")

        return {"videos": videos, "audios": audios}
