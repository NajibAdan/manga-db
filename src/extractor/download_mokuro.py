from urllib.parse import unquote
from pathlib import Path
import requests
from bs4 import BeautifulSoup
URL = 'https://www.mokuro.moe/manga/'

result = requests.get(URL)
home_page_soup = BeautifulSoup(result.text,'lxml')

# collect all the high level links
urls = []
for url in home_page_soup.find_all('a'):
    if url['href'][-1] == '/':
        urls.append(url['href'])

for i,url in enumerate(urls):
    manga_name = unquote(url[:-1])
    print(f"Going through {manga_name}")
    result = requests.get(f"{URL}{url}")
    page_soup = BeautifulSoup(result.text,'lxml')
    for href in page_soup.find_all('a'):
        if len(href['href']) >= 7 and href['href'][-7:] == '.mokuro':
            volume_name = href.text
            print(f"Downloading {volume_name}")
            mokuro_file_request = requests.get(f"{URL}{url}{href['href']}")
            p = Path(f"mokuro/{manga_name}")
            p.mkdir(parents=True, exist_ok=True)
            fn = volume_name 
            filepath = p / fn
            with filepath.open("wb") as f:
                f.write(mokuro_file_request.content)
    
# for each high level link pick all the files that have .mokuro extension