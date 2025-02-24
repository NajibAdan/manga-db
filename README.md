# About
Inspired by jpdb.io, which offers extensive details on the number of kanjis and characters in novels, visual novels, and anime, this project was created to address a missing piece—comprehensive data on mangas.


# Data sources
- Mokuro Files: We parse publicly available mokuro files to extract text data.
- Anilist API: Manga metadata is fetched via the Anilist API, enhancing the dataset with rich contextual information.

# Okay this is cool but where do I view it?
The project is hosted online, but you can also run it locally using Docker. Follow these steps:

1. Clone this repo
2. Copy the provided env example file as .env
```bash 
cp .env_example .env
```
3. Launch with Docker Compose
```bash 
docker compose up -d
``` 
4. Head to http://localhost:8501 to see the project!

Happy exploring!