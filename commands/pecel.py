import random
import time


class pecel:
    def __init__(self):
        self.keys = [
            ['пёсель', 'песель', 'пёсель.', 'песель.'],
            ['!аниме', '!аниму', '!вайфу'],
            ['!кот', '!котик', '!котэ']
        ]
        self.groups = [
            [-114941759, -132634913],
            [-129018451, -125712290, -141434552, -96517247, -137960766, -84180549],
            [-33124129]
        ]

    def run(self, bot, msg):
        msg_id, msg_type, msg_date, from_id, msg_text, peer_id = msg.get_all()
        count = 1

        for i in range(len(self.keys)):
            for key in self.keys[i]:
                if key in msg_text.lower():
                    if '*' in msg_text:
                        count = msg_text.split('*')[1]
                        try:
                            count = int(float(msg_text.split('*')[1]))
                        except Exception as error:
                            print(error)
                            bot.vk.send_msg(peer_id, 'Не выебывайся')
                            return
                        count = 10 if count > 10 else count
                    msg = ''
                    attachments = []
                    for j in range(count):
                        group = self.groups[i][random.randrange(len(self.groups[i]))]
                        attachment = bot.vk.get_random_wall_picture(group)
                        attachments.append(attachment)
                        time.sleep(0.6)
                    bot.vk.send_msg(peer_id, msg, attachments)
                    return
        return