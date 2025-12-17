import webbrowser
import telebot
from telebot import types
import json
import os

TOKEN = "8337544662:AAEBUgsWPbR4HhVEnRwOpNK5rUWXtv4C3Iw"
bot = telebot.TeleBot(TOKEN)

DESIGNS_FILE = "designs.json"

# временная память: в какой раздел сейчас добавляют фото
current_mood = {}
current_view={}
current_index={}

def load_designs():
    if not os.path.exists(DESIGNS_FILE):
        return {}
    with open(DESIGNS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_designs(data):
    with open(DESIGNS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "📸 Мой Instagram",
            url="https://www.instagram.com/anastasi.yarosh/"
        ),types.InlineKeyboardButton("💅 Идеи дизайна", callback_data="ideas"))

    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 💕\n"
        "Здесь ты можешь выбрать идеи дизайна и вдохновиться 🙂",
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "ideas")
def ideas_menu(call):
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌸 Нежное", callback_data="design_нежное"),
        types.InlineKeyboardButton("🤍 Минимализм", callback_data="design_минимализм"),
        types.InlineKeyboardButton("🖤 Тёмное", callback_data="design_темное"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main")
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выбери своё настроение 💅",
        reply_markup=markup)


# ---------- выбор раздела (режим добавления фото) ----------
# @bot.callback_query_handler(func=lambda call: call.data.startswith("design_"))
# def select_mood(call):
#     bot.answer_callback_query(call.id)
#
#     mood = call.data.replace("design_", "")
#     current_mood[call.from_user.id] = mood
#
#     bot.send_message(
#         call.message.chat.id,
#         f"📸 Отправь фото дизайна — я добавлю его в раздел «{mood}»"
#     )
def send_image(chat_id, user_id):
    designs = load_designs()
    mood = current_view.get(user_id)
    index = current_index.get(user_id, 0)

    items = designs.get(mood, [])

    if not items:
        bot.send_message(chat_id, "Пока нет картинок 😔")
        return

    if index >= len(items):
        current_index[user_id] = 0
        index = 0

    item=items[index]
    file_id = item["file_id"]

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⬅️ Назад", callback_data="back"),
        types.InlineKeyboardButton("🔁 Ещё", callback_data="more")
        )

    bot.send_photo(
        chat_id,
        file_id,
        caption=f"Настроение: {mood} 💅",
        reply_markup=markup
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith("design_"))
def choose_mood(call):
    bot.answer_callback_query(call.id)

    mood = call.data.replace("design_", "")
    user_id = call.from_user.id

    current_view[user_id] = mood
    current_index[user_id] = 0

    send_image(call.message.chat.id, user_id)


# ---------- добавление фото ----------
# @bot.message_handler(content_types=["photo"])
# def add_design_photo(message):
#     user_id = message.from_user.id
#
#     if user_id not in current_mood:
#         bot.reply_to(message, "Сначала выбери раздел дизайна 💅")
#         return
#
#     mood = current_mood[user_id]
#     file_id = message.photo[-1].file_id
#
#     designs = load_designs()
#     designs.setdefault(mood, []).append({
#         "photo": file_id
#     })
#
#     save_designs(designs)
#
#     bot.reply_to(message, f"✅ Фото добавлено в раздел «{mood}»")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back_to_moods(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌸 Нежное", callback_data="design_нежное"),
        types.InlineKeyboardButton("🤍 Минимализм", callback_data="design_минимализм"),
        types.InlineKeyboardButton("🖤 Тёмное", callback_data="design_темное"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="back_main")
    )
    bot.send_message(call.message.chat.id,
                     "Выбери своё настроение 💅",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "more")
def more_images(call):
    bot.answer_callback_query(call.id)

    user_id = call.from_user.id
    current_index[user_id] += 1

    send_image(call.message.chat.id, user_id)


@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call):
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "📸 Мой Instagram",
            url="https://www.instagram.com/anastasi.yarosh/"
        ),
        types.InlineKeyboardButton(
            "💅 Идеи дизайна",
            callback_data="ideas"
        )
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Главное меню 💕",
        reply_markup=markup
    )



# Если юзер мне присылает фото
# @bot.message_handler(content_types=['photo'])
# def get_photo(message):
#     bot.reply_to(message, 'Спасибо за отправленное фото!')

# Если юзер присылает текст
# @bot.message_handler()
# def info(message):
#     if message.text.lower()=='Привет':
#         bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}')
#     elif message.text.lower()=='id':
#         bot.reply_to(message, f'ID:{message.from_user.id}')

bot.polling(none_stop=True)