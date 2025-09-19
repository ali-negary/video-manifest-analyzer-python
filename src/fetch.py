import httpx
import logging


logger = logging.getLogger(__name__)


class Fetcher:
    """
    Simple HTTP(S) fetcher for retrieving manifest files.
    """

    @staticmethod
    def get(url: str) -> str:
        """
        Fetch a file from the internet and return its content as text.

        Args:
            url (str): The URI of the manifest file.

        Returns:
            str: Content of the file.

        Raises:
            ValueError: If the request fails or content is empty.
        """
        logger.debug(f"Attempting to fetch manifest from: {url}")

        try:
            resp = httpx.get(url, timeout=15)
            resp.raise_for_status()
            logger.info(
                f"Successfully fetched manifest from {url} (size={len(resp.text)} bytes)"
            )
        except Exception as e:
            logger.error(f"Failed to fetch manifest from {url}: {e}")
            raise ValueError(f"Failed to fetch manifest from {url}: {e}") from e

        if not resp.text.strip():
            logger.warning(f"Manifest at {url} is empty")
            raise ValueError(f"Manifest at {url} is empty")

        return resp.text
