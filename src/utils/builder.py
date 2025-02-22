import pandas as pd
import requests

df = pd.read_csv("data/dim_manga.csv")
json_l = pd.read_json("data/genres.jsonl", lines=True)
manual_cleaned = pd.read_csv("data/cleaned_titles.tsv", sep="\t")
manual_cleaned = manual_cleaned.merge(df[["clean_title", "title_uuid"]], how="inner")
manual_cleaned["clean_title"] = manual_cleaned["alternate_title"].fillna(
    manual_cleaned["clean_title"]
)
json_l["clean_title"] = json_l["romanji_title"]
pd.concat(
    [
        json_l[["clean_title", "title_uuid"]],
        manual_cleaned[["clean_title", "title_uuid"]],
    ]
).to_csv("data/temp.csv", index=False)
