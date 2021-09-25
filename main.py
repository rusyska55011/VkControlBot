from root import Window
import webbrowser


class ButtonActions:
    @staticmethod
    def _open_browser(url):
        webbrowser.open(url)


class Authorization(Window, ButtonActions):
    is_authorized = False
    elements = {
        'Label': [
            dict(font=("Lucida Grande", 26), text='Авторизация через токен', position=[70, 50]),
            dict(font=("Lucida Grande", 12), text='Введите токен:', position=[222, 165]),
        ],
        'Button': [
            dict(font=("Lucida Grande", 12), text='Подключиться', position=[220, 250]),
            dict(font=("Lucida Grande", 9), text='Как получить токен', position=[10, 363]),
        ],
        'Text': [
            dict(font=("Lucida Grande", 12), height=2, width=50, position=[50, 200])
        ],
    }

    def __init__(self):
        super(Authorization, self).__init__([554, 400], 'Авторизация', self.elements)

    def get_response(self):
        return self.is_authorized


class Start:
    def __init__(self):
        auth = Authorization()
        auth.draw_elements()
        auth.start()
        a = auth.get_elements()[0][0]


Start()

