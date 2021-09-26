from root import Window, VkBot
import webbrowser


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
                dict(font=("Lucida Grande", 26), text='Как получить токен?', position=[10, 30]),
            ] + self.generate_paragraphs(self.instruction_text, [10, 80], 25, dict(font=("Lucida Grande", 12)), True),
            'Button': [
                dict(font=("Lucida Grande", 12), text='Перейти на страницу получения токена', command=lambda: self._open_browser(self.link),
                     position=[10, 240]),
            ],
        }
        super(Instruction, self).__init__([554, 400], 'Иструкция', self.elements)


class Console(Window, ButtonActions):
    is_authorized = False
    message = str()

    def __init__(self, token):
        self.token = token
        self.vk = VkBot(self.token)

        if self.vk.get_token_valid():
            self.is_authorized = True
        else:
            self.message = 'Введенный токен некорректен'

        self.elements = {
        }
        if self.is_authorized:
            super(Console, self).__init__([554, 400], 'Консоль VkApi', self.elements)

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
                dict(font=("Lucida Grande", 26), text='Авторизация через токен', position=[70, 50]),
                dict(font=("Lucida Grande", 12), text='Введите токен:', position=[222, 165]),
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

    def __open_console(self, text_position: int):
        token = self.get_elements()['Entry'][int(text_position)].get()
        if not token:
            raise ValueError('Вы не ввели токен!')
        console = Console(token=token)
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

