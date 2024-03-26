# Скрипт для обработки выражений через SpaCy

# Не забыть установить/обновить всю вот эту дрянь, иначе они конфликтуют:
# Не забыть !pip install https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-any-py3-none-any.whl
# Не забыть !pip install typing_extensions==4.7.1 --upgrade
# Не забыть !pip install -U pydantic spacy==3.4.4
# Не забыть !pip install -U spacy
# Ещё для русского модель !py -m spacy download ru_core_news_sm
# пробовала !pip install cairosvg (from cairosvg import svg2png) для изменения формата изображений, 
# а чтобы он работал - !pip install pipwin, !pipwin install cairocffi,
# но лучше вышло !pip install svglib, !pip install rlPyCairo

import spacy
from spacy import displacy 
# морфосинт обработка еее!
import pandas as pd 
# чтобы всё было в таблице
from svglib.svglib import svg2rlg 
from reportlab.graphics import renderPM 
# перевод схем из формата svg в png, потому что с svg тгбот не работает
from pathlib import Path
import pathlib


nlpla = spacy.load('la_core_web_lg')
nlpru = spacy.load("ru_core_news_sm")
# загружаем модели для латыни (для разборов) и для русского (для последующего поиска по леммам)
data = pd.read_csv("phrases.csv", sep="\t")
data.rename(columns={'Unnamed: 0': 'phrases'}, inplace=True)
data['lemmas'] = True
data['analize'] = True
# открываем таблицу со скачанными фразами и добавляем в неё нужные колонки

# проходимся по всей таблице
for idx, row in data.iterrows():
    docla = nlpla(row[0])
    docru = nlpru(row[1])
    lemma_line = ""
    analize = "🍃Анализ фразы:🍃\n"
    # проходимся по латинским словам и делаем для каждого разбор
    for token in docla:
        morfa_features = list(token.morph)
        morphology = "\n🔦Признаки:\n"
        for i in range(len(morfa_features)):
            if len(morfa_features) != 0:
                feature = morfa_features[i].split("=")
                if i == len(morfa_features)-1:
                    morphology += f"{feature[0]}: {feature[1]} \n"
                else:
                    morphology += f"{feature[0]}: {feature[1]}, \n"
        lemma_line += f" {token.lemma_}" 
        # делаем лемматизированную строку на латыни (вдруг юзер будет на ней искать?)
        analize += f'\n\n👉Слово "{token.text}":\n💛Начальная форма — {token.lemma_},\n\
🖤Часть речи — {token.pos_}{morphology}'
        # собираем красивую строку морфразбора, которую можно будет вставлять в посты
    options = {"bg": "#E0D8A7", "font": "Times New Roman", "distance": 140}
    svg = displacy.render(docla, style="dep", options=options)
    output_path = Path("./plots/" + str(idx) + ".svg")
    output_path.open("w", encoding="utf-8").write(svg)
    # генерируем схему зависимостей в латинской фразе и 
    # сохраняем её в папочку с индексом фразы в названии
    drawing = svg2rlg(output_path)
    renderPM.drawToFile(drawing, f"plots/{str(idx)}.png", fmt='PNG', bg=14735527)
    # самое сложное: переформатируем схемы в картинки так, чтобы красота не уехала
    # в поисках подходящего модуля и инструкции к найденному модулю я чуть не умерла
    # ну вот кто делает десятиричную кодировку цветов? зачем? почему не прописать 
    # хотя бы где-нибудь, что это десятиричная кодировка?
    pathlib.Path.unlink(output_path)
    for t in docru:
        lemma_line += f" {t.lemma_}"
        # добавляем в проку лемм русские леммы тоже
    data.at[idx, 'lemmas'] = lemma_line
    data.at[idx, 'analize'] = analize
    # добавляем полученные строки в таблицу

data.to_csv('archieve/analize.csv', index=False)
# сохраняем нашу красивую табличку в файл
