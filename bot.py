# основной код бота

# Не забыть !pip install pyTelegramBotAPI
# Не забыть !pip install https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-any-py3-none-any.whl
# Не забыть !pip install typing_extensions==4.7.1 --upgrade
# Не забыть !pip install -U pydantic spacy==3.4.4
# Не забыть !pip install -U spacy
# Ещё для русского модель !py -m spacy download ru_core_news_sm
# Я безумно хотела сделать поиск по латинским словам тоже, но латинская модель весит слишком много, 
# чтобы загружать её на pythonanywhere, поэтому я везде закомментила её использование

import telebot  # модуль для управления ботом
from telebot import types  # для создания клавиатуры в боте
from pathlib import Path  # итерация по файлам
import random  # для функции выдачи рандомной фразы
import re
import spacy  # для функции поиска по лемме
import pandas as pd  # для функции анализа
import json  # для словаря с id пользователей и их коллекцией фраз
import matplotlib.pyplot as plt  # для красивого пайчарта в коллекции фраз


with open("token.ini", "r") as o:
    token = o.read()
bot = telebot.TeleBot(token)
# подключение к боту по его API из файла

data = pd.read_csv("archieve/analize.csv")
pic_path = Path("plots")  # для ф-ций выдачи разбора

nlpru = spacy.load("ru_core_news_sm")  # для ф-ции поиска по лемме
# nlpla = spacy.load('la_core_web_lg')

with open("archieve/col.json", "r", encoding="UTF-8") as j:
    jd = json.load(j)
# словарь с id пользователя и его коллекцией

tags_dict = {"funny": ["смешно", "🍹"], "intel": ["интеллектуально", "🍷"],
             "deep": ["глубоко", "🍸"], "other": ["другое", "🫗"]}
# словарь для удобной выдачи стоки для отправки

sours = f'https://ru.wikipedia.org/wiki/Список_крылатых_латинских_выражений'

main_keyboard = types.InlineKeyboardMarkup()  # создание главной клавиатуры для меню
key_random = types.InlineKeyboardButton(text='🎲Рандомная фраза🎲', callback_data='random')
main_keyboard.add(key_random)  # создание и добавление кнопки в клавиатуру
key_search = types.InlineKeyboardButton(text='🔍Поиск по слову🔍', callback_data='search')
main_keyboard.add(key_search)
key_collection = types.InlineKeyboardButton(text='📚Коллекция📚', callback_data='collection')
main_keyboard.add(key_collection)


# приветственный пост
@bot.message_handler(func=lambda message: message.text == '/start')
def start_1(message):
    hello = f'Привет, {message.from_user.first_name}!\n\
У меня тут есть немного латыни (взятой в хорошем качесте со страницы матушки \
нашей <a href="{sours}">Википедии</a>, потому что кто мы без неё). Ну как "немного"... 1374 фразы!\nКажется, \
по этим фразам можно гадать или пафосно подписывать ими фотки \
в нельзяграме. (А ещё понтоваться своей эрудированностью, если всё \
это запомнить, ещё и понимая структуру фраз, а не повторяя, как попугай)\n\n\
Гляди, в меню есть:\n\
1) 🎲 Случайная крылатая фраза - как раз на погадать\n\
2) 🔍 Поиск по слову - нажми на кнопку и введи любое слово, мы постараемся выдать фразы, его содержащие\n\
3) 📚 Коллекция - тут будут фразы, которые ты решишь сохранить на память\n\nТы всегда \
можешь вернуться в меню, написав/нажав /menu если в предыдущем посте не предложено иного'
    if jd.get(str(message.from_user.id)) is None:
        jd[str(message.from_user.id)] = [{"actuall_num": 0, "cur_tag": ""}, {"funny": [], "intel": [], "deep": [], "other": []}]
        with open("archieve/col.json", "w", encoding="UTF-8") as f:
            json.dump(jd, f, ensure_ascii=False)
    # Здесь и в функциях ниже прога проверяет, есть ли юзер в словаре и создаёт для него список, 
    # где в первом словаре лежат переменные, которые я хотела сделать глобальными, но они путались между юзерами
    bot.send_message(message.from_user.id, text=hello, reply_markup=main_keyboard, parse_mode="HTML")


# функция главного меню в ответ на письменное обращение
@bot.message_handler(func=lambda message: message.text == '/menu')
def start(message):
    if jd.get(str(message.from_user.id)) is None:
        jd[str(message.from_user.id)] = [{"actuall_num": 0, "cur_tag": ""}, {"funny": [], "intel": [], "deep": [], "other": []}]
        with open("archieve/col.json", "w", encoding="UTF-8") as f:
            json.dump(jd, f, ensure_ascii=False)
    t = 'Чего изволите?'
    bot.send_message(message.from_user.id, text=t, reply_markup=main_keyboard, parse_mode="HTML")


# функция главного меню при обращении по кнопке 
def menu(call):
    if jd.get(str(call.message.chat.id)) is None:
        jd[str(call.message.chat.id)] = [{"actuall_num": 0, "cur_tag": ""}, {"funny": [], "intel": [], "deep": [], "other": []}]
        with open("archieve/col.json", "w", encoding="UTF-8") as f:
            json.dump(jd, f, ensure_ascii=False)
    t = 'Чего изволите?'
    bot.send_message(call.message.chat.id, text=t, reply_markup=main_keyboard, parse_mode="HTML")


# функция поиска по лемме
def search(call):
#    if bool(re.search('[а-яА-Я]', call.text)) is True:
    doc = nlpru(call.text)  # загружаем модель русскую, если в сообщении кириллица
#    else:
#        doc = nlpla(call.text)
    lemma_keys = []
    possible = []
    for token in doc:
        key = token.lemma_
        lemma_keys.append(key)  # лемматизируем запрос пользователя (списком на случай, если он вводит фразу)
    lemset = set(lemma_keys)
    for idx, row in data.iterrows():
        quo = set(row['lemmas'].split(" "))
        if quo.issuperset(lemset):
            # если множество лемм запроса является подмножеством лемм какой-то фразы,
            # фразу и аргументы при ней сохраняем
            possible.append([str(idx), row['phrases'], row['meaning']])
    if len(possible) == 0:
        text = f"Прости, я ничего не нашёл😥\nПоищи что-нибудь другое?🥺"
        bot.send_sticker(
            call.from_user.id, sticker="CAACAgIAAxkBAAELzEVmAuzgSp32BrOhktE2rRc5jImHKwACVBQAAkmD-Euo9Qnwhai4_TQE")
        bot.send_message(call.from_user.id, text=text)
        bot.register_next_step_handler(call, search)
        # если ничего не нашлось, запускаем поиск сначала
    else:
        posll = []
        for i in possible:
            posl = " — ".join(i)
            posll.append(posl)
        poss = "\n\n".join(posll)
        text = f'Могут подойти эти выражения:\n\n{poss}\n\nНапиши номер выражения, разбор которого хочешь \
посмотреть\n\nМожешь отправить любое сообщение без цифр, чтобы выйти в меню'
        bot.send_message(call.from_user.id, text=text)
        bot.register_next_step_handler(call, send)
        # собираем все подходящие варианты в одно сообщение и просим юзера выбрать, что посмотреть


# функция для выдачи анализа найдённой через search фразы 
def send(call):
    if str(call.text).isdigit() is True:
        numer = int(call.text)
        jd[str(call.from_user.id)][0]["actuall_num"] = numer
        with open("archieve/col.json", "w", encoding="UTF-8") as f:
            json.dump(jd, f, ensure_ascii=False)
            # обновляем переменную, чтобы потом можно было добавить фразу в коллекцию
        pic = open(pic_path / f'{numer}.png', 'rb')
        # здесь ф-ция выдачи анализа, которая будет представлена ниже
        send = f"{analize(numer)}\n\nЕсли понравилась фраза, можешь сохранить👇"
        save_not_keyboard = types.InlineKeyboardMarkup()  # создание клавиатуры
        key_save = types.InlineKeyboardButton(text='📚Сохранить в коллекцию', callback_data=f"save")
        save_not_keyboard.add(key_save)
        key_new_search = types.InlineKeyboardButton(text='🔍Искать ещё', callback_data='search')
        save_not_keyboard.add(key_new_search)
        key_menue = types.InlineKeyboardButton(text='🔙Вернуться в меню', callback_data='menu')
        save_not_keyboard.add(key_menue)
        bot.send_photo(call.from_user.id, pic, caption=send, reply_markup=save_not_keyboard, parse_mode="HTML")
        # высылаем анализ фразы со схемой зависимостей и клавиатурой для дальнейших действий
    else:  # если юзер хочет выйти в меню
        start(call)


# функция для выдачи рандомной фразы
def random_v(call):
    num = random.randrange(0, len(data))  # берём рандомное число
    jd[str(call.from_user.id)][0]["actuall_num"] = num
    with open("archieve/col.json", "w", encoding="UTF-8") as f:
        json.dump(jd, f, ensure_ascii=False)
        # обновляем переменную, чтобы потом можно было добавить фразу в коллекцию
    pic = open(pic_path / f'{num}.png', 'rb')
    send = f"{analize(num)}\n\nЕсли понравилась фраза, можешь сохранить👇"
    save_not_keyboard = types.InlineKeyboardMarkup()  # создание клавиатуры
    key_save = types.InlineKeyboardButton(text='📚Сохранить в коллекцию', callback_data=f"save")
    save_not_keyboard.add(key_save)
    key_new_random = types.InlineKeyboardButton(text='🎲Другая рандомная фраза', callback_data='random')
    save_not_keyboard.add(key_new_random)
    key_menue = types.InlineKeyboardButton(text='🔙Вернуться в меню', callback_data='menu')
    save_not_keyboard.add(key_menue)
    bot.send_photo(call.from_user.id, pic, caption=send, reply_markup=save_not_keyboard, parse_mode="HTML")
    # всё почти также, как в прошлой функции, но кнопки и запрос другие 


# маленькая функция для сбора поста с анализом фрвзы
def analize(n):
    phrase = data.iloc[n]['phrases']
    meaning = data.iloc[n]['meaning']
    analize = data.iloc[n]['analize']
    # находим нужное в основной базе и красиво склеиваем
    post = f"✨{phrase}✨\n\n{meaning}\n\n{analize}"
    return post


# функция для сохранения фразы в коллекцию
def save_key(call):
    tag_keyboard = types.InlineKeyboardMarkup()
    # создание клавиатуры для разных разделов коллекции
    key_tag1 = types.InlineKeyboardButton(text='Смешно', callback_data='funny')
    tag_keyboard.add(key_tag1)
    key_tag2 = types.InlineKeyboardButton(text='Интеллектуально', callback_data='intel')
    tag_keyboard.add(key_tag2)
    key_tag3 = types.InlineKeyboardButton(text='Глубоко', callback_data='deep')
    tag_keyboard.add(key_tag3)
    key_tag4 = types.InlineKeyboardButton(text='Другое', callback_data='other')
    tag_keyboard.add(key_tag4)
    bot.send_message(call.message.chat.id, text='Под каким тегом сохранить эту фразу?', reply_markup=tag_keyboard)

    # новый хэндлер для клавиатуры, потому что она поменьбше
    @bot.callback_query_handler(
        func=lambda call: call.data == "funny" or call.data == "intel" or call.data == "deep" or call.data == "other")
    def callback_worker_tag(call):
        user_id = str(call.message.chat.id)
        tag = call.data
        # добавляем индекс фразы из глобальной переменной в словарь под нужным тэгом и обновляем файл
        jd[user_id][1][f"{tag}"].append(jd[user_id][0]["actuall_num"])
        with open("archieve/col.json", "w", encoding="UTF-8") as f:
            json.dump(jd, f, ensure_ascii=False)
        # пишем юзеру, что всё хорошо, и посылаем его в меню
        bot.send_sticker(
            call.from_user.id, sticker="CAACAgIAAxkBAAELzFFmAu--0F2FCbSEiXJGVYGTbzG2iwACch4AAmsdEEp8_ME3dpS6ajQE")
        bot.send_message(call.message.chat.id, text='Сохранилось! Вот снова меню:')
        menu(call)


# функция просмотра коллекции
def collection(call):
    user_id = str(call.message.chat.id)
    col_sum = 0
    for vu in jd[user_id][1].values():
        col_sum += len(vu)
    if col_sum == 0:
        bot.send_sticker(
            call.from_user.id, sticker="CAACAgIAAxkBAAELzE9mAu98fdfopnlWjVgw8e9BxA__iQACoRoAAobmEUrZ3um6wkbPzjQE")
        bot.send_message(call.message.chat.id, text='Тут пока пусто! Сначала надо хоть что-то сохранить!')
        menu(call)
    # если коллекция пустая, то возвращаем юзера в меню
    else:
        col_dict = jd[user_id][1]
        mat = pic(col_dict, user_id)
        cap = f"Фраз у тебя в коллекции: {mat[1]}\nНа картинке указано, \
сколько в каждом разделе\n\nКакой раздел хочешь посмотреть? Или, может, все разом?"
        # приделываем клавиатуру с кнопками только для непустых разделов
        tag1_keyboard = types.InlineKeyboardMarkup()
        key_tag0 = types.InlineKeyboardButton(text='Все', callback_data='all')
        tag1_keyboard.add(key_tag0)
        if len(col_dict["funny"]) > 0:
            key_tag11 = types.InlineKeyboardButton(text='Смешно', callback_data='1_funny')
            tag1_keyboard.add(key_tag11)
        if len(col_dict["intel"]) > 0:
            key_tag21 = types.InlineKeyboardButton(text='Интеллектуально', callback_data='1_intel')
            tag1_keyboard.add(key_tag21)
        if len(col_dict["deep"]) > 0:
            key_tag31 = types.InlineKeyboardButton(text='Глубоко', callback_data='1_deep')
            tag1_keyboard.add(key_tag31)
        if len(col_dict["other"]) > 0:
            key_tag41 = types.InlineKeyboardButton(text='Другое', callback_data='1_other')
            tag1_keyboard.add(key_tag41)
        bot.send_photo(call.message.chat.id, mat[0], caption=cap, reply_markup=tag1_keyboard)
        

        # снова хэндлер поменьбше, поскольку клавиатура маааааленькая
        @bot.callback_query_handler(func=lambda
                call: call.data == "1_funny" or call.data == "1_intel" or
                      call.data == "1_deep" or call.data == "1_other" or call.data == "all")
        def callback_worker_col(call):
            user_id1 = str(call.message.chat.id)
            col_dict1 = jd[user_id1][1]
            # выдаём всю коллекцию по разделам
            if call.data == 'all':
                tags = []
                for ke, va in col_dict1.items():
                    if len(va) > 0:  # выдаём только непустые разделы
                        va.sort()
                        one_tag = f'{tags_dict[ke][1]}Раздел "{tags_dict[ke][0]}":'
                        # собираем один раздел в единую строчку и закидываем в список
                        # реферируемся к тому самому словарю в начале файла с русскими названиями и смайликами
                        for i in va:
                            for idx, row in data.iterrows():
                                if idx == i:
                                    one_tag += f"\n{idx}. {row['phrases']} — {row['meaning']}"
                        # реферируемся к общей базе, заданной в начале 
                        tags.append(one_tag)
                ans = "\n\n".join(tags)
                text = f'🍱ВСЯ КОЛЛЕКЦИЯ🍱\n\n{ans}\n\nНапиши номер выражения, разбор которого хочешь \
посмотреть\n\nМожешь отправить любое сообщение без цифр, чтобы выйти отсюда в меню'
                # собираем текст поста на отправку
            else:
                tagl = call.data.split("_")
                tag = tagl[1]
                jd[str(call.from_user.id)][0]["cur_tag"] = tag
                with open("archieve/col.json", "w", encoding="UTF-8") as f:
                    json.dump(jd, f, ensure_ascii=False)
                    # обновляем переменную, чтобы можно было вернуться в раздел
                capit_id = col_dict1[tag]
                capit_id.sort()
                pr = f'{tags_dict[tag][1]}Раздел: "{tags_dict[tag][0]}"'
                for i in capit_id:
                    for idx, row in data.iterrows():
                        if idx == i:
                            pr += f"\n{idx}. {row['phrases']} — {row['meaning']}"
                text = f'{pr}\n\nНапиши номер выражения, разбор которого хочешь посмотреть\n\nМожешь \
отправить любое сообщение без цифр, чтобы выйти отсюда в меню'
                # собираем текст поста на отправку
            bot.send_message(call.from_user.id, text=text)
            bot.register_next_step_handler(call.message, overlook)
            # отправляем собранный пост и ждём номер фразы, которую юзер хочет посмотреть


# функция для создания пай-чарта, также выдаёт сумму фраз в коллекции
def pic(col_dict, user_id):
        taglen = []
        tags_list = []
        # готовим материал для картинки со статистикой:
        for k, v in col_dict.items():
            a = len(set(v))
            if  a > 0: # если в разделе что-то есть (иначе нулевые теги будут накладываться)
                b = tags_dict[k][0] + f": {a}"
                taglen.append(a)
                tags_list.append(b)
        # делаем и сохраняем картинку:
        plt.pie(x=taglen, labels=tags_list, colors=['goldenrod', 'gold', 'peru', 'white'],
                wedgeprops={'linewidth': 6.0, 'edgecolor': 'khaki'})
        my_circle = plt.Circle((0, 0), 0.7, color='khaki')
        plt.gcf().gca().add_artist(my_circle)
        plt.savefig(f'archieve/{user_id}_col.png')
        plt.clf() # если не удалить существующую картинку, то новая наложится на старую
        chart = open(f'archieve/{user_id}_col.png', 'rb')
        return chart, sum(taglen)


# функция просмотра фразы из коллекции
def overlook(call):
    if str(call.text).isdigit() is True:
        numer = int(call.text) 
        jd[str(call.from_user.id)][0]["actuall_num"] = numer
        with open("archieve/col.json", "w", encoding="UTF-8") as f:
            json.dump(jd, f, ensure_ascii=False)
            # обновляем переменную, чтобы можно было удалить фразу из коллекции
        pic = open(pic_path / f'{numer}.png', 'rb')
        send = f"{analize(numer)}\n\nЕсли разонравилась фраза, можешь удалить👇"
        # собираем текст поста с анализом и картинкой на отправку
        small_keyboard = types.InlineKeyboardMarkup()  # создание клавиатуры
        if jd[str(call.from_user.id)][0]["cur_tag"] != "":
            # если юзер случайно набрал номер фразы, которой нет в коллекции, то мы не показываем кнопки
            # "удалить" и "вернуться к разделу"
            key_del = types.InlineKeyboardButton(text='Удалить из раздела', callback_data="del")
            small_keyboard.add(key_del)
            key_back_1 = types.InlineKeyboardButton(text='🔙Вернуться к разделу', callback_data='back_1')
            small_keyboard.add(key_back_1)
        key_back_2 = types.InlineKeyboardButton(text='🔙Вернуться в коллекцию', callback_data="back_2")
        small_keyboard.add(key_back_2)
        key_menue = types.InlineKeyboardButton(text='🔙🔙Вернуться в меню', callback_data='menu')
        small_keyboard.add(key_menue)
        bot.send_photo(call.from_user.id, pic, caption=send, reply_markup=small_keyboard, parse_mode="HTML")
    else:
        a = str(call.text)
        a.lower()
        start(call)

    # обрабатываем запросы с маленькой клавиатуры
    @bot.callback_query_handler(
            func=lambda call: call.data == "del" or call.data == "back_1" or call.data == "back_2")
    def callback_worker_incoll(call):
        user_id = str(call.message.chat.id)
        user_tags_dict = jd[user_id][1]
        if call.data == "del":
            for k, v in user_tags_dict.items():
                for i in v:
                    if i == jd[str(call.from_user.id)][0]["actuall_num"] and k == jd[str(call.from_user.id)][0]["cur_tag"]:
                        # если нам нужно что-то удалить, мы это удаляем из правильного раздела,
                        # потому что юзер может сохранять одну фразу в разные разделы
                        v.remove(i)
                        user_tags_dict[k] = v
                        jd[user_id][1] = user_tags_dict
                        with open("archieve/col.json", "w", encoding="UTF-8") as f:
                            json.dump(jd, f, ensure_ascii=False)
                        bot.send_sticker(call.from_user.id, 
                                sticker="CAACAgIAAxkBAAELzE1mAu5wR453Q3jkpiay1cWwGioGxwACWhoAAtewWEoVSEt7yUPEQTQE")
                        text = f'Удалено!'
                        # когда удалили индекс фразы из коллекции, снова выдаём меню
                        bot.send_message(call.from_user.id, text=text)
                        smaller_keyboard = types.InlineKeyboardMarkup()
                        key_back_1 = types.InlineKeyboardButton(text='🔙Вернуться к разделу', callback_data='back_1')
                        smaller_keyboard.add(key_back_1)  # если мы что-то удалили, то раздел точно был
                        key_back_2 = types.InlineKeyboardButton(text='🔙Вернуться в коллекцию', callback_data="back_2")
                        smaller_keyboard.add(key_back_2)
                        key_menue = types.InlineKeyboardButton(text='🔙🔙Вернуться в меню', callback_data='menu')
                        smaller_keyboard.add(key_menue)
                        bot.send_message(call.from_user.id, text=text, reply_markup=smaller_keyboard)
        if call.data == "back_1":
            # если возвращаемся в раздел, то реферируем к глобальной переменной
            # и дублируем ф-цию выдачи раздела, но без заданного call
            tag = jd[str(call.from_user.id)][0]["cur_tag"]
            capit_id = user_tags_dict[tag]
            capit_id.sort()
            pr = f'{tags_dict[tag][1]}Раздел: "{tags_dict[tag][0]}"'
            for i in capit_id:
                for idx, row in data.iterrows():
                    if idx == i:
                        pr += f"\n{idx}. {row['phrases']} — {row['meaning']}"
            text = f'{pr}\n\nНапиши номер выражения, разбор которого хочешь посмотреть\n\nМожешь \
отправить любое сообщение без цифр, чтобы выйти отсюда в меню'
            bot.send_message(call.from_user.id, text=text)
            bot.register_next_step_handler(call.message, overlook)
        if call.data == "back_2":
            collection(call)


# главный хэндлер всея бота, он обрабатывает все запросы основного меню и те, что с ними совпадают
@bot.callback_query_handler(func=lambda call: call.data == 'menu' or call.data == "search"
                                or call.data == "random" or call.data == "collection" or call.data == "save")
def callback_worker(call):
    if call.data == 'menu':
        menu(call)
    elif call.data == "search":  # call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Введи слово/слова, которые ищешь.\
\n\nПожалуйста, не ищи по служебным словам, иначе поиск ничего не даст!\n\n\
Если передумал искать, то перед вызовом \menu отправь сообщение non')
        bot.register_next_step_handler(call.message, search)
        # Вот так по кнопке можно запустить функцию,
    elif call.data == "random":
        random_v(call)
    elif call.data == "collection":
        collection(call)
    elif call.data == "save":
        save_key(call)


bot.infinity_polling(none_stop=True, interval=0)
# без этой штуки бот не реагирует на сообщения
