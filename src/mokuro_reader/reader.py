import os
import json
import sqlite3
from pathlib import Path
# Set up the SQLite database connection
conn = sqlite3.connect('manga_ocr.db')
cur = conn.cursor()

# Create tables (simplified example)
cur.execute('''
CREATE TABLE IF NOT EXISTS Volumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    volume TEXT,
    title_uuid TEXT,
    volume_uuid TEXT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volume_id INTEGER,
    page_number INTEGER,
    text TEXT,
    FOREIGN KEY(volume_id) REFERENCES Volumes(id)
)
''')

conn.commit()

# Function to aggregate text from blocks
def extract_page_text(page):
    page_text = []
    for block in page.get('blocks', []):
        # Each block has a "lines" field (a list of strings)
        lines = block.get('lines', [])
        # Join lines if needed, or keep them separate
        page_text.append("。".join(lines))
    return "\n".join(page_text)

# Path to your folder containing JSON files
mokuro_path = Path('mokuro')

# Iterate over each JSON file in the folder (adjust as needed)
for manga in mokuro_path.iterdir() :
    for volume in manga.iterdir():
        with open(volume, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract volume-level metadata
        title = data.get('title', '')
        volume_title = data.get('volume', '')
        title_uuid = data.get('title_uuid', '')
        volume_uuid = data.get('volume_uuid', '')

        # Insert volume record and get its ID
        cur.execute('''
            INSERT INTO Volumes (title, volume, title_uuid, volume_uuid)
            VALUES (?, ?, ?, ?)
        ''', (title, volume_title, title_uuid, volume_uuid))
        volume_id = cur.lastrowid
        
        pages = data.get('pages', [])
        for page_number, page in enumerate(pages, start=1):
            text = extract_page_text(page)
            cur.execute('''
                INSERT INTO Pages (volume_id, page_number, text)
                VALUES (?, ?, ?)
            ''', (volume_id, page_number, text))
        
        # Commit after each file, or you can batch commit later
        conn.commit()

conn.close()
