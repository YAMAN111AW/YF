import telebot
from telebot import types
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import string
import os
from datetime import datetime, timezone, timedelta

# ============ الإعدادات ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8956086702:AAEtcqzxJwA7W7daV3s4DiDMjSMTt9InJ3k")
ADMIN_ID = 6382473367
PAYMENT_NUMBER = "0984674400"
SUPPORT_USERNAME = "@Yamen494"
CHANNEL_USERNAME = "@YF494YF"
CHANNEL_LINK = "https://t.me/YF494YF"
DATABASE_URL = os.environ.get("DATABASE_URL",
    "postgresql://postgres:FmMcTnFMJbldpynWXDwrFfXISsKbYKvt@postgres.railway.internal:5432/railway")

ORDERS_OPEN_HOUR = 12
ORDERS_CLOSE_HOUR = 22

bot = telebot.TeleBot(BOT_TOKEN)

# ============ الأسعار ============
PACKAGES = {
    "ff": {
        "title": {"ar": "🔥 فري فاير", "en": "🔥 Free Fire"},
        "items": {
            "ff_110": {"ar": "110 جوهرة 💎", "en": "110 Diamonds 💎", "price": "160 ل.س"},
            "ff_231": {"ar": "231 جوهرة 💎", "en": "231 Diamonds 💎", "price": "290 ل.س"},
            "ff_583": {"ar": "583 جوهرة 💎", "en": "583 Diamonds 💎", "price": "700 ل.س"},
        }
    },
    "pubg": {
        "title": {"ar": "🎯 ببجي", "en": "🎯 PUBG"},
        "items": {
            "pubg_60":   {"ar": "60 شدة 🪙",   "en": "60 UC 🪙",   "price": "135 ل.س"},
            "pubg_325":  {"ar": "325 شدة 🪙",  "en": "325 UC 🪙",  "price": "650 ل.س"},
            "pubg_660":  {"ar": "660 شدة 🪙",  "en": "660 UC 🪙",  "price": "1275 ل.س"},
            "pubg_1800": {"ar": "1800 شدة 🪙", "en": "1800 UC 🪙", "price": "3180 ل.س"},
        }
    }
}

# ============ الترجمة ============
TEXTS = {
    "ar": {
        "welcome": (
            "👋 أهلاً بك <b>{name}</b> في بوت شحن الجواهر والشدات 💎🔥\n\n"
            "🎯 <b>فكرة البوت:</b>\n"
            "يمكنك شحن فري فاير (جواهر) أو ببجي (شدات) عبر سيرياتيل كاش ✅\n\n"
            "📌 <b>طريقة الشراء:</b>\n"
            "1️⃣ اختر اللعبة\n2️⃣ اختر العرض\n3️⃣ أرسل ID حسابك\n"
            "4️⃣ أرسل اسمك في اللعبة\n5️⃣ حوّل المبلغ عبر سيرياتيل كاش\n"
            "6️⃣ انتظر موافقة الإدارة ✅\n\n"
            "⏰ <b>الطلبات تُقبل من 12 ظهرًا حتى 10 مساءً بتوقيت السعودية</b> 🇸🇦"
        ),
        "subscribe_required": (
            "🔒 <b>عذرًا عزيزي!</b>\n\n"
            "⚠️ يجب عليك <b>الاشتراك في قناتنا أولاً</b> لاستخدام البوت 💎\n\n"
            f"📢 القناة: {CHANNEL_USERNAME}\n\n"
            "1️⃣ اضغط زر <b>اشترك في القناة</b>\n2️⃣ اشترك ✅\n3️⃣ ارجع واضغط <b>تحقق</b> 🔄"
        ),
        "btn_subscribe": "📢 اشترك في القناة",
        "btn_check": "✅ تحقق من الاشتراك",
        "btn_ff": "🔥 Free Fire",
        "btn_pubg": "🎯 PUBG",
        "btn_info": "👤 معلوماتي",
        "btn_support": "🆘 تواصل مع الدعم",
        "btn_settings": "⚙️ الإعدادات",
        "btn_back": "⬅️ رجوع",
        "btn_cancel": "❌ إلغاء",
        "btn_send_message": "✉️ إرسال شكوى / اقتراح",
        "btn_inbox": "📬 البريد الوارد",
        "check_success": "✅ تم التحقق بنجاح! أهلاً بك 🎉",
        "check_fail": "❌ لم تشترك في القناة بعد!",
        "orders_closed": (
            "⛔ عذرًا، البوت لا يستقبل الطلبات حاليًا.\n"
            "🕛 ساعات العمل: من <b>12 ظهرًا</b> حتى <b>10 مساءً</b> بتوقيت السعودية 🇸🇦"
        ),
        "choose_package": "💎 <b>قائمة أسعار {game}:</b>\n\nاختر العرض الذي تريده 👇",
        "chosen": (
            "✅ اخترت: <b>{item}</b> بسعر <b>{price}</b>\n\n"
            "🆔 أرسل <b>ID حسابك في {game}</b>:\n\n"
            "💡 <i>ملاحظة: يجب أن يكون ID حقيقي (أرقام فقط)</i>"
        ),
        "invalid_id_ff": (
            "❌ <b>ID Free Fire غير صالح!</b>\n\n"
            "⚠️ {reason}\n\n"
            "📌 <b>شروط ID فري فاير:</b>\n"
            "• أرقام فقط 🔢\n"
            "• من 5 إلى 15 رقم\n"
            "• لا يبدأ بـ 0\n\n"
            "🔁 أرسل ID صحيح:"
        ),
        "invalid_id_pubg": (
            "❌ <b>ID PUBG غير صالح!</b>\n\n"
            "⚠️ {reason}\n\n"
            "📌 <b>شروط ID ببجي:</b>\n"
            "• أرقام فقط 🔢\n"
            "• من 9 إلى 12 رقم\n"
            "• لا يبدأ بـ 0\n\n"
            "🔁 أرسل ID صحيح:"
        ),
        "send_name": "📝 ممتاز! الآن أرسل <b>اسمك داخل اللعبة</b>:",
        "invalid_name": "❌ الاسم قصير جدًا! أرسل اسمك الصحيح:",
        "final_step": (
            "🎉 <b>الخطوة الأخيرة!</b>\n\n"
            "💳 أرسل المبلغ <b>{price}</b> إلى:\n"
            "<code>{number}</code>\n"
            "عبر <b>سيرياتيل كاش</b> حصرًا 📲\n\n"
            "⚠️ سيتم مراجعة طلبك ✅\n"
            "🔖 رقم طلبك: <b>#{oid}</b>"
        ),
        "accepted": "✅ <b>تم قبول طلبك!</b>\n\n💎 <b>{item}</b> سيصلك خلال <b>5 دقائق</b> ⏳\n\nشكرًا ❤️",
        "rejected": "❌ عذرًا، تم <b>رفض طلبك</b>.\nتواصل مع الدعم 🆘",
        "my_info": (
            "👤 <b>معلوماتك:</b>\n\n"
            "📛 الاسم: <b>{name}</b>\n"
            "🆔 الآيدي: <code>{rid}</code>\n"
            "📅 التسجيل: {joined}\n"
            "🌐 اللغة: {lang}\n\n"
            "🧾 <b>آخر عمليات الشراء:</b>\n{orders}"
        ),
        "no_orders": "لا يوجد أي عمليات شراء حتى الآن 😕",
        "support": (
            "🆘 <b>مركز الدعم الفني</b>\n\n"
            f"👨‍💻 للتواصل: {SUPPORT_USERNAME}\n\n"
            "📖 <b>طريقة الاستخدام:</b>\n"
            "1️⃣ اختر اللعبة\n2️⃣ اختر عرض الشحن 💎\n"
            "3️⃣ أرسل ID حسابك 🆔\n4️⃣ أرسل اسمك في اللعبة 📝\n"
            f"5️⃣ حوّل المبلغ عبر سيرياتيل كاش إلى:\n   <code>{PAYMENT_NUMBER}</code>\n"
            "6️⃣ انتظر الموافقة ✅\n7️⃣ تصلك الجواهر/الشدات خلال 5 دقائق ⏳\n\n"
            "⏰ <b>ساعات العمل:</b> 12 ظهرًا - 10 مساءً 🇸🇦\n\n"
            "👇 يمكنك إرسال شكوى أو اقتراح عبر الزر بالأسفل:"
        ),
        "btn_complaint": "✉️ إرسال شكوى / اقتراح",
        "ask_message": (
            "✉️ <b>أرسل رسالتك الآن</b>\n\n"
            "📝 اكتب شكواك، اقتراحك، أو أي استفسار\n"
            "سيتم إرسالها للإدارة مباشرة ✅\n\n"
            "لإلغاء الإرسال اضغط زر الرجوع 👇"
        ),
        "message_sent": "✅ <b>تم إرسال رسالتك بنجاح!</b>\n\nسيتم الرد عليك في أقرب وقت 📩",
        "message_too_short": "❌ الرسالة قصيرة جدًا! أرسل رسالة أطول:",
        "inbox_title": "📬 <b>البريد الوارد</b>\n\n📥 عدد الرسائل: <b>{count}</b>",
        "inbox_empty": "📭 لا يوجد رسائل حتى الآن",
        "inbox_item": (
            "📩 <b>رسالة #{n}</b>\n\n"
            "👤 من: <b>{name}</b>\n"
            "🆔 <code>{uid}</code>\n"
            "🕒 {time}\n\n"
            "💬 <b>الرسالة:</b>\n{msg}"
        ),
        "settings_admin": "⚙️ <b>الإعدادات (أدمن)</b>\n\nاختر:",
        "settings_user": "⚙️ <b>الإعدادات</b>\n\nاختر:",
        "btn_change_lang": "🌐 تغيير اللغة",
        "btn_change_order": "🔀 ترتيب الأزرار (أدمن)",
        "btn_reset_data": "🗑️ تصفير بياناتي",
        "lang_changed": "✅ تم تغيير اللغة إلى العربية 🇸🇦",
        "lang_pick": "🌐 اختر اللغة:",
        "reset_confirm": "⚠️ هل أنت متأكد من حذف كل بياناتك؟\n\nهذا لا يمكن التراجع عنه!",
        "reset_done": "🗑️ تم حذف جميع بياناتك ✅",
        "btn_yes": "✅ نعم، احذف",
        "btn_no": "❌ إلغاء",
        "order_current": "🔀 <b>ترتيب الأزرار الحالي:</b>\n\n{order}\n\nاختر:",
        "order_changed": "✅ تم تغيير الترتيب!",
        "btn_order_default": "1️⃣ Free Fire ثم PUBG",
        "btn_order_swapped": "2️⃣ PUBG ثم Free Fire",
        "cancelled": "❌ تم الإلغاء",
        "back_done": "⬅️ رجعنا للخطوة السابقة",
    },
    "en": {
        "welcome": (
            "👋 Welcome <b>{name}</b> to the Diamonds & UC bot 💎🔥\n\n"
            "🎯 <b>Bot purpose:</b>\nTop up Free Fire or PUBG via Syriatel Cash ✅\n\n"
            "📌 <b>How to buy:</b>\n1️⃣ Choose game\n2️⃣ Choose package\n"
            "3️⃣ Send your ID\n4️⃣ Send in-game name\n5️⃣ Pay via Syriatel Cash\n"
            "6️⃣ Wait for approval ✅\n\n"
            "⏰ <b>Orders: 12 PM - 10 PM (Saudi time)</b> 🇸🇦"
        ),
        "subscribe_required": (
            "🔒 <b>Sorry!</b>\n\n⚠️ Subscribe to our channel first 💎\n\n"
            f"📢 {CHANNEL_USERNAME}\n\n1️⃣ Subscribe\n2️⃣ Join ✅\n3️⃣ Check 🔄"
        ),
        "btn_subscribe": "📢 Subscribe",
        "btn_check": "✅ Check subscription",
        "btn_ff": "🔥 Free Fire",
        "btn_pubg": "🎯 PUBG",
        "btn_info": "👤 My info",
        "btn_support": "🆘 Support",
        "btn_settings": "⚙️ Settings",
        "btn_back": "⬅️ Back",
        "btn_cancel": "❌ Cancel",
        "btn_send_message": "✉️ Send complaint/suggestion",
        "btn_inbox": "📬 Inbox",
        "check_success": "✅ Verified! Welcome 🎉",
        "check_fail": "❌ Not subscribed yet!",
        "orders_closed": "⛔ Orders closed.\n🕛 Working: 12 PM - 10 PM 🇸🇦",
        "choose_package": "💎 <b>{game} prices:</b>\n\nChoose 👇",
        "chosen": (
            "✅ Chosen: <b>{item}</b> for <b>{price}</b>\n\n"
            "🆔 Send your <b>{game} ID</b>:\n\n"
            "💡 <i>Must be a valid ID (digits only)</i>"
        ),
        "invalid_id_ff": (
            "❌ <b>Invalid Free Fire ID!</b>\n\n⚠️ {reason}\n\n"
            "📌 <b>FF ID rules:</b>\n• Digits only 🔢\n• 5-15 digits\n• No leading 0\n\n"
            "🔁 Send a valid ID:"
        ),
        "invalid_id_pubg": (
            "❌ <b>Invalid PUBG ID!</b>\n\n⚠️ {reason}\n\n"
            "📌 <b>PUBG ID rules:</b>\n• Digits only 🔢\n• 9-12 digits\n• No leading 0\n\n"
            "🔁 Send a valid ID:"
        ),
        "send_name": "📝 Now send your <b>in-game name</b>:",
        "invalid_name": "❌ Name too short!",
        "final_step": (
            "🎉 <b>Final step!</b>\n\n"
            "💳 Send <b>{price}</b> to:\n<code>{number}</code>\n"
            "via <b>Syriatel Cash</b> only 📲\n\n"
            "⚠️ Will be reviewed ✅\n🔖 Order #<b>{oid}</b>"
        ),
        "accepted": "✅ <b>Accepted!</b>\n\n💎 <b>{item}</b> within <b>5 min</b> ⏳\n\nThanks ❤️",
        "rejected": "❌ Order <b>rejected</b>.\nContact support 🆘",
        "my_info": (
            "👤 <b>Your info:</b>\n\n📛 {name}\n🆔 <code>{rid}</code>\n"
            "📅 {joined}\n🌐 {lang}\n\n🧾 <b>Recent orders:</b>\n{orders}"
        ),
        "no_orders": "No orders yet 😕",
        "support": (
            "🆘 <b>Support Center</b>\n\n"
            f"👨‍💻 {SUPPORT_USERNAME}\n\n"
            "📖 <b>How to use:</b>\n"
            "1️⃣ Choose game\n2️⃣ Choose package 💎\n"
            "3️⃣ Send ID 🆔\n4️⃣ Send name 📝\n"
            f"5️⃣ Pay via Syriatel Cash to:\n   <code>{PAYMENT_NUMBER}</code>\n"
            "6️⃣ Wait ✅\n7️⃣ Receive in 5 min ⏳\n\n"
            "⏰ <b>Working: 12 PM - 10 PM</b> 🇸🇦\n\n"
            "👇 Send a complaint/suggestion:"
        ),
        "btn_complaint": "✉️ Send complaint/suggestion",
        "ask_message": (
            "✉️ <b>Send your message</b>\n\n"
            "📝 Complaint, suggestion, or inquiry\n"
            "Will be sent directly ✅\n\n"
            "To cancel, press Back 👇"
        ),
        "message_sent": "✅ <b>Message sent!</b>\n\nWe'll reply soon 📩",
        "message_too_short": "❌ Too short!",
        "inbox_title": "📬 <b>Inbox</b>\n\n📥 Messages: <b>{count}</b>",
        "inbox_empty": "📭 No messages yet",
        "inbox_item": (
            "📩 <b>Message #{n}</b>\n\n👤 From: <b>{name}</b>\n"
            "🆔 <code>{uid}</code>\n🕒 {time}\n\n💬 <b>Message:</b>\n{msg}"
        ),
        "settings_admin": "⚙️ <b>Settings (Admin)</b>\n\nChoose:",
        "settings_user": "⚙️ <b>Settings</b>\n\nChoose:",
        "btn_change_lang": "🌐 Change language",
        "btn_change_order": "🔀 Button order (Admin)",
        "btn_reset_data": "🗑️ Reset my data",
        "lang_changed": "✅ Language: English 🇬🇧",
        "lang_pick": "🌐 Choose language:",
        "reset_confirm": "⚠️ Delete all your data?\n\nCannot be undone!",
        "reset_done": "🗑️ Data deleted ✅",
        "btn_yes": "✅ Yes, delete",
        "btn_no": "❌ Cancel",
        "order_current": "🔀 <b>Current order:</b>\n\n{order}\n\nChoose:",
        "order_changed": "✅ Order changed!",
        "btn_order_default": "1️⃣ Free Fire then PUBG",
        "btn_order_swapped": "2️⃣ PUBG then Free Fire",
        "cancelled": "❌ Cancelled",
        "back_done": "⬅️ Back",
    }
}

# ============ قاعدة البيانات ============
def db_connect():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            random_id TEXT,
            language TEXT DEFAULT 'ar',
            joined_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            user_id BIGINT,
            game TEXT,
            package TEXT,
            price TEXT,
            game_id TEXT,
            player_name TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            full_name TEXT,
            message TEXT,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TEXT
        )
    """)
    cur.execute("INSERT INTO settings VALUES ('button_order', 'ff,pubg') ON CONFLICT (key) DO NOTHING")
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ============ دوال مساعدة ============
def gen_random_id():
    return "USR-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_user(uid):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
    u = cur.fetchone()
    cur.close(); conn.close()
    return u

def ensure_user(message):
    uid = message.from_user.id
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (uid,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, random_id, language, joined_at) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (uid, message.from_user.username or "", message.from_user.full_name,
             gen_random_id(), "ar", datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
    cur.close(); conn.close()

def get_lang(uid):
    u = get_user(uid)
    return u["language"] if u and u["language"] else "ar"

def t(uid, key, **kwargs):
    lang = get_lang(uid)
    text = TEXTS.get(lang, TEXTS["ar"]).get(key, "")
    return text.format(**kwargs) if kwargs else text

def get_button_order():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = 'button_order'")
    row = cur.fetchone()
    cur.close(); conn.close()
    return row["value"] if row else "ff,pubg"

def set_button_order(value):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET value = %s WHERE key = 'button_order'", (value,))
    conn.commit()
    cur.close(); conn.close()

def is_orders_open():
    now = datetime.now(timezone(timedelta(hours=3)))
    return ORDERS_OPEN_HOUR <= now.hour < ORDERS_CLOSE_HOUR

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"❌ {e}")
        return False

# ============ التحقق الذكي من ID ============
def validate_game_id(game_id: str, game: str):
    game_id = game_id.strip()
    
    # فحص عام
    if not game_id.isdigit():
        return False, "يجب أن يحتوي على أرقام فقط / digits only"
    if game_id.startswith("0"):
        return False, "لا يبدأ بـ 0 / no leading 0"

    # فحص حسب اللعبة
    if game == "ff":
        if len(game_id) < 5:
            return False, "ID فري فاير أقل من 5 أرقام / FF ID < 5 digits"
        if len(game_id) > 15:
            return False, "ID فري فاير أكثر من 15 رقم / FF ID > 15 digits"
    elif game == "pubg":
        if len(game_id) < 9:
            return False, "ID ببجي أقل من 9 أرقام / PUBG ID < 9 digits"
        if len(game_id) > 12:
            return False, "ID ببجي أكثر من 12 رقم / PUBG ID > 12 digits"

    return True, game_id

# ============ لوحات الأزرار ============
def main_keyboard(uid):
    lang = get_lang(uid)
    T = TEXTS[lang]
    order = get_button_order().split(",")
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    row1 = []
    for g in order:
        if g == "ff":
            row1.append(T["btn_ff"])
        elif g == "pubg":
            row1.append(T["btn_pubg"])
    kb.row(*row1)

    kb.row(T["btn_info"], T["btn_settings"])

    if uid == ADMIN_ID:
        kb.row(T["btn_support"], T["btn_inbox"])
    else:
        kb.row(T["btn_support"])

    return kb

def back_keyboard(uid):
    lang = get_lang(uid)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(TEXTS[lang]["btn_back"])
    return kb

# ============ رسالة الترحيب ============
def send_welcome(chat_id, first_name, uid):
    bot.send_message(
        chat_id, t(uid, "welcome", name=first_name),
        parse_mode="HTML", reply_markup=main_keyboard(uid)
    )

def show_subscription_message(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_subscribe"), url=CHANNEL_LINK))
    kb.add(types.InlineKeyboardButton(t(uid, "btn_check"), callback_data="check_sub"))
    bot.send_message(chat_id, t(uid, "subscribe_required"), parse_mode="HTML", reply_markup=kb)

# ============ حالة الرجوع ============
def save_step(uid, step, data=None):
    bot.user_data = getattr(bot, "user_data", {})
    if uid not in bot.user_data:
        bot.user_data[uid] = {}
    bot.user_data[uid]["step"] = step
    if data:
        bot.user_data[uid].update(data)

def go_back(message):
    uid = message.from_user.id
    bot.user_data = getattr(bot, "user_data", {})
    data = bot.user_data.get(uid, {})
    step = data.get("step", 1)

    if step <= 2:
        bot.send_message(message.chat.id, t(uid, "back_done"),
                         reply_markup=main_keyboard(uid))
        bot.user_data[uid]["step"] = 1
    elif step == 3:
        game = data.get("game", "ff")
        show_game_packages_manual(message.chat.id, uid, game)
        bot.user_data[uid]["step"] = 2
    elif step == 4:
        msg = bot.send_message(
            message.chat.id,
            t(uid, "chosen",
              item=data.get("package_name", ""),
              price=data.get("price", ""),
              game=PACKAGES[data.get("game", "ff")]["title"][get_lang(uid)]),
            parse_mode="HTML",
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_game_id)
        bot.user_data[uid]["step"] = 3
    elif step == 5:
        msg = bot.send_message(message.chat.id, t(uid, "send_name"),
                                parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_player_name)
        bot.user_data[uid]["step"] = 4

# ============ /start ============
@bot.message_handler(commands=['start'])
def cmd_start(message):
    ensure_user(message)
    uid = message.from_user.id
    if is_subscribed(uid):
        send_welcome(message.chat.id, message.from_user.first_name, uid)
        save_step(uid, 1)
    else:
        show_subscription_message(message.chat.id, uid)

# ============ التحقق من الاشتراك ============
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    uid = call.from_user.id
    if is_subscribed(uid):
        bot.answer_callback_query(call.id, t(uid, "check_success"))
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_welcome(call.message.chat.id, call.from_user.first_name, uid)
        save_step(uid, 1)
    else:
        bot.answer_callback_query(call.id, t(uid, "check_fail"), show_alert=True)

# ============ أزرار اللعب ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_ff"], TEXTS["en"]["btn_ff"]])
def show_ff(message):
    show_game_packages(message, "ff")

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_pubg"], TEXTS["en"]["btn_pubg"]])
def show_pubg(message):
    show_game_packages(message, "pubg")

def show_game_packages(message, game):
    ensure_user(message)
    uid = message.from_user.id

    if not is_subscribed(uid):
        show_subscription_message(message.chat.id, uid)
        return

    if not is_orders_open():
        bot.send_message(message.chat.id, t(uid, "orders_closed"), parse_mode="HTML")
        return

    save_step(uid, 2, {"game": game})
    show_game_packages_manual(message.chat.id, uid, game)

def show_game_packages_manual(chat_id, uid, game):
    lang = get_lang(uid)
    game_data = PACKAGES[game]
    game_title = game_data["title"][lang]

    kb = types.InlineKeyboardMarkup(row_width=1)
    for key, item in game_data["items"].items():
        kb.add(types.InlineKeyboardButton(
            text=f"{item[lang]} — {item['price']}",
            callback_data=f"pkg|{game}|{key}"
        ))

    bot.send_message(
        chat_id,
        t(uid, "choose_package", game=game_title),
        parse_mode="HTML",
        reply_markup=kb
    )

# ============ اختيار العرض ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg|"))
def choose_package(call):
    _, game, key = call.data.split("|")
    uid = call.from_user.id
    lang = get_lang(uid)
    item = PACKAGES[game]["items"][key]

    bot.answer_callback_query(call.id, "✅")
    save_step(uid, 3, {
        "game": game,
        "package_key": key,
        "package_name": item[lang],
        "price": item["price"]
    })

    game_title = PACKAGES[game]["title"][lang]
    msg = bot.send_message(
        call.message.chat.id,
        t(uid, "chosen", item=item[lang], price=item["price"], game=game_title),
        parse_mode="HTML",
        reply_markup=back_keyboard(uid)
    )
    bot.register_next_step_handler(msg, get_game_id)

# ============ ID اللعبة ============
def get_game_id(message):
    uid = message.from_user.id

    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        go_back(message)
        return

    bot.user_data = getattr(bot, "user_data", {})
    data = bot.user_data.get(uid)
    if not data:
        bot.send_message(message.chat.id, "⚠️ اضغط /start من جديد.")
        return

    game = data.get("game", "ff")
    game_id = message.text.strip() if message.text else ""
    valid, result = validate_game_id(game_id, game)

    if not valid:
        key = "invalid_id_ff" if game == "ff" else "invalid_id_pubg"
        msg = bot.send_message(
            message.chat.id,
            t(uid, key, reason=result),
            parse_mode="HTML",
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_game_id)
        return

    bot.user_data[uid]["game_id"] = result
    bot.user_data[uid]["step"] = 4

    msg = bot.send_message(
        message.chat.id, t(uid, "send_name"),
        parse_mode="HTML",
        reply_markup=back_keyboard(uid)
    )
    bot.register_next_step_handler(msg, get_player_name)

# ============ اسم اللاعب ============
def get_player_name(message):
    uid = message.from_user.id

    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        go_back(message)
        return

    bot.user_data = getattr(bot, "user_data", {})
    data = bot.user_data.get(uid)
    if not data:
        bot.send_message(message.chat.id, "⚠️ اضغط /start من جديد.")
        return

    player_name = message.text.strip() if message.text else ""
    if len(player_name) < 2:
        msg = bot.send_message(
            message.chat.id, t(uid, "invalid_name"),
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_player_name)
        return

    bot.user_data[uid]["player_name"] = player_name
    bot.user_data[uid]["step"] = 5

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, game, package, price, game_id, player_name, status, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_id",
        (uid, data["game"], data["package_name"], data["price"],
         data["game_id"], player_name, "pending",
         datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    order_id = cur.fetchone()["order_id"]
    conn.commit()
    cur.close(); conn.close()

    bot.send_message(
        message.chat.id,
        t(uid, "final_step", price=data["price"], number=PAYMENT_NUMBER, oid=order_id),
        parse_mode="HTML",
        reply_markup=main_keyboard(uid)
    )

    admin_text = (
        "🔔 <b>طلب شراء جديد!</b>\n\n"
        f"🔖 رقم الطلب: <b>#{order_id}</b>\n"
        f"👤 المستخدم: {message.from_user.full_name}\n"
        f"🆔 يوزر: @{message.from_user.username or 'لا يوجد'}\n"
        f"🆔 تلغرام آيدي: <code>{uid}</code>\n\n"
        f"🎮 اللعبة: <b>{data['game'].upper()}</b>\n"
        f"💎 العرض: <b>{data['package_name']}</b>\n"
        f"💰 السعر: <b>{data['price']}</b>\n"
        f"🎮 ID اللعبة: <code>{data['game_id']}</code>\n"
        f"📝 اسم اللاعب: <b>{player_name}</b>\n\n"
        "اضغط زر الموافقة بعد التأكد:"
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ قبول", callback_data=f"accept|{order_id}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"reject|{order_id}")
    )
    bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML", reply_markup=kb)

# ============ قبول / رفض ============
@bot.callback_query_handler(func=lambda c: c.data.startswith(("accept|", "reject|")))
def handle_decision(call):
    action, oid = call.data.split("|")
    oid = int(oid)

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT user_id, package FROM orders WHERE order_id = %s", (oid,))
    row = cur.fetchone()
    if not row:
        bot.answer_callback_query(call.id, "⚠️ غير موجود")
        cur.close(); conn.close(); return

    user_id = row["user_id"]
    package = row["package"]

    if action == "accept":
        cur.execute("UPDATE orders SET status = 'accepted' WHERE order_id = %s", (oid,))
        conn.commit()
        bot.send_message(user_id, t(user_id, "accepted", item=package), parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅")
    else:
        cur.execute("UPDATE orders SET status = 'rejected' WHERE order_id = %s", (oid,))
        conn.commit()
        bot.send_message(user_id, t(user_id, "rejected"), parse_mode="HTML")
        bot.answer_callback_query(call.id, "❌")

    cur.close(); conn.close()
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except: pass

# ============ زر معلوماتي ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_info"], TEXTS["en"]["btn_info"]])
def my_info(message):
    ensure_user(message)
    uid = message.from_user.id

    if not is_subscribed(uid):
        show_subscription_message(message.chat.id, uid)
        return

    u = get_user(uid)
    lang = get_lang(uid)

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT order_id, package, price, status, created_at FROM orders "
        "WHERE user_id = %s ORDER BY order_id DESC LIMIT 5", (uid,)
    )
    orders = cur.fetchall()
    cur.close(); conn.close()

    status_map = {
        "pending": "⏳ قيد المراجعة" if lang == "ar" else "⏳ Pending",
        "accepted": "✅ مقبول" if lang == "ar" else "✅ Accepted",
        "rejected": "❌ مرفوض" if lang == "ar" else "❌ Rejected",
    }

    if not orders:
        orders_text = t(uid, "no_orders")
    else:
        orders_text = ""
        for o in orders:
            orders_text += (
                f"\n🔖 #{o['order_id']} — {o['package']} ({o['price']})\n"
                f"   {status_map.get(o['status'], o['status'])} | {o['created_at']}\n"
            )

    bot.send_message(
        message.chat.id,
        t(uid, "my_info",
          name=message.from_user.full_name,
          rid=u["random_id"] if u else "-",
          joined=u["joined_at"] if u else "-",
          lang="العربية 🇸🇦" if lang == "ar" else "English 🇬🇧",
          orders=orders_text),
        parse_mode="HTML"
    )

# ============ زر الدعم ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_support"], TEXTS["en"]["btn_support"]])
def support(message):
    uid = message.from_user.id
    if not is_subscribed(uid):
        show_subscription_message(message.chat.id, uid)
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_complaint"), callback_data="send_complaint"))

    bot.send_message(message.chat.id, t(uid, "support"), parse_mode="HTML", reply_markup=kb)

# ============ إرسال شكوى / اقتراح ============
@bot.callback_query_handler(func=lambda c: c.data == "send_complaint")
def ask_complaint(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        t(uid, "ask_message"),
        parse_mode="HTML",
        reply_markup=back_keyboard(uid)
    )
    bot.register_next_step_handler(msg, receive_complaint)

def receive_complaint(message):
    uid = message.from_user.id

    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid))
        return

    text = message.text.strip() if message.text else ""
    if len(text) < 5:
        msg = bot.send_message(
            message.chat.id, t(uid, "message_too_short"),
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, receive_complaint)
        return

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (user_id, username, full_name, message, created_at) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (uid, message.from_user.username or "", message.from_user.full_name,
         text, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    msg_id = cur.fetchone()["id"]
    conn.commit()
    cur.close(); conn.close()

    bot.send_message(message.chat.id, t(uid, "message_sent"), parse_mode="HTML",
                     reply_markup=main_keyboard(uid))

    # إشعار الأدمن
    admin_text = (
        "📩 <b>رسالة جديدة من المستخدمين!</b>\n\n"
        f"🔖 رقم: #{msg_id}\n"
        f"👤 من: {message.from_user.full_name}\n"
        f"🆔 <code>{uid}</code>\n"
        f"🌐 @{message.from_user.username or 'لا يوجد'}\n\n"
        f"💬 <b>الرسالة:</b>\n{text}"
    )
    bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")

# ============ البريد الوارد (للأدمن) ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_inbox"], TEXTS["en"]["btn_inbox"]] and m.from_user.id == ADMIN_ID)
def show_inbox(message):
    uid = message.from_user.id

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 20")
    msgs = cur.fetchall()
    cur.close(); conn.close()

    if not msgs:
        bot.send_message(message.chat.id, t(uid, "inbox_empty"))
        return

    bot.send_message(message.chat.id, t(uid, "inbox_title", count=len(msgs)), parse_mode="HTML")

    for m in msgs:
        text = t(uid, "inbox_item",
                 n=m["id"], name=m["full_name"], uid=m["user_id"],
                 time=m["created_at"], msg=m["message"])
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            "👤 الرد على المستخدم", url=f"tg://user?id={m['user_id']}"
        ))
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=kb)

# ============ زر الإعدادات ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_settings"], TEXTS["en"]["btn_settings"]])
def settings_menu(message):
    uid = message.from_user.id
    ensure_user(message)

    if not is_subscribed(uid):
        show_subscription_message(message.chat.id, uid)
        return

    is_admin = (uid == ADMIN_ID)

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_change_lang"), callback_data="cfg_lang"))
    if is_admin:
        kb.add(types.InlineKeyboardButton(t(uid, "btn_change_order"), callback_data="cfg_order"))
    kb.add(types.InlineKeyboardButton(t(uid, "btn_reset_data"), callback_data="cfg_reset"))

    title = t(uid, "settings_admin") if is_admin else t(uid, "settings_user")
    bot.send_message(message.chat.id, title, parse_mode="HTML", reply_markup=kb)

# ============ معالج الإعدادات ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("cfg_"))
def cfg_handler(call):
    uid = call.from_user.id
    action = call.data

    if action == "cfg_lang":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang|ar"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang|en"),
        )
        bot.edit_message_text(
            t(uid, "lang_pick"),
            call.message.chat.id, call.message.message_id,
            reply_markup=kb
        )

    elif action == "cfg_order" and uid == ADMIN_ID:
        current = get_button_order()
        order_str = "🔥 FF → 🎯 PUBG" if current == "ff,pubg" else "🎯 PUBG → 🔥 FF"
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_default"), callback_data="set_order|ff,pubg"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_swapped"), callback_data="set_order|pubg,ff"))
        bot.edit_message_text(
            t(uid, "order_current", order=order_str),
            call.message.chat.id, call.message.message_id,
            parse_mode="HTML", reply_markup=kb
        )

    elif action == "cfg_reset":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton(t(uid, "btn_yes"), callback_data="do_reset"),
            types.InlineKeyboardButton(t(uid, "btn_no"), callback_data="cancel_reset"),
        )
        bot.edit_message_text(
            t(uid, "reset_confirm"),
            call.message.chat.id, call.message.message_id,
            reply_markup=kb
        )

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_lang|"))
def set_lang(call):
    uid = call.from_user.id
    new_lang = call.data.split("|")[1]

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET language = %s WHERE user_id = %s", (new_lang, uid))
    conn.commit()
    cur.close(); conn.close()

    bot.answer_callback_query(call.id, t(uid, "lang_changed"))
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, t(uid, "lang_changed"),
                     reply_markup=main_keyboard(uid))

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_order|"))
def set_order(call):
    uid = call.from_user.id
    if uid != ADMIN_ID:
        bot.answer_callback_query(call.id, "🚫", show_alert=True)
        return

    new_order = call.data.split("|")[1]
    set_button_order(new_order)

    bot.answer_callback_query(call.id, t(uid, "order_changed"))
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, t(uid, "order_changed"),
                     reply_markup=main_keyboard(uid))

@bot.callback_query_handler(func=lambda c: c.data == "do_reset")
def do_reset(call):
    uid = call.from_user.id

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE user_id = %s", (uid,))
    cur.execute("DELETE FROM users WHERE user_id = %s", (uid,))
    conn.commit()
    cur.close(); conn.close()

    bot.answer_callback_query(call.id, "🗑️")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass

    bot.send_message(call.message.chat.id, t(uid, "reset_done"))
    cmd_start(call.message)

@bot.callback_query_handler(func=lambda c: c.data == "cancel_reset")
def cancel_reset(call):
    bot.answer_callback_query(call.id, "✅")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass

# ============ تشغيل ============
print("🤖 البوت يعمل الآن...")
bot.infinity_polling()
