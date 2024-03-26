# краулер для создания базы латинских выражений с переводом

# Не забыть !pip install fake_useragent

import requests
from fake_useragent import UserAgent
# чтобы скачать википедию и точно не быть забаненным
from bs4 import BeautifulSoup
import re
# для обработки скачанного
import pandas as pd
# для сохранения результата обработки

user_agent = UserAgent().Chrome
response = requests.get(
    "https://ru.wikipedia.org/wiki/Список_крылатых_латинских_выражений", headers={'User-Agent': user_agent})
# скачиваем, собственно, википедию, прикидываяясь гуглхромом

phrases = {}
soup = BeautifulSoup(response.text, 'html.parser')
plines = soup.find_all('dd')
# ищем фразы в html-супе
# заменяем все гиперссылки на их текст
for line in plines:
    for match in soup.findAll("a"):
        match.replaceWithChildren()
# закидываем в словарь пары "фраза - перевод", но фактически перевод содержит в начале саму фразу тоже
# (просто разбить сплитом по тире нельзя, поскольку в самих фразах и переводах оно тоже есть)
for p in plines:
    a = p.find("b").text
    c = p.text
    phrases[a] = c

nphrases = {}
for k, v in phrases.items():
    # чистим от гадкого пробельного символа
    if k.count("\xa0") != 0:
        for i in range(0, k.count("\xa0")):
            a = k.replace("\xa0", " ")
            b = re.sub(r'\[\d{1,3}\]:\d{1,3}', "", v)
            c = re.sub(r'\xa0', " ", b)
        nphrases[a] = c
        # если стрёмный пробельный символ есть и в самой фразе, и в переводе
    else:
        b = re.sub(r'\[\d{1,3}\]:\d{1,3}', "", v)
        c = re.sub(r'\xa0', " ", b)
        nphrases[k] = c
        # если он только в переводе

# уберём дублирование фразы в переводе
for k, v in nphrases.items():
    s = k + " — "
    d = re.sub(f'{s}', "", v)
    e = re.sub(f'{k}', "", d)
    f = re.sub(r"[?\[] — ", "", e)
    nphrases[k] = f
    # какое-то неприятное форматирование, из-за которого пришлось проходить регуляркой несколько раз

# сохраним итог в таблицу
final = pd.DataFrame.from_dict(nphrases, orient='index', columns=["meaning"])
final.to_csv('phrases.csv', index=True, sep="\t") 
# разделение по табуляциям, поскольку фразы содержат запятые
