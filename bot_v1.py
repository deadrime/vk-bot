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
from vk import vk
from rate import rate_limited


class vk_msg:
    def __init__(self, type, id, date, by, from_id):
        self.type = type
        self.id = id
        self.date = date
        self.by = by
        self.msg = ''
        if type == 'peer':
            self.from_id = from_id + 2000000000
        else:
            self.from_id = from_id


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

        from commands.repeat import repeat
        c = repeat()
        self.commands_classes.append(c)

        from commands.pecel import pecel
        p = pecel()
        self.commands_classes.append(p)

        # for m in modules:
        #     name = m[0:-3]
        #     mod = __import__('commands.' + name, fromlist=name)
        #     command = getattr(mod, name)
        #     self.commands_classes.append(command)

    def check_for_command(self, msg):
        for c in self.commands_classes:
            c.run(self, msg)  # я решил дать полную свободу командам, так что там можно использовать все функции бота и всю инфу из сообщения

    def read_msgs(self, msgs):
        # print(msgs)
        for msg in msgs['items']:
            # print(msg)
            text = msg['body']
            by = msg['user_id']  # целое, а не строчка
            time = datetime.datetime.fromtimestamp(int(msg['date'])).strftime('%Y-%m-%d %H:%M:%S')
            type = 'peer' if ('chat_id' in msg) else 'ls'
            if type == 'peer':
                by = msg['chat_id'] + 2000000000
            print(text + ' ' + str(by) + ' ' + time + ' ' + type)
            self.check_for_command(msg)

    @rate_limited(1)
    def get_new_msg(self):
        try:
            msgs = self.vk.api.messages.getLongPollHistory(ts=self.ts, pts=self.pts)
            new_msg = False
            for event in msgs['history']:
                if event[0] == 4:  # если есть новое сообщение
                    new_msg = True
            if new_msg:
                self.read_msgs(msgs['messages'])
                self.pts = msgs['new_pts']

        except vk_requests.exceptions.VkAPIError as vk_error:
            error_code = vk_error.error_data['error_code']
            print('Что-то пошло не так')
            print(vk_error.error_data)
            # print(error_code)
            if error_code == 907 or error_code == 908:
                print('Сессия обновлена')
                self.get_lps()
                self.get_msgs()
                return -1
            if error_code == 14:
                print('Проблемесы с капчей')
                self.__init__()

        except socket.timeout as error:  # Не уверен, что это должно работать именно так. Вроде оно и не работает...
            print(error)
            pass

        except requests.exceptions.ReadTimeout as error:  # Так что попробуем так. Тут вроде ловит ошибку.
            print(error)
            pass

        finally:  # Ну в целом можно повесить сюда увеличение таймаута при повторной ошибки...
            pass

    def get_lps(self):
        lps = self.vk.api.messages.getLongPollServer(need_pts=1)
        self.key = lps['key']
        self.server = lps['server']
        self.ts = lps['ts']
        self.pts = lps['pts']

    def get_msgs(self):
        while True:
            self.get_new_msg()


bot = vk_bot()
bot.get_lps()
bot.import_commands()
bot.get_msgs()