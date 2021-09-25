from root import Window
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


class Authorization(Window, ButtonActions):
    is_authorized = False

    def __init__(self):
        self.elements = {
            'Label': [
                dict(font=("Lucida Grande", 26), text='Авторизация через токен', position=[70, 50]),
                dict(font=("Lucida Grande", 12), text='Введите токен:', position=[222, 165]),
            ],
            'Button': [
                dict(font=("Lucida Grande", 12), text='Подключиться', position=[220, 250]),
                dict(font=("Lucida Grande", 9), text='Как получить токен',
                     command=lambda: Instruction().draw_elements(), position=[10, 363]),
            ],
            'Text': [
                dict(font=("Lucida Grande", 12), height=2, width=50, position=[50, 200])
            ],
        }
        super(Authorization, self).__init__([554, 400], 'Авторизация', self.elements)

    def get_response(self):
        return self.is_authorized


class Start:
    def __init__(self):
        auth = Authorization()
        auth.draw_elements()
        auth.start()


Start()

