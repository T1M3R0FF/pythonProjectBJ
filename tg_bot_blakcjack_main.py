import time

import telebot
import config
import random
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

# данные карт

cards = {'Шесть': 6, 'Семь': 7, 'Восемь': 8,
         'Девять': 9, 'Десять': 10, 'Валет': 2,
         'Дама': 3, 'Король': 4, 'Туз': 11}
data = list(cards.items())
suits = ['пики', 'крести', 'черви', 'буби']
counter = {}  # база данных игроков
general_message = ""
check_set = set()


@bot.message_handler(commands=['start'])  # старт игры
def start(message):
    global general_message
    bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if message.from_user.id in counter:
        del_mes = bot.send_message(message.chat.id, "Ты уже зарегистрирован в игре")
        start_game = ""
        for i in counter:
            start_game+=counter[i]["name"]+"\n"
        bot.edit_message_text(chat_id=general_message.chat.id, message_id=general_message.message_id,
                              text='Приветствую, Вы начали игру Black Jack!\n'
                                   f'Подожди, пока зарегистрируется другие игроки. Готовы к игре:\n\n{start_game}')
        time.sleep(2)
        bot.delete_message(chat_id=del_mes.chat.id, message_id=del_mes.message_id)
        return True
    counter.update({message.from_user.id: {"points":0,"name":message.from_user.first_name,"end_game":False}})
    if len(counter) < bot.get_chat_member_count(message.chat.id)-1:
        start_game = ""
        for i in counter:
            start_game+=counter[i]["name"]+"\n"
        if len(counter)==1:
            general_message = bot.send_message(message.chat.id, 'Приветствую, Вы начали игру Black Jack!\n'
                                          f'Подожди, пока зарегистрируется другие игроки. Готовы к игре:\n\n{start_game}')
            bot.pin_chat_message(chat_id=general_message.chat.id, message_id=general_message.message_id)
        elif len(counter)>1 and general_message!="":bot.edit_message_text(chat_id=general_message.chat.id, message_id=general_message.message_id,text='Приветствую, Вы начали игру Black Jack!\n'
                                          f'Подожди, пока зарегистрируется другие игроки. Готовы к игре:\n\n{start_game}')
        else:
            del_mes = bot.send_message(message.chat.id, "Попробуйте ещё раз")
            time.sleep(2)
            bot.delete_message(chat_id=del_mes.chat.id, message_id=del_mes.message_id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        button0 = types.InlineKeyboardButton('Показать очки', callback_data='view')
        button1 = types.InlineKeyboardButton('Взять карту', callback_data='card')
        button2 = types.InlineKeyboardButton('Завершить набор карт', callback_data='finish')
        markup.add(button0,button1, button2)
        general_message = bot.edit_message_text(reply_markup=markup,text='Оба игрока на месте, игра начинается! Добро пожаловать в BlackJack!\n'
                              'Возьмите себе карту',chat_id=general_message.chat.id,message_id=general_message.message_id)
    print("FFFFFFFFFFF")


# взятие карты и зачисление очков
def card(call):
    global counter

    if counter[call.from_user.id]["end_game"]:
        send_a(call, f'Для вас игра завершена. Cумма ваших очков: {counter[call.from_user.id]["points"]}')
        return True

    key, value = random.choice(data)
    random_suit = random.choice(suits)
    counter[call.from_user.id]['points'] += value

    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Взять карту', callback_data='card')
    button2 = types.InlineKeyboardButton('Завершить набор карт', callback_data='finish')
    markup.add(button1, button2)
    send_a(call, f'Ваша карта : {key} {random_suit}, сумма очков: {counter[call.from_user.id]["points"]}')

    if counter[call.from_user.id]["points"] == 21:
        finish(call)
        return True

    elif counter[call.from_user.id]["points"] > 21:
        finish(call)
        return True


# окончание игры
def finish(call):
    global check_set
    global counter, general_message
    counter[call.from_user.id]["end_game"]=True
    send_a(call, f'Вы закончили игру.\nСумма ваших очков: {counter[call.from_user.id]["points"]}.')
    check_set.add(call.from_user.id)

    # отправка очков сопернику
    if len(check_set) != len(counter):
        ends_game = ""
        for i in check_set:
            ends_game+=counter[i]["name"]+"\n"
        if f'Закончили: {ends_game}'==f'{general_message.text}\n':
            return True
        markup = types.InlineKeyboardMarkup(row_width=1)
        button0 = types.InlineKeyboardButton('Показать очки', callback_data='view')
        button1 = types.InlineKeyboardButton('Взять карту', callback_data='card')
        button2 = types.InlineKeyboardButton('Завершить набор карт', callback_data='finish')
        markup.add(button0,button1, button2)
        general_message = bot.edit_message_text(f"Закончили: \n{ends_game}", chat_id=general_message.chat.id, message_id=general_message.message_id,reply_markup=markup)

    else:
        result = ""
        winner = ""
        for i in counter:
            result+=f"{counter[i]['name']}: {counter[i]['points']}\n"
        bot.edit_message_text(f'Все закончили игру.\nРезультаты:\n{result}',chat_id=general_message.chat.id,message_id=general_message.message_id)





def view(call):
    send_a(call,f"Ваши очки {counter[call.from_user.id]['points']}")



def send_a(call, message):
    bot.answer_callback_query(callback_query_id=call.id, text=message,show_alert=True)
@bot.message_handler(content_types=['text'])
def text_message(message):
    bot.send_message(message.chat.id, 'Никакого общения, только игра')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'card':
            card(call)
        if call.data == 'finish':
            finish(call)
        if call.data == "view":
            view(call)


bot.polling(non_stop=True)