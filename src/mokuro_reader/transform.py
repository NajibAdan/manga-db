# %%
import pandas as pd
import sqlite3
import logging
import re

# Read sqlite query results into a pandas DataFrame
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_kanji(text):
    """
    Extracts all Kanji characters from the given text.
    This function includes:
      - Extension A: U+3400 to U+4DBF
      - CJK Unified Ideographs: U+4E00 to U+9FFF
    """
    # The regex finds any character in the specified Unicode ranges.
    kanji_matches = re.findall(r"[\u3400-\u4DBF\u4E00-\u9FFF]", text)
    kanji_matches_set = set(kanji_matches)
    return kanji_matches_set


with sqlite3.connect("manga_ocr.db") as con:
    logging.info("Connected to the sqlite db")
    pages = pd.read_sql_query(
        """select title, title_uuid, string_agg(text, '。') as text, count(p.page_number) as page_count, count(distinct v.volume) as volume_count from pages p 
        inner join volumes v on v.id = p.volume_id 
        group by v.title, title_uuid;""",
        con,
    )
    logging.info("Successfully run the unified_view query")

    pages["unique_chrs"] = pages["text"].apply(extract_kanji)
    pages["num_of_unique_chrs"] = pages["unique_chrs"].str.len()
    pages["unique_chrs"] = pages["unique_chrs"].apply(lambda x: ", ".join(x))
    pages["num_of_chrs"] = pages["text"].str.len()
    pages["pages_per_volume"] = pages["page_count"] / pages["volume_count"]
    pages["avg_chr_per_page"] = pages["num_of_chrs"] / pages["page_count"]
    pages["avg_chr_per_volume"] = pages["num_of_chrs"] / pages["volume_count"]
    pages["clean_title"] = pages["title"].str.replace("(Upscaled)", "").str.strip()
    pages = pages.sort_values(
        by=["clean_title", "volume_count"], ascending=[True, False]
    )
    # pages[pages['clean_title'].duplicated()].sort_values(by='title')
    pages_dedup = pages.drop_duplicates(subset=["clean_title"])
    logging.info("Completed cleaning the data")
    cols = [
        "clean_title",
        "title_uuid",
        "volume_count",
        "page_count",
        "num_of_unique_chrs",
        "num_of_chrs",
        "avg_chr_per_page",
        "avg_chr_per_volume",
    ]
    pages_dedup[cols].to_csv("data/dim_manga.csv", index=False)
    logging.info("Extracted the data to the data folder")

    volumes = pd.read_sql_query(
        """select title, title_uuid, v.volume_number, length(string_agg(text, '。')) as length, count(p.page_number) as page_count from pages p 
        inner join volumes v on v.id = p.volume_id 
        group by v.title, title_uuid, volume_number;""",
        con,
    )
    logging.info("Successfully run the volume query")
    volumes["clean_title"] = volumes["title"].str.replace("(Upscaled)", "").str.strip()
    volumes = volumes.sort_values(
        by=["clean_title", "volume_number", "page_count", "length"],
        ascending=[True, True, True, True],
    )
    volumes_dedup = volumes.drop_duplicates(subset=["clean_title", "volume_number"])
    volumes_dedup.to_csv("data/dim_volume.csv", index=False)
    logging.info("Extracted the data to the data folder")
