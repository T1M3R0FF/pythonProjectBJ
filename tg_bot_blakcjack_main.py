import telebot
import config
import random
import time

bot = telebot.TeleBot(config.TOKEN)

# данные карт

cards = {'Шесть': 6, 'Семь': 7, 'Восемь': 8,
         'Девять': 9, 'Десять': 10, 'Валет': 2,
         'Дама': 3, 'Король': 4, 'Туз': 11}
data = list(cards.items())
suits = ['пики', 'крести', 'черви', 'буби']
counter = {}  # база данных игроков
check_list = []

@bot.message_handler(commands=['start'])  # старт игры
def start(message):
    if message.from_user.id in counter:
        bot.reply_to(message, "Ты уже зарегистрирован в игре")
        return True
    counter.update({message.from_user.id: 0})
    if len(counter) == 1:
        bot.send_message(message.chat.id, 'Подожди, пока зарегистрируется второй игрок')
    elif len(counter) == 2:
        for key in counter:
            bot.send_message(key, 'Добро пожаловать в игру BlackJack! Да начнется игра!\n'
                                  'Возьмите себе карту через пункт меню "card"')


@bot.message_handler(commands=['card'])  # взятие карты и зачисление очков
def card(message):
    global counter

    if len(counter) == 1:
        bot.send_message(message.chat.id, 'Подожди, пока зарегистрируется второй игрок')

    if counter[message.from_user.id] > 21:
        bot.send_message(message.chat.id, f'Вы проиграли! Сумма ваших очков: {counter[message.from_user.id]}.'
                                          'Нажмите /finish, чтобы узнать, кто победил')
        counter[message.from_user.id] = 0
        return True

    key, value = random.choice(data)
    random_suit = random.choice(suits)
    counter[message.from_user.id] += value
    if counter[message.from_user.id] == 21:
        bot.send_message(message.chat.id, 'Блекджек! Вы набрали 21 очко, поздравляем!'
                                          'Нажмите /finish, чтобы узнать, кто победил')
        for key in counter:
            if key != message.from_user.id:
                bot.send_message(key, 'У вашего соперника блекджек!')
        return True

    elif counter[message.from_user.id] > 21:
        bot.send_message(message.chat.id, f'Игра окончена! Сумма ваших очков: {counter[message.from_user.id]}.\n'
                                          'Нажмите /finish, чтобы узнать, кто победил')
        return True

    else:
        bot.send_message(message.chat.id, f'Ваша карта : {key} {random_suit}\n'
                                          'Если хотите завершить набор карт, нажмите /finish')


@bot.message_handler(commands=['finish'])  # окончание игры
def finish(message):
    global check_list
    global counter

    bot.send_message(message.chat.id, 'Вы решили закончить игру.')
    bot.send_message(message.chat.id, f'Сумма ваших очков: {counter[message.from_user.id]}.')
    check_list.append(message.chat.id)

    # отправка очков сопернику
    if len(check_list) == 1:
        bot.send_message(message.chat.id, 'Жду окончания игры твоего соперника')

    elif len(check_list) == 2:
        for key, key1 in counter, counter:
            if key != message.from_user.id and key1 == message.from_user.id:
                bot.send_message(key, f'Соперник решил закончить набор карт, сумма его очков: {counter[key1]}')
                bot.send_message(key1, f'Соперник решил закончить набор карт, сумма очков соперника: {counter[key]}')
                break
            else:
                bot.send_message(key, f'Соперник решил закончить набор карт, сумма его очков: {counter[key1]}')
                bot.send_message(key1, f'Соперник решил закончить набор карт, сумма очков соперника: {counter[key]}')
                break
        if (counter[key1] > 22 > counter[key]) or ((counter[key1] and counter[key]) < 22
                                                   and (counter[key] > counter[key1])):
            bot.send_message(key, 'Вы победили, поздравляю!')
            bot.send_message(key1, 'К сожалению, вы проиграли:(')
        elif (counter[key1] == counter[key] and (counter[key1] and counter[key]) < 22) or ((counter[key]
                                                                                            and counter[key1]) > 22):
            bot.send_message(key1, 'У вас ничья!')
            bot.send_message(key, 'У вас ничья!')
        elif (counter[key] > 22 > counter[key1]) or ((counter[key1] and counter[key]) < 22
                                                     and (counter[key1] > counter[key])):
            bot.send_message(key1, 'Вы победили, поздравляю!')
            bot.send_message(key, 'К сожалению,вы проиграли:(')
        bot.send_message(key, 'Если хотите сыграть еще, жмите /start')
        bot.send_message(key1, 'Если хотите сыграть еще, жмите /start')
    counter.clear()
    check_list = []
    return True


@bot.message_handler(content_types=['text'])
def text_message(message):
    bot.send_message(message.chat.id, 'Никакого общения, только игра')


bot.polling(non_stop=True)