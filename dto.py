from typing import List, Optional, Union, Dict
from datetime import datetime
import json
from collections import OrderedDict

class Links:
    education_data: Optional['Data']
    job_data: Optional['Data']

    def __init__(self) -> None:
        self.education_data = Data(set(), set())
        self.job_data = Data(set(), set())

class Data:
    node_types: set
    link_types: set

    def __init__(self, node_types: set, link_types: set) -> None:
        self.node_types = node_types
        self.link_types = link_types

class Info:
    label: str
    node_type: str
    link_type: List[str]
    info: Optional[List['Info']]

    def __init__(self, label: str, node_type: str, link_type: List[str], info: Optional['Info']) -> None:
        self.label = label
        self.node_type = node_type
        self.link_type = link_type
        self.info = info


class Occupation:
    label: str
    node_type: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    link_type: List[str]
    info: Optional[List[Info]]

    def __init__(self, label: str, node_type: str, start_date: Optional[datetime], end_date: Optional[datetime], link_type: List[str], info: Optional[List[Info]]) -> None:
        self.label = label
        self.node_type = node_type
        self.start_date = start_date
        self.end_date = end_date
        self.link_type = link_type
        self.info = info


class Fraction:
    name: str
    start_date: datetime
    end_date: datetime

    def __init__(self, name: str, start_date: datetime, end_date: datetime) -> None:
        self.name = name
        self.start_date = start_date
        self.end_date = end_date


class Person:
    index: str
    name: str
    age: int
    birthdate: datetime
    education: List[Occupation]
    job: List[Occupation]
    fractions: List[Fraction]
    terms: List[int]

    def __init__(self, index: str, name: List[str], age: int, birthdate: datetime, education: List[Occupation], job: List[Occupation], fractions: List[Fraction], terms: List[int]) -> None:
        self.name = name
        self.index = index
        self.age = age
        self.birthdate = birthdate
        self.education = education
        self.job = job
        self.fractions = fractions
        self.terms = terms

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

#предобработанный список merged, если имя повторяется,то в term добавляется второй созыв,
# checked false -  нет в deputies, true в списке есть

class FilterPerson:
    name: str
    terms: List[int]
    checked: bool

    def __init__(self, name: str, terms: List[int]) -> None:
        self.name = name
        self.terms = terms
        self.checked = False

#ндексированный список депутатов в merged, индекс - имя

class PrepData:
    index_data: Dict[str, FilterPerson]

    def __init__(self) -> None:
        self.index_data = {}

def process(merged: Union[List[dict], dict], deputies: List[bytes]) -> List[Person]:
    merg = PrepData()
    dep = []
    # dep = List[Person]
    links = Links() 


    for i in merged:
        n = i['name']
        t = i['term']
        if n in merg.index_data:
            merg.index_data[n].terms.append(t)
        else:
            merg.index_data[n] = FilterPerson(n, [t])

    for i in deputies:
        if i["_source"]['name'][0] not in merg.index_data:
            continue
        merg.index_data[i["_source"]['name'][0]].checked = True
        name = i["_source"]['name'][0]
        index = i['_index']
        age = i["_source"]['age']
        birthdate = i["_source"]['birthdate']
        terms = merg.index_data[name].terms
        
        educations = info_append("education", i["_source"]['education'], links)
        jobs = info_append("job", i["_source"]['job'], links)
        fractions = []
        # fractions = List[Fraction]
        if i["_source"]['fractions'] is not None:
            for frac in i["_source"]['fractions']:
                fractions.append(Fraction(frac["name"], frac["start_date"], frac["end_date"]))

        dep.append(Person(index, name, age, birthdate, educations, jobs, fractions, terms))

#использовать здесь wikipedia api 

    for n, pf in list(merg.index_data.items()):
        t = pf.terms
        if pf.checked == False:
            dep.append(Person('handmade', n, None, None, None, None, None, t))
            merg.index_data[n].checked = True
    return dep

# checked false -  нет в deputies



def info_append(type:str, data:bytes, links:Links) -> List[Occupation]:
    d = []
    # d = List[Occupation]
    for raw_data in data:
        if  type == "education":
            links.education_data.link_types.add(raw_data['link_type'][0])
            links.education_data.node_types.add(raw_data['node_type'][0])
        elif type == "job":
            links.job_data.link_types.add(raw_data['link_type'][0])
            links.job_data.node_types.add(raw_data['node_type'][0])
        inf_list = []
        # inf_list = List[Info]
        if raw_data['info'] is None:
            inf_list = None
            occupation = Occupation(raw_data["label"],raw_data["node_type"], raw_data["start_date"],raw_data["end_date"],raw_data["link_type"], inf_list)
            d.append(occupation)
            continue
        for inf in raw_data['info']:
            inf2_list = []
            # inf2_list = List[Info]
            if inf['info'] is None:
                inf2_list = None
                continue
            for inf2 in inf['info']:
                inf2_list.append(Info(inf2["label"], inf2["node_type"], inf2["link_type"], None))

            inf_list.append(Info(inf["label"], inf["node_type"], inf["link_type"], inf2_list))

        occupation = Occupation(raw_data["label"],raw_data["node_type"], raw_data["start_date"],raw_data["end_date"],raw_data["link_type"], inf_list)
        d.append(occupation)
    return d


