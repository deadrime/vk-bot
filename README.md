# vk-bot
Самописный бот для вк написанный на python с использованием библиотеки vk_requests

# Что умеет?

  - Авторизация через логин/пароль, считывание конфига из config.conf
  - Кривая система команд с возможнотью добавления своих команд.
  - Подключение к long poll для чтения сообщений
  - Обработка ошибок

Функционал вк:
  - Отправка сообщений в личку/беседу
  - Чтение сообщений
  - Получение информации о пользователе
  - Получение рандомной картинки со стены группы

Команды:
  - Повторение всех сообщений за человеком, вызвавшим команду !повторяй
  - Отправление песелей, котелей, аниме-девочек и т.д. из тематических групп для указанных команд
  - Викторина

# Что хочу сделать
- [x] Добавить систему комнат в викторину, чтобы для каждой беседы в вк была своя викторина с блэкджеком и лидербордом
- [ ] Нормальный импорт команд
- [ ] Логи
- [ ] Возможность создавать отдельные потоки
- [ ] Обнаружение текста на картинках с песелями, чтобы не отсылать рекламные пикчи
