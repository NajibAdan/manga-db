import logging
from urllib.parse import unquote, urljoin
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://www.mokuro.moe/manga/"


def get_soup(url, session, timeout=10) -> BeautifulSoup:
    """Fetch a URL and return a BeautifulSoup object, or None if there was an error."""
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None
    return BeautifulSoup(response.text, "lxml")


def get_high_level_links(soup: BeautifulSoup) -> List[str]:
    """Extract all anchor tags whose href ends with '/' (indicating a directory)."""
    links = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if href.endswith("/"):
            links.append(href)
    return links


def download_mokuro_files(
    manga_url: str, manga_name: str, session: requests.Session
) -> None:
    """
    Given a manga URL and its name, find and download all .mokuro files.
    The downloaded files are stored under mokuro/<manga_name>/.
    """
    full_url = urljoin(BASE_URL, manga_url)
    logging.info(f"Processing manga: {manga_name} ({full_url})")

    soup = get_soup(full_url, session)
    if soup is None:
        return

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if href.lower().endswith(".mokuro"):
            volume_name = anchor.get_text(strip=True) or Path(href).stem
            logging.info(f"Downloading volume: {volume_name}")

            file_url = urljoin(full_url, href)
            try:
                file_response = session.get(file_url, timeout=10)
                file_response.raise_for_status()
            except requests.RequestException as e:
                logging.error(f"Failed to download {file_url}: {e}")
                continue

            output_dir = Path("mokuro") / manga_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Ensure a proper filename with .mokuro extension
            volume_filename = (
                volume_name
                if volume_name.lower().endswith(".mokuro")
                else f"{volume_name}.mokuro"
            )
            output_path = output_dir / volume_filename

            with output_path.open("wb") as f:
                f.write(file_response.content)
            logging.info(f"Saved file to {output_path}")


def main() -> None:
    session = requests.Session()

    # Get the home page and extract the manga directories
    soup = get_soup(BASE_URL, session)
    if soup is None:
        logging.error("Could not retrieve the home page.")
        return

    manga_links = get_high_level_links(soup)
    for manga_url in manga_links:
        # The manga name is the decoded URL without its trailing slash.
        manga_name = unquote(manga_url.rstrip("/"))
        download_mokuro_files(manga_url, manga_name, session)


if __name__ == "__main__":
    main()
