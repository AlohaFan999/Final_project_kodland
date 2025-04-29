import telebot
from config import *
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from db import DatabaseManager

manager = DatabaseManager(DATABASE)

bot = telebot.TeleBot(TOKEN, parse_mode="html")


@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.chat.id, "Привет!")


@bot.message_handler(commands=["question"])
def question(message: Message):
    bot.send_message(message.chat.id, "Пришли сюда мне свой вопрос! Одним сообщением!")
    bot.register_next_step_handler(message, get_question)

def get_question(message: Message):
    text = message.text
    bot.send_message(message.chat.id, "Обрабатываем ваш вопрос, подождите немного")
    manager.add_request(message.from_user.id, text)
    request_id = manager.get_last_request(message.from_user.id)[0]
    manager.add_message(request_id, message.from_user.id, text)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('vzat zapros', callback_data=f"confirm_{request_id}"))
    bot.send_message(ID_GROUP_CHAT, f"Поступил запрос от пользователя @{message.from_user.username if message.from_user.username else ''}\n\n{text}", reply_markup=markup)

@bot.callback_query_handler()
def callback(call:CallbackQuery):
    data = call.data.split('_')
    if 'confirm' in data:
        request_id = data[-1]
        moder_id = call.from_user.id
        manager.update_request(request_id, moder_id)
        bot.send_message(call.message.chat.id, f"Принят запрос модератором {call.from_user.username}, запрос номер {request_id}")
        #бот доден отправить соо,щение модератору с кнопкой dialog_5 на каоторой написано начать разговор
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Napisat soobsheniye", callback_data=f"dialog_{request_id}"))
        bot.send_message(moder_id, "Вы приняли запрос, можете начать диалог", reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.id)
        return
    if "dialog" in data:
        request_id = data[-1]
        unknown_user = call.from_user.id
        bot.send_message(call.message.chat.id, "Napishite chno")
        bot.register_next_step_handler(call.message, get_answer, request_id)


def get_answer(message: Message, request_id):
    text = message.text
    unknown_user = message.from_user.id
    manager.add_message(request_id, unknown_user, text)
    result = manager.get_request(request_id)
    moder_id = result[0]
    user_id = result[1]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Napisat soobsheniye", callback_data=f"dialog_{request_id}"))
    dialog = ""
    all_text = manager.get_all_text(request_id)
    for msg in all_text:
        tg, txt = msg
        dialog += f"{'Модератор:' if unknown_user == tg else 'Вы:'} {txt}\n"
    if unknown_user == moder_id:
        bot.send_message(user_id, dialog, reply_markup=markup)
    elif unknown_user == user_id:
        dialog += f"\n\nЗапрос номер {request_id}"
        bot.send_message(moder_id, dialog, reply_markup=markup)


bot.infinity_polling()


#таблица с запросом - айди запроса, сам вопрос, id статуса, id модератора который взял пользователя, id пользователя
#таблица с диалога - айди сообщения, айди запроса, text
#таблица пользователей *
#таблица с готовыми вопросами - id вопроса, question_text, answer_text
#таблица со статусами статус айди, статус
#добавить в git *
