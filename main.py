from root import Window, VkBot, VkBase, Window1
import webbrowser
from tkinter import Tk, Label, Button, Listbox, Entry, Checkbutton, IntVar, END


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


class DbView(Window1,ButtonActions):
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


class Console(Window, ButtonActions):
    is_authorized = False
    message = str()

    def __init__(self, token):
        self.token = token
        self.vk = VkBot(self.token)

        if self.vk.get_token_valid():
            self.is_authorized = True

            user_info = self.vk.get_profile_info()
            self.elements = {
                'Label': [
                    dict(font=("Lucida Grande", 26), text='Консоль управления ботом', bg='#fff', position=[50, 10]),
                    dict(font=("Lucida Grande", 16), text=f'Приветсвую, {user_info["first_name"]}!', bg='#fff', position=[50, 55])
                ],
                'Button': [
                    dict(font=("Lucida Grande", 12), text='Посмотреть базу данных пользователей', position=[50, 100], command=lambda: DbView().start()),
                    dict(font=("Lucida Grande", 12), text='Редактировать базу данных', position=[50, 140]),
                    dict(font=("Lucida Grande", 12), text='Запушить сообщения', position=[50, 200]),
                ]
            }
        else:
            self.message = 'Введенный токен некорректен'
            self.elements = dict()

        if self.is_authorized:
            super(Console, self).__init__([554, 250], 'Консоль VkApi', self.elements)

    def get_response(self) -> dict:
        message = self.message
        self.message = str()
        return {
            'status': self.is_authorized,
            'message': message
        }


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
                console.draw_elements()
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

