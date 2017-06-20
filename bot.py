#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import vk_requests
import time
import datetime
import requests
import socket
import os
import importlib
import json
from vk import vk
from rate import rate_limited


class vk_msg:
    def __init__(self, msg_id, msg_type, msg_date,from_id, msg_text, peer_id):
        self.id = msg_id
        self.type = msg_type
        self.date = msg_date
        self.from_id = from_id
        self.text = msg_text
        self.peer_id = peer_id

    def get_all(self):
        return self.id, self.type, self.date, self.from_id, self.text, self.peer_id


class vk_bot:
    def __init__(self):
        # добавить парсинг из конфига
        self.vk = vk()
        self.vk.init_vk()

        self.key = ''
        self.server = ''
        self.ts = 0
        self.pts = 0

        self.commands = []
        self.commands_classes = []

    def import_commands(self):
        # files = os.listdir("commands")
        # modules = filter(lambda x: x.endswith('.py'), files)
        # надо присрать сюда каким-то образом автоматический импорт
        from commands.victorina import victorina
        v = victorina()
        self.commands_classes.append(v)

        from commands.repeat import repeat
        c = repeat()
        self.commands_classes.append(c)

        from commands.pecel import pecel
        p = pecel()
        self.commands_classes.append(p)

    def check_for_command(self, msg):
        for c in self.commands_classes:
            c.run(self, msg)  # полная свобода командам, можно использовать все функции бота и всю инфу из сообщения

    def read_msg(self, msg_data):  # Чтение сообщения из 'updates'
        # print(msg_data)
        msg_text = msg_data[5]
        msg_date = datetime.datetime.fromtimestamp(msg_data[4]).strftime('%H:%M:%S')  # %Y-%m-%d %H:%M:%S
        peer_id = msg_data[3]
        msg_id = msg_data[2]
        from_id = peer_id
        if 'from' in msg_data[6]:
            from_id = int(msg_data[6]['from'])
            msg_type = 'peer'
            # print('Сообщение из беседы от ' + str(from_id))
        else:
            msg_type = 'ls'
            # print('Сообщение из личной беседы с ' + str(from_id))
        msg = vk_msg(msg_id, msg_type, msg_date,from_id, msg_text, peer_id)  # можно было обойтись массивом =/
        self.check_for_command(msg)
        print(msg_text + ' ' + msg_date)

    @rate_limited(1)  # Не думаю, что он тут нужен
    def get_new_msg(self):
        try:
            # https://{$server}?act=a_check&key={$key}&ts={$ts}&wait=25&mode=2&version=2
            params = {  # Стандартные параметры указанные в документации
                'act': 'a_check',
                'key': self.key,
                'ts': self.ts,
                'wait': 25,
                'mode': 2,
                'version': 2
            }
            url = self.server
            r = requests.request(method='GET', url=url, params=params, timeout=30)  # Если поставить 25 - сервер немного не успевает
            data = json.loads(r.text)
            # print(data)

            if 'failed' in data:
                print(data)
                if data['failed'] == 1:
                    self.ts = data['ts']
                    return
                if data['failed'] in [2, 3]:
                    self.get_lps()
                    return

            if 'ts' in data:  # Обновляем ts
                self.ts = data['ts']

            for upd in data['updates']:  # Ищем событие о новом сообщении
                if upd[0] == 4:  # Обрабатываем, если нашли
                    self.read_msg(upd)

        except vk_requests.exceptions.VkAPIError as vk_error:  # Ошибки вк
            error_code = vk_error.error_data['error_code']
            print('Что-то пошло не так')
            print(vk_error.error_data)
            print(error_code)
            if error_code == 907 or error_code == 908:
                print('Сессия обновлена')
                self.get_lps()
                return -1
            if error_code == 14:
                print('Проблемесы с капчей, все пропало!')
                self.__init__()

        except requests.exceptions.ReadTimeout as error:
            print('Read timeout')
            pass

        except requests.exceptions.ConnectTimeout:
            print('Connection timeout')
            pass

        finally:  # Ну в целом можно повесить сюда увеличение таймаута при повторной ошибки...
            return

    def get_lps(self):
        lps = self.vk.api.messages.getLongPollServer(need_pts=1)
        self.key = lps['key']
        self.server = 'https://' + lps['server']
        self.ts = lps['ts']
        self.pts = lps['pts']

    def get_msgs(self):
        while True:
            self.get_new_msg()


bot = vk_bot()
bot.get_lps()
bot.import_commands()
bot.get_msgs()