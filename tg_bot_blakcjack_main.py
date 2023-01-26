import time
import telebot
import random
from telebot import types

bot = telebot.TeleBot("5871645650:AAF2l3jxWR_ka7gjurM5qwrmIeyCDVSzXKY")

# данные карт

cards = {'Шесть': 6, 'Семь': 7, 'Восемь': 8,
         'Девять': 9, 'Десять': 10, 'Валет': 2,
         'Дама': 3, 'Король': 4, 'Туз': 11}
data = list(cards.items())
suits = ['пики', 'крести', 'черви', 'буби']
counter = {}  # база данных игроков
general_message = ""


@bot.message_handler(commands=['start'])  # старт игры
def start(message):
    chat_id = message.chat.id
    if chat_id not in list(counter.keys()):
        counter.update({chat_id: {"general_message": "", "players": {}, "start_game": False}})
        print(counter)
    # админ    bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if message.from_user.id in list(counter[chat_id]["players"].keys()):
        if not counter[chat_id]["start_game"]:
            del_mes = bot.send_message(chat_id, f"{message.from_user.first_name} ты уже зарегистрирован в игре.")
            start_game = ""
            for i in counter[chat_id]["players"]:
                start_game += counter[chat_id]["players"][i]["name"] + "\n"
            text = f'Приветствую, Вы начали игру Black Jack!\n' \
                   f'Подожди, пока зарегистрируется другие игроки. Готовы к игре:\n\n{start_game}'

            print(counter[chat_id]["general_message"].text + "\n##########\n" + text)
            if counter[chat_id]["general_message"].text + "\n" != text:
                bot.edit_message_text(chat_id=counter[chat_id]["general_message"].chat.id,
                                      message_id=counter[chat_id]["general_message"].message_id,
                                      text=text)
        else:
            del_mes = bot.send_message(chat_id, f"{message.from_user.first_name} игра уже идёт.")
        time.sleep(2)
        bot.delete_message(chat_id=del_mes.chat.id, message_id=del_mes.message_id)
        return True
    counter[chat_id]["players"].update({message.from_user.id: {"points": 0, "name": message.from_user.first_name,
                                                               "end_game": False}})
    if len(counter[chat_id]["players"]) < bot.get_chat_member_count(chat_id) - 1:
        start_game = ""
        for i in counter[chat_id]["players"]:
            start_game += counter[chat_id]["players"][i]["name"] + "\n"
        if len(counter[message.chat.id]["players"]) == 1:
            counter[chat_id]["general_message"] = bot.send_message(chat_id, 'Приветствую, Вы начали игру Black Jack!\n'
                                                                            f'Подожди, пока зарегистрируется другие '
                                                                            f'игроки. '
                                                                            f' Готовы к игре:\n\n{start_game}')
        # админ    bot.pin_chat_message(chat_id=message.chat.id,
        # message_id=counter[chat_id]["general_message"].message_id)
        elif len(counter[message.chat.id]["players"]) > 1 and counter[chat_id]["general_message"] != "":
            bot.edit_message_text(chat_id=counter[chat_id]["general_message"].chat.id,
                                  message_id=counter[chat_id]["general_message"].message_id,
                                  text='Приветствую, Вы начали игру Black Jack!\n'
                                       f'Подожди, пока зарегистрируется другие игроки. Готовы к игре:\n\n{start_game}')
        else:
            del_mes = bot.send_message(message.chat.id, "Попробуйте ещё раз")
            time.sleep(2)
            bot.delete_message(chat_id=del_mes.chat.id, message_id=del_mes.message_id)
    else:
        counter[chat_id]["start_game"] = True
        markup = types.InlineKeyboardMarkup(row_width=1)
        button0 = types.InlineKeyboardButton('Показать очки', callback_data='view')
        button1 = types.InlineKeyboardButton('Взять карту', callback_data='card')
        button2 = types.InlineKeyboardButton('Завершить набор карт', callback_data='finish')
        markup.add(button0, button1, button2)
        counter[chat_id]["general_massage"] = bot.edit_message_text(reply_markup=markup,
                                                                    text='Все игрока на месте, игра начинается!'
                                                                         ' Добро пожаловать в BlackJack!\n'
                                                                         'Возьмите себе карту',
                                                                    chat_id=counter[chat_id]["general_message"].chat.id,
                                                                    message_id=counter[chat_id][
                                                                        "general_message"].message_id)


# взятие карты и зачисление очков
def card(call):
    chat_id = call.message.chat.id
    global counter
    if counter[chat_id]["players"][call.from_user.id]["end_game"]:
        send_a(call,
               f'Для вас игра завершена. Cумма ваших очков: '
               f'{counter[chat_id]["players"][call.from_user.id]["points"]}')
        return True

    key, value = random.choice(data)
    random_suit = random.choice(suits)
    counter[chat_id]["players"][call.from_user.id]['points'] += value

    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Взять карту', callback_data='card')
    button2 = types.InlineKeyboardButton('Завершить набор карт', callback_data='finish')
    markup.add(button1, button2)
    send_a(call,
           f'Ваша карта : {key} {random_suit}, сумма очков: '
           f'{counter[chat_id]["players"][call.from_user.id]["points"]}')

    if counter[chat_id]["players"][call.from_user.id]["points"] == 21:
        finish(call)
        return True

    elif counter[chat_id]["players"][call.from_user.id]["points"] > 21:
        finish(call)
        return True


# окончание игры
def finish(call):
    chat_id = call.message.chat.id
    global counter
    if counter[chat_id]["players"][call.from_user.id]["end_game"]:
        send_a(call,
               f'Для вас игра завершена. Cумма ваших очков:'
               f' {counter[chat_id]["players"][call.from_user.id]["points"]}')
        return True
    counter[chat_id]["players"][call.from_user.id]["end_game"] = True
    send_a(call,
           f'Вы закончили игру.\nСумма ваших очков: {counter[chat_id]["players"][call.from_user.id]["points"]}.')
    counter[chat_id]["players"][call.from_user.id]["end_game"] = True
    counter_end_player = []
    for i in counter[chat_id]["players"]:
        if counter[chat_id]["players"][i]["end_game"]:
            counter_end_player.append(i)
    print(counter)
    # отправка очков сопернику
    if len(counter_end_player) != len(counter[chat_id]["players"]):
        ends_game = ""
        for i in counter[chat_id]["players"]:
            if counter[chat_id]["players"][i]["end_game"]:
                ends_game += counter[chat_id]["players"][i]["name"] + "\n"
        if f'Закончили: {ends_game}' == f'{counter[chat_id]["general_message"].text}\n':
            return True
        markup = types.InlineKeyboardMarkup(row_width=1)
        button0 = types.InlineKeyboardButton('Показать очки', callback_data='view')
        button1 = types.InlineKeyboardButton('Взять карту', callback_data='card')
        button2 = types.InlineKeyboardButton('Завершить набор карт', callback_data='finish')
        markup.add(button0, button1, button2)
        counter[chat_id]["general_message"] = bot.edit_message_text(f"Закончили: \n{ends_game}",
                                                                    chat_id=counter[chat_id]["general_message"].chat.id,
                                                                    message_id=counter[chat_id][
                                                                        "general_message"].message_id,
                                                                    reply_markup=markup)

    else:
        result = ""
        winner = ""
        for i in counter[chat_id]["players"]:
            result += f"{counter[chat_id]['players'][i]['name']}: {counter[chat_id]['players'][i]['points']}\n"
        bot.edit_message_text(f'Все закончили игру.\nРезультаты:\n{result}',
                              chat_id=counter[chat_id]["general_message"].chat.id,
                              message_id=counter[chat_id]["general_message"].message_id)
        counter[chat_id]["players"] = {}
        counter[chat_id]["start_game"] = False


def view(call):
    send_a(call, f"Ваши очки {counter[call.message.chat.id]['players'][call.from_user.id]['points']}")


def send_a(call, message):
    bot.answer_callback_query(callback_query_id=call.id, text=message, show_alert=True)


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
