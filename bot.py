import telebot
from telebot import types
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import string
from datetime import datetime, timezone, timedelta

# ============ الإعدادات ============
BOT_TOKEN = "8956086702:AAEtcqzxJwA7W7daV3s4DiDMjSMTt9InJ3k"
ADMIN_ID = 6382473367
PAYMENT_NUMBER = "0984674400"
SUPPORT_USERNAME = "@Yamen494"
CHANNEL_USERNAME = "@YF494YF"
CHANNEL_LINK = "https://t.me/YF494YF"

DATABASE_URL = "postgresql://postgres:gGhvPiJBIxsFZdgZaMKmfuzSHwfjBRbV@postgres.railway.internal:5432/railway"

ORDERS_OPEN_HOUR = 12
ORDERS_CLOSE_HOUR = 22

bot = telebot.TeleBot(BOT_TOKEN)

# ============ الأسعار ============
PACKAGES = {
    "ff": {
        "title": {"ar": "🔥 فري فاير", "en": "🔥 Free Fire"},
        "currency": {"ar": "جوهرة", "en": "Diamond"},
        "items": {
            "ff_110": {"ar": "110 جوهرة 💎", "en": "110 Diamonds 💎", "price": "160 ل.س"},
            "ff_231": {"ar": "231 جوهرة 💎", "en": "231 Diamonds 💎", "price": "290 ل.س"},
            "ff_583": {"ar": "583 جوهرة 💎", "en": "583 Diamonds 💎", "price": "700 ل.س"},
        }
    },
    "pubg": {
        "title": {"ar": "🎯 ببجي", "en": "🎯 PUBG"},
        "currency": {"ar": "شدة", "en": "UC"},
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
            "يمكنك شحن فري فاير (جواهر) أو ببجي (شدات) بسهولة عبر سيرياتيل كاش ✅\n\n"
            "📌 <b>طريقة الشراء:</b>\n"
            "1️⃣ اختر اللعبة من الأزرار\n"
            "2️⃣ اختر العرض المناسب\n"
            "3️⃣ أرسل ID حسابك في اللعبة\n"
            "4️⃣ أرسل اسمك داخل اللعبة\n"
            "5️⃣ حوّل المبلغ عبر سيرياتيل كاش\n"
            "6️⃣ انتظر موافقة الإدارة ✅\n\n"
            "⏰ <b>ملاحظة:</b> الطلبات تُقبل من 12 ظهرًا حتى 10 مساءً بتوقيت السعودية 🇸🇦"
        ),
        "subscribe_required": (
            "🔒 <b>عذرًا عزيزي!</b>\n\n"
            "⚠️ يجب عليك <b>الاشتراك في قناتنا أولاً</b> لاستخدام البوت 💎\n\n"
            f"📢 القناة: {CHANNEL_USERNAME}\n\n"
            "1️⃣ اضغط زر <b>اشترك في القناة</b>\n"
            "2️⃣ اشترك ✅\n"
            "3️⃣ ارجع واضغط <b>تحقق من الاشتراك</b> 🔄"
        ),
        "btn_subscribe": "📢 اشترك في القناة",
        "btn_check": "✅ تحقق من الاشتراك",
        "btn_ff": "🔥 Free Fire",
        "btn_pubg": "🎯 PUBG",
        "btn_info": "👤 معلوماتي",
        "btn_support": "🆘 تواصل مع الدعم",
        "btn_settings": "⚙️ الإعدادات",
        "check_success": "✅ تم التحقق بنجاح! أهلاً بك 🎉",
        "check_fail": "❌ لم تشترك في القناة بعد! اشترك ثم اضغط تحقق.",
        "orders_closed": (
            "⛔ عذرًا، البوت لا يستقبل الطلبات حاليًا.\n"
            "🕛 ساعات العمل: من <b>12 ظهرًا</b> حتى <b>10 مساءً</b> بتوقيت السعودية 🇸🇦"
        ),
        "choose_package": "💎 <b>قائمة أسعار {game}:</b>\n\nاختر العرض الذي تريده 👇",
        "chosen": "✅ اخترت: <b>{item}</b> بسعر <b>{price}</b>\n\n🆔 الرجاء إرسال <b>ID حسابك في اللعبة</b>:",
        "invalid_id": "❌ <b>ID غير صالح!</b>\n\n{reason}\n\n🔁 أرسل ID صحيح (أرقام فقط، من 6 إلى 12 رقم):",
        "send_name": "📝 ممتاز! الآن أرسل <b>اسمك داخل اللعبة</b>:",
        "invalid_name": "❌ الاسم قصير جدًا! أرسل اسمك داخل اللعبة بشكل صحيح:",
        "final_step": (
            "🎉 <b>الخطوة الأخيرة!</b>\n\n"
            "💳 أرسل المبلغ <b>{price}</b> إلى الرقم:\n"
            "<code>{number}</code>\n"
            "عبر <b>سيرياتيل كاش</b> حصرًا 📲\n\n"
            "⚠️ بعد الإرسال سيتم مراجعة طلبك ✅\n"
            "🔖 رقم طلبك: <b>#{oid}</b>"
        ),
        "accepted": "✅ <b>تم قبول طلبك!</b>\n\n💎 سيتم إرسال <b>{item}</b> خلال <b>5 دقائق</b> ⏳\n\nشكرًا لثقتك ❤️",
        "rejected": "❌ عذرًا، تم <b>رفض طلبك</b>.\nللاستفسار تواصل مع الدعم 🆘",
        "my_info": (
            "👤 <b>معلوماتك:</b>\n\n"
            "📛 الاسم: <b>{name}</b>\n"
            "🆔 الآيدي: <code>{rid}</code>\n"
            "📅 تاريخ التسجيل: {joined}\n"
            "🌐 اللغة: {lang}\n\n"
            "🧾 <b>آخر عمليات الشراء:</b>\n{orders}"
        ),
        "no_orders": "لا يوجد أي عمليات شراء حتى الآن 😕",
        "support": (
            "🆘 <b>مركز الدعم الفني</b>\n\n"
            f"👨‍💻 للتواصل: {SUPPORT_USERNAME}\n\n"
            "📖 <b>طريقة الاستخدام:</b>\n"
            "1️⃣ اختر اللعبة (Free Fire / PUBG)\n"
            "2️⃣ اختر عرض الشحن 💎\n"
            "3️⃣ أرسل ID حسابك 🆔\n"
            "4️⃣ أرسل اسمك داخل اللعبة 📝\n"
            f"5️⃣ حوّل المبلغ عبر سيرياتيل كاش إلى:\n   <code>{PAYMENT_NUMBER}</code>\n"
            "6️⃣ انتظر موافقة الإدارة ✅\n"
            "7️⃣ تصلك الجواهر/الشدات خلال 5 دقائق ⏳\n\n"
            "⏰ <b>ساعات العمل:</b> 12 ظهرًا - 10 مساءً 🇸🇦"
        ),
        "settings_admin": "⚙️ <b>الإعدادات (أدمن)</b>\n\nاختر ما تريد:",
        "settings_user": "⚙️ <b>الإعدادات</b>\n\nاختر ما تريد:",
        "btn_change_lang": "🌐 تغيير اللغة",
        "btn_change_order": "🔀 ترتيب الأزرار (أدمن)",
        "btn_reset_data": "🗑️ تصفير بياناتي",
        "lang_changed": "✅ تم تغيير اللغة إلى العربية 🇸🇦",
        "lang_pick": "🌐 اختر اللغة:",
        "reset_confirm": "⚠️ هل أنت متأكد من حذف كل بياناتك (سجل الشراء + الآيدي)؟\n\nهذا الإجراء لا يمكن التراجع عنه!",
        "reset_done": "🗑️ تم حذف جميع بياناتك بنجاح ✅\nيمكنك البدء من جديد عبر /start",
        "btn_yes": "✅ نعم، احذف",
        "btn_no": "❌ إلغاء",
        "order_current": "🔀 <b>ترتيب الأزرار الحالي:</b>\n\n{order}\n\nاختر الترتيب الجديد:",
        "order_changed": "✅ تم تغيير ترتيب الأزرار!",
        "btn_order_default": "1️⃣ Free Fire ثم PUBG",
        "btn_order_swapped": "2️⃣ PUBG ثم Free Fire",
    },
    "en": {
        "welcome": (
            "👋 Welcome <b>{name}</b> to the Diamonds & UC bot 💎🔥\n\n"
            "🎯 <b>Bot purpose:</b>\n"
            "Top up Free Fire (Diamonds) or PUBG (UC) via Syriatel Cash ✅\n\n"
            "📌 <b>How to buy:</b>\n"
            "1️⃣ Choose the game\n"
            "2️⃣ Choose a package\n"
            "3️⃣ Send your in-game ID\n"
            "4️⃣ Send your in-game name\n"
            "5️⃣ Pay via Syriatel Cash\n"
            "6️⃣ Wait for admin approval ✅\n\n"
            "⏰ <b>Note:</b> Orders accepted from 12 PM to 10 PM (Saudi time) 🇸🇦"
        ),
        "subscribe_required": (
            "🔒 <b>Sorry!</b>\n\n"
            "⚠️ You must <b>subscribe to our channel first</b> to use the bot 💎\n\n"
            f"📢 Channel: {CHANNEL_USERNAME}\n\n"
            "1️⃣ Click <b>Subscribe</b>\n"
            "2️⃣ Join ✅\n"
            "3️⃣ Come back and click <b>Check subscription</b> 🔄"
        ),
        "btn_subscribe": "📢 Subscribe",
        "btn_check": "✅ Check subscription",
        "btn_ff": "🔥 Free Fire",
        "btn_pubg": "🎯 PUBG",
        "btn_info": "👤 My info",
        "btn_support": "🆘 Support",
        "btn_settings": "⚙️ Settings",
        "check_success": "✅ Verified! Welcome 🎉",
        "check_fail": "❌ You haven't subscribed yet!",
        "orders_closed": (
            "⛔ Orders are currently closed.\n"
            "🕛 Working hours: 12 PM - 10 PM (Saudi time) 🇸🇦"
        ),
        "choose_package": "💎 <b>{game} price list:</b>\n\nChoose a package 👇",
        "chosen": "✅ You chose: <b>{item}</b> for <b>{price}</b>\n\n🆔 Send your <b>in-game ID</b>:",
        "invalid_id": "❌ <b>Invalid ID!</b>\n\n{reason}\n\n🔁 Send a valid ID (digits only, 6-12):",
        "send_name": "📝 Now send your <b>in-game name</b>:",
        "invalid_name": "❌ Name too short! Send a valid in-game name:",
        "final_step": (
            "🎉 <b>Final step!</b>\n\n"
            "💳 Send <b>{price}</b> to:\n"
            "<code>{number}</code>\n"
            "via <b>Syriatel Cash</b> only 📲\n\n"
            "⚠️ Your order will be reviewed ✅\n"
            "🔖 Order #<b>{oid}</b>"
        ),
        "accepted": "✅ <b>Order accepted!</b>\n\n💎 <b>{item}</b> will arrive within <b>5 minutes</b> ⏳\n\nThanks ❤️",
        "rejected": "❌ Sorry, your order was <b>rejected</b>.\nContact support 🆘",
        "my_info": (
            "👤 <b>Your info:</b>\n\n"
            "📛 Name: <b>{name}</b>\n"
            "🆔 ID: <code>{rid}</code>\n"
            "📅 Joined: {joined}\n"
            "🌐 Language: {lang}\n\n"
            "🧾 <b>Recent orders:</b>\n{orders}"
        ),
        "no_orders": "No orders yet 😕",
        "support": (
            "🆘 <b>Support Center</b>\n\n"
            f"👨‍💻 Contact: {SUPPORT_USERNAME}\n\n"
            "📖 <b>How to use:</b>\n"
            "1️⃣ Choose game (Free Fire / PUBG)\n"
            "2️⃣ Choose package 💎\n"
            "3️⃣ Send your in-game ID 🆔\n"
            "4️⃣ Send your in-game name 📝\n"
            f"5️⃣ Pay via Syriatel Cash to:\n   <code>{PAYMENT_NUMBER}</code>\n"
            "6️⃣ Wait for approval ✅\n"
            "7️⃣ Receive within 5 minutes ⏳\n\n"
            "⏰ <b>Working hours:</b> 12 PM - 10 PM 🇸🇦"
        ),
        "settings_admin": "⚙️ <b>Settings (Admin)</b>\n\nChoose:",
        "settings_user": "⚙️ <b>Settings</b>\n\nChoose:",
        "btn_change_lang": "🌐 Change language",
        "btn_change_order": "🔀 Button order (Admin)",
        "btn_reset_data": "🗑️ Reset my data",
        "lang_changed": "✅ Language changed to English 🇬🇧",
        "lang_pick": "🌐 Choose language:",
        "reset_confirm": "⚠️ Delete all your data (orders + ID)?\n\nThis cannot be undone!",
        "reset_done": "🗑️ All your data has been deleted ✅\nStart fresh with /start",
        "btn_yes": "✅ Yes, delete",
        "btn_no": "❌ Cancel",
        "order_current": "🔀 <b>Current button order:</b>\n\n{order}\n\nChoose new order:",
        "order_changed": "✅ Button order changed!",
        "btn_order_default": "1️⃣ Free Fire then PUBG",
        "btn_order_swapped": "2️⃣ PUBG then Free Fire",
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
    # ترتيب الأزرار الافتراضي
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
    cur.close()
    conn.close()
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
    cur.close()
    conn.close()

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
    cur.close()
    conn.close()
    return row["value"] if row else "ff,pubg"

def set_button_order(value):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET value = %s WHERE key = 'button_order'", (value,))
    conn.commit()
    cur.close()
    conn.close()

def is_orders_open():
    now = datetime.now(timezone(timedelta(hours=3)))
    return ORDERS_OPEN_HOUR <= now.hour < ORDERS_CLOSE_HOUR

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"❌ خطأ في التحقق من الاشتراك: {e}")
        return False

def validate_game_id(game_id: str):
    game_id = game_id.strip()
    if not game_id.isdigit():
        return False, "أرقام فقط / Digits only 🔢"
    if len(game_id) < 6:
        return False, "6 أرقام على الأقل / min 6 digits ⚠️"
    if len(game_id) > 12:
        return False, "12 رقم كحد أقصى / max 12 digits ⚠️"
    if game_id.startswith("0"):
        return False, "لا يبدأ بـ 0 / no leading 0 ⚠️"
    return True, game_id

# ============ لوحة الأزرار الرئيسية ============
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
    kb.row(T["btn_support"])
    return kb

# ============ رسالة الترحيب ============
def send_welcome(chat_id, first_name, uid):
    bot.send_message(
        chat_id,
        t(uid, "welcome", name=first_name),
        parse_mode="HTML",
        reply_markup=main_keyboard(uid)
    )

def show_subscription_message(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_subscribe"), url=CHANNEL_LINK))
    kb.add(types.InlineKeyboardButton(t(uid, "btn_check"), callback_data="check_sub"))
    bot.send_message(chat_id, t(uid, "subscribe_required"), parse_mode="HTML", reply_markup=kb)

# ============ /start ============
@bot.message_handler(commands=['start'])
def cmd_start(message):
    ensure_user(message)
    uid = message.from_user.id
    if is_subscribed(uid):
        send_welcome(message.chat.id, message.from_user.first_name, uid)
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
        except:
            pass
        send_welcome(call.message.chat.id, call.from_user.first_name, uid)
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
        message.chat.id,
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

    bot.user_data = getattr(bot, "user_data", {})
    bot.user_data[uid] = {
        "game": game,
        "package_key": key,
        "package_name": item[lang],
        "price": item["price"]
    }

    msg = bot.send_message(
        call.message.chat.id,
        t(uid, "chosen", item=item[lang], price=item["price"]),
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, get_game_id)

# ============ ID اللعبة ============
def get_game_id(message):
    uid = message.from_user.id
    data = bot.user_data.get(uid) if hasattr(bot, "user_data") else None
    if not data:
        bot.send_message(message.chat.id, "⚠️ اضغط /start من جديد.")
        return

    game_id = message.text.strip() if message.text else ""
    valid, result = validate_game_id(game_id)

    if not valid:
        msg = bot.send_message(message.chat.id, t(uid, "invalid_id", reason=result), parse_mode="HTML")
        bot.register_next_step_handler(msg, get_game_id)
        return

    data["game_id"] = result
    msg = bot.send_message(message.chat.id, t(uid, "send_name"), parse_mode="HTML")
    bot.register_next_step_handler(msg, get_player_name)

# ============ اسم اللاعب ============
def get_player_name(message):
    uid = message.from_user.id
    data = bot.user_data.get(uid) if hasattr(bot, "user_data") else None
    if not data:
        bot.send_message(message.chat.id, "⚠️ اضغط /start من جديد.")
        return

    player_name = message.text.strip() if message.text else ""
    if len(player_name) < 2:
        msg = bot.send_message(message.chat.id, t(uid, "invalid_name"))
        bot.register_next_step_handler(msg, get_player_name)
        return

    data["player_name"] = player_name

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, game, package, price, game_id, player_name, status, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_id",
        (uid, data["game"], data["package_name"], data["price"],
         data["game_id"], data["player_name"], "pending",
         datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    order_id = cur.fetchone()["order_id"]
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(
        message.chat.id,
        t(uid, "final_step", price=data["price"], number=PAYMENT_NUMBER, oid=order_id),
        parse_mode="HTML"
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
        f"📝 اسم اللاعب: <b>{data['player_name']}</b>\n\n"
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
    except:
        pass

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
    if not is_subscribed(message.from_user.id):
        show_subscription_message(message.chat.id, message.from_user.id)
        return
    bot.send_message(message.chat.id, t(message.from_user.id, "support"), parse_mode="HTML")

# ============ زر الإعدادات ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_settings"], TEXTS["en"]["btn_settings"]])
def settings_menu(message):
    uid = message.from_user.id
    ensure_user(message)

    if not is_subscribed(uid):
        show_subscription_message(message.chat.id, uid)
        return

    lang = get_lang(uid)
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
    except:
        pass
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
    except:
        pass
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
    except:
        pass

    bot.send_message(call.message.chat.id, t(uid, "reset_done"))
    # نرسل /start تلقائيًا
    cmd_start(call.message)

@bot.callback_query_handler(func=lambda c: c.data == "cancel_reset")
def cancel_reset(call):
    bot.answer_callback_query(call.id, "✅")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

# ============ تشغيل ============
print("🤖 البوت يعمل الآن على Railway...")
bot.infinity_polling()
