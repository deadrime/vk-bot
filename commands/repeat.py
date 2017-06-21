# -*- coding: utf-8 -*-
from vk import vk

class repeat:
    def __init__(self):
        self.keys = ['!повторяй', '!стоп']
        self.last_msg_id = 0
        self.users_to_repeat = []

    def run(self, msg):
        # print(msg)
        # print(self.users_to_repeat)
        msg_id, msg_type, msg_date, from_id, msg_text, peer_id = msg

        if from_id != vk.self['id'] and type == 'peer':
            if '!повторяй' in msg_text:
                print(self.users_to_repeat)
                if from_id not in self.users_to_repeat:
                    self.users_to_repeat.append(from_id)
                    # vk.send_msg(peer_id, 'Ты пидор ' + str(from_id), '')
                return

            if '!стоп' in msg_text:
                if from_id in self.users_to_repeat:
                    self.users_to_repeat.remove(from_id)
                return

            if from_id in self.users_to_repeat:
                vk.send_msg(peer_id, msg_text, '')
