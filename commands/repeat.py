# -*- coding: utf-8 -*-
class repeat:
    def __init__(self):
        self.keys = ['!повторяй', '!стоп']
        self.last_msg_id = 0
        self.users_to_repeat = []

    def run(self, bot, msg):
        # print(msg)
        # print(self.users_to_repeat)
        msg_id, msg_type, msg_date, from_id, msg_text, peer_id = msg.get_all()

        if from_id != bot.vk.self['id'] and type == 'peer':
            if '!повторяй' in msg_text:
                print(self.users_to_repeat)
                if from_id not in self.users_to_repeat:
                    self.users_to_repeat.append(from_id)
                    # bot.vk.send_msg(peer_id, 'Ты пидор ' + str(from_id), '')
                return

            if '!стоп' in msg_text:
                if from_id in self.users_to_repeat:
                    self.users_to_repeat.remove(from_id)
                return

            if from_id in self.users_to_repeat:
                bot.vk.send_msg(peer_id, msg_text, '')
