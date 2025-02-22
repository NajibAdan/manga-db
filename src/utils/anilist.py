import random
import requests
import pandas as pd
import json
import time

OUTPUT_DATA = "data/anilist_data.jsonl"
ANILIST_URL = "https://graphql.anilist.co"
# session = requests.Session()
df = pd.read_csv("data/temp.csv")
# Here we define our query as a multi-line string
ANILIST_QUERY = """
query ($title: String) {
  Media(search: $title, type: MANGA) {
    id
    title {
      romaji
      english
      native
    }
    status
    startDate{
      day
      month
      year
    }
    chapters
    volumes
    description
    genres
    averageScore
    coverImage {
      large
    }
  }
}
"""
session = requests.Session()


def fetch_json(title: str) -> dict:
    global session
    variables = {"title": f"{title}"}
    backoff_factor = 0.3
    attempt = 1
    while True:
        try:
            response = session.post(
                ANILIST_URL, json={"query": ANILIST_QUERY, "variables": variables}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed for {title}: {e}")
            if response.status_code == 404:
                print(f"{title} doesn't exist")
                return None
            delay = int(response.headers.get("Retry-After", "60"))
            print(f"Sleeping {delay}..........")
            time.sleep(delay)
            attempt += 1
            session = requests.Session()
        except json.JSONDecodeError:
            print("Failed to decode JSON")
    return None


def process_row(row):
    title = row.clean_title
    title_uuid = row.title_uuid
    print(f"Extracting data for {title}")
    json_r = fetch_json(title)
    if json_r:
        manga_data = json_r["data"]["Media"]
        romaji_title = manga_data["title"]["romaji"]
        jp_title = manga_data["title"]["native"]
        year = manga_data["startDate"]["year"]
        genres = manga_data["genres"]
        score = manga_data["averageScore"]
        record = {
            "title": title,
            "romanji_title": romaji_title,
            "jp_title": jp_title,
            "title_uuid": title_uuid,
            "start_year": year,
            "score": score,
            "genres": genres,
        }
        return record
    else:
        return None


def save_record(record: dict, file_path: str) -> None:
    with open(file_path, "a") as file:
        file.write(json.dumps(record) + "\n")


open(OUTPUT_DATA, "w").close()

for row in df.itertuples(index=True):
    result = process_row(row)
    save_record(result, OUTPUT_DATA)
