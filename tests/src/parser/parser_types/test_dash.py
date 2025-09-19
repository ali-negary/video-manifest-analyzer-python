import pytest
import logging

from src.parser.parser_types.dash import DashParser


def test_empty_manifest(caplog):
    parser = DashParser()
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Manifest is empty"):
            parser.analyze("   ")
    assert any("Manifest is empty" in rec.message for rec in caplog.records)


def test_invalid_xml(caplog):
    parser = DashParser()
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Invalid XML manifest"):
            parser.analyze("<MPD><Broken></MPD>")
    assert any("Invalid XML manifest" in rec.message for rec in caplog.records)


def test_skip_adaptation_without_mime(caplog):
    xml = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">
      <Period>
        <AdaptationSet>
          <Representation id="v1" codecs="avc1" bandwidth="1000" width="100" height="100"/>
        </AdaptationSet>
      </Period>
    </MPD>"""
    parser = DashParser()
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError, match="No valid video or audio tracks found"):
            parser.analyze(xml)
    assert any(
        "Skipping AdaptationSet without mimeType" in rec.message
        for rec in caplog.records
    )


def test_skip_rep_missing_codec_or_bitrate(caplog):
    xml = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">
      <Period>
        <AdaptationSet mimeType="video/mp4">
          <Representation id="v1" bandwidth="0" width="100" height="100"/>
        </AdaptationSet>
      </Period>
    </MPD>"""
    parser = DashParser()
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError, match="No valid video or audio tracks found"):
            parser.analyze(xml)
    assert any(
        "Skipping Representation with missing codec/bitrate" in rec.message
        for rec in caplog.records
    )


def test_skip_video_invalid_resolution(caplog):
    xml = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">
      <Period>
        <AdaptationSet mimeType="video/mp4">
          <Representation id="v1" codecs="avc1" bandwidth="1000" width="0" height="0"/>
        </AdaptationSet>
      </Period>
    </MPD>"""
    parser = DashParser()
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError, match="No valid video or audio tracks found"):
            parser.analyze(xml)
    assert any(
        "Skipping video rep with invalid resolution" in rec.message
        for rec in caplog.records
    )


def test_valid_video_track(caplog):
    xml = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">
      <Period>
        <AdaptationSet mimeType="video/mp4">
          <Representation id="v1" codecs="avc1.42C00D" bandwidth="401000" width="224" height="100"/>
        </AdaptationSet>
      </Period>
    </MPD>"""
    parser = DashParser()
    result = parser.analyze(xml)
    assert len(result["videos"]) == 1
    v = result["videos"][0]
    assert v.codec == "avc1.42C00D"
    assert v.bitrate == 401000
    assert v.resolution == "224x100"


def test_valid_audio_track(caplog):
    xml = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">
      <Period>
        <AdaptationSet mimeType="audio/mp4" lang="en">
          <Representation id="a1" codecs="mp4a.40.2" bandwidth="64008">
            <AudioChannelConfiguration value="2"/>
          </Representation>
        </AdaptationSet>
      </Period>
    </MPD>"""
    parser = DashParser()
    result = parser.analyze(xml)
    assert len(result["audios"]) == 1
    a = result["audios"][0]
    assert a.codec == "mp4a.40.2"
    assert a.bitrate == 64008
    assert a.channels == 2
    assert a.language == "en"


def test_audio_invalid_channel_value_logs_warning(caplog):
    xml = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">
      <Period>
        <AdaptationSet mimeType="audio/mp4">
          <Representation id="a1" codecs="mp4a.40.2" bandwidth="64008">
            <AudioChannelConfiguration value="not-a-number"/>
          </Representation>
        </AdaptationSet>
      </Period>
    </MPD>"""
    parser = DashParser()
    with caplog.at_level(logging.WARNING):
        result = parser.analyze(xml)
        assert result["audios"][0].channels is None
        assert any("Invalid channel value" in rec.message for rec in caplog.records)


def test_no_tracks_found(caplog):
    xml = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"><Period></Period></MPD>"""
    parser = DashParser()
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="No valid video or audio tracks found"):
            parser.analyze(xml)
    assert any(
        "No valid video or audio tracks found" in rec.message for rec in caplog.records
    )
