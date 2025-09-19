import json
import logging
import typer

from src.configuration.log_config import setup_logging
from src.fetch import Fetcher
from src.parser.parser_factory import ParserFactory, ParserTypes, detect_format


app = typer.Typer(help="Video Manifest Analyzer CLI")

# Initialize logging once at startup
setup_logging()


@app.command()
def analyze(
    p: str = typer.Option(
        "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.mpd",
        "-p",
        "--playlist",
        help="Playlist URI (supports .m3u8 for HLS and .mpd for DASH)",
    )
):
    """
    Download and analyze a DASH or HLS manifest.
    """

    format_type = detect_format(p)
    if format_type == "Unknown":
        logging.error(
            "Unsupported manifest format. Only .m3u8 (HLS) and .mpd (DASH) are supported"
        )
        raise typer.Exit(code=1)

    logging.info("Manifest Analyzer CLI")
    logging.info(f"Format: {format_type} (auto-detected)")
    logging.info(f"URI: {p}")

    # Fetch manifest
    try:
        content = Fetcher.get(p)
        logging.info(f"Fetched {format_type} manifest, size: {len(content)} bytes")
    except Exception as e:
        logging.error(f"Error fetching playlist: {e}")
        raise typer.Exit(code=1)

    # Select parser
    if format_type == "DASH":
        parser = ParserFactory.create(ParserTypes.DASH)
    elif format_type == "HLS":
        logging.error("HLS parser not implemented yet")
        raise typer.Exit(code=1)
    else:
        raise RuntimeError("Unhandled format type")

    # Parse and output JSON
    try:
        summary = parser.analyze(content)
        json_output = json.dumps(summary, default=lambda o: o.__dict__, indent=2)
        typer.echo(json_output)
    except Exception as e:
        logging.error(f"Error parsing manifest: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
