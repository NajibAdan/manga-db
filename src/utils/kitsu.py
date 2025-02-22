from concurrent.futures import ThreadPoolExecutor
import requests
import pandas as pd
import json

BASE_URL = "https://kitsu.app/api/edge/manga?filter[text]="
OUTPUT_PATH = "data/genres.jsonl"
CSV_PATH = "data/dim_manga.csv"
session = requests.Session()

df = pd.read_csv(CSV_PATH)


def fetch_json(url: str) -> dict:
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON")
    return None


def extract_data(url: str):
    json_dict = fetch_json(url)
    if not json_dict or "data" not in json_dict:
        return []
    return [
        (
            item["attributes"].get("title")
            if item["type"] == "categories"
            else item["attributes"].get("name")
        )
        for item in json_dict["data"]
    ]


def save_data(json_dict: dict) -> None:
    with open("data/genres.json", "w") as file:
        file.write(json.dumps(json_dict))


def save_record(record: dict, file_path: str) -> None:
    with open(file_path, "a") as file:
        file.write(json.dumps(record) + "\n")


def process_row(row):
    title = row.clean_title
    title_uuid = row.title_uuid
    search_url = f"{BASE_URL}{title}"
    print(f"Searching {title}")
    json_r = fetch_json(search_url)
    if len(json_r["data"]) > 0:
        print(f"Extracting data for {title}")
        # we pick the first one
        manga_data = json_r["data"][0]
        start_date = manga_data["attributes"]["startDate"]
        romaji_title = manga_data["attributes"]["titles"].get("en_jp", "")
        jp_title = manga_data["attributes"]["titles"].get("ja_jp", "")
        relationship_genre_link = manga_data["relationships"]["genres"]["links"][
            "related"
        ]
        category_genre_link = manga_data["relationships"]["categories"]["links"][
            "related"
        ]
        genres = extract_data(relationship_genre_link)
        categories = extract_data(category_genre_link)
        record = {
            "title": title,
            "romanji_title": romaji_title,
            "jp_title": jp_title,
            "title_uuid": title_uuid,
            "start_date": start_date,
            "categories": categories,
            "genres": genres,
        }
        return record
    else:
        print(f"No data found for {title}")
    return None


with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(process_row, df.itertuples(index=False))
    for record in results:
        if record:
            with open(OUTPUT_PATH, "a") as file:
                file.write(json.dumps(record) + "\n")
