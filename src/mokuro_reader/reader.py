import json
import sqlite3
from pathlib import Path
import logging
from typing import List
import uuid

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_tables(conn: sqlite3.Connection) -> None:
    """Create the necessary database tables if they don't already exist."""
    cur = conn.cursor()
    cur.execute("""
        CREATE OR REPLACE TABLE IF NOT EXISTS Volumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            volume TEXT,
            title_uuid TEXT,
            volume_uuid TEXT
        )
    """)
    cur.execute("""
        CREATE OR REPLACE TABLE IF NOT EXISTS Pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volume_id INTEGER,
            page_number INTEGER,
            text TEXT,
            FOREIGN KEY(volume_id) REFERENCES Volumes(id)
        )
    """)
    conn.commit()


def extract_page_text(page: List[dict]) -> str:
    """
    Aggregate text from all blocks in a page.
    Each block's "lines" field (a list of strings) is joined by a Japanese full stop,
    and then the blocks are joined with newlines.
    """
    return "\n".join(
        "。".join(block.get("lines", [])) for block in page.get("blocks", [])
    )

def generate_uuid() -> str:
    """
    Generates a UUID version 4 as a string
    """
    return str(uuid.uuid4())

def process_volume_file(volume_file: Path, conn: sqlite3.Connection, title_uuid: str = None) -> None:
    """
    Process a single JSON file representing a volume:
    - Load the JSON
    - Insert the volume metadata into the Volumes table
    - Insert each page's aggregated text into the Pages table
    """
    try:
        with open(volume_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {volume_file.name}: {e}")
        return
    except Exception as e:
        logging.error(f"Error reading {volume_file.name}: {e}")
        return

    logging.info(f"Processing volume: {volume_file.name}")

    # Extract volume-level metadata
    title = data.get("title", "")
    volume_title = data.get("volume", "")
    if title_uuid is None:
        title_uuid = generate_uuid()    
    volume_uuid = data.get("volume_uuid", "")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Volumes (title, volume, title_uuid, volume_uuid)
        VALUES (?, ?, ?, ?)
    """,
        (title, volume_title, title_uuid, volume_uuid),
    )
    volume_id = cur.lastrowid

    pages = data.get("pages", [])
    for page_number, page in enumerate(pages, start=1):
        text = extract_page_text(page)
        cur.execute(
            """
            INSERT INTO Pages (volume_id, page_number, text)
            VALUES (?, ?, ?)
        """,
            (volume_id, page_number, text),
        )

    conn.commit()


def main() -> None:
    db_path = "manga_ocr.db"
    data_folder = Path("mokuro")

    with sqlite3.connect(db_path) as conn:
        create_tables(conn)
        for manga_dir in sorted(data_folder.iterdir()):
            title_uuid = generate_uuid() # Sometimes a manga can have a different uuid for the same volume, lets make it constant
            if manga_dir.is_dir():
                logging.info(f"Processing manga: {manga_dir.name}")
                for volume_file in sorted(manga_dir.iterdir()):
                    if volume_file.is_file() and volume_file.suffix == ".mokuro":
                        process_volume_file(volume_file, conn, title_uuid)
                    else:
                        logging.warning(f"Skipping non-JSON file: {volume_file.name}")


if __name__ == "__main__":
    main()
