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
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text
    return None

def parse_information_from_wikipedia(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    info_missing = {}
    
    
    paragraphs = soup.find_all('p')


    biography = ' '.join(p.get_text(strip=True) for p in paragraphs)
    if biography:
        info_missing['biography'] = biography
    return info_missing


def scrape_deputies_data8(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')   
    pattern = r'\(р\. \d{4}\)'
    pattern_ = r'\(.*?\d{4}—\d{4}\)'


    deputies_table = soup.find("table", {"class": "wikitable sortable"})
    if deputies_table:
            deputies_data1 = []

            for row in deputies_table.find_all('tr')[1:]:
                cells = row.find_all('td')
                name_comma = cells[2].text.strip()
                name_ = re.sub(pattern, '', name_comma.replace(",", ''))
                name = re.sub(pattern_, '', name_)
                deputy_dict = {"name": name, "term": 8}
                deputies_data1.append(deputy_dict)

            return deputies_data1


def scrape_deputies_data9(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')   
    pattern = r' Архивная\sкопия\sот\s\d+\s\w+\s\d{4}\sна\sWayback\sMachine'

    deputies_table = soup.find("table", {"class": "wikitable sortable"})    
    if deputies_table:
            deputies_data2 = []

            for row in deputies_table.find_all('tr')[1:]:
                cells = row.find_all('td')
                name_ = cells[1].text.strip()
                name =  re.sub(pattern, '', name_)
                deputy_dict = {"name": name, "term": 9}
                deputies_data2.append(deputy_dict)

            return deputies_data2



#функция чтобы найти базовую информацию по 141 человеку с айди "handmade"


"""

"age": xx
"birthdate": xxxx-xx-xx
"education":
    "label": "name",
    "start_date":дата начала "xxxx-xx-xx" ,
    "end_date": дата конца "xxxx-xx-xx",
    "link_type": [
        "Учеба",
"job": 
    "label": "name",
   "start_date":дата начала "xxxx-xx-xx" ,
    "end_date": дата конца "xxxx-xx-xx",
    "link_type": [
        "Работает (персона-организация)"
                ],
"fractions": 
    "name": "name",
   "start_date":дата начала "xxxx-xx-xx" ,
    "end_date": дата конца "xxxx-xx-xx",

"""
def process_people_data(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    handmade_people = [person for person in data if person.get('index') == 'handmade']

    results = []
    for person in handmade_people:
        name = person.get('name')
        if not name:
            continue
        
        wikipedia_html = fetch_wikipedia_page_html(name, 'ru')

        if not wikipedia_html:
            wikipedia_html = fetch_wikipedia_page_html(name, 'uk')

        info = None
        
        if wikipedia_html:
            info = parse_information_from_wikipedia(wikipedia_html)
    
            
            results.append({
                'name': name,
                'info': info
            })
    
    return results


def save_json(data: Union[List[dict], dict], path: str) -> Union[List[dict], dict]:
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return data

def save_pers(data: List[Person], path: str) -> Union[List[dict], dict]:
    with open(path, 'w', encoding='utf-8') as file:
        data = json.dumps(data, default=lambda o: o.__dict__, sort_keys=False, indent=4, ensure_ascii=False)
        file.write(data)
        file.close()
     


if __name__ == '__main__':
    #url8 = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BD%D0%B0%D1%80%D0%BE%D0%B4%D0%BD%D1%8B%D1%85_%D0%B4%D0%B5%D0%BF%D1%83%D1%82%D0%B0%D1%82%D0%BE%D0%B2_%D0%92%D0%B5%D1%80%D1%85%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D1%80%D0%B0%D0%B4%D1%8B_%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%8B_VIII_%D1%81%D0%BE%D0%B7%D1%8B%D0%B2%D0%B0"
    #url9 = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BD%D0%B0%D1%80%D0%BE%D0%B4%D0%BD%D1%8B%D1%85_%D0%B4%D0%B5%D0%BF%D1%83%D1%82%D0%B0%D1%82%D0%BE%D0%B2_%D0%92%D0%B5%D1%80%D1%85%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D1%80%D0%B0%D0%B4%D1%8B_%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D1%8B_IX_%D1%81%D0%BE%D0%B7%D1%8B%D0%B2%D0%B0'
    #parl8 = scrape_deputies_data8(url8)
    #parl9 = scrape_deputies_data9(url9)
    #merged = save_json(parl8 + parl9, f"merged_test.json")
    #with open("deputies.json", 'r', encoding='utf-8') as fp:
        #data = json.load(fp)
   # clean_data = process(merged, data)
    #clean_merged_data = save_pers(clean_data, f"clean_data.json")

    file_path = 'clean_data.json'  
    results = process_people_data(file_path)
    missing_people = save_json(results, f"missing people.json")
