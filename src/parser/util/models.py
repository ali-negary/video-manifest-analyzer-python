from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoTrack:
    codec: str
    bitrate: int
    resolution: str


@dataclass
class AudioTrack:
    codec: str
    bitrate: int
    channels: Optional[int] = None
    language: Optional[str] = None
