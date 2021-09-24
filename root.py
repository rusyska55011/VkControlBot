import sqlite3

from time import sleep
from random import randint

import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType


class DataBase:
    db_name = 'ClientBase.db'

    def __init__(self, table_name, cols, key_col_name):
        self.table_name = table_name
        self.cols = cols
        self.cols_names = self.__get_cols_names(self.cols)
        self.key = key_col_name

        self.db = sqlite3.connect(self.db_name)
        self.create_table()

    @staticmethod
    def __get_cols_names(cols) -> str:
        cols_list = cols.split(',')
        cols_names_list = [item.split()[0] for item in cols_list]
        return ', '.join(cols_names_list)

    def connect(func):
        def wrapper(self, *args, **kwargs):
            cursor = self.db.cursor()
            returned = func(self, cursor, *args, **kwargs)
            self.db.commit()
            return returned
        return wrapper

    @connect
    def create_table(self, cursor):
        def __do_key(cols, key_col_name) -> str:
            querys = list()
            for item in cols.split(','):
                if key_col_name in item:
                    item += ' PRIMARY KEY'
                querys.append(item.strip())
            return ', '.join(querys)

        cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} ({__do_key(self.cols, self.key)})')

    @connect
    def add(self, cursor, *args: list):
        for arg in args:
            arg = tuple(map(lambda item: str(item), arg))
            arg = '"' + '", "'.join(arg) + '"'
            try:
                cursor.execute(f'INSERT INTO {self.table_name} ({self.cols_names}) VALUES ({arg});')
            except sqlite3.IntegrityError:
                print(f'Добавление {arg} невозможно. Элемент с данным ID уже существует')

    @connect
    def delete(self, cursor, *args: int):
        for arg in args:
            cursor.execute(f'DELETE FROM {self.table_name} WHERE {self.key} = {str(arg)}')

    @connect
    def read(self, cursor) -> list:
        return cursor.execute(f'SELECT * FROM {self.table_name}').fetchall()

    def get_col_names(self) -> str:
        return self.cols

    def open_db(self):
        self.db = sqlite3.connect(self.db_name)

    def close_db(self):
        self.db.close()


class VkBase(DataBase):
    def __init__(self):
        super().__init__(table_name='vk', cols='vk_id INT, name TEXT', key_col_name='vk_id')


class Bot:
    @staticmethod
    def _find_vars_in_text(text: str, vars: dict) -> str:
        """ Переменная считывается если она обернута в знак +переменная+ """

        plus_amount = len([letter for letter in text if letter == '+'])
        if plus_amount % 2:
            print(f'Число знаков "+" равно {plus_amount}. Оно должно быть как минимум четным.\nПроверь правильность написания')
            return 'Error'

        splited = text.split('+')
        for item_num in range(1, len(splited), 2):
            var = splited[item_num]
            try:
                splited[item_num] = str(vars[var])
            except KeyError:
                print(f'Значения "+{var}+" не существует')
                return 'Error'
        return ''.join(splited)


class VkBot(Bot):
    def __init__(self, access_token):
        self.access_token = access_token

        self.vk = vk_api.VkApi(token=access_token)
        self.base = VkBase()

    def get_vk_name(self, vk_id: int) -> str:
        user_get = self.vk.method('users.get', {
            'user_id': vk_id
        })[0]
        return user_get['first_name'] + ' ' + user_get['last_name']

    def get_friends_list(self) -> list:
        friends = self.vk.method('friends.get')
        return friends['items']

    def start_longpoll(self, bot_asks):
        longpoll = VkLongPoll(self.vk)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.from_user:
                    message_from = str(event.text).capitalize()
                    try:
                        message = bot_asks[message_from]
                    except KeyError:
                        continue
                    else:
                        self.send_message(event.user_id, message)

    def send_message(self, vk_id: int, message: str):
        message = self._find_vars_in_text(message, vars={'vk_id': vk_id, 'name': self.get_vk_name(vk_id)})
        if message == 'Error':
            return 'Error'
        self.vk.method('messages.send', {
            'user_id': vk_id,
            'message': message,
            'random_id': get_random_id()
        })

    def push_messages(self, message: str):
        base_items = self.base.read()
        for vk_id, name in base_items:
            answer = self.send_message(vk_id, message)
            if answer == 'Error':
                print('Рассылка остановлена из-за ошибки.')
                break
            sleep(randint(1, 5))
        else:
            print('Рассылка успешно завершена!')

    def add_by_id(self, vk_id: int):
        name = self.get_vk_name(vk_id)
        self.base.add([vk_id, name])