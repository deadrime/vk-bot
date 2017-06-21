# -*- coding: utf-8 -*-
import vk_requests
import datetime
import random
from rate import rate_limited
import configparser


class vkapi:
    def __init__(self):
        self.app_id = 0
        self.login = ''
        self.password = ''
        self.api_version = '5.63'
        self.api = None
        self.self = None
        self.load_config()

    def load_config(self):
        conf = configparser.RawConfigParser()
        conf.read("config.conf")
        self.login = conf['VK']['login']
        self.password = conf['VK']['password']
        self.app_id = conf['VK']['app_id']

    def init_vk(self):
        self.api = vk_requests.create_api(app_id=self.app_id, login=self.login, password=self.password,
                                          scope=['offline', 'status', 'messages', 'docs', 'photos'], api_version=self.api_version)
        if self.api:
            print('Сессия создана')

        self.self = self.api.users.get()[0]
        print(self.self)

    @rate_limited(1.5)
    def send_msg(self, peer_id, msg, attachment=''):
        if not msg and not attachment:
            return
        self.api.messages.send(peer_id=peer_id, message=msg, attachment=attachment)

    @staticmethod
    def msg_info(msg):
        id = msg['id']
        text = msg['body']
        by = msg['user_id']  # целое, а не строчка
        time = datetime.datetime.fromtimestamp(int(msg['date'])).strftime('%Y-%m-%d %H:%M:%S')
        type = 'peer' if ('chat_id' in msg) else 'ls'
        peer_id = by
        if type == 'peer':
            peer_id = msg['chat_id'] + 2000000000
        return id, text, by, time, type, peer_id

    @rate_limited(0.3)
    def get_user(self, user):
        return self.api.users.get(user_ids=user)

    @rate_limited(0.3)
    def get_random_wall_picture(self, group_id, count=1):
        max_num = self.api.photos.get(owner_id=group_id, album_id='wall', count=0)['count']
        num = random.randint(1, max_num)
        photos = self.api.photos.get(owner_id=str(group_id), album_id='wall', count=count, offset=num)['items']
        # print(photos)
        attachment =''
        if count == 1:
            attachment += 'photo' + str(group_id) + '_' + str(photos[0]['id']) + ','
            return attachment
        else:
            for photo in photos:
                attachment += 'photo' + str(group_id) + '_' + str(photo['id']) + ','
            # print(attachment)
            return attachment[0:-1]  # обрезаю последнюю запятую

vk = vkapi()