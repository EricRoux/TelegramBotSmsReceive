from json import dumps
from os import path
from settings import url, proxy, token, offset
from tbot import BotHandler
from parse import search_phone


def message_processing(message, bot, new_offset):
    path_file = exists_file(message, new_offset)
    if message['text'] == '/start':
        bot.get_start(message)
    elif message['text'] == '/reload':
        bot.get_reload(message, path_file)
    else:
        bot.get_none(message)


def callback_processing(data, bot, new_offset):
    path_file = exists_file(data, new_offset)
    send_message = lambda x: bot.send_message(data['message']['chat']['id'], x)
    if data['data'] in bot.array_of_countries.keys():
        bot.country = data['data']
        bot.array_of_phones = search_phone(url + bot.array_of_countries[bot.country][0])
        bot.get_callback_query(data)
    elif data['data'] in bot.array_of_phones.keys():
        bot.phone = data['data']
        send_message("Страна {}\t Телефон {}".format(bot.country, bot.phone))
        send_message(bot.phone)
        result = bot.send_document(data, bot.phone)
        with open(path_file, 'a') as w:
            w.write(dumps(result) + '\n')
    else:
        send_message('Время вышло :(\nВыбирите /start')


def exists_file(message, new_offset):
    file_name = '_'.join(str(message['from'][i]) for i in ['first_name', 'last_name', 'id'])
    path_file = './messages/' + file_name + '.logs'
    if not path.exists(path_file):
        open(path_file, 'w').close()
    if not str(message) in open(path_file).read():
        with open(path_file, 'a') as file:
            file.write(dumps(message) + '\n')
    if offset < new_offset + 1: change_offset(new_offset)
    return path_file


def change_offset(new_offset):
    with open('settings.py', 'w') as w:
        w.write('url="{}"\n'.format(url))
        w.write('proxy={}\n'.format(proxy))
        w.write('token="{}"\n'.format(token))
        w.write('offset={}\n'.format(new_offset + 1))


if __name__ == '__main__':
    bot = BotHandler(token, url, proxy)
    new_offset = offset
    while True:
        update = bot.get_updates(new_offset)
        if len(update) > 0: new_offset = update[-1]['update_id'] + 1
        for i in update:
            if 'message' in i.keys():
                message_processing(i['message'], bot, new_offset)
            elif 'callback_query' in i.keys():
                callback_processing(i['callback_query'], bot, new_offset)
