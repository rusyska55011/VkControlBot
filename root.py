import sqlite3
import os
from tkinter import *

from time import sleep
from random import randint
from threading import Thread

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
                raise sqlite3.IntegrityError(f'Добавление {arg} невозможно. Элемент с данным ID уже существует')

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
    chat_bot_work = True

    def __init__(self, access_token):
        self.access_token = access_token

        self.vk = vk_api.VkApi(token=access_token)
        self.base = VkBase()

    def get_profile_info(self) -> dict:
        return self.vk.method('account.getProfileInfo')

    def get_vk_name(self, vk_id: int) -> str:
        user_get = self.vk.method('users.get', {
            'user_id': vk_id
        })[0]
        return user_get['first_name'] + ' ' + user_get['last_name']

    def get_friends_list(self) -> list:
        friends = self.vk.method('friends.get')
        return friends['items']

    def get_token_valid(self) -> bool:
        # Отправляем любой запрос
        try:
            self.get_friends_list()
        except vk_api.exceptions.ApiError:
            return False
        else:
            return True

    def start_longpoll(self, bot_asks: dict):
        new_dict = dict()
        for key, item in bot_asks.items():
            new_dict[str(key).capitalize()] = item
        bot_asks = new_dict

        longpoll = VkLongPoll(self.vk)
        for event in longpoll.listen():
            if not self.chat_bot_work:
                break
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

    def send_friend_add_request(self, message: str, *vk_id: int):
        message = self._find_vars_in_text(message, vars={'vk_id': vk_id, 'name': self.get_vk_name(vk_id)})
        if message == 'Error':
            return 'Error'
        for user_id in vk_id:
            try:
                self.vk.method('friends.add', {
                    'user_id': int(user_id),
                    'text': message
                })
            except:
                pass
            sleep(1.5)


class Window:
    h1 = dict(font=("Lucida Grande", 26), bg='#fafafa', padx=30)
    h2, h2['font'] = h1.copy(), ("Lucida Grande", 18)
    h3 = dict(font=("Lucida Grande", 13))

    entry_style = dict(font=("Lucida Grande", 12))

    button_style = dict(font=("Lucida Grande", 10), pady=5, padx=5)
    button_style_big, button_style_big['font'] = button_style.copy(), dict(font=("Lucida Grande", 16))
    start_button_style, start_button_style['font'] = button_style.copy(), ("Lucida Grande", 15)

    def __init__(self, title: str, size: list):
        self.root = Tk()

        self.root.wm_title(title)
        self.root.geometry('x'.join(map(lambda item: str(item), size)))
        self.root.minsize(*size)
        self.root.maxsize(*size)
        self.elements()

    def start(self):
        self.root.mainloop()

    def quit(self):
        self.root.destroy()

    def elements(self):
        pass


class File:
    def __init__(self, folder_path: str = '.\\'):
        self.folder_path = folder_path
        if self.folder_path[-1] != '\\':
            self.folder_path += '\\'

    def __setitem__(self, key, value):
        self.rewriting(key, *value)

    def __getitem__(self, path_from_folder) -> tuple:
        return self.read(path_from_folder)

    def append(self, path_from_folder: str, *args: str):
        with open(self.folder_path + path_from_folder, 'a') as file:
            self.__write_data(file, *args)

    def rewriting(self, path_from_folder: str, *args: str):
        with open(self.folder_path + path_from_folder, 'w') as file:
            self.__write_data(file, *args)

    def create_dirs(self, path_from_folder: str):
        if path_from_folder[-1] == '\\':
            path_from_folder = path_from_folder[:-1]
        try:
            os.makedirs(self.folder_path + path_from_folder)
        except FileExistsError:
            pass

    def read(self, path_from_folder: str) -> tuple:
        with open(self.folder_path + path_from_folder, 'r') as file:
            return self.__delete_n(*file.readlines())

    @staticmethod
    def __write_data(file: open, *args: str):
        for arg in args:
            if isinstance(arg, (list, tuple, set, frozenset)):
                line = str([*arg])
            else:
                line = str(arg)
            try:
                file.write(line + '\n')
            except UnicodeEncodeError:
                pass

    @staticmethod
    def __delete_n(*args: str) -> tuple:
        data = list()
        for arg in args:
            if arg == '\n':
                arg = ''
            elif arg[-1] == '\n':
                arg = arg[:-1]
            data.append(arg)
        return tuple(data)


class AddUsersChecker:
    work = True

    def __init__(self, vk_bot, message_for_added_users: str, friends_list: list):
        self.message_for_added_users = message_for_added_users
        self.friends_list = friends_list
        self.vk_bot = vk_bot

    def start(self):
        userschecker_thread = Thread(target=self.__process)
        userschecker_thread.start()

    def __process(self):
        while True:
            if not self.work:
                break

            get_friends = self.vk_bot.get_friends_list()
            check = self.check_friends(self.friends_list, get_friends)

            if check:
                print('Обнаружены новые друзья! ID:', check)
                for vk_id in check:
                    self.vk_bot.send_message(vk_id, self.message_for_added_users)
                # Чтобы бот забывал друзей, которые удались из списка друзей,
                # можно передвинуть переменную за блок if
            self.friends_list = get_friends.copy()

            sleep(randint(5, 15))

    @staticmethod
    def check_friends(actual_friends_list: list, new_friends_list: list) -> list:
        if actual_friends_list != new_friends_list:
            new_friends = [item for item in new_friends_list if item not in actual_friends_list]
            return new_friends
        else:
            return list()
