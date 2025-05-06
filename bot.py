import telebot
from config import *
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from db import DatabaseManager

manager = DatabaseManager(DATABASE)

bot = telebot.TeleBot(TOKEN, parse_mode="html")


@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.chat.id, "Привет! Вот такие функции есть у этого бота:\n\n/FAQ - выводит часто задаваемые вопросы\n/question - позволяет задать ваш уникальный вопрос в скором времени на который ответит модератор")


@bot.message_handler(commands=["FAQ"])
def faq(message: Message):
    db_questions = manager.get_prep_questions()
    processed_questions = [f'{i[0]} --- {i[1]}\n\n' for i in db_questions]
    f_questions = []
    for i, m in enumerate(processed_questions, start=1):
        f_questions.append(((str(i) + ". ") + m))
    questions = "".join(f_questions)
    bot.send_message(message.from_user.id, (f"Часто задаваемые вопросы:\n\n" + questions))
    return


@bot.message_handler(commands=["question"])
def question(message: Message):
    bot.send_message(message.chat.id, "Пришли сюда мне свой вопрос! Одним сообщением!")
    manager.add_user(message.from_user.id, message.from_user.username)
    bot.register_next_step_handler(message, get_question)

def get_question(message: Message):
    text = message.text
    deleted_msg = bot.send_message(message.chat.id, "Обрабатываем ваш вопрос, подождите немного")
    manager.add_request(message.from_user.id, text)
    request_id = manager.get_last_request(message.from_user.id)[0]
    manager.add_message(request_id, message.from_user.id, text)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Взять запрос', callback_data=f"confirm_{request_id}_{deleted_msg.message_id}"), InlineKeyboardButton('Отклонить запрос', callback_data=f"cancel_{request_id}_{deleted_msg.message_id}"))
    bot.send_message(ID_GROUP_CHAT, f"Поступил запрос от пользователя @{message.from_user.username if message.from_user.username else ''}\n\n{text}", reply_markup=markup)

@bot.callback_query_handler()
def callback(call:CallbackQuery):
    data = call.data.split('_')
    if 'confirm' in data:
        request_id = data[-2]
        dlt_msg = data[-1]
        moder_id = call.from_user.id
        res = manager.get_request(request_id)
        user_id = res[1]
        manager.update_request(request_id, moder_id)
        bot.send_message(call.message.chat.id, f"Принят запрос модератором {call.from_user.username}, запрос номер {request_id}")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Написать сообщение", callback_data=f"dialog_{request_id}"))
        bot.send_message(moder_id, "Вы приняли запрос, можете начать диалог", reply_markup=markup)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.delete_message(user_id, dlt_msg)
    if "dialog" in data:
        request_id = data[-1]
        manager.update_status(request_id, status_id=2)
        chat_id = call.message.chat.id
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        pishite_msg = bot.send_message(call.message.chat.id, "Пишите")
        pishite_msg_id = pishite_msg.message_id
        bot.register_next_step_handler(call.message, get_answer, request_id, pishite_msg_id)
    if "cancel" in data:
        request_id = data[-2]
        dlt_msg = data[-1]
        result = manager.get_request(request_id)
        moder_id = result[0]
        user_id = result[1]
        bot.delete_message(user_id, dlt_msg)
        bot.send_message(call.message.chat.id, f"Запрос отклонен модератором {call.from_user.username}, номер запроса {request_id}")
        bot.send_message(user_id, "Ваш запрос был отклонен, посмотрите ответ в часто задаваемых вопросах по команде /FAQ")
        bot.delete_message(call.message.chat.id, call.message.id)
    if "close" in data:
        request_id = data[-1]
        res = manager.get_request(request_id)
        user_id = res[1]
        bot.send_message(user_id, "Сессия закрыта\n\nСпасибо за то что обратились в поддержку, надеемся что наши модераторы смогли вам помочь!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return


def get_answer(message: Message, request_id, pishite_msg_id):
    try:
        bot.delete_message(message.chat.id, pishite_msg_id)
    except:
        pass
    text = message.text
    unknown_user = message.from_user.id
    manager.add_message(request_id, unknown_user, text)
    result = manager.get_request(request_id)
    moder_id = result[0]
    user_id = result[1]
    user_markup = InlineKeyboardMarkup()
    moder_markup = InlineKeyboardMarkup()
    user_markup.add(InlineKeyboardButton("Написать сообщение", callback_data=f"dialog_{request_id}"))
    moder_markup.add(InlineKeyboardButton("Написать сообщение", callback_data=f"dialog_{request_id}"), InlineKeyboardButton("Закрыть сессию", callback_data=f"close_{request_id}"))
    dialog = ""
    all_text = manager.get_all_text(request_id)
    for msg in all_text:
        tg, txt = msg
        dialog += f"{'Модератор:' if unknown_user == tg else 'Вы:'} {txt}\n"
    if unknown_user == moder_id:
        bot.send_message(user_id, dialog, reply_markup=user_markup)
    elif unknown_user == user_id:
        dialog += f"\n\nЗапрос номер {request_id}"
        bot.send_message(moder_id, dialog, reply_markup=moder_markup)


bot.infinity_polling()
