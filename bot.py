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
DATABASE_URL = os.environ.get("DATABASE_URL",
    "postgresql://postgres:FmMcTnFMJbldpynWXDwrFfXISsKbYKvt@postgres.railway.internal:5432/railway")

SHAM_IMAGE_PATH = "sham.jpg"

ORDERS_OPEN_HOUR = 12
ORDERS_CLOSE_HOUR = 22
PAYMENT_TIMEOUT_SECONDS = 300
REQUIRED_JOINS = 5

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
        print(f"🔧 allowed_updates: {allowed}")

        if "callback_query" in allowed and "chat_member" in allowed:
            print("✅ callback_query + chat_member مسموحان!")
            return True
        return False
    except Exception as e:
        print(f"❌ fix_allowed_updates: {e}")
        return False

fix_allowed_updates()
time.sleep(1)

def check_bot_admin():
    try:
        me = bot.get_me()
        member = bot.get_chat_member(CHANNEL_USERNAME, me.id)
        status = member.status
        print(f"🤖 حالة البوت في القناة: {status}")
        if status not in ("administrator", "creator"):
            print("⚠️⚠️⚠️ البوت ليس مشرف!")
            return False
        if status == "administrator":
            can_invite = getattr(member, "can_invite_users", False)
            print(f"🔑 can_invite_users: {can_invite}")
            if not can_invite:
                print("⚠️ البوت يحتاج صلاحية invite users!")
                return False
        return True
    except Exception as e:
        print(f"❌ check_bot_admin: {e}")
        return False

check_bot_admin()

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
    },
    "bs_global": {
        "title": {"ar": "🌍 Blood Strike — عالمي", "en": "🌍 Blood Strike — Global"},
        "items": {
            "bs_g_51":    {"ar": "51 Gold 🥇",              "en": "51 Gold 🥇",              "price": "75 ل.س"},
            "bs_g_105":   {"ar": "105 Gold 🥇",             "en": "105 Gold 🥇",             "price": "120 ل.س"},
            "bs_g_320":   {"ar": "320 Gold 🥇",             "en": "320 Gold 🥇",             "price": "340 ل.س"},
            "bs_g_540":   {"ar": "540 Gold 🥇",             "en": "540 Gold 🥇",             "price": "550 ل.س"},
            "bs_g_1100":  {"ar": "1100 Gold 🥇",            "en": "1100 Gold 🥇",            "price": "1060 ل.س"},
            "bs_g_lucky": {"ar": "Ultra Skin Lucky Chest 🎁","en": "Ultra Skin Lucky Chest 🎁","price": "620 ل.س"},
            "bs_g_bag":   {"ar": "Lucky Bag Week 💰",       "en": "Lucky Bag Week 💰",       "price": "1220 ل.س"},
            "bs_g_pass_p":{"ar": "Strike Pass Premium 🎫",  "en": "Strike Pass Premium 🎫",  "price": "1080 ل.س"},
            "bs_g_pass_e":{"ar": "Strike Pass Elite 🎫",    "en": "Strike Pass Elite 🎫",    "price": "500 ل.س"},
        }
    }
}

# ============ الترجمة ============
TEXTS = {
    "ar": {
        "welcome": (
            "👋 أهلاً بك <b>{name}</b> في بوت شحن الجواهر والشدات 💎🔥\n\n"
            "🎯 <b>فكرة البوت:</b>\n"
            "يمكنك شحن فري فاير، ببجي، جواكر، أو Blood Strike عبر سيرياتيل كاش أو شام كاش ✅\n\n"
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
        "btn_blood": "🩸 Blood Strike",
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
        "choose_ff_type": "🔥 <b>اختر نوع الشحن في فري فاير:</b>\n\n👇 من الأزرار بالأسفل",
        "btn_ff_diamonds": "💎 شحن جواهر",
        "btn_ff_membership": "⭐ شحن عضوية",
        "choose_bs_server": (
            "🩸 <b>اختر سيرفر Blood Strike:</b>\n\n"
            "🌍 <b>عالمي</b> — يتوفر بشحن فوري\n"
            "🌐 <b>مينا / العرب</b> — قريبًا\n\n"
            "👇 اختر:"
        ),
        "btn_bs_global": "🌍 عالمي",
        "btn_bs_mena": "🌐 مينا / العرب",
        "bs_mena_soon": (
            "🌐 <b>Blood Strike — سيرفر مينا / العرب</b>\n\n"
            "⏳ <b>سيتوفر قريبًا!</b>\n\n"
            "🔔 تابع قناتنا لتصلك أخبار توفره فورًا.\n"
            "شكرًا لصبرك 🙏"
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
        "invalid_id_bs": (
            "❌ <b>ID Blood Strike غير صالح!</b>\n\n"
            "⚠️ {reason}\n\n"
            "📌 <b>شروط ID Blood Strike:</b>\n"
            "• أرقام فقط 🔢\n• من 6 إلى 15 رقم\n• لا يبدأ بـ 0\n\n"
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
        "contest_disabled": "🚫 <b>المسابقة متوقفة حاليًا</b>\n\nعد قريبًا!",
        "contest_title": (
            "🎁 <b>مسابقة البوت!</b>\n\n"
            "🎯 <b>الشروط:</b>\n"
            f"📢 اجلب <b>{REQUIRED_JOINS} أشخاص</b> يشتركوا في القناة عبر رابطك الخاص\n\n"
            "🔗 <b>رابطك الخاص بالدعوة:</b>\n"
            "<code>{link}</code>\n\n"
            "📌 <b>كيف يعمل؟</b>\n"
            "1️⃣ انسخ رابطك بالأعلى ☝️\n"
            "2️⃣ شاركه مع أصحابك\n"
            "3️⃣ كل من يشترك في القناة عبر رابطك = +1 تلقائيًا\n"
            f"4️⃣ عند {REQUIRED_JOINS} مشتركين → تدخل السحب تلقائيًا 🎉\n\n"
            "📊 <b>مدعوينك الحاليين:</b> <b>{count}/{required}</b>\n"
            "🎯 الحالة: {status}"
        ),
        "btn_copy_link": "📋 انسخ الرابط",
        "contest_loading": "⏳ جاري إنشاء رابطك الخاص...",
        "contest_created": (
            "🎉 <b>تم إنشاء رابطك الخاص!</b>\n\n"
            "🔗 <b>رابطك:</b>\n<code>{link}</code>\n\n"
            "📤 شاركه مع أصحابك:\n"
            "📊 <b>مدعوينك:</b> <b>{count}/{required}</b>\n\n"
            "🔔 كل شخص يشترك في القناة عبر رابطك يُحسب تلقائيًا!"
        ),
        "contest_status_active": "🎯 مسابقة نشطة",
        "contest_status_qualified": "🏆 مؤهل للسحب",
        "contest_status_rejected": "❌ مرفوض",
        "contestant_joined": (
            "🎉 <b>مبروك!</b>\n\n"
            "شخص جديد اشترك في القناة عبر رابطك!\n"
            "👤 الاسم: <b>{name}</b>\n\n"
            "📊 <b>مدعوينك الآن:</b> {count}/{required}\n"
            "{extra}"
        ),
        "contestant_complete": (
            "🏆 <b>ألف مبروك!</b>\n\n"
            f"🎊 لقد أكملت <b>{REQUIRED_JOINS} مدعوين</b> ودخلت <b>سحب المسابقة</b> تلقائيًا!\n\n"
            "🍀 حظًا موفقًا! سيتم إعلان الفائز قريبًا."
        ),
        "contestants_title": (
            "🏆 <b>قائمة المتسابقين</b>\n\n"
            "📊 الإجمالي: <b>{total}</b>\n"
            "✅ مؤهلون: <b>{qualified}</b>\n"
            "🎯 نشطون: <b>{active}</b>\n\n"
            "👇 تفاصيل كل متسابق:"
        ),
        "contestants_empty": "📭 لا يوجد متسابقون حتى الآن",
        "contestant_item": (
            "━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>{name}</b>\n"
            "🆔 تلغرام آيدي: <code>{uid}</code>\n"
            "🌐 يوزر: @{username}\n"
            "📊 <b>المدعوين: {count}/{required}</b>\n"
            "🎯 الحالة: {status}\n"
            "🕒 <b>بدأ المسابقة:</b> {time}\n"
            "🕐 <b>آخر مدعو:</b> {last}\n"
            "🔗 <b>رابطه:</b> <code>{link}</code>\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        "contestant_no_last": "لا يوجد بعد",
        "btn_view_details": "📋 تفاصيل كاملة",
        "btn_view_user": "👤 فتح حساب",
        "contestant_full_details": (
            "━━━━━━━━━━━━━━━━━━\n"
            "📋 <b>تفاصيل المتسابق</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "👤 <b>الاسم:</b> {name}\n"
            "🆔 <b>تلغرام آيدي:</b> <code>{uid}</code>\n"
            "🌐 <b>يوزر:</b> @{username}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>بيانات المسابقة</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📊 <b>المدعوين:</b> <b>{count}/{required}</b>\n"
            "🎯 <b>الحالة:</b> {status}\n"
            "🕒 <b>بدأ المسابقة:</b> {created}\n"
            "🕐 <b>آخر مدعو:</b> {last}\n\n"
            "🔗 <b>رابط الدعوة:</b>\n"
            "<code>{link}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "👥 <b>قائمة المدعوين ({count}):</b>\n"
            "{referrals_list}"
        ),
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
        "btn_change_lang": "🌐 تغيير اللغة",
        "btn_change_order": "🔀 ترتيب الأزرار (أدمن)",
        "btn_reset_data": "🗑️ تصفير بياناتي",
        "btn_dev_mode": "🔧 وضع المطور (تشغيل البوت)",
        "btn_contest_toggle": "🎁 إدارة المسابقة",
        "contest_toggle_current_on": (
            "🎁 <b>حالة المسابقة:</b> ✅ مفعّلة\n\n"
            "المستخدمون يمكنهم المشاركة في المسابقة حاليًا.\n\n"
            "اضغط لإيقافها:"
        ),
        "contest_toggle_current_off": (
            "🎁 <b>حالة المسابقة:</b> ❌ متوقفة\n\n"
            "المستخدمون لا يمكنهم المشاركة حاليًا.\n\n"
            "اضغط لتشغيلها:"
        ),
        "btn_contest_toggle_on": "✅ تشغيل المسابقة",
        "btn_contest_toggle_off": "🛑 إيقاف المسابقة",
        "contest_enabled_msg": "✅ <b>تم تشغيل المسابقة</b>\n\nالمستخدمون يمكنهم المشاركة الآن 🎉",
        "contest_disabled_msg": "🛑 <b>تم إيقاف المسابقة</b>\n\nلن يستقبل البوت مشاركات جديدة.",
        "dev_mode_current_on": (
            "🔧 <b>حالة وضع المطور:</b> ✅ مفعّل\n\n"
            "البوت يعمل حاليًا خارج ساعات العمل.\n\n"
            "اضغط لإيقافه:"
        ),
        "dev_mode_current_off": (
            "🔧 <b>حالة وضع المطور:</b> ❌ موقّف\n\n"
            "البوت يتبع ساعات العمل الرسمية (12 - 10).\n\n"
            "اضغط لتشغيله:"
        ),
        "btn_dev_on": "✅ تشغيل البوت مؤقتًا",
        "btn_dev_off": "🛑 إيقاف البوت مؤقتًا",
        "dev_mode_enabled": "✅ <b>وضع المطور مفعّل</b> — البوت يعمل خارج الساعات 🚀",
        "dev_mode_disabled": "🛑 <b>وضع المطور موقّف</b> — عاد لساعات العمل.",
        "lang_changed": "✅ تم تغيير اللغة إلى العربية 🇸🇦",
        "lang_pick": "🌐 اختر اللغة:",
        "reset_confirm": "⚠️ متأكد من حذف كل بياناتك؟",
        "reset_done": "🗑️ تم حذف جميع بياناتك ✅",
        "btn_yes": "✅ نعم، احذف",
        "btn_no": "❌ إلغاء",
        "order_current": "🔀 <b>ترتيب الأزرار:</b>\n\n{order}\n\nاختر:",
        "order_changed": "✅ تم تغيير الترتيب!",
        "btn_order_1": "1️⃣ FF → PUBG → Jawaker → Blood",
        "btn_order_2": "2️⃣ Blood → FF → PUBG → Jawaker",
        "btn_order_3": "3️⃣ Jawaker → Blood → FF → PUBG",
        "back_done": "⬅️ رجعنا للخطوة السابقة",
        "unknown_msg": "🤔 لم أفهم رسالتك. استخدم الأزرار بالأسفل 👇",
        "ask_message": (
            "✉️ <b>أرسل رسالتك الآن</b>\n\n"
            "📝 اكتب شكواك، اقتراحك، أو أي استفسار\n"
            "سيتم إرسالها للإدارة مباشرة ✅"
        ),
        "message_sent": "✅ <b>تم إرسال رسالتك!</b>\n\nسيتم الرد قريبًا 📩",
        "message_too_short": "❌ الرسالة قصيرة! أرسل أطول:",
    },
    "en": {
        "welcome": (
            "👋 Welcome <b>{name}</b> 💎🔥\n\n"
            "🎯 Top up Free Fire, PUBG, Jawaker, or Blood Strike via Syriatel Cash or Sham Cash ✅\n\n"
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
        "btn_blood": "🩸 Blood Strike",
        "btn_info": "👤 My info",
        "btn_support": "🆘 Support",
        "btn_settings": "⚙️ Settings",
        "btn_back": "⬅️ Back",
        "btn_inbox": "📬 Inbox",
        "btn_contestants": "🏆 Contestants",
        "btn_contest": "🎁 Contest",
        "check_success": "✅ Verified! 🎉",
        "check_fail": "❌ Not subscribed!",
        "orders_closed": "⛔ Orders closed.\n🕛 Working: 12 PM - 10 PM 🇸🇦",
        "orders_closed_dev": "🔧 <b>Bot is in maintenance mode</b>",
        "choose_ff_type": "🔥 <b>Choose FF type:</b>\n\n👇 From buttons",
        "btn_ff_diamonds": "💎 Diamonds",
        "btn_ff_membership": "⭐ Membership",
        "choose_bs_server": (
            "🩸 <b>Choose Blood Strike server:</b>\n\n"
            "🌍 <b>Global</b>\n🌐 <b>MENA / Arab</b> — Coming soon\n\n👇"
        ),
        "btn_bs_global": "🌍 Global",
        "btn_bs_mena": "🌐 MENA / Arab",
        "bs_mena_soon": "🌐 <b>Blood Strike — MENA</b>\n\n⏳ <b>Coming soon!</b>",
        "choose_package": "💎 <b>{game} prices:</b>\n\nChoose 👇",
        "chosen": "✅ Chosen: <b>{item}</b> for <b>{price}</b>\n\n🆔 Send your <b>{game} ID</b>:",
        "invalid_id_ff": "❌ <b>Invalid FF ID!</b>\n\n⚠️ {reason}\n\n• Digits only 🔢\n• 5-15 digits\n• No leading 0\n\n🔁 Send valid:",
        "invalid_id_pubg": "❌ <b>Invalid PUBG ID!</b>\n\n⚠️ {reason}\n\n• Digits only 🔢\n• 9-12 digits\n\n🔁 Send valid:",
        "invalid_id_jawaker": "❌ <b>Invalid Jawaker ID!</b>\n\n⚠️ {reason}\n\n🔁 Send valid:",
        "invalid_id_bs": "❌ <b>Invalid Blood Strike ID!</b>\n\n⚠️ {reason}\n\n🔁 Send valid:",
        "send_name": "📝 Now send your <b>in-game name</b>:",
        "invalid_name": "❌ Name too short!",
        "choose_payment": "💳 <b>Choose payment method:</b>",
        "btn_syriatel": "💳 Syriatel Cash",
        "btn_sham": "📷 Sham Cash",
        "payment_with_timer": (
            "💳 <b>Payment: {method}</b>\n\n"
            "📌 <b>Steps:</b>\n{steps}\n\n"
            "⏳ <b>Time left: {remaining}</b>\n\n"
            "🔔 You must pay within <b>5 minutes</b>!\n\n"
            "⚠️ Reviewed by admin ✅\n🔖 Order #<b>{oid}</b>"
        ),
        "payment_expired": "⌛ <b>Payment expired!</b>\n\n🔖 Order #<b>{oid}</b>",
        "sham_image_caption": "📷 <b>Scan to pay via Sham Cash</b>\n\n💰 Amount: <b>{price}</b>",
        "accepted": "✅ <b>Accepted!</b>\n\n💎 <b>{item}</b> within <b>5 min</b> ⏳",
        "rejected": "❌ Order <b>rejected</b>.",
        "my_info": "👤 <b>Info:</b>\n\n📛 {name}\n🆔 <code>{rid}</code>\n📅 {joined}\n🌐 {lang}\n\n🧾 <b>Orders:</b>\n{orders}",
        "no_orders": "No orders yet 😕",
        "contest_disabled": "🚫 <b>Contest is disabled</b>",
        "contest_title": (
            "🎁 <b>Contest!</b>\n\n"
            f"📢 Invite <b>{REQUIRED_JOINS} people</b> to the channel via your link\n\n"
            "🔗 <b>Your link:</b>\n<code>{link}</code>\n\n"
            "📊 <b>Invites:</b> <b>{count}/{required}</b>\n"
            "🎯 Status: {status}"
        ),
        "btn_copy_link": "📋 Copy link",
        "contest_loading": "⏳ Creating your link...",
        "contest_created": "🎉 <b>Link ready!</b>\n\n🔗 <code>{link}</code>\n\n📊 <b>Invites:</b> <b>{count}/{required}</b>",
        "contest_status_active": "🎯 Active",
        "contest_status_qualified": "🏆 Qualified",
        "contest_status_rejected": "❌ Rejected",
        "contestant_joined": "🎉 <b>Someone joined via your link!</b>\n\n👤 {name}\n\n📊 {count}/{required}\n{extra}",
        "contestant_complete": "🏆 <b>Congrats! You entered the draw!</b>",
        "contestants_title": "🏆 <b>Contestants</b>\n\n📊 Total: <b>{total}</b>\n✅ {qualified}\n🎯 {active}",
        "contestants_empty": "📭 No contestants yet",
        "contestant_item": (
            "━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>{name}</b>\n🆔 <code>{uid}</code>\n🌐 @{username}\n"
            "📊 <b>{count}/{required}</b>\n🎯 {status}\n"
            "🕒 {time}\n🕐 {last}\n🔗 <code>{link}</code>\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        "contestant_no_last": "No invites yet",
        "btn_view_details": "📋 Details",
        "btn_view_user": "👤 User",
        "contestant_full_details": (
            "📋 <b>Contestant Details</b>\n\n"
            "👤 <b>{name}</b>\n🆔 <code>{uid}</code>\n🌐 @{username}\n\n"
            "📊 <b>{count}/{required}</b>\n🎯 {status}\n"
            "🕒 {created}\n🕐 {last}\n🔗 <code>{link}</code>\n\n"
            "👥 <b>Invited ({count}):</b>\n{referrals_list}"
        ),
        "inbox_title": "📬 <b>Inbox</b>\n\n📥 Last <b>{count}</b>",
        "inbox_empty": "📭 No messages",
        "inbox_item": "📩 <b>#{n}</b>\n\n👤 {name}\n🆔 <code>{uid}</code>\n🕒 {time}\n\n💬 {msg}",
        "settings_admin": "⚙️ <b>Settings (Admin)</b>",
        "settings_user": "⚙️ <b>Settings</b>",
        "btn_change_lang": "🌐 Change language",
        "btn_change_order": "🔀 Button order",
        "btn_reset_data": "🗑️ Reset my data",
        "btn_dev_mode": "🔧 Developer mode",
        "btn_contest_toggle": "🎁 Manage Contest",
        "contest_toggle_current_on": "🎁 <b>Contest:</b> ✅ ON\n\nPress to disable:",
        "contest_toggle_current_off": "🎁 <b>Contest:</b> ❌ OFF\n\nPress to enable:",
        "btn_contest_toggle_on": "✅ Enable Contest",
        "btn_contest_toggle_off": "🛑 Disable Contest",
        "contest_enabled_msg": "✅ <b>Contest enabled</b>",
        "contest_disabled_msg": "🛑 <b>Contest disabled</b>",
        "dev_mode_current_on": "🔧 <b>Dev Mode:</b> ✅ ON",
        "dev_mode_current_off": "🔧 <b>Dev Mode:</b> ❌ OFF",
        "btn_dev_on": "✅ Enable bot",
        "btn_dev_off": "🛑 Disable bot",
        "dev_mode_enabled": "✅ <b>Dev Mode enabled</b>",
        "dev_mode_disabled": "🛑 <b>Dev Mode disabled</b>",
        "lang_changed": "✅ Language: English 🇬🇧",
        "lang_pick": "🌐 Choose language:",
        "reset_confirm": "⚠️ Delete all your data?",
        "reset_done": "🗑️ Data deleted ✅",
        "btn_yes": "✅ Yes, delete",
        "btn_no": "❌ Cancel",
        "order_current": "🔀 <b>Order:</b>\n\n{order}\n\nChoose:",
        "order_changed": "✅ Order changed!",
        "btn_order_1": "1️⃣ FF → PUBG → Jawaker → Blood",
        "btn_order_2": "2️⃣ Blood → FF → PUBG → Jawaker",
        "btn_order_3": "3️⃣ Jawaker → Blood → FF → PUBG",
        "back_done": "⬅️ Back",
        "unknown_msg": "🤔 I didn't understand.",
        "ask_message": "✉️ <b>Send your message</b>",
        "message_sent": "✅ <b>Sent!</b>",
        "message_too_short": "❌ Too short!",
    }
}

# ============ قاعدة البيانات ============
def db_connect():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY, username TEXT, full_name TEXT,
        random_id TEXT, language TEXT DEFAULT 'ar', joined_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS orders (
        order_id SERIAL PRIMARY KEY, user_id BIGINT, game TEXT, package TEXT,
        price TEXT, game_id TEXT, player_name TEXT, payment_method TEXT,
        status TEXT, created_at TEXT)""")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_method TEXT")
    cur.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY, user_id BIGINT, username TEXT, full_name TEXT,
        message TEXT, is_read BOOLEAN DEFAULT FALSE, created_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS contest (
        user_id BIGINT PRIMARY KEY, username TEXT, full_name TEXT,
        invite_link TEXT UNIQUE, invite_link_name TEXT,
        joins_count INT DEFAULT 0, status TEXT DEFAULT 'active', created_at TEXT)""")
    cur.execute("ALTER TABLE contest ADD COLUMN IF NOT EXISTS username TEXT")
    cur.execute("ALTER TABLE contest ADD COLUMN IF NOT EXISTS full_name TEXT")
    cur.execute("ALTER TABLE contest ADD COLUMN IF NOT EXISTS invite_link TEXT")
    cur.execute("ALTER TABLE contest ADD COLUMN IF NOT EXISTS invite_link_name TEXT")
    cur.execute("ALTER TABLE contest ADD COLUMN IF NOT EXISTS joins_count INT DEFAULT 0")
    cur.execute("ALTER TABLE contest ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active'")
    cur.execute("ALTER TABLE contest ADD COLUMN IF NOT EXISTS created_at TEXT")
    cur.execute("""CREATE TABLE IF NOT EXISTS referrals (
        id SERIAL PRIMARY KEY, referrer_id BIGINT, referred_id BIGINT UNIQUE,
        invite_link TEXT, joined_at TEXT)""")
    cur.execute("ALTER TABLE referrals ADD COLUMN IF NOT EXISTS referrer_id BIGINT")
    cur.execute("ALTER TABLE referrals ADD COLUMN IF NOT EXISTS referred_id BIGINT")
    cur.execute("ALTER TABLE referrals ADD COLUMN IF NOT EXISTS invite_link TEXT")
    cur.execute("ALTER TABLE referrals ADD COLUMN IF NOT EXISTS joined_at TEXT")

    cur.execute("SELECT value FROM settings WHERE key = 'button_order'")
    row = cur.fetchone()
    if row:
        if "blood" not in row["value"]:
            cur.execute("UPDATE settings SET value = 'ff,pubg,jawaker,blood' WHERE key = 'button_order'")
    else:
        cur.execute("INSERT INTO settings VALUES ('button_order', 'ff,pubg,jawaker,blood')")

    cur.execute("INSERT INTO settings VALUES ('dev_mode', 'off') ON CONFLICT (key) DO NOTHING")
    cur.execute("INSERT INTO settings VALUES ('contest_mode', 'on') ON CONFLICT (key) DO NOTHING")

    conn.commit()
    cur.close(); conn.close()
    print("✅ قاعدة البيانات جاهزة")

init_db()

# ============ دوال مساعدة ============
def gen_random_id():
    return str(random.randint(10000000, 99999999))

def get_user(uid):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
    u = cur.fetchone(); cur.close(); conn.close()
    return u

def ensure_user(message):
    uid = message.from_user.id
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (uid,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, random_id, language, joined_at) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (uid, message.from_user.username or "", message.from_user.full_name,
             gen_random_id(), "ar", datetime.now().strftime("%Y-%m-%d %H:%M")))
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
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = 'button_order'")
    row = cur.fetchone(); cur.close(); conn.close()
    return row["value"] if row else "ff,pubg,jawaker,blood"

def set_button_order(value):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE settings SET value = %s WHERE key = 'button_order'", (value,))
    conn.commit(); cur.close(); conn.close()

def get_setting(key, default=None):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row["value"] if row else default

def set_setting(key, value):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""INSERT INTO settings VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value""", (key, value))
    conn.commit(); cur.close(); conn.close()

def is_orders_open():
    if get_setting("dev_mode", "off") == "on":
        return True
    now = datetime.now(timezone(timedelta(hours=3)))
    return ORDERS_OPEN_HOUR <= now.hour < ORDERS_CLOSE_HOUR

def is_contest_open():
    return get_setting("contest_mode", "on") == "on"

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"❌ is_subscribed: {e}")
        return False

def validate_game_id(game_id: str, game: str):
    game_id = game_id.strip()
    if not game_id.isdigit():
        return False, "يجب أن يحتوي على أرقام فقط"
    if game_id.startswith("0"):
        return False, "لا يبدأ بـ 0"
    if game in ("ff", "ff_membership"):
        if len(game_id) < 5: return False, "ID أقل من 5 أرقام"
        if len(game_id) > 15: return False, "ID أكثر من 15 رقم"
    elif game == "pubg":
        if len(game_id) < 9: return False, "ID أقل من 9 أرقام"
        if len(game_id) > 12: return False, "ID أكثر من 12 رقم"
    elif game == "jawaker":
        if len(game_id) < 6: return False, "ID أقل من 6 أرقام"
        if len(game_id) > 12: return False, "ID أكثر من 12 رقم"
    elif game == "bs_global":
        if len(game_id) < 6: return False, "ID أقل من 6 أرقام"
        if len(game_id) > 15: return False, "ID أكثر من 15 رقم"
    return True, game_id

# ============ المسابقة ============
def create_user_invite_link(uid):
    """
    ينشئ رابط دعوة فريد للمستخدم
    ✅ بدون member_limit — يقبل عدداً غير محدود من المدعوين
    """
    try:
        link_name = f"ref_{uid}_{int(time.time())}"
        result = bot.create_chat_invite_link(
            chat_id=CHANNEL_USERNAME,
            name=link_name,
            creates_join_request=False
            # ✅ لا نستخدم member_limit — حتى يبقى الرابط فعالاً
        )
        return result.invite_link, link_name
    except Exception as e:
        print(f"❌ create_user_invite_link: {e}")
        return None, None

def get_contest_entry(uid):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM contest WHERE user_id = %s", (uid,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row

def register_contest_user(uid, username, full_name):
    invite_link, link_name = create_user_invite_link(uid)
    if not invite_link:
        return None
    conn = db_connect(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO contest (user_id, username, full_name, invite_link, invite_link_name, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
        (uid, username, full_name, invite_link, link_name,
         datetime.now().strftime("%Y-%m-%d %H:%M")))
    row = cur.fetchone(); conn.commit(); cur.close(); conn.close()
    return row

def get_all_contestants():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM contest ORDER BY joins_count DESC, created_at DESC")
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def get_last_referral_time(referrer_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT joined_at FROM referrals WHERE referrer_id = %s "
                "ORDER BY joined_at DESC LIMIT 1", (referrer_id,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row["joined_at"] if row else None

def get_referrals_list(referrer_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("""SELECT r.referred_id, r.joined_at, u.full_name, u.username
        FROM referrals r LEFT JOIN users u ON u.user_id = r.referred_id
        WHERE r.referrer_id = %s ORDER BY r.joined_at ASC""", (referrer_id,))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def contest_status_text(lang, status):
    if status == "qualified":
        return TEXTS[lang]["contest_status_qualified"]
    elif status == "rejected":
        return TEXTS[lang]["contest_status_rejected"]
    else:
        return TEXTS[lang]["contest_status_active"]

# ============ العداد الحي ============
def format_remaining(seconds, lang):
    m = seconds // 60; s = seconds % 60
    if lang == "en":
        if m > 0 and s > 0: return f"{m} min {s} sec"
        elif m > 0: return f"{m} min"
        else: return f"{s} sec"
    else:
        if m > 0 and s > 0: return f"{m} دقيقة و {s} ثانية"
        elif m > 0: return f"{m} دقيقة"
        else: return f"{s} ثانية"

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
        print(f"⏳ بدء العداد #{order_id}")
        steps_text, method_name = build_payment_steps(method, lang, price_str)
        remaining = total_seconds
        while remaining > 0:
            time.sleep(60); remaining -= 60
            if COUNTDOWNS.get(order_id) is True:
                COUNTDOWNS.pop(order_id, None); return
            try:
                conn = db_connect(); cur = conn.cursor()
                cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
                r = cur.fetchone(); cur.close(); conn.close()
                if r and r["status"] != "pending":
                    COUNTDOWNS.pop(order_id, None); return
            except Exception as e:
                print(f"⚠️ DB check #{order_id}: {e}")
            if remaining > 0:
                remaining_text = format_remaining(remaining, lang)
                text = t_lang(lang, "payment_with_timer", method=method_name,
                              steps=steps_text, remaining=remaining_text, oid=order_id)
                try:
                    bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
                except Exception as e:
                    err = str(e).lower()
                    if "message to edit not found" in err or "message can't be edited" in err:
                        COUNTDOWNS.pop(order_id, None); return
        try:
            conn = db_connect(); cur = conn.cursor()
            cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
            r = cur.fetchone()
            if r and r["status"] == "pending":
                cur.execute("UPDATE orders SET status = 'expired' WHERE order_id = %s", (order_id,))
                conn.commit(); cur.close(); conn.close()
                try:
                    bot.edit_message_text(t_lang(lang, "payment_expired", oid=order_id),
                                          chat_id=chat_id, message_id=message_id, parse_mode="HTML")
                except: pass
                try:
                    bot.send_message(ADMIN_ID, f"⌛ <b>طلب #{order_id} انتهى وقته</b>", parse_mode="HTML")
                except: pass
            else:
                cur.close(); conn.close()
            COUNTDOWNS.pop(order_id, None)
        except Exception as e:
            print(f"❌ countdown end: {e}")
            COUNTDOWNS.pop(order_id, None)
    th = threading.Thread(target=run, daemon=True); th.start()

# ============ لوحات الأزرار ============
def games_row(uid):
    T = TEXTS[get_lang(uid)]
    order = get_button_order().split(",")
    game_map = {
        "ff": T["btn_ff"],
        "pubg": T["btn_pubg"],
        "jawaker": T["btn_jawaker"],
        "blood": T["btn_blood"],
    }
    return [game_map[g] for g in order if g in game_map]

def main_keyboard(uid):
    lang = get_lang(uid); T = TEXTS[lang]
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    games = games_row(uid)
    # نوزع الأزرار 2-2
    if len(games) == 4:
        kb.row(games[0], games[1]); kb.row(games[2], games[3])
    elif len(games) == 3:
        kb.row(games[0], games[1]); kb.row(games[2])
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
    lang = get_lang(uid); T = TEXTS[lang]
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(T["btn_back"])
    games = games_row(uid)
    if len(games) == 4:
        kb.row(games[0], games[1]); kb.row(games[2], games[3])
    elif len(games) == 3:
        kb.row(games[0], games[1]); kb.row(games[2])
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
    bot.send_message(chat_id, t(uid, "welcome", name=first_name),
                     parse_mode="HTML", reply_markup=main_keyboard(uid))

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
            callback_data=f"pkg|{game_key}|{key}"))
    bot.send_message(chat_id, t(uid, "choose_package", game=game_title),
                     parse_mode="HTML", reply_markup=kb)
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {}); USER_DATA[uid]["step"] = 3

def show_ff_types(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(uid, "btn_ff_diamonds"), callback_data="ff_type|diamonds"),
        types.InlineKeyboardButton(t(uid, "btn_ff_membership"), callback_data="ff_type|membership"))
    bot.send_message(chat_id, t(uid, "choose_ff_type"), parse_mode="HTML", reply_markup=kb)
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {}); USER_DATA[uid]["step"] = 2

def show_bs_servers(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(uid, "btn_bs_global"), callback_data="bs_server|global"),
        types.InlineKeyboardButton(t(uid, "btn_bs_mena"), callback_data="bs_server|mena"))
    bot.send_message(chat_id, t(uid, "choose_bs_server"), parse_mode="HTML", reply_markup=kb)
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {}); USER_DATA[uid]["step"] = 2

# ============ زر الرجوع ============
def go_back(message):
    uid = message.from_user.id
    data = USER_DATA.get(uid, {}); step = data.get("step", 1)
    if step <= 1:
        bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid))
        USER_DATA[uid] = {"step": 1}; return
    if step == 2:
        bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid))
        USER_DATA[uid] = {"step": 1}; return
    if step == 3:
        game = data.get("game", "")
        if game in ("ff", "ff_membership"):
            USER_DATA[uid] = {"game": "ff", "step": 2}
            show_ff_types(message.chat.id, uid)
        elif game == "bs_global":
            USER_DATA[uid] = {"game": "blood", "step": 2}
            show_bs_servers(message.chat.id, uid)
        else:
            bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid))
            USER_DATA[uid] = {"step": 1}
        return
    if step == 4:
        game = data.get("game", "ff")
        USER_DATA[uid]["step"] = 3
        show_packages_for_game(message.chat.id, uid, game); return
    if step == 5:
        game = data.get("game", "ff")
        game_title = PACKAGES[game]["title"][get_lang(uid)]
        USER_DATA[uid]["step"] = 4
        msg = bot.send_message(message.chat.id,
            t(uid, "chosen", item=data.get("package_name", ""),
              price=data.get("price", ""), game=game_title),
            parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_game_id); return
    if step == 6:
        USER_DATA[uid]["step"] = 5
        msg = bot.send_message(message.chat.id, t(uid, "send_name"),
                               parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_player_name); return
    bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid))
    USER_DATA[uid] = {"step": 1}

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]])
def back_button_handler(message):
    try:
        ensure_user(message); go_back(message)
    except Exception as e:
        print(f"❌ back_button_handler: {e}")

# ============ /start ============
@bot.message_handler(commands=['start'])
def cmd_start(message):
    ensure_user(message); uid = message.from_user.id
    if is_subscribed(uid):
        send_welcome(message.chat.id, message.from_user.first_name, uid)
        USER_DATA[uid] = {"step": 1}
    else:
        show_subscription_message(message.chat.id, uid)

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    try:
        uid = call.from_user.id
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, t(uid, "check_success"))
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            send_welcome(call.message.chat.id, call.from_user.first_name, uid)
            USER_DATA[uid] = {"step": 1}
        else:
            bot.answer_callback_query(call.id, t(uid, "check_fail"), show_alert=True)
    except Exception as e: print(f"❌ {e}")

# ============ حدث انضمام عضو ============
@bot.chat_member_handler()
def on_chat_member(update):
    try:
        new_member = update.new_chat_member
        old_member = update.old_chat_member
        if not (old_member.status in ("left", "kicked") and new_member.status == "member"):
            return
        new_user_id = new_member.user.id
        new_user_name = new_member.user.full_name
        invite_link = update.invite_link
        if not invite_link:
            print(f"⚠️ انضم بدون رابط: {new_user_name}")
            return
        used_link = invite_link.invite_link
        print(f"🎉 عضو جديد: {new_user_name} | رابط: {used_link}")
        conn = db_connect(); cur = conn.cursor()
        cur.execute("SELECT user_id FROM contest WHERE invite_link = %s", (used_link,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            print(f"⚠️ الرابط غير مرتبط")
            return
        referrer_id = row["user_id"]
        cur.execute("SELECT id FROM referrals WHERE referred_id = %s", (new_user_id,))
        if cur.fetchone():
            cur.close(); conn.close(); return
        cur.execute(
            "INSERT INTO referrals (referrer_id, referred_id, invite_link, joined_at) "
            "VALUES (%s, %s, %s, %s)",
            (referrer_id, new_user_id, used_link, datetime.now().strftime("%Y-%m-%d %H:%M")))
        cur.execute("UPDATE contest SET joins_count = joins_count + 1 WHERE user_id = %s RETURNING joins_count",
                    (referrer_id,))
        new_count = cur.fetchone()["joins_count"]
        conn.commit(); cur.close(); conn.close()
        # إعلام الداعي — نستخدم t_lang لتجنب التعارض
        referrer_lang = get_lang(referrer_id)
        try:
            extra = ""
            if new_count >= REQUIRED_JOINS:
                extra = TEXTS[referrer_lang]["contestant_complete"]
            msg_text = t_lang(referrer_lang, "contestant_joined",
                              name=new_user_name, count=new_count,
                              required=REQUIRED_JOINS, extra=extra)
            bot.send_message(referrer_id, msg_text, parse_mode="HTML")
            print(f"✅ إشعار {referrer_id}: {new_count}/{REQUIRED_JOINS}")
        except Exception as e:
            print(f"⚠️ فشل إشعار الداعي: {e}")
        if new_count >= REQUIRED_JOINS:
            conn = db_connect(); cur = conn.cursor()
            cur.execute("UPDATE contest SET status = 'qualified' WHERE user_id = %s", (referrer_id,))
            conn.commit(); cur.close(); conn.close()
            try:
                bot.send_message(ADMIN_ID,
                    f"🏆 <b>متسابق مؤهل جديد!</b>\n🆔 <code>{referrer_id}</code>\n📊 {new_count}",
                    parse_mode="HTML")
            except: pass
    except Exception as e:
        print(f"❌ on_chat_member: {e}")

# ============ أزرار الألعاب ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_ff"], TEXTS["en"]["btn_ff"]])
def show_ff(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    if not is_orders_open():
        bot.send_message(message.chat.id, t(uid, "orders_closed_dev") if get_setting("dev_mode", "off") == "on" else t(uid, "orders_closed"), parse_mode="HTML")
        return
    USER_DATA[uid] = {"game": "ff", "step": 2}
    show_ff_types(message.chat.id, uid)

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_blood"], TEXTS["en"]["btn_blood"]])
def show_blood(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    if not is_orders_open():
        bot.send_message(message.chat.id, t(uid, "orders_closed_dev") if get_setting("dev_mode", "off") == "on" else t(uid, "orders_closed"), parse_mode="HTML")
        return
    USER_DATA[uid] = {"game": "blood", "step": 2}
    show_bs_servers(message.chat.id, uid)

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_pubg"], TEXTS["en"]["btn_pubg"]])
def show_pubg(message): show_game_packages(message, "pubg")

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_jawaker"], TEXTS["en"]["btn_jawaker"]])
def show_jawaker(message): show_game_packages(message, "jawaker")

def show_game_packages(message, game):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    if not is_orders_open():
        bot.send_message(message.chat.id, t(uid, "orders_closed_dev") if get_setting("dev_mode", "off") == "on" else t(uid, "orders_closed"), parse_mode="HTML")
        return
    USER_DATA[uid] = {"game": game, "step": 3}
    show_packages_for_game(message.chat.id, uid, game)

@bot.callback_query_handler(func=lambda c: c.data.startswith("ff_type|"))
def choose_ff_type(call):
    try:
        ff_type = call.data.split("|")[1]; uid = call.from_user.id
        bot.answer_callback_query(call.id, "✅")
        if ff_type == "diamonds":
            USER_DATA[uid] = {"game": "ff", "step": 3}
            show_packages_for_game(call.message.chat.id, uid, "ff")
        else:
            USER_DATA[uid] = {"game": "ff_membership", "step": 3}
            show_packages_for_game(call.message.chat.id, uid, "ff_membership")
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("bs_server|"))
def choose_bs_server(call):
    try:
        server = call.data.split("|")[1]; uid = call.from_user.id
        bot.answer_callback_query(call.id, "✅")
        if server == "global":
            USER_DATA[uid] = {"game": "bs_global", "step": 3}
            show_packages_for_game(call.message.chat.id, uid, "bs_global")
        else:
            # MENA — قريباً
            bot.send_message(call.message.chat.id, t(uid, "bs_mena_soon"),
                             parse_mode="HTML", reply_markup=main_keyboard(uid))
            USER_DATA[uid] = {"step": 1}
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg|"))
def choose_package(call):
    try:
        _, game, key = call.data.split("|")
        uid = call.from_user.id; lang = get_lang(uid)
        item = PACKAGES[game]["items"][key]
        bot.answer_callback_query(call.id, "✅")
        USER_DATA[uid] = {"game": game, "package_key": key,
                          "package_name": item[lang], "price": item["price"], "step": 4}
        game_title = PACKAGES[game]["title"][lang]
        msg = bot.send_message(call.message.chat.id,
            t(uid, "chosen", item=item[lang], price=item["price"], game=game_title),
            parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_game_id)
    except Exception as e:
        print(f"❌ {e}")
        try: bot.answer_callback_query(call.id, "⚠️")
        except: pass

def get_game_id(message):
    uid = message.from_user.id
    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        go_back(message); return
    data = USER_DATA.get(uid)
    if not data:
        bot.send_message(message.chat.id, "⚠️ /start", reply_markup=main_keyboard(uid)); return
    game = data.get("game", "ff")
    game_id = message.text.strip() if message.text else ""
    valid, result = validate_game_id(game_id, game)
    if not valid:
        if game in ("ff", "ff_membership"): key = "invalid_id_ff"
        elif game == "pubg": key = "invalid_id_pubg"
        elif game == "jawaker": key = "invalid_id_jawaker"
        else: key = "invalid_id_bs"
        msg = bot.send_message(message.chat.id, t(uid, key, reason=result),
                               parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_game_id); return
    USER_DATA[uid]["game_id"] = result; USER_DATA[uid]["step"] = 5
    msg = bot.send_message(message.chat.id, t(uid, "send_name"),
                           parse_mode="HTML", reply_markup=back_keyboard(uid))
    bot.register_next_step_handler(msg, get_player_name)

def get_player_name(message):
    uid = message.from_user.id
    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        go_back(message); return
    data = USER_DATA.get(uid)
    if not data:
        bot.send_message(message.chat.id, "⚠️ /start", reply_markup=main_keyboard(uid)); return
    player_name = message.text.strip() if message.text else ""
    if len(player_name) < 2:
        msg = bot.send_message(message.chat.id, t(uid, "invalid_name"),
                               reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_player_name); return
    USER_DATA[uid]["player_name"] = player_name; USER_DATA[uid]["step"] = 6
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(t(uid, "btn_syriatel"), callback_data="pay|syriatel"),
        types.InlineKeyboardButton(t(uid, "btn_sham"), callback_data="pay|sham"))
    bot.send_message(message.chat.id, t(uid, "choose_payment"), parse_mode="HTML", reply_markup=kb)
    bot.send_message(message.chat.id, "🔽", reply_markup=back_keyboard(uid))

@bot.callback_query_handler(func=lambda c: c.data.startswith("pay|"))
def choose_payment(call):
    try:
        method = call.data.split("|")[1]; uid = call.from_user.id
        data = USER_DATA.get(uid)
        if not data or "game_id" not in data:
            bot.answer_callback_query(call.id, "⚠️ /start", show_alert=True); return
        bot.answer_callback_query(call.id, "✅")
        conn = db_connect(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (user_id, game, package, price, game_id, player_name, payment_method, status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_id",
            (uid, data["game"], data["package_name"], data["price"],
             data["game_id"], data["player_name"], method, "pending",
             datetime.now().strftime("%Y-%m-%d %H:%M")))
        order_id = cur.fetchone()["order_id"]
        conn.commit(); cur.close(); conn.close()
        lang = get_lang(uid)
        if method == "sham":
            try:
                with open(SHAM_IMAGE_PATH, "rb") as photo:
                    bot.send_photo(call.message.chat.id, photo,
                                   caption=t(uid, "sham_image_caption", price=data["price"]),
                                   parse_mode="HTML")
            except FileNotFoundError:
                bot.send_message(call.message.chat.id, "⚠️ sham.jpg")
        steps_text, method_name = build_payment_steps(method, lang, data["price"])
        remaining_text = "5 دقائق" if lang == "ar" else "5 min"
        sent_msg = bot.send_message(call.message.chat.id,
            t_lang(lang, "payment_with_timer", method=method_name, steps=steps_text,
                   remaining=remaining_text, oid=order_id),
            parse_mode="HTML", reply_markup=main_keyboard(uid))
        start_countdown(call.message.chat.id, sent_msg.message_id, order_id,
                        method, uid, lang, data["price"], PAYMENT_TIMEOUT_SECONDS)
        method_label = "💳 سيرياتيل كاش" if method == "syriatel" else "📷 شام كاش"
        admin_text = (
            "🔔 <b>طلب شراء جديد!</b>\n\n"
            f"🔖 رقم الطلب: <b>#{order_id}</b>\n"
            f"👤 {call.from_user.full_name}\n"
            f"🆔 <code>{uid}</code>\n\n"
            f"🎮 {data['game'].upper()}\n"
            f"💎 <b>{data['package_name']}</b>\n"
            f"💰 <b>{data['price']}</b>\n"
            f"🎮 ID: <code>{data['game_id']}</code>\n"
            f"📝 <b>{data['player_name']}</b>\n"
            f"💳 <b>{method_label}</b>")
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"accept|{order_id}"),
               types.InlineKeyboardButton("❌ رفض", callback_data=f"reject|{order_id}"))
        bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML", reply_markup=kb)
        USER_DATA.pop(uid, None)
    except Exception as e: print(f"❌ choose_payment: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("accept|") or c.data.startswith("reject|"))
def handle_decision(call):
    try:
        action, oid = call.data.split("|"); oid = int(oid)
        COUNTDOWNS[oid] = True
        conn = db_connect(); cur = conn.cursor()
        cur.execute("SELECT user_id, package FROM orders WHERE order_id = %s", (oid,))
        row = cur.fetchone()
        if not row:
            bot.answer_callback_query(call.id, "⚠️"); cur.close(); conn.close(); return
        user_id = row["user_id"]; package = row["package"]
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
        try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except: pass
    except Exception as e: print(f"❌ {e}")

# ============ معلوماتي ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_info"], TEXTS["en"]["btn_info"]])
def my_info(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    u = get_user(uid); lang = get_lang(uid)
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT order_id, package, price, status, created_at FROM orders "
                "WHERE user_id = %s ORDER BY order_id DESC LIMIT 5", (uid,))
    orders = cur.fetchall(); cur.close(); conn.close()
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
            orders_text += (f"\n🔖 #{o['order_id']} — {o['package']} ({o['price']})\n"
                            f"   {status_map.get(o['status'], o['status'])} | {o['created_at']}\n")
    bot.send_message(message.chat.id,
        t(uid, "my_info", name=message.from_user.full_name,
          rid=u["random_id"] if u else "-", joined=u["joined_at"] if u else "-",
          lang="العربية 🇸🇦" if lang == "ar" else "English 🇬🇧", orders=orders_text),
        parse_mode="HTML")
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_contest"), callback_data="contest_show"))
    bot.send_message(message.chat.id,
        "🎁 <b>هل تريد المشاركة في المسابقة؟</b>\n👇",
        parse_mode="HTML", reply_markup=kb)

# ============ المسابقة ============
@bot.callback_query_handler(func=lambda c: c.data == "contest_show")
def contest_show(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id)

    # 🚫 إذا المسابقة متوقفة
    if not is_contest_open():
        bot.send_message(uid, t(uid, "contest_disabled"), parse_mode="HTML")
        return

    entry = get_contest_entry(uid)
    lang = get_lang(uid)
    if entry:
        status = contest_status_text(lang, entry["status"])
        text = t(uid, "contest_title", link=entry["invite_link"],
                 count=entry["joins_count"], required=REQUIRED_JOINS, status=status)
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(t(uid, "btn_copy_link"), url=entry["invite_link"]))
        bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
    else:
        msg = bot.send_message(uid, t(uid, "contest_loading"))
        try: bot.delete_message(uid, msg.message_id)
        except: pass
        try:
            me = bot.get_me()
            member = bot.get_chat_member(CHANNEL_USERNAME, me.id)
            if member.status not in ("administrator", "creator"):
                bot.send_message(uid, "⚠️ البوت غير مضاف كمشرف!\n👨‍💻 " + SUPPORT_USERNAME)
                return
        except Exception as e: print(f"❌ {e}")
        new_entry = register_contest_user(uid, call.from_user.username or "", call.from_user.full_name)
        if not new_entry:
            bot.send_message(uid, "⚠️ حدث خطأ في إنشاء الرابط.")
            return
        text = t(uid, "contest_created", link=new_entry["invite_link"],
                 count=0, required=REQUIRED_JOINS)
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(t(uid, "btn_copy_link"), url=new_entry["invite_link"]))
        bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
        try:
            bot.send_message(ADMIN_ID,
                f"🎁 <b>متسابق جديد!</b>\n\n"
                f"👤 {call.from_user.full_name}\n🆔 <code>{uid}</code>\n"
                f"🌐 @{call.from_user.username or 'لا يوجد'}\n"
                f"🔗 {new_entry['invite_link']}", parse_mode="HTML")
        except: pass

# ============ قائمة المتسابقين ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_contestants"], TEXTS["en"]["btn_contestants"]] and m.from_user.id == ADMIN_ID)
def show_contestants(message):
    uid = message.from_user.id
    contestants = get_all_contestants()
    if not contestants:
        bot.send_message(uid, t(uid, "contestants_empty")); return
    total = len(contestants)
    qualified = sum(1 for c in contestants if c["status"] == "qualified")
    active = sum(1 for c in contestants if c["status"] == "active")
    bot.send_message(uid,
        t(uid, "contestants_title", total=total, qualified=qualified, active=active),
        parse_mode="HTML")
    for c in contestants:
        status_txt = contest_status_text(get_lang(uid), c["status"])
        last_ref = get_last_referral_time(c["user_id"])
        last_txt = last_ref if last_ref else t(uid, "contestant_no_last")
        text = t(uid, "contestant_item",
                 name=c["full_name"] or "-", uid=c["user_id"],
                 username=c["username"] or "لا يوجد",
                 count=c["joins_count"], required=REQUIRED_JOINS,
                 status=status_txt, time=c["created_at"] or "-",
                 last=last_txt, link=c["invite_link"] or "-")
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(t(uid, "btn_view_details"),
                                          callback_data=f"cdetails|{c['user_id']}"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_view_user"),
                                          url=f"tg://user?id={c['user_id']}"))
        bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("cdetails|"))
def contestant_details(call):
    try:
        uid_admin = call.from_user.id
        if uid_admin != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True); return
        target_uid = int(call.data.split("|")[1])
        bot.answer_callback_query(call.id)
        conn = db_connect(); cur = conn.cursor()
        cur.execute("SELECT * FROM contest WHERE user_id = %s", (target_uid,))
        entry = cur.fetchone(); cur.close(); conn.close()
        if not entry:
            bot.send_message(uid_admin, "⚠️ غير موجود"); return
        last_ref = get_last_referral_time(target_uid)
        last_txt = last_ref if last_ref else "لا يوجد بعد"
        refs = get_referrals_list(target_uid)
        if refs:
            refs_text = ""
            for i, r in enumerate(refs, 1):
                name = r["full_name"] or "مستخدم"
                refs_text += f"   {i}. 👤 {name} — <code>{r['referred_id']}</code> — {r['joined_at']}\n"
        else:
            refs_text = "   لم يدعُ أحدًا بعد"
        status_txt = contest_status_text(get_lang(uid_admin), entry["status"])
        text = t(uid_admin, "contestant_full_details",
                 name=entry["full_name"] or "-", uid=entry["user_id"],
                 username=entry["username"] or "لا يوجد",
                 count=entry["joins_count"], required=REQUIRED_JOINS,
                 status=status_txt, created=entry["created_at"] or "-",
                 last=last_txt, link=entry["invite_link"] or "-",
                 referrals_list=refs_text)
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("👤 فتح حساب",
                                          url=f"tg://user?id={entry['user_id']}"))
        bot.send_message(uid_admin, text, parse_mode="HTML", reply_markup=kb)
    except Exception as e: print(f"❌ {e}")

# ============ الدعم ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_support"], TEXTS["en"]["btn_support"]])
def support(message):
    uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_complaint"), callback_data="send_complaint"))
    bot.send_message(message.chat.id, t(uid, "support"), parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "send_complaint")
def ask_complaint(call):
    try:
        uid = call.from_user.id
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, t(uid, "ask_message"),
                               parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, receive_complaint)
    except Exception as e: print(f"❌ {e}")

def receive_complaint(message):
    uid = message.from_user.id
    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]:
        bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid)); return
    text = message.text.strip() if message.text else ""
    if len(text) < 5:
        msg = bot.send_message(message.chat.id, t(uid, "message_too_short"),
                               reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, receive_complaint); return
    conn = db_connect(); cur = conn.cursor()
    cur.execute("INSERT INTO messages (user_id, username, full_name, message, created_at) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (uid, message.from_user.username or "", message.from_user.full_name,
                 text, datetime.now().strftime("%Y-%m-%d %H:%M")))
    msg_id = cur.fetchone()["id"]; conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, t(uid, "message_sent"), parse_mode="HTML",
                     reply_markup=main_keyboard(uid))
    bot.send_message(ADMIN_ID,
        f"📩 <b>رسالة جديدة!</b>\n\n🔖 #{msg_id}\n👤 {message.from_user.full_name}\n"
        f"🆔 <code>{uid}</code>\n🌐 @{message.from_user.username or 'لا يوجد'}\n\n💬 {text}",
        parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_inbox"], TEXTS["en"]["btn_inbox"]] and m.from_user.id == ADMIN_ID)
def show_inbox(message):
    uid = message.from_user.id
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 10")
    msgs = cur.fetchall(); cur.close(); conn.close()
    if not msgs:
        bot.send_message(message.chat.id, t(uid, "inbox_empty")); return
    bot.send_message(message.chat.id, t(uid, "inbox_title", count=len(msgs)), parse_mode="HTML")
    for m in msgs:
        text = t(uid, "inbox_item", n=m["id"], name=m["full_name"],
                 uid=m["user_id"], time=m["created_at"], msg=m["message"])
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("👤 الرد", url=f"tg://user?id={m['user_id']}"))
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=kb)

# ============ الإعدادات ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_settings"], TEXTS["en"]["btn_settings"]])
def settings_menu(message):
    uid = message.from_user.id; ensure_user(message)
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    is_admin = (uid == ADMIN_ID)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(t(uid, "btn_change_lang"), callback_data="cfg_lang"))
    if is_admin:
        kb.add(types.InlineKeyboardButton(t(uid, "btn_change_order"), callback_data="cfg_order"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_dev_mode"), callback_data="cfg_dev"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_contest_toggle"), callback_data="cfg_contest"))
    kb.add(types.InlineKeyboardButton(t(uid, "btn_reset_data"), callback_data="cfg_reset"))
    title = t(uid, "settings_admin") if is_admin else t(uid, "settings_user")
    bot.send_message(message.chat.id, title, parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "cfg_lang")
def cfg_lang(call):
    try:
        uid = call.from_user.id
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang|ar"),
               types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang|en"))
        bot.edit_message_text(t(uid, "lang_pick"), call.message.chat.id,
                              call.message.message_id, reply_markup=kb)
        bot.answer_callback_query(call.id)
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cfg_order")
def cfg_order(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True); return
        current = get_button_order()
        order_display = {
            "ff,pubg,jawaker,blood": "1️⃣ FF → PUBG → Jawaker → Blood",
            "blood,ff,pubg,jawaker": "2️⃣ Blood → FF → PUBG → Jawaker",
            "jawaker,blood,ff,pubg": "3️⃣ Jawaker → Blood → FF → PUBG",
        }
        order_str = order_display.get(current, current)
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_1"), callback_data="set_order|ff,pubg,jawaker,blood"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_2"), callback_data="set_order|blood,ff,pubg,jawaker"))
        kb.add(types.InlineKeyboardButton(t(uid, "btn_order_3"), callback_data="set_order|jawaker,blood,ff,pubg"))
        bot.edit_message_text(t(uid, "order_current", order=order_str),
                              call.message.chat.id, call.message.message_id,
                              parse_mode="HTML", reply_markup=kb)
        bot.answer_callback_query(call.id)
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cfg_dev")
def cfg_dev(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True); return
        current = get_setting("dev_mode", "off")
        if current == "on":
            text = t(uid, "dev_mode_current_on"); btn = t(uid, "btn_dev_off"); cb = "dev|off"
        else:
            text = t(uid, "dev_mode_current_off"); btn = t(uid, "btn_dev_on"); cb = "dev|on"
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(btn, callback_data=cb))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="HTML", reply_markup=kb)
        bot.answer_callback_query(call.id)
    except Exception as e: print(f"❌ {e}")

# ============ إدارة المسابقة ============
@bot.callback_query_handler(func=lambda c: c.data == "cfg_contest")
def cfg_contest(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True); return
        current = get_setting("contest_mode", "on")
        if current == "on":
            text = t(uid, "contest_toggle_current_on")
            btn = t(uid, "btn_contest_toggle_off"); cb = "contest|off"
        else:
            text = t(uid, "contest_toggle_current_off")
            btn = t(uid, "btn_contest_toggle_on"); cb = "contest|on"
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(btn, callback_data=cb))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="HTML", reply_markup=kb)
        bot.answer_callback_query(call.id)
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("contest|"))
def contest_toggle(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True); return
        action = call.data.split("|")[1]
        if action == "on":
            set_setting("contest_mode", "on")
            bot.answer_callback_query(call.id, t(uid, "contest_enabled_msg"), show_alert=True)
            try:
                bot.edit_message_text(t(uid, "contest_toggle_current_on"),
                    call.message.chat.id, call.message.message_id, parse_mode="HTML",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton(t(uid, "btn_contest_toggle_off"), callback_data="contest|off")))
            except: pass
        else:
            set_setting("contest_mode", "off")
            bot.answer_callback_query(call.id, t(uid, "contest_disabled_msg"), show_alert=True)
            try:
                bot.edit_message_text(t(uid, "contest_toggle_current_off"),
                    call.message.chat.id, call.message.message_id, parse_mode="HTML",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton(t(uid, "btn_contest_toggle_on"), callback_data="contest|on")))
            except: pass
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("dev|"))
def dev_toggle(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True); return
        action = call.data.split("|")[1]
        if action == "on":
            set_setting("dev_mode", "on")
            bot.answer_callback_query(call.id, t(uid, "dev_mode_enabled"), show_alert=True)
            try:
                bot.edit_message_text(t(uid, "dev_mode_current_on"),
                    call.message.chat.id, call.message.message_id, parse_mode="HTML",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton(t(uid, "btn_dev_off"), callback_data="dev|off")))
            except: pass
        else:
            set_setting("dev_mode", "off")
            bot.answer_callback_query(call.id, t(uid, "dev_mode_disabled"), show_alert=True)
            try:
                bot.edit_message_text(t(uid, "dev_mode_current_off"),
                    call.message.chat.id, call.message.message_id, parse_mode="HTML",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton(t(uid, "btn_dev_on"), callback_data="dev|on")))
            except: pass
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cfg_reset")
def cfg_reset(call):
    try:
        uid = call.from_user.id
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton(t(uid, "btn_yes"), callback_data="do_reset"),
               types.InlineKeyboardButton(t(uid, "btn_no"), callback_data="cancel_reset"))
        bot.edit_message_text(t(uid, "reset_confirm"), call.message.chat.id,
                              call.message.message_id, reply_markup=kb)
        bot.answer_callback_query(call.id)
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_lang|"))
def set_lang(call):
    try:
        uid = call.from_user.id
        new_lang = call.data.split("|")[1]
        conn = db_connect(); cur = conn.cursor()
        cur.execute("UPDATE users SET language = %s WHERE user_id = %s", (new_lang, uid))
        conn.commit(); cur.close(); conn.close()
        bot.answer_callback_query(call.id, t(uid, "lang_changed"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, t(uid, "lang_changed"),
                         reply_markup=main_keyboard(uid))
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_order|"))
def set_order(call):
    try:
        uid = call.from_user.id
        if uid != ADMIN_ID:
            bot.answer_callback_query(call.id, "🚫", show_alert=True); return
        new_order = call.data.split("|")[1]
        set_button_order(new_order)
        bot.answer_callback_query(call.id, t(uid, "order_changed"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, t(uid, "order_changed"),
                         reply_markup=main_keyboard(uid))
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "do_reset")
def do_reset(call):
    try:
        uid = call.from_user.id
        conn = db_connect(); cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE user_id = %s", (uid,))
        cur.execute("DELETE FROM users WHERE user_id = %s", (uid,))
        conn.commit(); cur.close(); conn.close()
        bot.answer_callback_query(call.id, "🗑️")
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, t(uid, "reset_done"))
        USER_DATA.pop(uid, None)
        cmd_start(call.message)
    except Exception as e: print(f"❌ {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cancel_reset")
def cancel_reset(call):
    try:
        bot.answer_callback_query(call.id, "✅")
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
    except Exception as e: print(f"❌ {e}")

# ============ رسائل غير معروفة ============
@bot.message_handler(func=lambda m: True)
def unknown_message(message):
    try:
        uid = message.from_user.id
        ensure_user(message)
        if is_subscribed(uid):
            bot.send_message(message.chat.id, t(uid, "unknown_msg"),
                             reply_markup=main_keyboard(uid))
        else:
            show_subscription_message(message.chat.id, uid)
    except Exception as e: print(f"❌ {e}")

# ============ تشغيل ============
print("🤖 البوت يعمل الآن...")
print("🩸 Blood Strike مضاف")
print("🎁 إدارة المسابقة في الإعدادات")
print("🔗 member_limit محذوف — روابط دائمة")

bot.infinity_polling(
    allowed_updates=[
        "message", "edited_message", "callback_query",
        "inline_query", "chosen_inline_result",
        "channel_post", "edited_channel_post",
        "chat_member", "my_chat_member", "chat_join_request"
    ],
    skip_pending=True,
    timeout=30,
    long_polling_timeout=30
    )
