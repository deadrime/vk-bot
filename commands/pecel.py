import random
from vk import vk


class pecel:
    def __init__(self):
        self.keys = [
            ['пёсел', 'песел', '!песел', '!пёсел'],
            ['!аниме', '!аниму', '!вайфу', 'вайфу'],
            ['!кот', '!котик', '!котэ']
        ]
        self.groups = [
            [-114941759, -132634913],
            [-129018451, -125712290, -141434552, -96517247, -137960766, -84180549],
            [-33124129]
        ]

    def run(self, msg):
        msg_id, msg_type, msg_date, from_id, msg_text, peer_id = msg
        count = 1
        for i in range(len(self.keys)):  # нужно попробовать сделать через словари, keys { ['!кот', '!котик', '!котэ']: [-33124129]}
            for key in self.keys[i]:
                if key in msg_text.lower():
                    if '*' in msg_text:
                        try:
                            count = int(float(msg_text.split('*')[1]))
                        except Exception as error:  # Добавить сюда нормальную обработку ошибок, когда не получается преобразовать
                            print(error)            # текст в число
                            vk.send_msg(peer_id, 'Не выебывайся')
                            return
                        count = 10 if count > 10 else count
                    msg = ''
                    group = self.groups[i][random.randrange(len(self.groups[i]))]  # рандомная группа из списка групп
                    attachment = vk.get_random_wall_picture(group, count)  # n рандомных картинок из этой группы
                    # print(attachment)
                    vk.send_msg(peer_id, msg, attachment)
                    return
        return