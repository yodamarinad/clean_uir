import requests
from bs4 import BeautifulSoup
import json
import re
from time import sleep
from typing import List, Union
from dto import process, Person
from collections import OrderedDict


def fetch_wikipedia_page_html(title, language='ru'):
    url = f"https://{language}.wikipedia.org/wiki/{title}"
    print(url, 'url')
    response = requests.get(url)
    print(response, 'response wiki')
    if response.status_code == 200:
        return response.text
    title = title.replace(' ', ', ', 1)
    url = f"https://{language}.wikipedia.org/wiki/{title}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

    

def parse_information_from_wikipedia(html):
    soup = BeautifulSoup(html, 'html.parser')

    info_missing = {}

    paragraphs = soup.find_all('p')
    biography = ' '.join(p.get_text(strip=True) for p in paragraphs)
    if len(biography) < 50:
        return None
    if biography:
        info_missing['biography'] = biography
    return info_missing

def fetch_dosye_page_html(title):
    url = f"https://dosye.info/{title}"
    print(url, 'url')
    response = requests.get(url)
    print(response, 'response dosye')
    if response.status_code == 200:
        return response.text
    return None


def parse_dosye_biography(html):
    soup = BeautifulSoup(html, 'html.parser')

    info_missing_dosye = {}

    #search_results = soup.find_all('a', href=True)
    bio_sections = soup.find_all('p')
    biography = " ".join(p.get_text(strip=True) for p in bio_sections)
    print(biography, 'biography dosye')
    if biography:
        info_missing_dosye['biography'] = biography
    return info_missing_dosye


def process_people_data(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    handmade_people = [person for person in data if person.get('index') == 'handmade']
    # handmade_people = [1]

    results = []

    #найти по имени
    for person in handmade_people:
        name = person.get('name')
        # name = 'Подлесецкий Лев Теофилович'
        
        if not name:
            continue

        name = name.replace('ё', 'е')

        wikipedia_html = fetch_wikipedia_page_html(name, 'ru')
        if not wikipedia_html:
            wikipedia_html = fetch_wikipedia_page_html(name, 'uk')

        if wikipedia_html:
            info = parse_information_from_wikipedia(wikipedia_html)

        dosye_html = fetch_dosye_page_html(name)
        if not dosye_html:
            dosye_html = fetch_dosye_page_html(name.replace(' ', ', ', 1))
        if dosye_html:
            info = parse_dosye_biography(dosye_html)
            print(info, 'info dosye')  
        else:
            info = 'null'          

        # else:
        #     dosye_html = fetch_dosye_page_html(name.replace(' ', ', ', 1))
        #     dosye_bio = parse_dosye_biography(dosye_html)
        #     print(dosye_bio, 'dosye bio')
        #     info = {'biography': dosye_bio}
        #     print(info, 'info dosye')
        if info:
            results.append({
                'name': name,
                'info': info
            })

    return results


def save_json(data: Union[List[dict], dict], path: str) -> Union[List[dict], dict]:
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return data

# Example usage

if __name__ == '__main__':

    file_path = 'clean_data.json'
    results_missing = process_people_data(file_path)
    missing_results = save_json(results_missing, f"missing_test_people.json")
