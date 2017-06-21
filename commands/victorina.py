# -*- coding: utf-8 -*-
import random
import _pickle as pickle
from pathlib import Path
from vk import vk


class vk_room:
    def __init__(self, room_id, bd):
        # self.bd = bd
        self.room_id = room_id
        self.is_guessed = False
        self.current_question = ''
        self.current_answer = ''
        self.current_hint = []
        self.leaders = {}
        self.last_question = ''
        self.last_answer = ''

    def prepare_question(self, bd):  # Создание нового вопроса и подсказки
        self.last_question = self.current_question
        self.last_answer = self.current_answer
        q = bd[random.randrange(len(bd))]
        self.current_question = q[0]
        self.current_answer = q[1]
        self.prepare_hint()
        msg = self.current_question
        return msg

    def change_hint(self):  # Добавление нового символа в подсказку
        correct = False
        letter_pos = 0
        new_letter = ''
        if '_' not in self.current_hint:
            return
        while not correct:
            letter_pos = random.randrange(len(self.current_answer))
            if self.current_hint[letter_pos] != self.current_answer[letter_pos]:
                correct = True
                new_letter = self.current_answer[letter_pos]
        self.current_hint[letter_pos] = new_letter

    def helping(self):
        self.change_hint()
        return ''.join(self.current_hint) # что нужно отправить

    def prepare_hint(self):
        self.current_hint = list('_' * len(self.current_answer))
        for i in range(len(self.current_answer)):
            if self.current_answer[i] == ' ':
                self.current_hint[i] = ' '

    def letters_in_answer(self):
        if ' ' in self.current_answer:
            words = self.current_answer.split(' ')
            r = str(len(words)) + ' слова, ' + ''.join(self.current_hint)
        else:
            r = str(len(self.current_answer)) + ' букв.'
        return r

    def update_leaders(self, user_id, points):
        if user_id not in self.leaders:
            self.leaders[user_id] = points
        else:
            self.leaders[user_id] += points
        return


class victorina:
    def __init__(self):
        self.keys = ['!викторина']  # Нужно только для импорта в общий список доступных команд
        self.bd = []  # база данных вопросов
        self.active_rooms = []
        self.rooms = {}  # список текущих активных комнат
        self.time_for_hint = 30  # Если введу когда-нибудь подсказки в отдельном потоке
        self.good_questions = {}

        self.load_files()  # Грузим базу вопросов, свою базу хороших вопросов и комнаты

    def load_files(self):
        bd = Path('commands/questions/bd.txt')
        if bd.is_file():
            f = open(bd, 'r', encoding='utf-8')
            for line in f.readlines():
                q = line.replace('\n', '').split('|')
                self.bd.append(q)
            f.close()
        rooms = Path('rooms.pickle')
        if rooms.is_file():
            f = open(rooms, 'rb')
            self.rooms = pickle.load(f)
            f.close()
        gq = Path('good_questions.pickle')
        if gq.is_file():
            f = open(gq, 'rb')
            self.good_questions = pickle.load(f)

    def run(self, msg):
        msg_id, msg_type, msg_date, from_id, msg_text, peer_id = msg

        if msg_text == '!викторина':  # Запускаем гуся
            if peer_id not in self.active_rooms: # Если нет среди активных
                if peer_id not in self.rooms: # Если команда запущена впервые
                    # print('Запущено впервые')
                    new_room = vk_room(peer_id, self.bd)
                    new_room.prepare_question(self.bd)
                    vk.send_msg(peer_id,
                                     'Викторина запущена!\nДоступные команды: !подсказка, !ответ, !стоп, !топ, !команды\n'
                                     'Если текущий вопрос хороший - напишете "+", если предыдущий - "++" \n'
                                     'Вопрос: '
                                     + new_room.current_question + ', ' + new_room.letters_in_answer())
                    self.rooms[peer_id] = new_room
                    self.active_rooms.append(peer_id)
                    # print(self.active_rooms)
                else:
                    # print('Есть в бд')
                    self.rooms[peer_id].prepare_question(self.bd)
                    vk.send_msg(peer_id,
                                    'Викторина запущена!\nДоступные команды: !подсказка, !ответ, !стоп, !топ, !команды\n'
                                    'Если текущий вопрос хороший - напишете "+", если предыдущий - "++" \n'
                                    'Вопрос: '
                                    + self.rooms[peer_id].current_question + ', ' + self.rooms[peer_id].letters_in_answer())
                    self.active_rooms.append(peer_id) # Добавляем в активные комнаты
            else:   # Если есть среди активных
                vk.send_msg(peer_id,'Текущий вопрос:'
                                + self.rooms[peer_id].current_question + ', ' + self.rooms[peer_id].letters_in_answer())
            return

        if peer_id in self.active_rooms:
            room = self.rooms[peer_id]
            if not room.is_guessed:  # И еще никто не угадал ответ
                if msg_text == '!подсказка':  # Если нужна подсказка
                    hint = room.helping()
                    vk.send_msg(room.room_id, hint)
                    return

                elif room.current_answer.lower() == msg_text.lower():  # Если дан верный ответ
                    user = vk.api.users.get(user_ids=from_id)
                    points = (len(room.current_answer))
                    room.update_leaders(from_id, points)
                    msg = user[0]['first_name'] + ' ' + user[0]['last_name'] + ' верно ответил на вопрос и получает ' +  str(points) + ' очков!'
                    vk.send_msg(room.room_id, msg, '')
                    room.prepare_question(self.bd)
                    vk.send_msg(room.room_id, 'Следующий вопрос:\n' + room.current_question + ', ' + room.letters_in_answer())

                    with open('rooms.pickle', 'wb') as f:
                        pickle.dump(self.rooms, f)
                        # print(self.active_rooms)
                    return

                elif msg_text == '!топ':
                    msg = 'Топ этой беседы: '
                    for leader in room.leaders:
                        user = vk.api.users.get(user_ids=leader)
                        msg += '\n' + user[0]['first_name'] + ' ' + user[0]['last_name'] + ': ' + str(room.leaders[leader]) + ' очков'
                    vk.send_msg(room.room_id, msg)
                    return

                elif msg_text == '!ответ':  # Если нужен след. вопрос
                    vk.send_msg(peer_id, room.current_answer, '')
                    room.prepare_question(self.bd)
                    vk.send_msg(peer_id, 'Следующий вопрос:\n' + room.current_question + ', ' + room.letters_in_answer())
                    return

                elif msg_text == '!стоп':  # Если надо остановить викторину
                    vk.send_msg(peer_id, 'Викторина остановлена\nОтвет на последний вопрос: ' + room.current_answer, '')
                    self.active_rooms.remove(peer_id)
                    # print(self.active_rooms)
                    return

                elif msg_text == '+':
                    self.good_questions[room.current_question] = room.current_answer
                    vk.send_msg(peer_id, 'Вопрос добавлен в бд')
                    with open('good_questions.pickle', 'wb') as f:
                        pickle.dump(self.good_questions, f)
                    return

                elif msg_text == '++':
                    self.good_questions[room.last_question] = room.last_answer
                    vk.send_msg(peer_id, 'Предыдущий вопрос добавлен в бд')
                    with open('good_questions.pickle', 'wb') as f:
                        pickle.dump(self.good_questions, f)
                    return

                elif msg_text == '!помощь':
                    vk.send_msg(peer_id, 'Список команд:\n'
                                             '!викторина - запустить викторину\n'
                                             '!ответ - получить ответ и новый вопрос\n'
                                             '!стоп - остановить викторину\n'
                                             '!топ - статистика игроков\n'
                                             '+ - пометить текущий вопрос как хороший\n'
                                             '++ - пометить предыдущий вопрос как хороший\n'
                                    )
                    return
