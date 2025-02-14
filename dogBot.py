import telebot
import config
from telebot import types
from getter import getDb, update


bot = telebot.TeleBot(config.token)


@bot.callback_query_handler(func=lambda call: call.data == 'real_pay_day')
def real_pay_day(call):
    db = getDb()
    db['payment'] = 0
    update(db)
    cancel(call)


@bot.callback_query_handler(func=lambda call: call.data == 'pay_day')
def pay_day(call):
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Ага, ща переведу', callback_data='real_pay_day')
    button_no = types.InlineKeyboardButton('Нееее, я передумала', callback_data='cancel')
    markup.add(button_yes, button_no)
    bot.send_message(call.message.chat.id, 'Ну шо, закрываем счёт?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'how_much')
def how_much(call):
    db = getDb()
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Думаю заплатить', callback_data='pay_day')
    button_no = types.InlineKeyboardButton('Не, я только посмотреть', callback_data='cancel')
    markup.add(button_yes, button_no)
    payment = db['payment']
    bot.send_message(call.message.chat.id, f'Итого надо {payment} денях', reply_markup=markup)
    update(db)


def is_int(text):
    for i in range(len(text)):
        if text[i] < '0' or text[i] > '9':
            return False
    return True


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel(call, need_message = True, strn = 'Ладно', bool_call=True):
    if bool_call:
        message = call.message
    else:
        message = call
    if need_message:
        bot.send_message(message.chat.id, strn)
    start(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('real_pay '))
def real_pay(call):
    payment = int(call.data[9:])
    db = getDb()
    db['payment'] += payment
    update(db)
    cancel(call, strn=f'Добавил {str(payment)}')


def unstandart_pay(message):
    if is_int(message.text):
        pay(message, call_bool=False)
    else:
        bot.send_message(message.chat.id, 'Давай заново и введи пожалуйста только циферами и без пробелов')
        cancel(message, bool_call=False)


@bot.callback_query_handler(func=lambda call: call.data == 'unstandart')
def unstandart(call):
    bot.send_message(call.message.chat.id, 'Напиши циферами сколько')
    bot.register_next_step_handler(call.message, unstandart_pay)


@bot.callback_query_handler(func=lambda call: call.data.startswith('pay '))
def pay(call, call_bool = True):
    if call_bool:
        message = call.message
        payment = call.data[4:]
    else:
        message = call
        payment = message.text
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text=f'Подтверждаем {payment}', callback_data=f'real_pay {payment}')
    button_no = types.InlineKeyboardButton(text='Нееее', callback_data='cancel')
    markup.add(button_yes, button_no)
    bot.send_message(message.chat.id, 'Агааааа, деньги', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    db = getDb()
    if str(message.chat.id) not in db['users']:
        db['users'].append(str(message.chat.id))
    update(db)
    markup = types.InlineKeyboardMarkup()
    for elem in config.cases:
        button = types.InlineKeyboardButton(text=elem[0], callback_data=elem[1])
        markup.add(button)
    bot.send_message(message.chat.id, "Шо почем?", reply_markup=markup)



def main():
    bot.infinity_polling()