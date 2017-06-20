# -*- coding: utf-8 -*-
import random
import time
import json
import os


class victorina:
    def __init__(self):
        self.keys = ['!викторина', '!стоп']
        self.bd = []
        self.init_bd()
        self.is_active = False
        self.is_started = False
        self.is_guessed = False
        self.current_question = ''
        self.current_answer = ''
        self.current_hint = []
        # self.rooms = []
        # self.leaders = {}
        self.vk = None

        self.time_for_hint = 30

    def init_bd(self):
        with open('commands\\questions\\bd.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                q = line.replace('\n', '').split('|')
                self.bd.append(q)
        #print(self.bd)

    def prepare_question(self):
        q = self.bd[random.randrange(len(self.bd))]
        self.current_question = q[0]
        self.current_answer = q[1]
        self.prepare_hint()
        msg = self.current_question
        return msg

    def check_answer(self, room_id, answer, by, bot):
        if answer == self.current_answer:
            bot.vk.send_msg(room_id, 'Верно')

    def change_hint(self):
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

    def helping(self, peer_id):
        self.change_hint()
        self.vk.send_msg(peer_id, ''.join(self.current_hint))

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

    def run(self, bot, msg):
        msg_id, msg_type, msg_date, from_id, msg_text, peer_id = msg.get_all()
        self.vk = bot.vk

        if msg_text == '!викторина':  # Запускаем гуся
            if self.is_active:  # Если уже запущена
                bot.vk.send_msg(peer_id, 'Викторина уже запущена. Текущий вопрос:' + self.current_question + ', ' + self.letters_in_answer())
            else:  # Если еще не запущена
                self.is_active = True
                self.prepare_question()
                self.vk.send_msg(peer_id, 'Викторина запущена!\nДоступные команды: !подсказка, !ответ, !стоп\nВопрос: ' + self.current_question + ', ' + self.letters_in_answer())

        if self.is_active:  # Если викторина активка
            if not self.is_guessed:  # И еще никто не угадал ответ
                if msg_text == '!подсказка':
                    self.helping(peer_id)

                if self.current_answer.lower() in msg_text.lower():
                    user = bot.vk.api.users.get(user_ids=from_id)
                    msg = user[0]['first_name'] + ' ' + user[0]['last_name'] + ' верно ответил на вопрос и получает нихуя!'
                    bot.vk.send_msg(peer_id, msg, '')
                    self.prepare_question()
                    bot.vk.send_msg(peer_id, 'Следующий вопрос:\n' + self.current_question + ', ' + self.letters_in_answer())

                if msg_text == '!ответ':
                    bot.vk.send_msg(peer_id, self.current_answer, '')
                    self.prepare_question()
                    bot.vk.send_msg(peer_id, 'Следующий вопрос:\n' + self.current_question + ', ' + self.letters_in_answer())

                if msg_text == '!стоп':
                    bot.vk.send_msg(peer_id, 'Викторина остановлена\nОтвет на последний вопрос: ' + self.current_answer, '')
                    self.is_active = False