import webbrowser
import sqlite3
from root import Window, VkBot, VkBase, Window1, File, AddUsersChecker
from tkinter import Tk, Label, Button, Listbox, Entry, Checkbutton, Radiobutton, IntVar, END


class ButtonActions:
    @staticmethod
    def _open_browser(url):
        webbrowser.open(url)


class Instruction(Window, ButtonActions):
    link = 'https://oauth.vk.com/authorize?client_id=2685278&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1'
    instruction_text = [
        'Нажать на кнопку ниже и перейти на страницу', 'Авторезироваться через свой аккаунт',
        'Дать доступ', 'После получения доступа обратите внимание на адресную строку',
        'Токен находится в ссылке начиная от access_token= до &expires_in', 'Скопируйте токен'
    ]

    def __init__(self):
        self.elements = {
            'Label': [
                dict(font=("Lucida Grande", 26), text='Как получить токен?', bg='#fff', position=[10, 30]),
            ] + self.generate_paragraphs(self.instruction_text, [10, 80], 25, dict(font=("Lucida Grande", 12)), True),
            'Button': [
                dict(font=("Lucida Grande", 12), text='Перейти на страницу получения токена', command=lambda: self._open_browser(self.link),
                     position=[10, 240]),
            ],
        }
        super(Instruction, self).__init__([554, 400], 'Инструкция', self.elements)


class DbView(Window1, ButtonActions):
    def __init__(self):
        vk_base = VkBase()
        self.cols = vk_base.get_col_names().split(',')
        self.data = vk_base.read()

        super(DbView, self).__init__('Просмотр Базы Данных', [554, 400])

        self.__append_listbox()

    def start(self):
        self.root.mainloop()

    def __append_listbox(self):
        for item in self.data:
            total = str()
            for i in range(len(item)):
                total += f'{self.cols[i]} : {item[i]}'
                if i != len(item) - 1:
                    total += ' | '

            self.listbox.insert(END, str(total))

    def elements(self):
        #Labels
        self.label = Label(self.root, text='Просмотр базы данных', **self.h1)
        self.label.place(x=55, y=10)

        # ListBoxes
        self.listbox = Listbox(self.root, width=48, height=13, font=("Lucida Grande", 15))
        self.listbox.place(x=10, y=70)


class DbChange(Window1, ButtonActions):
    def __init__(self, vk: VkBot):
        self.vk = vk
        self.VkBase = VkBase()
        super(DbChange, self).__init__('Реактирование Базы Данных', [554, 400])

    def elements(self):
        #Labels
        self.label = Label(self.root, text='Редактирование базы данных', **self.h1)
        self.label.place(x=8, y=10)

        self.label2 = Label(self.root, text='Введите ID', **self.h3)
        self.label2.place(x=230, y=120)

        self.event_label = Label(self.root, text='', fg='#f00', **self.h3)
        self.event_label.place(x=10, y=360)

        #Buttons
        self.button_add = Button(self.root, text='Добавить', command=lambda: self.__append_base(self.entry.get()), **self.button_style_big)
        self.button_add.place(x=180, y=180)

        self.button_delete = Button(self.root, text='Удалить', command=lambda: self.__delete_base(self.entry.get()), **self.button_style_big)
        self.button_delete.place(x=280, y=180)

        #Entries
        self.entry = Entry(self.root, width=45, **self.entry_style)
        self.entry.place(x=70, y=150)

    def __check_mistakes(self, args: str) -> bool:
        if not args:
            self.event_label['text'] = 'Введите значение!'
            return False
        else:
            values = args.split(',')
            try:
                for item in values:
                    int(item)
            except ValueError:
                self.event_label['text'] = 'Ввести можно только числа!'
                return False
        return True

    def __append_base(self, args: str):
        if self.__check_mistakes(args):
            values = args.split(',')
            mistakes = list()
            for item in values:
                try:
                    self.vk.add_by_id(int(item))
                except sqlite3.IntegrityError:
                    mistakes.append(item)
            if mistakes:
                self.event_label['text'] = f'Записи с ID {",".join(mistakes)} уже существует!'

    def __delete_base(self, args):
        if self.__check_mistakes(args):
            values = args.split(',')
            self.VkBase.delete(*values)
            self.event_label['text'] = f'Записи с ID {",".join(values)} успешно удалены!'


class MessagePush(Window1, ButtonActions):
    def __init__(self, vk: VkBot):
        self.vk = vk
        self.VkBase = VkBase()
        super(MessagePush, self).__init__('Запушить сообщения', [554, 400])

    def elements(self):
        # Labels
        self.label = Label(self.root, text='Пуш сообщений в ЛС', **self.h1)
        self.label.place(x=66, y=10)

        self.label2 = Label(self.root, text='Введите текст сообщения', **self.h3)
        self.label2.place(x=170, y=120)

        self.event_label = Label(self.root, text='', fg='#f00', **self.h3)
        self.event_label.place(x=10, y=360)

        # Entries
        self.entry = Entry(self.root, width=45, **self.entry_style)
        self.entry.place(x=70, y=150)

        # Buttons
        self.button = Button(self.root, text='Запушить', **self.button_style_big, command=lambda: self.__message_push(self.entry.get()))
        self.button.place(x=225, y=180)

    def __message_push(self, message: str) -> str:
        self.event_label['text'] = 'Идет процесс пуша. Не выключайте программу'
        try:
            self.vk.push_messages(message)
        except:
            self.event_label['text'] = 'Процесс приостановлен из-за ошибки'
        else:
            self.event_label['text'] = 'Успешно!'


class AuthAddSettings(Window1, ButtonActions):
    def __init__(self):
        self.file = File()
        super(AuthAddSettings, self).__init__('Настройка автодобавления в друзья', [554, 350])
        self.entry.insert(0, self.file['config'][0])

    def elements(self):
        # Labels
        self.label1 = Label(self.root, text='Настройка автодобавления', **self.h1)
        self.label1.place(x=50, y=10)

        self.label2 = Label(self.root, text='Введите текст сообщения при добавлении', **self.h3)
        self.label2.place(x=108, y=120)

        # Entries
        self.entry = Entry(self.root, width=45, **self.entry_style)
        self.entry.place(x=70, y=150)

        # Buttons
        self.button = Button(self.root, text='Сохранить', command=lambda: self.__save_config(self.entry.get()), **self.button_style_big)
        self.button.place(x=225, y=180)

    def __save_config(self, value):
        self.file['config'] = (value, )


class Console(Window1, ButtonActions):
    is_authorized = False
    message = str()

    def __init__(self, token):
        self.token = token
        self.vk = VkBot(self.token)

        if self.vk.get_token_valid():
            self.is_authorized = True
            self.user_info = self.vk.get_profile_info()
            if self.is_authorized:
                super(Console, self).__init__('Консоль VkApi', [554, 350])
                self.elements()
        else:
            self.message = 'Введенный токен некорректен'

    def elements(self):
        # Labels
        self.label1 = Label(self.root, text='Консоль управления ботом', **self.h1)
        self.label1.place(x=50, y=10)

        self.label2 = Label(self.root, text=f'Приветсвую, {self.user_info["first_name"]}!', **self.h2)
        self.label2.place(x=50, y=55)

        self.label3 = Label(self.root, text=f'Автодобавление:', **self.h3)
        self.label3.place(x=50, y=265)

        self.label4 = Label(self.root, text=f'выключено', fg='red', **self.h3)
        self.label4.place(x=185, y=265)

        # Buttons
        self.button1 = Button(self.root, font=("Lucida Grande", 12), text='Посмотреть базу данных пользователей', command=lambda: DbView().start())
        self.button1.place(x=50, y=100)

        self.button2 = Button(self.root, font=("Lucida Grande", 12), text='Редактировать базу данных', command=lambda: DbChange(self.vk).start())
        self.button2.place(x=50, y=140)

        self.button3 = Button(self.root, font=("Lucida Grande", 12), text='Запушить сообщения', command=lambda: MessagePush(self.vk).start())
        self.button3.place(x=50, y=210)

        self.button4 = Button(self.root, font=("Lucida Grande", 8), text='Настроить', command=lambda: AuthAddSettings().start())
        self.button4.place(x=145, y=295)

        self.button5 = Button(self.root, text='Включить', command=lambda: self.__add_friend_checker(), **self.h3)
        self.button5.place(x=50, y=290)

    def get_response(self) -> dict:
        message = self.message
        self.message = str()
        return {
            'status': self.is_authorized,
            'message': message
        }

    def __add_friend_checker(self):
        self.label4['text'] = '  включено'
        file = File()
        message = file['config'][0]
        self.user_checker = AddUsersChecker(self.vk, message, self.vk.get_friends_list()).start()


class Authorization(Window, ButtonActions):
    token = None

    def __init__(self):
        self.elements = {
            'Label': [
                dict(font=("Lucida Grande", 26), text='Авторизация через токен', bg='#fff', position=[70, 50]),
                dict(font=("Lucida Grande", 12), text='Введите токен:', position=[222, 165]),
                dict(font=("Lucida Grande", 12), fg='#F00', position=[200, 300])
            ],
            'Button': [
                dict(font=("Lucida Grande", 12), text='Подключиться',
                     command=lambda: self.__open_console(0), position=[220, 250]),
                dict(font=("Lucida Grande", 9), text='Как получить токен',
                     command=lambda: self.__open_instruction(), position=[10, 363]),
            ],
            'Entry': [
                dict(font=("Lucida Grande", 12), width=50, position=[50, 200])
            ],
        }
        super(Authorization, self).__init__([554, 400], 'Авторизация', self.elements)

    def __open_console(self, text_position: int) -> dict:
        token = self.get_entry_text(self.get_elements()['Entry'][int(text_position)])
        if not token:
            self.change_element('Label', 2, dict(text='Вы не ввели значение!', position=[200, 300]))
            self.draw_elements()
        else:
            console = Console(token=token)
            response, message = console.get_response().values()
            if not response:
                self.change_element('Label', 2, dict(text=message, position=[180, 300]))
                self.draw_elements()
            else:
                self.quit()

    @staticmethod
    def __open_instruction():
        Instruction().draw_elements()


class Start:
    def __init__(self):
        auth = Authorization()
        auth.draw_elements()
        auth.start()


Start()
