from json import dumps, loads
import requests
from parse import search_country, search_image


class BotHandler:

    def __init__(self, token, url, proxy):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(self.token)
        self.url = url
        self.array_of_countries = search_country(self.url)
        self.array_of_phones = {}
        self.country = None
        self.phone = None
        self.r = requests.Session()
        self.r.proxies = proxy

    def get_updates(self, new_offset):
        method = 'getUpdates'
        params = {'offset': new_offset}
        resp = self.r.get(self.api_url + method, data=params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text, reply_markup=None):
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup}
        method = 'sendMessage'
        self.r.post(self.api_url + method, params)  # Сервер возвращает ответ на запрос

    def send_document(self, user, phone):
        img = search_image(self.url + self.array_of_phones[phone][0])
        params = {"chat_id": user['message']['chat']['id'], "document": self.url + img}
        method = 'sendDocument'
        self.r.post(self.api_url + method, params)  # Сервер возвращает ответ на запрос
        return params

    def get_start(self, message):
        self.send_message(message['chat']['id'], 'Привет')
        self.array_of_countries = search_country(self.url)
        keyboard = dumps({"inline_keyboard":
                              [[{'text': "{}:\t{}".format(i, self.array_of_countries[i][1]), 'callback_data': i}]
                               for i in self.array_of_countries.keys()]})
        self.send_message(message['chat']['id'],
                          'Данный бот выполняет функцию "Receive Free SMS"\n'
                          'Выберите страну, номер которой вы хотите использовать.\n'
                          'Через двоеточие указано количество доступных номеров.',
                          reply_markup=keyboard)

    def get_reload(self, message, path_file):
        with open(path_file) as file:
            r = file.read().split('\n')
            r.reverse()
            for i in r:
                if 'jpg' in i:
                    self.r.post(self.api_url + 'sendDocument',
                                {'chat_id': message['chat']['id'], 'document': loads(i)['document']})
                    break

    def get_callback_query(self, message):
        keyboard = dumps(
            {"inline_keyboard": [[{'text': '{} - {}'.format(i, self.array_of_phones[i][1]), 'callback_data': i}]
                                 for i in self.array_of_phones.keys()]})
        self.send_message(message['message']['chat']['id'],
                          'Выберите удобный номер телефона - количество сообщений', reply_markup=keyboard)

    def get_none(self, message):
        self.send_message(message['chat']['id'], 'Пожалуйста нажмите /start')
