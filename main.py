import telebot
from telebot import types

API_TOKEN = '6730091039:AAFQruxelojCr-J19dKbY9Uu4aOMO_t6jfg'
CHANNEL_USERNAME = '@y_muhammadyusufxon'
ADMIN_ID = 6855997739  # Sizning Telegram ID'ingiz

bot = telebot.TeleBot(API_TOKEN)

user_likes = {}  # user_id: [post_ids]
post_likes = {}  # post_id: like_count

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

def create_like_button(post_id):
    like_count = post_likes.get(post_id, 0)
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(f"👍 Like ({like_count})", callback_data=f"like|{post_id}")
    keyboard.add(button)
    return keyboard

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "👋 Salom! Kanal postlariga like bosish uchun obuna bo‘ling va postlarni ko‘ring.\nAdmin uchun: /admin_post")

@bot.message_handler(commands=['admin_post'])
def handle_admin_post(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Siz admin emassiz.")
        return

    if message.reply_to_message:
        caption = message.text[12:].strip() or "📹"

        if message.reply_to_message.video:
            sent = bot.send_video(
                chat_id=CHANNEL_USERNAME,
                video=message.reply_to_message.video.file_id,
                caption=caption,
                reply_markup=create_like_button(message.reply_to_message.message_id)
            )
        else:
            sent = bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=caption,
                reply_markup=create_like_button(message.message_id)
            )

    else:
        text = message.text[12:].strip()
        sent = bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=text,
            reply_markup=create_like_button(message.message_id)
        )

    post_likes[sent.message_id] = 0
    bot.reply_to(message, "✅ Post kanalga yuborildi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("like|"))
def handle_like(call):
    user_id = call.from_user.id
    post_id = int(call.data.split('|')[1])

    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "📛 Obuna bo‘ling: {}".format(CHANNEL_USERNAME), show_alert=True)
        return

    if user_id in user_likes and post_id in user_likes[user_id]:
        bot.answer_callback_query(call.id, "✅ Siz allaqachon like bosgansiz.")
        return

    post_likes[post_id] = post_likes.get(post_id, 0) + 1
    user_likes.setdefault(user_id, []).append(post_id)

    new_markup = create_like_button(post_id)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=new_markup)
    except:
        pass

    bot.answer_callback_query(call.id, "👍 Like qabul qilindi!")

if __name__ == '__main__':
    bot.polling(none_stop=True)
