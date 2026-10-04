import telebot
from telebot import types
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import os
import time
import threading
from datetime import datetime, timezone, timedelta

# ============ الإعدادات ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8956086702:AAEtcqzxJwA7W7daV3s4DiDMjSMTt9InJ3k")
ADMIN_ID = 6382473367
PAYMENT_NUMBER_SYRIATEL = "0984674400"
SUPPORT_USERNAME = "@Yamen494"
CHANNEL_USERNAME = "@YF494YF"
CHANNEL_LINK = "https://t.me/YF494YF"
CONTEST_LINK = "https://t.me/YF494Y"   # رابط المسابقة
DATABASE_URL = os.environ.get("DATABASE_URL",
    "postgresql://postgres:FmMcTnFMJbldpynWXDwrFfXISsKbYKvt@postgres.railway.internal:5432/railway")

SHAM_IMAGE_PATH = "sham.jpg"

ORDERS_OPEN_HOUR = 12
ORDERS_CLOSE_HOUR = 22
PAYMENT_TIMEOUT_SECONDS = 300

REQUIRED_SHARES = 5   # عدد المشاركات المطلوب

bot = telebot.TeleBot(BOT_TOKEN)
USER_DATA = {}
COUNTDOWNS = {}

import requests

def fix_allowed_updates():
    try:
        r1 = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
            params={"drop_pending_updates": "true"},
            timeout=10
        )
        print(f"🔧 deleteWebhook: {r1.json()}")

        r2 = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params={
                "allowed_updates": '["message","edited_message","channel_post","edited_channel_post","callback_query","inline_query","chosen_inline_result","poll","poll_answer","my_chat_member","chat_member","chat_join_request"]',
                "timeout": 1
            },
            timeout=15
        )
        print(f"🔧 getUpdates: {r2.json().get('ok')}")

        r3 = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo",
            timeout=10
        )
        info = r3.json()
        allowed = info.get("result", {}).get("allowed_updates", [])
        print(f"🔧 allowed_updates الآن: {allowed}")

        if "callback_query" in allowed:
            print("✅ callback_query مسموح — الأزرار ستشتغل!")
            return True
        else:
            print("⚠️ callback_query لا يزال غير مسموح")
            return False
    except Exception as e:
        print(f"❌ خطأ في fix_allowed_updates: {e}")
        return False

fix_allowed_updates()
time.sleep(1)

# ============ الأسعار ============
PACKAGES = {
    "ff": {
        "title": {"ar": "💎 شحن جواهر فري فاير", "en": "💎 Free Fire Diamonds"},
        "items": {
            "ff_110": {"ar": "110 جوهرة 💎", "en": "110 Diamonds 💎", "price": "160 ل.س"},
            "ff_231": {"ar": "231 جوهرة 💎", "en": "231 Diamonds 💎", "price": "290 ل.س"},
            "ff_583": {"ar": "583 جوهرة 💎", "en": "583 Diamonds 💎", "price": "700 ل.س"},
        }
    },
    "ff_membership": {
        "title": {"ar": "⭐ عضوية فري فاير", "en": "⭐ Free Fire Membership"},
        "items": {
            "ffm_week":  {"ar": "عضوية أسبوعية ⭐", "en": "Weekly Membership ⭐", "price": "340 ل.س"},
            "ffm_month": {"ar": "عضوية شهرية ⭐",  "en": "Monthly Membership ⭐", "price": "1540 ل.س"},
        }
    },
    "pubg": {
        "title": {"ar": "🎯 ببجي", "en": "🎯 PUBG"},
        "items": {
            "pubg_60":   {"ar": "60 شدة 🪙",   "en": "60 UC 🪙",   "price": "140 ل.س"},
            "pubg_325":  {"ar": "325 شدة 🪙",  "en": "325 UC 🪙",  "price": "670 ل.س"},
            "pubg_660":  {"ar": "660 شدة 🪙",  "en": "660 UC 🪙",  "price": "1300 ل.س"},
            "pubg_1800": {"ar": "1800 شدة 🪙", "en": "1800 UC 🪙", "price": "3210 ل.س"},
        }
    },
    "jawaker": {
        "title": {"ar": "🃏 جواكر", "en": "🃏 Jawaker"},
        "items": {
            "jw_10000": {"ar": "10000 توكنز ♦️", "en": "10000 Tokens ♦️", "price": "180 ل.س"},
            "jw_15000": {"ar": "15000 توكنز ♠️", "en": "15000 Tokens ♠️", "price": "260 ل.س"},
            "jw_20000": {"ar": "20000 توكنز ♥️", "en": "20000 Tokens ♥️", "price": "340 ل.س"},
            "jw_30000": {"ar": "30000 توكنز ♣️", "en": "30000 Tokens ♣️", "price": "490 ل.س"},
        }
    }
}

# ============ الترجمة ============
TEXTS = {
    "ar": {
        "welcome": (
            "👋 أهلاً بك <b>{name}</b> في بوت شحن الجواهر والشدات 💎🔥\n\n"
            "🎯 <b>فكرة البوت:</b>\n"
            "يمكنك شحن فري فاير، ببجي، أو جواكر عبر سيرياتيل كاش أو شام كاش ✅\n\n"
            "📌 <b>طريقة الشراء:</b>\n"
            "1️⃣ اختر اللعبة\n2️⃣ اختر العرض\n3️⃣ أرسل ID حسابك\n"
            "4️⃣ أرسل اسمك في اللعبة\n5️⃣ اختر طريقة الدفع\n6️⃣ حوّل المبلغ خلال 5 دقائق\n"
            "7️⃣ انتظر موافقة الإدارة ✅\n\n"
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
        "btn_jawaker": "🃏 Jawaker",
        "btn_info": "👤 معلوماتي",
        "btn_support": "🆘 تواصل مع الدعم",
        "btn_settings": "⚙️ الإعدادات",
        "btn_back": "⬅️ رجوع",
        "btn_inbox": "📬 البريد الوارد",
        "btn_contestants": "🏆 المتسابقين",
        "btn_contest": "🎁 المسابقة",
        "check_success": "✅ تم التحقق بنجاح! أهلاً بك 🎉",
        "check_fail": "❌ لم تشترك في القناة بعد!",
        "orders_closed": (
            "⛔ عذرًا، البوت لا يستقبل الطلبات حاليًا.\n"
            "🕛 ساعات العمل: من <b>12 ظهرًا</b> حتى <b>10 مساءً</b> بتوقيت السعودية 🇸🇦"
        ),
        "orders_closed_dev": (
            "🔧 <b>البوت في وضع الصيانة/التجارب مؤقتًا</b>\n\n"
            "⛔ لا يستقبل الطلبات حاليًا.\n"
            "🔄 يرجى المحاولة لاحقًا."
        ),
        "choose_ff_type": (
            "🔥 <b>اختر نوع الشحن في فري فاير:</b>\n\n"
            "👇 من الأزرار بالأسفل"
        ),
        "btn_ff_diamonds": "💎 شحن جواهر",
        "btn_ff_membership": "⭐ شحن عضوية",
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
            "• أرقام فقط 🔢\n• من 5 إلى 15 رقم\n• لا يبدأ بـ 0\n\n"
            "🔁 أرسل ID صحيح:"
        ),
        "invalid_id_pubg": (
            "❌ <b>ID PUBG غير صالح!</b>\n\n"
            "⚠️ {reason}\n\n"
            "📌 <b>شروط ID ببجي:</b>\n"
            "• أرقام فقط 🔢\n• من 9 إلى 12 رقم\n• لا يبدأ بـ 0\n\n"
            "🔁 أرسل ID صحيح:"
        ),
        "invalid_id_jawaker": (
            "❌ <b>ID جواكر غير صالح!</b>\n\n"
            "⚠️ {reason}\n\n"
            "📌 <b>شروط ID جواكر:</b>\n"
            "• أرقام فقط 🔢\n• من 6 إلى 12 رقم\n• لا يبدأ بـ 0\n\n"
            "🔁 أرسل ID صحيح:"
        ),
        "send_name": "📝 ممتاز! الآن أرسل <b>اسمك داخل اللعبة</b>:",
        "invalid_name": "❌ الاسم قصير جدًا! أرسل اسمك الصحيح:",
        "choose_payment": "💳 <b>اختر طريقة الدفع:</b>\n\n👇 اختر من الأزرار بالأسفل",
        "btn_syriatel": "💳 سيرياتيل كاش",
        "btn_sham": "📷 شام كاش",
        "payment_with_timer": (
            "💳 <b>طريقة الدفع: {method}</b>\n\n"
            "📌 <b>الخطوات:</b>\n"
            "{steps}\n\n"
            "⏳ <b>المتبقي للتسديد: {remaining}</b>\n\n"
            "🔔 <b>ملاحظة مهمة:</b>\n"
            "يجب تسديد المبلغ خلال <b>5 دقائق</b> وإلا سيُلغى الطلب تلقائيًا!\n\n"
            "⚠️ سيتم مراجعة طلبك من قِبَل الإدارة ✅\n"
            "🔖 رقم طلبك: <b>#{oid}</b>"
        ),
        "payment_expired": (
            "⌛ <b>انتهى وقت التسديد!</b>\n\n"
            "عذرًا، لم يتم تسديد المبلغ خلال <b>5 دقائق</b>.\n"
            "🔖 رقم طلبك: <b>#{oid}</b>\n\n"
            "🔄 يمكنك إنشاء طلب جديد عبر /start"
        ),
        "sham_image_caption": "📷 <b>امسح هذا الكود للدفع عبر شام كاش</b>\n\n💰 المبلغ المطلوب: <b>{price}</b>",
        "accepted": (
            "✅ <b>تم قبول طلبك!</b>\n\n"
            "💎 <b>{item}</b> سيصلك خلال <b>5 دقائق</b> ⏳\n\n"
            "شكرًا لثقتك ❤️"
        ),
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
        "contest_title": (
            "🎁 <b>مسابقة البوت!</b>\n\n"
            "🎯 <b>شروط المشاركة:</b>\n"
            f"📢 شارك رابط القناة مع <b>{REQUIRED_SHARES} أشخاص</b>\n\n"
            f"🔗 <b>رابط القناة:</b>\n<code>{CONTEST_LINK}</code>\n\n"
            "📌 <b>الخطوات:</b>\n"
            "1️⃣ انسخ الرابط بالأعلى ☝️\n"
            "2️⃣ شاركه مع 5 أشخاص على الأقل\n"
            "3️⃣ اضغط زر <b>✅ أكملت المشاركة</b>\n"
            "4️⃣ انتظر تأكيد الإدارة لدخول السحب 🎉"
        ),
        "btn_share_done": "✅ أكملت المشاركة",
        "btn_copy_link": "📋 انسخ الرابط",
        "contest_registered": (
            "🎉 <b>تم تسجيلك بنجاح!</b>\n\n"
            "📩 طلبك الآن <b>قيد المراجعة</b> من قِبَل الإدارة.\n\n"
            "🔔 سيتم إشعارك عند دخولك السحب الرسمي 🎊"
        ),
        "contest_already": (
            "✅ <b>أنت مسجل بالفعل في المسابقة!</b>\n\n"
            "🕐 الحالة: {status}\n\n"
            "🍀 حظًا موفقًا!"
        ),
        "contest_status_pending": "⏳ قيد المراجعة",
        "contest_status_approved": "🏆 مؤهل للسحب",
        "contest_status_rejected": "❌ مرفوض",
        "contest_approved_msg": (
            "🏆 <b>ألف مبروك!</b>\n\n"
            "🎊 تم تأكيد دخولك في <b>سحب المسابقة</b> رسميًا!\n\n"
            "🍀 حظًا موفقًا! سيتم إعلان الفائز قريبًا."
        ),
        "contest_rejected_msg": (
            "❌ <b>عذرًا!</b>\n\n"
            "لم يتم تأكيد مشاركتك في المسابقة.\n"
            "تواصل مع الدعم إذا كنت تعتقد أن هناك خطأ 🆘"
        ),
        "contestants_title": (
            "🏆 <b>قائمة المتسابقين</b>\n\n"
            "📊 الإجمالي: <b>{total}</b>\n"
            "✅ مؤهلون: <b>{approved}</b>\n"
            "⏳ معلّقون: <b>{pending}</b>\n"
            "❌ مرفوضون: <b>{rejected}</b>"
        ),
        "contestants_empty": "📭 لا يوجد متسابقون حتى الآن",
        "contestant_item": (
            "👤 <b>{name}</b>\n"
            "🆔 <code>{uid}</code>\n"
            "🌐 @{username}\n"
            "🎯 الحالة: {status}\n"
            "🕒 {time}"
        ),
        "contestant_notified": "✅ تم إشعار المتسابق",
        "inbox_title": "📬 <b>البريد الوارد</b>\n\n📥 آخر <b>{count}</b> رسالة",
        "inbox_empty": "📭 لا يوجد رسائل حتى الآن",
        "inbox_item": (
            "📩 <b>شكوى رقم #{n}</b>\n\n"
            "👤 الاسم: <b>{name}</b>\n"
            "🆔 <code>{uid}</code>\n"
            "🕒 {time}\n\n"
            "💬 <b>الشكوى:</b>\n{msg}"
        ),
        "settings_admin": "⚙️ <b>الإعدادات (أدمن)</b>\n\nاختر:",
        "settings_user": "⚙️ <b>الإعدادات</b>\n\nاختر:",
        "settings_dev": "🔧 <b>وضع المطور</b>",
        "btn_change_lang": "🌐 تغيير اللغة",
        "btn_change_order": "🔀 ترتيب الأزرار (أدمن)",
        "btn_reset_data": "🗑️ تصفير بياناتي",
        "btn_dev_mode": "🔧 وضع المطور (تشغيل البوت)",
        "dev_mode_current_on": (
            "🔧 <b>حالة وضع المطور:</b> ✅ مفعّل\n\n"
            "البوت يعمل حاليًا خارج ساعات العمل الرسمية.\n\n"
            "اضغط الزر لإيقافه:"
        ),
        "dev_mode_current_off": (
            "🔧 <b>حالة وضع المطور:</b> ❌ موقّف\n\n"
            "البوت يتبع ساعات العمل الرسمية (12 ظهرًا - 10 مساءً).\n\n"
            "اضغط الزر لتشغيله مؤقتًا:"
        ),
        "btn_dev_on": "✅ تشغيل البوت مؤقتًا",
        "btn_dev_off": "🛑 إيقاف البوت مؤقتًا",
        "dev_mode_enabled": "✅ <b>تم تفعيل وضع المطور</b>\n\nالبوت يقبل الطلبات الآن خارج ساعات العمل 🚀",
        "dev_mode_disabled": "🛑 <b>تم إيقاف وضع المطور</b>\n\nالبوت عاد لساعات العمل الرسمية.",
        "lang_changed": "✅ تم تغيير اللغة إلى العربية 🇸🇦",
        "lang_pick": "🌐 اختر اللغة:",
        "reset_confirm": "⚠️ هل أنت متأكد من حذف كل بياناتك؟\n\nهذا لا يمكن التراجع عنه!",
        "reset_done": "🗑️ تم حذف جميع بياناتك ✅",
        "btn_yes": "✅ نعم، احذف",
        "btn_no": "❌ إلغاء",
        "order_current": "🔀 <b>ترتيب الأزرار الحالي:</b>\n\n{order}\n\nاختر:",
        "order_changed": "✅ تم تغيير الترتيب!",
        "btn_order_1": "1️⃣ FF → PUBG → Jawaker",
        "btn_order_2": "2️⃣ Jawaker → FF → PUBG",
        "btn_order_3": "3️⃣ PUBG → Jawaker → FF",
        "back_done": "⬅️ رجعنا للخطوة السابقة",
        "unknown_msg": "🤔 لم أفهم رسالتك. استخدم الأزرار بالأسفل 👇",
    },
    "en": {
        "welcome": (
            "👋 Welcome <b>{name}</b> to the Top-Up bot 💎🔥\n\n"
            "🎯 <b>Bot purpose:</b>\n"
            "Top up Free Fire, PUBG, or Jawaker via Syriatel Cash or Sham Cash ✅\n\n"
            "📌 <b>How to buy:</b>\n1️⃣ Choose game\n2️⃣ Choose package\n"
            "3️⃣ Send your ID\n4️⃣ Send in-game name\n5️⃣ Choose payment\n"
            "6️⃣ Pay within 5 minutes\n7️⃣ Wait for approval ✅\n\n"
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
        "btn_jawaker": "🃏 Jawaker",
        "btn_info": "👤 My info",
        "btn_support": "🆘 Support",
        "btn_settings": "⚙️ Settings",
        "btn_back": "⬅️ Back",
        "btn_inbox": "📬 Inbox",
        "btn_contestants": "🏆 Contestants",
        "btn_contest": "🎁 Contest",
        "check_success": "✅ Verified! Welcome 🎉",
        "check_fail": "❌ Not subscribed yet!",
        "orders_closed": "⛔ Orders closed.\n🕛 Working: 12 PM - 10 PM 🇸🇦",
        "orders_closed_dev": (
            "🔧 <b>Bot is in maintenance/test mode</b>\n\n"
            "⛔ Not accepting orders right now.\n"
            "🔄 Please try again later."
        ),
        "choose_ff_type": "🔥 <b>Choose Free Fire top-up type:</b>\n\n👇 From buttons below",
        "btn_ff_diamonds": "💎 Diamonds",
        "btn_ff_membership": "⭐ Membership",
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
        "invalid_id_jawaker": (
            "❌ <b>Invalid Jawaker ID!</b>\n\n⚠️ {reason}\n\n"
            "📌 <b>Jawaker ID rules:</b>\n• Digits only 🔢\n• 6-12 digits\n• No leading 0\n\n"
            "🔁 Send a valid ID:"
        ),
        "send_name": "📝 Now send your <b>in-game name</b>:",
        "invalid_name": "❌ Name too short!",
        "choose_payment": "💳 <b>Choose payment method:</b>\n\n👇 From buttons below",
        "btn_syriatel": "💳 Syriatel Cash",
        "btn_sham": "📷 Sham Cash",
        "payment_with_timer": (
            "💳 <b>Payment: {method}</b>\n\n"
            "📌 <b>Steps:</b>\n"
            "{steps}\n\n"
            "⏳ <b>Time left to pay: {remaining}</b>\n\n"
            "🔔 <b>Important:</b>\n"
            "You must pay within <b>5 minutes</b> or the order will be auto-cancelled!\n\n"
            "⚠️ Reviewed by admin ✅\n"
            "🔖 Order #<b>{oid}</b>"
        ),
        "payment_expired": (
            "⌛ <b>Payment time expired!</b>\n\n"
            "Sorry, you didn't pay within <b>5 minutes</b>.\n"
            "🔖 Order #<b>{oid}</b>\n\n"
            "🔄 Create a new order via /start"
        ),
        "sham_image_caption": "📷 <b>Scan this code to pay via Sham Cash</b>\n\n💰 Amount: <b>{price}</b>",
        "accepted": (
            "✅ <b>Accepted!</b>\n\n"
            "💎 <b>{item}</b> within <b>5 min</b> ⏳\n\n"
            "Thanks ❤️"
        ),
        "rejected": "❌ Order <b>rejected</b>.\nContact support 🆘",
        "my_info": (
            "👤 <b>Your info:</b>\n\n📛 {name}\n🆔 <code>{rid}</code>\n"
            "📅 {joined}\n🌐 {lang}\n\n🧾 <b>Recent orders:</b>\n{orders}"
        ),
        "no_orders": "No orders yet 😕",
        "contest_title": (
            "🎁 <b>Bot Contest!</b>\n\n"
            "🎯 <b>Participation rules:</b>\n"
            f"📢 Share the channel link with <b>{REQUIRED_SHARES} people</b>\n\n"
            f"🔗 <b>Channel link:</b>\n<code>{CONTEST_LINK}</code>\n\n"
            "📌 <b>Steps:</b>\n"
            "1️⃣ Copy the link above ☝️\n"
            "2️⃣ Share with at least 5 people\n"
            "3️⃣ Click <b>✅ Done sharing</b>\n"
            "4️⃣ Wait for admin confirmation 🎉"
        ),
        "btn_share_done": "✅ Done sharing",
        "btn_copy_link": "📋 Copy link",
        "contest_registered": (
            "🎉 <b>Registered successfully!</b>\n\n"
            "📩 Your request is <b>pending review</b>.\n\n"
            "🔔 You'll be notified once approved 🎊"
        ),
        "contest_already": (
            "✅ <b>You're already registered!</b>\n\n"
            "🕐 Status: {status}\n\n"
            "🍀 Good luck!"
        ),
        "contest_status_pending": "⏳ Pending",
        "contest_status_approved": "🏆 Qualified",
        "contest_status_rejected": "❌ Rejected",
        "contest_approved_msg": (
            "🏆 <b>Congratulations!</b>\n\n"
            "🎊 You're officially in the <b>contest draw</b>!\n\n"
            "🍀 Good luck!"
        ),
        "contest_rejected_msg": (
            "❌ <b>Sorry!</b>\n\n"
            "Your contest entry wasn't approved.\n"
            "Contact support if you believe this is an error 🆘"
        ),
        "contestants_title": (
            "🏆 <b>Contestants List</b>\n\n"
            "📊 Total: <b>{total}</b>\n"
            "✅ Approved: <b>{approved}</b>\n"
            "⏳ Pending: <b>{pending}</b>\n"
            "❌ Rejected: <b>{rejected}</b>"
        ),
        "contestants_empty": "📭 No contestants yet",
        "contestant_item": (
            "👤 <b>{name}</b>\n"
            "🆔 <code>{uid}</code>\n"
            "🌐 @{username}\n"
            "🎯 Status: {status}\n"
            "🕒 {time}"
        ),
        "contestant_notified": "✅ Contestant notified",
        "inbox_title": "📬 <b>Inbox</b>\n\n📥 Last <b>{count}</b> messages",
        "inbox_empty": "📭 No messages yet",
        "inbox_item": (
            "📩 <b>Complaint #{n}</b>\n\n👤 Name: <b>{name}</b>\n"
            "🆔 <code>{uid}</code>\n🕒 {time}\n\n💬 <b>Message:</b>\n{msg}"
        ),
        "settings_admin": "⚙️ <b>Settings (Admin)</b>\n\nChoose:",
        "settings_user": "⚙️ <b>Settings</b>\n\nChoose:",
        "settings_dev": "🔧 <b>Developer Mode</b>",
        "btn_change_lang": "🌐 Change language",
        "btn_change_order": "🔀 Button order (Admin)",
        "btn_reset_data": "🗑️ Reset my data",
        "btn_dev_mode": "🔧 Developer mode (Bot toggle)",
        "dev_mode_current_on": (
            "🔧 <b>Developer Mode:</b> ✅ ON\n\n"
            "Bot is accepting orders outside working hours.\n\n"
            "Press to disable:"
        ),
        "dev_mode_current_off": (
            "🔧 <b>Developer Mode:</b> ❌ OFF\n\n"
            "Bot follows working hours (12 PM - 10 PM).\n\n"
            "Press to enable temporarily:"
        ),
        "btn_dev_on": "✅ Enable bot temporarily",
        "btn_dev_off": "🛑 Disable bot temporarily",
        "dev_mode_enabled": "✅ <b>Developer Mode enabled</b>\n\nBot is now accepting orders outside hours 🚀",
        "dev_mode_disabled": "🛑 <b>Developer Mode disabled</b>\n\nBot returned to working hours.",
        "lang_changed": "✅ Language: English 🇬🇧",
        "lang_pick": "🌐 Choose language:",
        "reset_confirm": "⚠️ Delete all your data?\n\nCannot be undone!",
        "reset_done": "🗑️ Data deleted ✅",
        "btn_yes": "✅ Yes, delete",
        "btn_no": "❌ Cancel",
        "order_current": "🔀 <b>Current order:</b>\n\n{order}\n\nChoose:",
        "order_changed": "✅ Order changed!",
        "btn_order_1": "1️⃣ FF → PUBG → Jawaker",
        "btn_order_2": "2️⃣ Jawaker → FF → PUBG",
        "btn_order_3": "3️⃣ PUBG → Jawaker → FF",
        "back_done": "⬅️ Back",
        "unknown_msg": "🤔 I didn't understand. Use the buttons below 👇",
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
            payment_method TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_method TEXT")
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
    # ========== جدول المسابقة ==========
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contest (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            status TEXT DEFAULT 'pending',
            registered_at TEXT,
            approved_at TEXT
        )
    """)

    cur.execute("SELECT value FROM settings WHERE key = 'button_order'")
    row = cur.fetchone()
    if row:
        if "jawaker" not in row["value"]:
            cur.execute("UPDATE settings SET value = 'ff,pubg,jawaker' WHERE key = 'button_order'")
            print("🔧 تحديث ترتيب الأزرار: ff,pubg,jawaker")
    else:
        cur.execute("INSERT INTO settings VALUES ('button_order', 'ff,pubg,jawaker')")

    cur.execute("INSERT INTO settings VALUES ('dev_mode', 'off') ON CONFLICT (key) DO NOTHING")

    conn.commit()
    cur.close(); conn.close()

init_db()

# ============ دوال مساعدة ============
def gen_random_id():
    return str(random.randint(10000000, 99999999))

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

def t_lang(lang, key, **kwargs):
    text = TEXTS.get(lang, TEXTS["ar"]).get(key, "")
    return text.format(**kwargs) if kwargs else text

def get_button_order():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = 'button_order'")
    row = cur.fetchone()
    cur.close(); conn.close()
    return row["value"] if row else "ff,pubg,jawaker"

def set_button_order(value):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET value = %s WHERE key = 'button_order'", (value,))
    conn.commit()
    cur.close(); conn.close()

def get_setting(key, default=None):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row["value"] if row else default

def set_setting(key, value):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO settings VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (key, value))
    conn.commit()
    cur.close(); conn.close()

def is_orders_open():
    if get_setting("dev_mode", "off") == "on":
        return True
    now = datetime.now(timezone(timedelta(hours=3)))
    return ORDERS_OPEN_HOUR <= now.hour < ORDERS_CLOSE_HOUR

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"❌ خطأ في التحقق من الاشتراك: {e}")
        return False

def validate_game_id(game_id: str, game: str):
    game_id = game_id.strip()
    if not game_id.isdigit():
        return False, "يجب أن يحتوي على أرقام فقط"
    if game_id.startswith("0"):
        return False, "لا يبدأ بـ 0"

    if game in ("ff", "ff_membership"):
        if len(game_id) < 5:
            return False, "ID فري فاير أقل من 5 أرقام"
        if len(game_id) > 15:
            return False, "ID فري فاير أكثر من 15 رقم"
    elif game == "pubg":
        if len(game_id) < 9:
            return False, "ID ببجي أقل من 9 أرقام"
        if len(game_id) > 12:
            return False, "ID ببجي أكثر من 12 رقم"
    elif game == "jawaker":
        if len(game_id) < 6:
            return False, "ID جواكر أقل من 6 أرقام"
        if len(game_id) > 12:
            return False, "ID جواكر أكثر من 12 رقم"

    return True, game_id

# ============ دوال المسابقة ============
def get_contest_entry(uid):
    """يرجّع بيانات المتسابق إذا موجود"""
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contest WHERE user_id = %s", (uid,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

def register_contest(message):
    """تسجيل المستخدم في المسابقة (بحالة pending)"""
    uid = message.from_user.id
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM contest WHERE user_id = %s", (uid,))
    if cur.fetchone():
        cur.close(); conn.close()
        return False
    cur.execute(
        "INSERT INTO contest (user_id, username, full_name, status, registered_at) "
        "VALUES (%s, %s, %s, 'pending', %s)",
        (uid, message.from_user.username or "", message.from_user.full_name,
         datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    cur.close(); conn.close()
    return True

def approve_contest(uid):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE contest SET status = 'approved', approved_at = %s WHERE user_id = %s",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), uid)
    )
    conn.commit()
    cur.close(); conn.close()

def reject_contest(uid):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE contest SET status = 'rejected' WHERE user_id = %s", (uid,))
    conn.commit()
    cur.close(); conn.close()

def get_all_contestants():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM contest ORDER BY registered_at DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def contest_status_text(uid, status):
    lang = get_lang(uid)
    if status == "pending":
        return TEXTS[lang]["contest_status_pending"]
    elif status == "approved":
        return TEXTS[lang]["contest_status_approved"]
    else:
        return TEXTS[lang]["contest_status_rejected"]

# ============ العداد الحي ============
def format_remaining(seconds, lang):
    m = seconds // 60
    s = seconds % 60
    if lang == "en":
        if m > 0 and s > 0:
            return f"{m} min {s} sec"
        elif m > 0:
            return f"{m} min"
        else:
            return f"{s} sec"
    else:
        if m > 0 and s > 0:
            return f"{m} دقيقة و {s} ثانية"
        elif m > 0:
            return f"{m} دقيقة"
        else:
            return f"{s} ثانية"

def build_payment_steps(method, lang, price):
    if method == "syriatel":
        if lang == "ar":
            return (
                "1️⃣ افتح تطبيق <b>سيرياتيل كاش</b>\n"
                "2️⃣ اختر <b>تحويل</b>\n"
                f"3️⃣ أدخل الرقم: <code>{PAYMENT_NUMBER_SYRIATEL}</code>\n"
                f"4️⃣ أدخل المبلغ: <b>{price}</b>\n"
                "5️⃣ أكّد العملية ✅"
            ), "سيرياتيل كاش 💳"
        else:
            return (
                "1️⃣ Open <b>Syriatel Cash</b>\n"
                "2️⃣ Choose <b>Transfer</b>\n"
                f"3️⃣ Enter: <code>{PAYMENT_NUMBER_SYRIATEL}</code>\n"
                f"4️⃣ Enter amount: <b>{price}</b>\n"
                "5️⃣ Confirm ✅"
            ), "Syriatel Cash 💳"
    else:
        if lang == "ar":
            return (
                "1️⃣ افتح تطبيق <b>شام كاش</b>\n"
                "2️⃣ اختر <b>مسح QR</b>\n"
                "3️⃣ امسح الكود المرسل بالصورة ☝️\n"
                f"4️⃣ أدخل المبلغ: <b>{price}</b>\n"
                "5️⃣ أكّد العملية ✅"
            ), "شام كاش 📷"
        else:
            return (
                "1️⃣ Open <b>Sham Cash</b>\n"
                "2️⃣ Choose <b>Scan QR</b>\n"
                "3️⃣ Scan the code above ☝️\n"
                f"4️⃣ Enter amount: <b>{price}</b>\n"
                "5️⃣ Confirm ✅"
            ), "Sham Cash 📷"


def start_countdown(chat_id, message_id, order_id, method, uid, lang, price_str, total_seconds=300):
    COUNTDOWNS[order_id] = False

    def run():
        print(f"⏳ بدء العداد للطلب #{order_id} | المدة {total_seconds} ث | الدفع: {method}")
        steps_text, method_name = build_payment_steps(method, lang, price_str)

        remaining = total_seconds
        while remaining > 0:
            time.sleep(60)
            remaining -= 60

            if COUNTDOWNS.get(order_id) is True:
                print(f"🛑 العداد #{order_id} أُلغي (قرار الأدمن)")
                COUNTDOWNS.pop(order_id, None)
                return

            try:
                conn = db_connect()
                cur = conn.cursor()
                cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
                r = cur.fetchone()
                cur.close(); conn.close()
                if r and r["status"] != "pending":
                    print(f"🛑 العداد #{order_id} توقف (status={r['status']})")
                    COUNTDOWNS.pop(order_id, None)
                    return
            except Exception as e:
                print(f"⚠️ DB check #{order_id}: {e}")

            if remaining > 0:
                remaining_text = format_remaining(remaining, lang)
                text = t_lang(lang, "payment_with_timer",
                              method=method_name,
                              steps=steps_text,
                              remaining=remaining_text,
                              oid=order_id)
                try:
                    bot.edit_message_text(
                        text,
                        chat_id=chat_id,
                        message_id=message_id,
                        parse_mode="HTML"
                    )
                    print(f"✅ تم تعديل #{order_id} → المتبقي {remaining}ث")
                except Exception as e:
                    err = str(e).lower()
                    if "message to edit not found" in err or "message can't be edited" in err:
                        print(f"🛑 العداد #{order_id} توقف (الرسالة اختفت)")
                        COUNTDOWNS.pop(order_id, None)
                        return
                    print(f"⚠️ تعديل #{order_id} فشل: {e}")

        try:
            conn = db_connect()
            cur = conn.cursor()
            cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
            r = cur.fetchone()
            if r and r["status"] == "pending":
                cur.execute("UPDATE orders SET status = 'expired' WHERE order_id = %s", (order_id,))
                conn.commit()
                cur.close(); conn.close()

                try:
                    bot.edit_message_text(
                        t_lang(lang, "payment_expired", oid=order_id),
                        chat_id=chat_id,
                        message_id=message_id,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"⚠️ تعديل انتهاء #{order_id}: {e}")

                try:
                    bot.send_message(
                        ADMIN_ID,
                        f"⌛ <b>طلب #{order_id} انتهى وقته</b> (لم يُسدَّد خلال 5 دقائق)",
                        parse_mode="HTML"
                    )
                except: pass
            else:
                cur.close(); conn.close()
            COUNTDOWNS.pop(order_id, None)
            print(f"⌛ العداد #{order_id} انتهى")
        except Exception as e:
            print(f"❌ countdown end: {e}")
            COUNTDOWNS.pop(order_id, None)

    th = threading.Thread(target=run, daemon=True)
    th.start()

# ============ لوحات الأزرار ============
def games_row(uid):
    T = TEXTS[get_lang(uid)]
    order = get_button_order().split(",")
    game_map = {
        "ff": T["btn_ff"],
        "pubg": T["btn_pubg"],
        "jawaker": T["btn_jawaker"],
    }
    return [game_map[g] for g in order if g in game_map]

def main_keyboard(uid):
    lang = get_lang(uid)
    T = TEXTS[lang]
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    games = games_row(uid)
    if len(games) == 3:
        kb.row(games[0], games[1])
        kb.row(games[2])
    else:
        kb.row(*games)

    kb.row(T["btn_info"], T["btn_settings"])

    if uid == ADMIN_ID:
        kb.row(T["btn_support"], T["btn_inbox"])
        kb.row(T["btn_contestants"])
    else:
        kb.row(T["btn_support"])

    return kb

def back_keyboard(uid):
    lang = get_lang(uid)
    T = TEXTS[lang]
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row(T["btn_back"])

    games = games_row(uid)
    if len(games) == 3:
        kb.row(games[0], games[1])
        kb.row(games[2])
    else:
        kb.row(*games)

    kb.row(T["btn_info"], T["btn_settings"])
    if uid == ADMIN_ID:
        kb.row(T["btn_support"], T["btn_inbox"])
        kb.row(T["btn_contestants"])
    else:
        kb.row(T["btn_support"])

    return kb

# ============ رسائل ============
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

def show_packages_for_game(chat_id, uid, game_key):
    lang = get_lang(uid)
    game_data = PACKAGES[game_key]
    game_title = game_data["title"][lang]

    kb = types.InlineKeyboardMarkup(row_width=1)
    for key, item in game_data["items"].items():
        kb.add(types.InlineKeyboardButton(
            text=f"{item[lang]} — {item['price']}",
            callback_data=f"pkg|{game_key}|{key}"
        ))

    bot.send_message(
        chat_id,
        t(uid, "choose_package", game=game_title),
        parse_mode="HTML",
        reply_markup=kb
    )
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {})
    USER_DATA[uid]["step"] = 3

def show_ff_types(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(uid, "btn_ff_diamonds"), callback_data="ff_type|diamonds"),
        types.InlineKeyboardButton(t(uid, "btn_ff_membership"), callback_data="ff_type|membership"),
    )
    bot.send_message(
        chat_id,
        t(uid, "choose_ff_type"),
        parse_mode="HTML",
        reply_markup=kb
    )
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {})
    USER_DATA[uid]["step"] = 2

# ============ زر الرجوع الذكي ============
def go_back(message):
    uid = message.from_user.id
    data = USER_DATA.get(uid, {})
    step = data.get("step", 1)
    print(f"⬅️ go_back: uid={uid} step={step} data={data}")

    if step <= 1:
        bot.send_message(message.chat.id, t(uid, "back_done"),
                         reply_markup=main_keyboard(uid))
        USER_DATA[uid] = {"step": 1}
        return

    if step == 2:
        bot.send_message(message.chat.id, t(uid, "back_done"),
                         reply_markup=main_keyboard(uid))
        USER_DATA[uid] = {"step": 1}
        return

    if step == 3:
        game = data.get("game", "")
        if game in ("ff", "ff_membership"):
            USER_DATA[uid] = {"game": "ff", "step": 2}
            show_ff_types(message.chat.id, uid)
        else:
            bot.send_message(message.chat.id, t(uid, "back_done"),
                             reply_markup=main_keyboard(uid))
            USER_DATA[uid] = {"step": 1}
        return

    if step == 4:
        game = data.get("game", "ff")
        USER_DATA[uid]["step"] = 3
        show_packages_for_game(message.chat.id, uid, game)
        return

    if step == 5:
        game = data.get("game", "ff")
        game_title = PACKAGES[game]["title"][get_lang(uid)]
        USER_DATA[uid]["step"] = 4
        msg = bot.send_message(
            message.chat.id,
            t(uid, "chosen",
              item=data.get("package_name", ""),
              price=data.get("price", ""),
              game=game_title),
            parse_mode="HTML",
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_game_id)
        return

    if step == 6:
        USER_DATA[uid]["step"] = 5
        msg = bot.send_message(
            message.chat.id, t(uid, "send_name"),
            parse_mode="HTML", reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_player_name)
        return

    bot.send_message(message.chat.id, t(uid, "back_done"),
                     reply_markup=main_keyboard(uid))
    USER_DATA[uid] = {"step": 1}

# ============ 🎯 معالج زر الرجوع ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]])
def back_button_handler(message):
    try:
        ensure_user(message)
        go_back(message)
    except Exception as e:
        print(f"❌ back_button_handler: {e}")
        try:
            bot.send_message(
                message.chat.id,
                "⚠️ حدث خطأ، جرّب مرة أخرى",
                reply_markup=main_keyboard(message.from_user.id)
            )
        except: pass

# ============ /start ============
@bot.message_handler(commands=['start'])
def cmd_start(message):
    ensure_user(message)
    uid = message.from_user.id
    if is_subscribed(uid):
        send_welcome(message.chat.id, message.from_user.first_name, uid)
        USER_DATA[uid] = {"step": 1}
    else:
        show_subscription_message(message.chat.id, uid)

# ============ التحقق من الاشتراك ============
@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    try:
        uid = call.from_user.id
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, t(uid, "check_success"))
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            send_welcome(call.message.chat.id, call.from_user.first_name, uid)
            USER_DATA[uid] = {"step": 1}
        else:
            bot.answer_callback_query(call.id, t(uid, "check_fail"), show_alert=True)
    except Exception as e:
        print(f"❌ {e}")

# ============ زر Free Fire ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_ff"], TEXTS["en"]["btn_ff"]])
def show_ff(message):
    ensure_user(message)
    uid = message.from_user.id

    if not is_subscribed(uid):
        show_subscription_message(message.chat.id, uid)
        return

    if not is_orders_open():
        if get_setting("dev_mode", "off") == "on":
            bot.send_message(message.chat.id, t(uid, "orders_closed_dev"), parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, t(uid, "orders_closed"), parse_mode="HTML")
        return

    USER_DATA[uid] = {"game": "ff", "step": 2}
    show_ff_types(message.chat.id, uid)

# ============ PUBG / Jawaker ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_pubg"], TEXTS["en"]["btn_pubg"]])
def show_pubg(message):
    show_game_packages(message, "pubg")

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_jawaker"], TEXTS["en"]["btn_jawaker"]])
def show_jawaker(message):
    show_game_packages(message, "jawaker")

def show_game_packages(message, game):
    ensure_user(message)
    uid = message.from_user.id

    if not is_subscribed(uid):
        show_subscription_message(message.chat.id, uid)
        return

    if not is_orders_open():
        if get_setting("dev_mode", "off") == "on":
            bot.send_message(message.chat.id, t(uid, "orders_closed_dev"), parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, t(uid, "orders_closed"), parse_mode="HTML")
        return

    USER_DATA[uid] = {"game": game, "step": 3}
    show_packages_for_game(message.chat.id, uid, game)

# ============ اختيار نوع FF ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("ff_type|"))
def choose_ff_type(call):
    try:
        ff_type = call.data.split("|")[1]
        uid = call.from_user.id

        bot.answer_callback_query(call.id, "✅")

        if ff_type == "diamonds":
            USER_DATA[uid] = {"game": "ff", "step": 3}
            show_packages_for_game(call.message.chat.id, uid, "ff")
        else:
            USER_DATA[uid] = {"game": "ff_membership", "step": 3}
            show_packages_for_game(call.message.chat.id, uid, "ff_membership")
    except Exception as e:
        print(f"❌ ff_type: {e}")

# ============ اختيار العرض ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg|"))
def choose_package(call):
    try:
        _, game, key = call.data.split("|")
        uid = call.from_user.id
        lang = get_lang(uid)
        item = PACKAGES[game]["items"][key]

        bot.answer_callback_query(call.id, "✅")

        USER_DATA[uid] = {
            "game": game,
            "package_key": key,
            "package_name": item[lang],
            "price": item["price"],
            "step": 4
        }

        game_title = PACKAGES[game]["title"][lang]
        msg = bot.send_message(
            call.message.chat.id,
            t(uid, "chosen", item=item[lang], price=item["price"], game=game_title),
            parse_mode="HTML",
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_game_id)
    except Exception as e:
        print(f"❌ خطأ في choose_package: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ خطأ، حاول من جديد")
        except: pass

# ============ ID ============
def get_game_id(message):
    uid = message.from_user.id

    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        go_back(message)
        return

    data = USER_DATA.get(uid)
    if not data:
        bot.send_message(message.chat.id, "⚠️ اضغط /start من جديد.",
                         reply_markup=main_keyboard(uid))
        return

    game = data.get("game", "ff")
    game_id = message.text.strip() if message.text else ""
    valid, result = validate_game_id(game_id, game)

    if not valid:
        key = "invalid_id_ff" if game in ("ff", "ff_membership") else ("invalid_id_pubg" if game == "pubg" else "invalid_id_jawaker")
        msg = bot.send_message(
            message.chat.id,
            t(uid, key, reason=result),
            parse_mode="HTML",
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_game_id)
        return

    USER_DATA[uid]["game_id"] = result
    USER_DATA[uid]["step"] = 5

    msg = bot.send_message(
        message.chat.id, t(uid, "send_name"),
        parse_mode="HTML",
        reply_markup=back_keyboard(uid)
    )
    bot.register_next_step_handler(msg, get_player_name)

# ============ الاسم ============
def get_player_name(message):
    uid = message.from_user.id

    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        go_back(message)
        return

    data = USER_DATA.get(uid)
    if not data:
        bot.send_message(message.chat.id, "⚠️ اضغط /start من جديد.",
                         reply_markup=main_keyboard(uid))
        return

    player_name = message.text.strip() if message.text else ""
    if len(player_name) < 2:
        msg = bot.send_message(
            message.chat.id, t(uid, "invalid_name"),
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, get_player_name)
        return

    USER_DATA[uid]["player_name"] = player_name
    USER_DATA[uid]["step"] = 6

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(uid, "btn_syriatel"), callback_data="pay|syriatel"),
        types.InlineKeyboardButton(t(uid, "btn_sham"), callback_data="pay|sham"),
    )
    bot.send_message(
        message.chat.id,
        t(uid, "choose_payment"),
        parse_mode="HTML",
        reply_markup=kb
    )
    bot.send_message(message.chat.id, "🔽", reply_markup=back_keyboard(uid))

# ============ اختيار الدفع ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("pay|"))
def choose_payment(call):
    try:
        method = call.data.split("|")[1]
        uid = call.from_user.id
        data = USER_DATA.get(uid)
        if not data or "game_id" not in data:
            bot.answer_callback_query(call.id, "⚠️ اضغط /start من جديد", show_alert=True)
            return

        bot.answer_callback_query(call.id, "✅")

        conn = db_connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (user_id, game, package, price, game_id, player_name, payment_method, status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_id",
            (uid, data["game"], data["package_name"], data["price"],
             data["game_id"], data["player_name"], method, "pending",
             datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        order_id = cur.fetchone()["order_id"]
        conn.commit()
        cur.close(); conn.close()

        lang = get_lang(uid)

        if method == "sham":
            try:
                with open(SHAM_IMAGE_PATH, "rb") as photo:
                    bot.send_photo(
                        call.message.chat.id,
                        photo,
                        caption=t(uid, "sham_image_caption", price=data["price"]),
                        parse_mode="HTML"
                    )
            except FileNotFoundError:
                bot.send_message(call.message.chat.id, "⚠️ صورة sham.jpg غير موجودة")

        steps_text, method_name = build_payment_steps(method, lang, data["price"])
        remaining_text = "5 دقائق" if lang == "ar" else "5 min"

        sent_msg = bot.send_message(
            call.message.chat.id,
            t_lang(lang, "payment_with_timer",
                   method=method_name,
                   steps=steps_text,
                   remaining=remaining_text,
                   oid=order_id),
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )

        start_countdown(
            chat_id=call.message.chat.id,
            message_id=sent_msg.message_id,
            order_id=order_id,
            method=method,
            uid=uid,
            lang=lang,
            price_str=data["price"],
            total_seconds=PAYMENT_TIMEOUT_SECONDS
        )

        method_label = "💳 سيرياتيل كاش" if method == "syriatel" else "📷 شام كاش"
        admin_text = (
            "🔔 <b>طلب شراء جديد!</b>\n\n"
            f"🔖 رقم الطلب: <b>#{order_id}</b>\n"
            f"👤 المستخدم: {call.from_user.full_name}\n"
            f"🆔 يوزر: @{call.from_user.username or 'لا يوجد'}\n"
            f"🆔 تلغرام آيدي: <code>{uid}</code>\n\n"
            f"🎮 اللعبة: <b>{data['game'].upper()}</b>\n"
            f"💎 العرض: <b>{data['package_name']}</b>\n"
            f"💰 السعر: <b>{data['price']}</b>\n"
            f"🎮 ID اللعبة: <code>{data['game_id']}</code>\n"
            f"📝 اسم اللاعب: <b>{data['player_name']}</b>\n"
            f"💳 طريقة الدفع: <b>{method_label}</b>\n"
            f"⏳ <b>مهلة التسديد: 5 دقائق</b>\n\n"
            "اضغط زر الموافقة بعد التأكد:"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"accept|{order_id}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"reject|{order_id}")
        )
        bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML", reply_markup=kb)

        USER_DATA.pop(uid, None)

    except Exception as e:
        print(f"❌ خطأ في choose_payment: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ خطأ، حاول مرة أخرى")
        except: pass

# ============ قبول / رفض ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("accept|") or c.data.startswith("reject|"))
def handle_decision(call):
    try:
        action, oid = call.data.split("|")
        oid = int(oid)

        COUNTDOWNS[oid] = True

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
    except Exception as e:
        print(f"❌ {e}")

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
        "expired": "⌛ انتهى الوقت" if lang == "ar" else "⌛ Expired",
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
    # ✅ إضافة زر المسابقة
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_contest"), callback_data="contest_show"))
    bot.send_message(
        message.chat.id,
        "🎁 <b>هل تريد المشاركة في المسابقة؟</b>\n👇 اضغط الزر بالأسفل",
        parse_mode="HTML",
        reply_markup=kb
    )

# ============ زر المسابقة ============
@bot.callback_query_handler(func=lambda c: c.data == "contest_show")
def contest_show(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id)

    # إذا مسجل من قبل
    entry = get_contest_entry(uid)
    if entry:
        status = contest_status_text(uid, entry["status"])
        bot.send_message(uid, t(uid, "contest_already", status=status), parse_mode="HTML")
        return

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_copy_link"), url=CONTEST_LINK))
    kb.add(types.InlineKeyboardButton(t(uid, "btn_share_done"), callback_data="contest_register"))

    bot.send_message(uid, t(uid, "contest_title"), parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "contest_register")
def contest_register(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id)

    # إذا مسجل من قبل
    entry = get_contest_entry(uid)
    if entry:
        status = contest_status_text(uid, entry["status"])
        bot.send_message(uid, t(uid, "contest_already", status=status), parse_mode="HTML")
        return

    success = register_contest(call.message)
    if success:
        bot.send_message(uid, t(uid, "contest_registered"), parse_mode="HTML")

        # إشعار الأدمن
        admin_text = (
            "🎁 <b>متسابق جديد في المسابقة!</b>\n\n"
            f"👤 الاسم: {call.from_user.full_name}\n"
            f"🆔 <code>{uid}</code>\n"
            f"🌐 @{call.from_user.username or 'لا يوجد'}\n"
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            "👇 راجع المشاركة وقرّر:"
        )
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"contest_ok|{uid}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"contest_no|{uid}"),
        )
        bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML", reply_markup=kb)
    else:
        bot.send_message(uid, "⚠️ أنت مسجل بالفعل!", parse_mode="HTML")

# ============ المطور: قبول/رفض مشارك ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("contest_ok|") or c.data.startswith("contest_no|"))
def contest_decision(call):
    try:
        action, uid_str = call.data.split("|")
        target_uid = int(uid_str)

        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True)
            return

        if action == "contest_ok":
            approve_contest(target_uid)
            bot.answer_callback_query(call.id, "✅ تم القبول")
            try:
                bot.send_message(target_uid, t(target_uid, "contest_approved_msg"), parse_mode="HTML")
            except: pass
        else:
            reject_contest(target_uid)
            bot.answer_callback_query(call.id, "❌ تم الرفض")
            try:
                bot.send_message(target_uid, t(target_uid, "contest_rejected_msg"), parse_mode="HTML")
            except: pass

        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except: pass
    except Exception as e:
        print(f"❌ contest_decision: {e}")

# ============ المطور: زر المتسابقين ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_contestants"], TEXTS["en"]["btn_contestants"]] and m.from_user.id == ADMIN_ID)
def show_contestants(message):
    uid = message.from_user.id

    contestants = get_all_contestants()

    if not contestants:
        bot.send_message(uid, t(uid, "contestants_empty"))
        return

    total = len(contestants)
    approved = sum(1 for c in contestants if c["status"] == "approved")
    pending = sum(1 for c in contestants if c["status"] == "pending")
    rejected = sum(1 for c in contestants if c["status"] == "rejected")

    bot.send_message(
        uid,
        t(uid, "contestants_title", total=total, approved=approved, pending=pending, rejected=rejected),
        parse_mode="HTML"
    )

    for c in contestants:
        status_txt = contest_status_text(uid, c["status"])
        text = t(uid, "contestant_item",
                 name=c["full_name"] or "-",
                 uid=c["user_id"],
                 username=c["username"] or "لا يوجد",
                 status=status_txt,
                 time=c["registered_at"] or "-")

        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton("👤 فتح حساب", url=f"tg://user?id={c['user_id']}"))
        if c["status"] == "pending":
            kb.add(
                types.InlineKeyboardButton("✅ قبول", callback_data=f"contest_ok|{c['user_id']}"),
                types.InlineKeyboardButton("❌ رفض", callback_data=f"contest_no|{c['user_id']}")
            )

        bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)

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

# ============ إرسال شكوى ============
@bot.callback_query_handler(func=lambda c: c.data == "send_complaint")
def ask_complaint(call):
    try:
        uid = call.from_user.id
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            t(uid, "ask_message"),
            parse_mode="HTML",
            reply_markup=back_keyboard(uid)
        )
        bot.register_next_step_handler(msg, receive_complaint)
    except Exception as e:
        print(f"❌ {e}")

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

    admin_text = (
        "📩 <b>رسالة جديدة من المستخدمين!</b>\n\n"
        f"🔖 رقم: #{msg_id}\n"
        f"👤 من: {message.from_user.full_name}\n"
        f"🆔 <code>{uid}</code>\n"
        f"🌐 @{message.from_user.username or 'لا يوجد'}\n\n"
        f"💬 <b>الرسالة:</b>\n{text}"
    )
    bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")

# ============ البريد الوارد ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_inbox"], TEXTS["en"]["btn_inbox"]] and m.from_user.id == ADMIN_ID)
def show_inbox(message):
    uid = message.from_user.id

    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 10")
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

# ============ الإعدادات ============
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
        kb.add(types.InlineKeyboardButton(t(uid, "btn_dev_mode"), callback_data="cfg_dev"))
    kb.add(types.InlineKeyboardButton(t(uid, "btn_reset_data"), callback_data="cfg_reset"))

    title = t(uid, "settings_admin") if is_admin else t(uid, "settings_user")
    bot.send_message(message.chat.id, title, parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "cfg_lang")
def cfg_lang(call):
    try:
        uid = call.from_user.id
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
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cfg_order")
def cfg_order(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True)
            return

        current = get_button_order()
        order_display = {
            "ff,pubg,jawaker": "1️⃣ FF → PUBG → Jawaker",
            "jawaker,ff,pubg": "2️⃣ Jawaker → FF → PUBG",
            "pubg,jawaker,ff": "3️⃣ PUBG → Jawaker → FF",
        }
        order_str = order_display.get(current, current)

        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_1"), callback_data="set_order|ff,pubg,jawaker"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_2"), callback_data="set_order|jawaker,ff,pubg"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_3"), callback_data="set_order|pubg,jawaker,ff"))

        bot.edit_message_text(
            t(uid, "order_current", order=order_str),
            call.message.chat.id, call.message.message_id,
            parse_mode="HTML", reply_markup=kb
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cfg_dev")
def cfg_dev(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True)
            return

        current = get_setting("dev_mode", "off")
        if current == "on":
            text = t(uid, "dev_mode_current_on")
            btn = t(uid, "btn_dev_off")
            cb = "dev|off"
        else:
            text = t(uid, "dev_mode_current_off")
            btn = t(uid, "btn_dev_on")
            cb = "dev|on"

        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(btn, callback_data=cb))

        bot.edit_message_text(
            text,
            call.message.chat.id, call.message.message_id,
            parse_mode="HTML", reply_markup=kb
        )
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("dev|"))
def dev_toggle(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True)
            return

        action = call.data.split("|")[1]
        if action == "on":
            set_setting("dev_mode", "on")
            bot.answer_callback_query(call.id, t(uid, "dev_mode_enabled"), show_alert=True)
            try:
                bot.edit_message_text(
                    t(uid, "dev_mode_current_on"),
                    call.message.chat.id, call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton(t(uid, "btn_dev_off"), callback_data="dev|off")
                    )
                )
            except: pass
        else:
            set_setting("dev_mode", "off")
            bot.answer_callback_query(call.id, t(uid, "dev_mode_disabled"), show_alert=True)
            try:
                bot.edit_message_text(
                    t(uid, "dev_mode_current_off"),
                    call.message.chat.id, call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton(t(uid, "btn_dev_on"), callback_data="dev|on")
                    )
                )
            except: pass
    except Exception as e:
        print(f"❌ dev_toggle: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cfg_reset")
def cfg_reset(call):
    try:
        uid = call.from_user.id
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
    except Exception as e:
        print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_lang|"))
def set_lang(call):
    try:
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
    except Exception as e:
        print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_order|"))
def set_order(call):
    try:
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
    except Exception as e:
        print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "do_reset")
def do_reset(call):
    try:
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
        USER_DATA.pop(uid, None)
        cmd_start(call.message)
    except Exception as e:
        print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cancel_reset")
def cancel_reset(call):
    try:
        bot.answer_callback_query(call.id, "✅")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
    except Exception as e:
        print(f"❌ {e}")

# ============ رسائل غير معروفة ============
@bot.message_handler(func=lambda m: True)
def unknown_message(message):
    try:
        uid = message.from_user.id
        ensure_user(message)
        if is_subscribed(uid):
            bot.send_message(
                message.chat.id,
                t(uid, "unknown_msg"),
                reply_markup=main_keyboard(uid)
            )
        else:
            show_subscription_message(message.chat.id, uid)
    except Exception as e:
        print(f"❌ {e}")

# ============ تشغيل ============
print("🤖 البوت يعمل الآن...")
print("🎁 نظام المسابقة مضاف")

bot.infinity_polling(
    allowed_updates=[
        "message",
        "edited_message",
        "callback_query",
        "inline_query",
        "chosen_inline_result",
        "channel_post",
        "edited_channel_post"
    ],
    skip_pending=True,
    timeout=30,
    long_polling_timeout=30
)
