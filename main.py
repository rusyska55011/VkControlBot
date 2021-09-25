import root


class Authorization(root.Window):
    is_authorized = False
    elements = {
        'Label': [
            dict(font=("Lucida Grande", 12), text='Введите бюджет', position=[10, 10]),
            dict(font=("Lucida Grande", 12), text='1111', position=[60, 100]),
        ],
        'Button': [
            dict(font=("Lucida Grande", 12), text='Введите бюджет', position=[10, 200]),
            dict(font=("Lucida Grande", 12), text='Отправить', position=[10, 300]),
        ]
    }

    def __init__(self):
        super(Authorization, self).__init__([554, 400], 'Авторизация', self.elements)

    def get_response(self):
        return self.is_authorized


class Start:
    def __init__(self):
        print(Authorization().get_elements())


Start()

