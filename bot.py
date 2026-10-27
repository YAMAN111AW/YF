import telebot
from telebot import types
import sqlite3
import random
import os
import time
import threading
from datetime import datetime, timezone, timedelta
import requests

# ============ الإعدادات ============
BOT_TOKEN = "8956086702:AAEtcqzxJwA7W7daV3s4DiDMjSMTt9InJ3k"
ADMIN_ID = 6382473367
SUPPORT_USERNAME = "@Yamen494"
CHANNEL_USERNAME = "@YF494YF"
CHANNEL_LINK = "https://t.me/YF494YF"
SHAM_IMAGE_PATH = "sham.jpg"

# إعدادات API SYRIA
API_SYRIA_KEY = "aedbba18bca3c5d4dd6ce5e0ac92db9451c36561f95aad69cba348338c67fed7"
API_SYRIA_ACCOUNT = "86471023dde39efc379b0f2fad8592e4"

ORDERS_OPEN_HOUR = 12
ORDERS_CLOSE_HOUR = 22
REQUIRED_JOINS = 5

bot = telebot.TeleBot(BOT_TOKEN)
USER_DATA = {}

def fix_allowed_updates():
    try:
        r1 = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook", params={"drop_pending_updates": "true"}, timeout=10)
        r2 = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params={"allowed_updates": '["message","edited_message","channel_post","edited_channel_post","callback_query","inline_query","chosen_inline_result","poll","poll_answer","my_chat_member","chat_member","chat_join_request"]', "timeout": 1}, timeout=15)
        print("✅ تم إعداد التحديثات")
        return True
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
        return status in ("administrator", "creator")
    except Exception as e:
        print(f"❌ check_bot_admin: {e}")
        return False

check_bot_admin()

# ============ الأسعار ============
PACKAGES = {
    "ff": {
        "title": {"ar": "💎 شحن جواهر فري فاير", "en": "💎 Free Fire Diamonds"},
        "items": {
            "ff_110": {"ar": "110 جوهرة 💎", "en": "110 Diamonds 💎", "price": 160.0},
            "ff_231": {"ar": "231 جوهرة 💎", "en": "231 Diamonds 💎", "price": 290.0},
            "ff_583": {"ar": "583 جوهرة 💎", "en": "583 Diamonds 💎", "price": 700.0},
        }
    },
    "ff_membership": {
        "title": {"ar": "⭐ عضوية فري فاير", "en": "⭐ Free Fire Membership"},
        "items": {
            "ffm_week":  {"ar": "عضوية أسبوعية ⭐", "en": "Weekly Membership ⭐", "price": 340.0},
            "ffm_month": {"ar": "عضوية شهرية ⭐",  "en": "Monthly Membership ⭐", "price": 1540.0},
        }
    },
    "pubg": {
        "title": {"ar": "🎯 ببجي", "en": "🎯 PUBG"},
        "items": {
            "pubg_60":   {"ar": "60 شدة 🪙",   "en": "60 UC 🪙",   "price": 140.0},
            "pubg_325":  {"ar": "325 شدة 🪙",  "en": "325 UC 🪙",  "price": 670.0},
            "pubg_660":  {"ar": "660 شدة 🪙",  "en": "660 UC 🪙",  "price": 1300.0},
            "pubg_1800": {"ar": "1800 شدة 🪙", "en": "1800 UC 🪙", "price": 3210.0},
        }
    },
    "jawaker": {
        "title": {"ar": "🃏 شحن توكنز جواكر", "en": "🃏 Jawaker Tokens"},
        "items": {
            "jw_10000":  {"ar": "10000 توكنز ♦️",  "en": "10000 Tokens ♦️",  "price": 180.0},
            "jw_15000":  {"ar": "15000 توكنز ♠️",  "en": "15000 Tokens ♠️",  "price": 260.0},
            "jw_20000":  {"ar": "20000 توكنز ♥️",  "en": "20000 Tokens ♥️",  "price": 340.0},
            "jw_30000":  {"ar": "30000 توكنز ♣️",  "en": "30000 Tokens ♣️",  "price": 490.0},
            "jw_50000":  {"ar": "50000 توكنز 🃏",  "en": "50000 Tokens 🃏",  "price": 790.0},
            "jw_100000": {"ar": "100000 توكنز 👑", "en": "100000 Tokens 👑", "price": 1550.0},
        }
    },
    "jawaker_premium": {
        "title": {"ar": "👑 بريميوم جواكر", "en": "👑 Jawaker Premium"},
        "items": {
            "jw_prem_silver": {"ar": "بريميوم جواكر 🃏 (فضي)", "en": "Jawaker Premium 🃏 (Silver)", "price": 900.0},
            "jw_prem_red":    {"ar": "بريميوم جواكر 🃏 (أحمر)", "en": "Jawaker Premium 🃏 (Red)",    "price": 3750.0},
        }
    },
    "bs_global": {
        "title": {"ar": "🌍 Blood Strike — عالمي", "en": "🌍 Blood Strike — Global"},
        "items": {
            "bs_g_51":    {"ar": "51 Gold 🥇",              "en": "51 Gold 🥇",              "price": 75.0},
            "bs_g_105":   {"ar": "105 Gold 🥇",             "en": "105 Gold 🥇",             "price": 120.0},
            "bs_g_320":   {"ar": "320 Gold 🥇",             "en": "320 Gold 🥇",             "price": 340.0},
            "bs_g_540":   {"ar": "540 Gold 🥇",             "en": "540 Gold 🥇",             "price": 550.0},
            "bs_g_1100":  {"ar": "1100 Gold 🥇",            "en": "1100 Gold 🥇",            "price": 1060.0},
            "bs_g_lucky": {"ar": "Ultra Skin Lucky Chest 🎁","en": "Ultra Skin Lucky Chest 🎁","price": 620.0},
            "bs_g_bag":   {"ar": "Lucky Bag Week 💰",       "en": "Lucky Bag Week 💰",       "price": 1220.0},
            "bs_g_pass_p":{"ar": "Strike Pass Premium 🎫",  "en": "Strike Pass Premium 🎫",  "price": 1080.0},
            "bs_g_pass_e":{"ar": "Strike Pass Elite 🎫",    "en": "Strike Pass Elite 🎫",    "price": 500.0},
        }
    }
}

# ============ الترجمة ============
TEXTS = {
    "ar": {
        "welcome": "👋 أهلاً بك <b>{name}</b> في بوت شحن الجواهر والشدات 💎🔥\n\n🎯 <b>فكرة البوت:</b>\nيمكنك شحن فري فاير، ببجي، جواكر، أو Blood Strike عبر رصيد المحفظة الداخلي ✅\n\n💰 <b>رصيدك الحالي:</b> <b>{balance} ل.س</b>\n\n📌 <b>طريقة الشراء:</b>\n1️⃣ اختر اللعبة\n2️⃣ اختر العرض\n3️⃣ أرسل ID حسابك\n4️⃣ أرسل اسمك في اللعبة\n5️⃣ سيتم خصم المبلغ وإرسال الطلب للإدارة ✅\n\n⏰ <b>الطلبات تُقبل من 12 ظهرًا حتى 10 مساءً بتوقيت السعودية</b> 🇸🇦",
        "subscribe_required": "🔒 <b>عذرًا عزيزي!</b>\n\n⚠️ يجب عليك <b>الاشتراك في قناتنا أولاً</b> لاستخدام البوت 💎\n\n📢 القناة: {CHANNEL_USERNAME}\n\n1️⃣ اضغط زر <b>اشترك في القناة</b>\n2️⃣ اشترك ✅\n3️⃣ ارجع واضغط <b>تحقق</b> 🔄",
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
        "btn_deposit": "💳 إيداع رصيد",
        "btn_wallet": "💰 محفظتي",
        "check_success": "✅ تم التحقق بنجاح! أهلاً بك 🎉",
        "check_fail": "❌ لم تشترك في القناة بعد!",
        "orders_closed": "⛔ عذرًا، البوت لا يستقبل الطلبات حاليًا.\n🕛 ساعات العمل: من <b>12 ظهرًا</b> حتى <b>10 مساءً</b> بتوقيت السعودية 🇸🇦",
        "orders_closed_dev": "🔧 <b>البوت في وضع الصيانة/التجارب مؤقتًا</b>\n\n⛔ لا يستقبل الطلبات حاليًا.\n🔄 يرجى المحاولة لاحقًا.",
        "choose_ff_type": "🔥 <b>اختر نوع الشحن في فري فاير:</b>\n\n👇 من الأزرار بالأسفل",
        "btn_ff_diamonds": "💎 شحن جواهر",
        "btn_ff_membership": "⭐ شحن عضوية",
        "choose_jw_type": "🃏 <b>اختر نوع الشحن في جواكر:</b>\n\n👇 اختر من الأزرار بالأسفل",
        "btn_jw_tokens": "💰 شحن توكنز",
        "btn_jw_premium": "👑 شحن بريميوم",
        "choose_bs_server": "🩸 <b>اختر سيرفر Blood Strike:</b>\n\n🌍 <b>عالمي</b> — يتوفر بشحن فوري\n🌐 <b>مينا / العرب</b> — قريبًا\n\n👇 اختر:",
        "btn_bs_global": "🌍 عالمي",
        "btn_bs_mena": "🌐 مينا / العرب",
        "bs_mena_soon": "🌐 <b>Blood Strike — سيرفر مينا / العرب</b>\n\n⏳ <b>سيتوفر قريبًا!</b>\n\n🔔 تابع قناتنا لتصلك أخبار توفره فورًا.\nشكرًا لصبرك 🙏",
        "choose_package": "💎 <b>قائمة أسعار {game}:</b>\n\nاختر العرض الذي تريده 👇",
        "chosen": "✅ اخترت: <b>{item}</b> بسعر <b>{price}</b> ل.س\n\n🆔 أرسل <b>ID حسابك في {game}</b>:\n\n💡 <i>ملاحظة: يجب أن يكون ID حقيقي (أرقام فقط)</i>",
        "invalid_id_ff": "❌ <b>ID Free Fire غير صالح!</b>\n\n⚠️ {reason}\n\n📌 <b>شروط ID فري فاير:</b>\n• أرقام فقط 🔢\n• من 5 إلى 15 رقم\n• لا يبدأ بـ 0\n\n🔁 أرسل ID صحيح:",
        "invalid_id_pubg": "❌ <b>ID PUBG غير صالح!</b>\n\n⚠️ {reason}\n\n📌 <b>شروط ID ببجي:</b>\n• أرقام فقط 🔢\n• من 9 إلى 12 رقم\n• لا يبدأ بـ 0\n\n🔁 أرسل ID صحيح:",
        "invalid_id_jawaker": "❌ <b>ID جواكر غير صالح!</b>\n\n⚠️ {reason}\n\n📌 <b>شروط ID جواكر:</b>\n• أرقام فقط 🔢\n• من 6 إلى 12 رقم\n• لا يبدأ بـ 0\n\n🔁 أرسل ID صحيح:",
        "invalid_id_bs": "❌ <b>ID Blood Strike غير صالح!</b>\n\n⚠️ {reason}\n\n📌 <b>شروط ID Blood Strike:</b>\n• أرقام فقط 🔢\n• من 6 إلى 15 رقم\n• لا يبدأ بـ 0\n\n🔁 أرسل ID صحيح:",
        "send_name": "📝 ممتاز! الآن أرسل <b>اسمك داخل اللعبة</b>:",
        "invalid_name": "❌ الاسم قصير جدًا! أرسل اسمك الصحيح:",
        "accepted": "✅ <b>تم قبول طلبك!</b>\n\n💎 <b>{item}</b> سيصلك خلال <b>5 دقائق</b> ⏳\n\nشكرًا لثقتك ❤️",
        "rejected": "❌ عذرًا، تم <b>رفض طلبك</b>.\nتواصل مع الدعم 🆘",
        "wallet_paid": "✅ <b>تم خصم {price} ل.س من محفظتك بنجاح!</b>\n\n💎 طلبك قيد المعالجة الآن.",
        "wallet_insufficient": "❌ <b>رصيدك غير كافي!</b>\n\n💰 رصيدك الحالي: <b>{balance} ل.س</b>\n💵 المطلوب: <b>{price} ل.س</b>\n\nقم بالإيداع أولاً عبر زر (💳 إيداع رصيد).",
        "my_info": "👤 <b>معلوماتك:</b>\n\n📛 الاسم: <b>{name}</b>\n🆔 الآيدي: <code>{rid}</code>\n💰 الرصيد: <b>{balance} ل.س</b>\n📅 التسجيل: {joined}\n🌐 اللغة: {lang}\n\n🧾 <b>آخر عمليات الشراء:</b>\n{orders}",
        "no_orders": "لا يوجد أي عمليات شراء حتى الآن 😕",
        "wallet_info": "💰 <b>محفظتك:</b>\n\nرصيدك الحالي هو: <b>{balance} ل.س</b>",
        "deposit_caption": "💳 <b>الإيداع عبر شام كاش</b>\n\n📷 امسح الكود بالأعلى للتحويل إلى الحساب التالي:\n<code>{account}</code>\n\n💰 المبلغ: <b>{amount} ل.س</b>\n\nبعد التحويل، أرسل <b>رقم عملية التحويل (Transaction ID)</b> هنا:",
        "deposit_ask_amount": "💳 <b>أدخل المبلغ الذي تريد إيداعه بالليرة السورية (ل.س):</b>\n\nمثال: 500",
        "deposit_verify": "⏳ جاري التحقق من عملية التحويل...",
        "deposit_success": "✅ <b>تم التحقق من التحويل بنجاح!</b>\n\n💰 تم إضافة <b>{amount} ل.س</b> إلى محفظتك.\n💳 رصيدك الجديد: <b>{balance} ل.س</b>",
        "deposit_fail": "❌ <b>فشل التحقق:</b> {reason}",
        "deposit_used": "❌ رقم العملية هذا تم استخدامه مسبقاً!",
        "deposit_expired": "❌ رقم العملية هذا قديم! يجب أن يتم التحويل خلال 5 دقائق من إرسال الرقم.",
        "deposit_invalid_amount": "❌ الرجاء إدخال مبلغ صحيح (أرقام فقط).",
        "deposit_invalid_tx": "❌ رقم العملية يجب أن يكون أرقاماً فقط.",
        "admin_add_balance_usage": "⚠️ <b>طريقة الاستخدام:</b>\n<code>/sendrasid [ID/Username] [Amount]</code>\n\n<b>أمثلة:</b>\n<code>/sendrasid 6382473367 500</code> (آيدي تلغرام)\n<code>/sendrasid @Yamen 500</code> (يوزر)\n<code>/sendrasid 12345678 500</code> (آيدي البوت)",
        "admin_user_not_found": "❌ لم يتم العثور على مستخدم بهذا الآيدي أو اليوزر.",
        "admin_balance_added": "✅ تم إضافة <b>{amount} ل.س</b> إلى رصيد المستخدم <b>{name}</b>.\n💰 رصيده الجديد: <b>{balance} ل.س</b>",
        "contest_disabled": "🚫 <b>المسابقة متوقفة حاليًا</b>\n\nعد قريبًا!",
        "contest_title": "🎁 <b>مسابقة البوت!</b>\n\n🎯 <b>الشروط:</b>\n📢 اجلب <b>{REQUIRED_JOINS} أشخاص</b> يشتركوا في القناة عبر رابطك الخاص\n\n🔗 <b>رابطك الخاص بالدعوة:</b>\n<code>{link}</code>\n\n📌 <b>كيف يعمل؟</b>\n1️⃣ انسخ رابطك بالأعلى ☝️\n2️⃣ شاركه مع أصحابك\n3️⃣ كل من يشترك في القناة عبر رابطك = +1 تلقائيًا\n4️⃣ عند {REQUIRED_JOINS} مشتركين → تدخل السحب تلقائيًا 🎉\n\n📊 <b>مدعوينك الحاليين:</b> <b>{count}/{required}</b>\n🎯 الحالة: {status}",
        "btn_copy_link": "📋 انسخ الرابط",
        "contest_loading": "⏳ جاري إنشاء رابطك الخاص...",
        "contest_created": "🎉 <b>تم إنشاء رابطك الخاص!</b>\n\n🔗 <b>رابطك:</b>\n<code>{link}</code>\n\n📤 شاركه مع أصحابك:\n📊 <b>مدعوينك:</b> <b>{count}/{required}</b>\n\n🔔 كل شخص يشترك في القناة عبر رابطك يُحسب تلقائيًا!",
        "contest_status_active": "🎯 مسابقة نشطة",
        "contest_status_qualified": "🏆 مؤهل للسحب",
        "contest_status_rejected": "❌ مرفوض",
        "contestant_joined": "🎉 <b>مبروك!</b>\n\nشخص جديد اشترك في القناة عبر رابطك!\n👤 الاسم: <b>{name}</b>\n\n📊 <b>مدعوينك الآن:</b> {count}/{required}\n{extra}",
        "contestant_complete": "🏆 <b>ألف مبروك!</b>\n\n🎊 لقد أكملت <b>{REQUIRED_JOINS} مدعوين</b> ودخلت <b>سحب المسابقة</b> تلقائيًا!\n\n🍀 حظًا موفقًا! سيتم إعلان الفائز قريبًا.",
        "contestants_title": "🏆 <b>قائمة المتسابقين</b>\n\n📊 الإجمالي: <b>{total}</b>\n✅ مؤهلون: <b>{qualified}</b>\n🎯 نشطون: <b>{active}</b>\n\n👇 تفاصيل كل متسابق:",
        "contestants_empty": "📭 لا يوجد متسابقون حتى الآن",
        "contestant_item": "━━━━━━━━━━━━━━━━━━\n👤 <b>{name}</b>\n🆔 تلغرام آيدي: <code>{uid}</code>\n🌐 يوزر: @{username}\n📊 <b>المدعوين: {count}/{required}</b>\n🎯 الحالة: {status}\n🕒 <b>بدأ المسابقة:</b> {time}\n🕐 <b>آخر مدعو:</b> {last}\n🔗 <b>رابطه:</b> <code>{link}</code>\n━━━━━━━━━━━━━━━━━━",
        "contestant_no_last": "لا يوجد بعد",
        "btn_view_details": "📋 تفاصيل كاملة",
        "btn_view_user": "👤 فتح حساب",
        "contestant_full_details": "━━━━━━━━━━━━━━━━━━\n📋 <b>تفاصيل المتسابق</b>\n━━━━━━━━━━━━━━━━━━\n\n👤 <b>الاسم:</b> {name}\n🆔 <b>تلغرام آيدي:</b> <code>{uid}</code>\n🌐 <b>يوزر:</b> @{username}\n\n━━━━━━━━━━━━━━━━━━\n🎁 <b>بيانات المسابقة</b>\n━━━━━━━━━━━━━━━━━━\n\n📊 <b>المدعوين:</b> <b>{count}/{required}</b>\n🎯 <b>الحالة:</b> {status}\n🕒 <b>بدأ المسابقة:</b> {created}\n🕐 <b>آخر مدعو:</b> {last}\n\n🔗 <b>رابط الدعوة:</b>\n<code>{link}</code>\n\n━━━━━━━━━━━━━━━━━━\n👥 <b>قائمة المدعوين ({count}):</b>\n{referrals_list}",
        "inbox_title": "📬 <b>البريد الوارد</b>\n\n📥 آخر <b>{count}</b> رسالة",
        "inbox_empty": "📭 لا يوجد رسائل حتى الآن",
        "inbox_item": "📩 <b>شكوى رقم #{n}</b>\n\n👤 الاسم: <b>{name}</b>\n🆔 <code>{uid}</code>\n🕒 {time}\n\n💬 <b>الشكوى:</b>\n{msg}",
        "settings_admin": "⚙️ <b>الإعدادات (أدمن)</b>\n\nاختر:",
        "settings_user": "⚙️ <b>الإعدادات</b>\n\nاختر:",
        "btn_change_lang": "🌐 تغيير اللغة",
        "btn_change_order": "🔀 ترتيب الأزرار (أدمن)",
        "btn_reset_data": "🗑️ تصفير بياناتي",
        "btn_dev_mode": "🔧 وضع المطور (تشغيل البوت)",
        "btn_contest_toggle": "🎁 إدارة المسابقة",
        "contest_toggle_current_on": "🎁 <b>حالة المسابقة:</b> ✅ مفعّلة\n\nالمستخدمون يمكنهم المشاركة حاليًا.\n\nاضغط لإيقافها:",
        "contest_toggle_current_off": "🎁 <b>حالة المسابقة:</b> ❌ متوقفة\n\nالمستخدمون لا يمكنهم المشاركة حاليًا.\n\nاضغط لتشغيلها:",
        "btn_contest_toggle_on": "✅ تشغيل المسابقة",
        "btn_contest_toggle_off": "🛑 إيقاف المسابقة",
        "contest_enabled_msg": "✅ <b>تم تشغيل المسابقة</b>\n\nالمستخدمون يمكنهم المشاركة الآن 🎉",
        "contest_disabled_msg": "🛑 <b>تم إيقاف المسابقة</b>\n\nلن يستقبل البوت مشاركات جديدة.",
        "dev_mode_current_on": "🔧 <b>حالة وضع المطور:</b> ✅ مفعّل\n\nالبوت يعمل حاليًا خارج ساعات العمل.\n\nاضغط لإيقافه:",
        "dev_mode_current_off": "🔧 <b>حالة وضع المطور:</b> ❌ موقّف\n\nالبوت يتبع ساعات العمل الرسمية (12 - 10).\n\nاضغط لتشغيله:",
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
        "ask_message": "✉️ <b>أرسل رسالتك الآن</b>\n\n📝 اكتب شكواك، اقتراحك، أو أي استفسار\nسيتم إرسالها للإدارة مباشرة ✅",
        "message_sent": "✅ <b>تم إرسال رسالتك!</b>\n\nسيتم الرد قريبًا 📩",
        "message_too_short": "❌ الرسالة قصيرة! أرسل أطول:",
        "support": "🆘 <b>مركز الدعم الفني</b>\n\n👨‍💻 للتواصل: {SUPPORT_USERNAME}\n\n📖 <b>طريقة الاستخدام:</b>\n1️⃣ اختر اللعبة\n2️⃣ اختر عرض الشحن 💎\n3️⃣ أرسل ID حسابك 🆔\n4️⃣ أرسل اسمك في اللعبة 📝\n5️⃣ تأكيد الطلب\n\n⏰ <b>ساعات العمل:</b> 12 ظهرًا - 10 مساءً 🇸🇦\n\n👇 يمكنك إرسال شكوى أو اقتراح عبر الزر بالأسفل:",
        "btn_complaint": "✉️ إرسال شكوى / اقتراح",
    },
    "en": {
        "welcome": "👋 Welcome <b>{name}</b> 💎🔥\n\n🎯 Top up Free Fire, PUBG, Jawaker, or Blood Strike via Wallet ✅\n\n💰 <b>Current Balance:</b> <b>{balance} SYP</b>\n\n📌 <b>How to buy:</b>\n1️⃣ Choose game\n2️⃣ Choose package\n3️⃣ Send your ID\n4️⃣ Send in-game name\n5️⃣ Amount deducted, order sent to admin ✅\n\n⏰ <b>Orders: 12 PM - 10 PM (Saudi time)</b> 🇸🇦",
        "subscribe_required": "🔒 <b>Sorry!</b>\n\n⚠️ Subscribe to our channel first 💎\n\n📢 {CHANNEL_USERNAME}\n\n1️⃣ Subscribe\n2️⃣ Join ✅\n3️⃣ Check 🔄",
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
        "btn_deposit": "💳 Deposit",
        "btn_wallet": "💰 My Wallet",
        "check_success": "✅ Verified! 🎉",
        "check_fail": "❌ Not subscribed!",
        "orders_closed": "⛔ Orders closed.\n🕛 Working: 12 PM - 10 PM 🇸🇦",
        "orders_closed_dev": "🔧 <b>Bot is in maintenance mode</b>",
        "choose_ff_type": "🔥 <b>Choose FF type:</b>\n\n👇 From buttons",
        "btn_ff_diamonds": "💎 Diamonds",
        "btn_ff_membership": "⭐ Membership",
        "choose_jw_type": "🃏 <b>Choose Jawaker top-up type:</b>\n\n👇 From buttons below",
        "btn_jw_tokens": "💰 Tokens",
        "btn_jw_premium": "👑 Premium",
        "choose_bs_server": "🩸 <b>Choose Blood Strike server:</b>\n\n🌍 <b>Global</b>\n🌐 <b>MENA / Arab</b> — Coming soon\n\n👇",
        "btn_bs_global": "🌍 Global",
        "btn_bs_mena": "🌐 MENA / Arab",
        "bs_mena_soon": "🌐 <b>Blood Strike — MENA</b>\n\n⏳ <b>Coming soon!</b>",
        "choose_package": "💎 <b>{game} prices:</b>\n\nChoose 👇",
        "chosen": "✅ Chosen: <b>{item}</b> for <b>{price} SYP</b>\n\n🆔 Send your <b>{game} ID</b>:",
        "invalid_id_ff": "❌ <b>Invalid FF ID!</b>\n\n⚠️ {reason}\n\n• Digits only 🔢\n• 5-15 digits\n• No leading 0\n\n🔁 Send valid:",
        "invalid_id_pubg": "❌ <b>Invalid PUBG ID!</b>\n\n⚠️ {reason}\n\n• Digits only 🔢\n• 9-12 digits\n\n🔁 Send valid:",
        "invalid_id_jawaker": "❌ <b>Invalid Jawaker ID!</b>\n\n⚠️ {reason}\n\n🔁 Send valid:",
        "invalid_id_bs": "❌ <b>Invalid Blood Strike ID!</b>\n\n⚠️ {reason}\n\n🔁 Send valid:",
        "send_name": "📝 Now send your <b>in-game name</b>:",
        "invalid_name": "❌ Name too short!",
        "accepted": "✅ <b>Accepted!</b>\n\n💎 <b>{item}</b> within <b>5 min</b> ⏳",
        "rejected": "❌ Order <b>rejected</b>.",
        "wallet_paid": "✅ <b>{price} SYP deducted from wallet!</b>\n\n💎 Processing...",
        "wallet_insufficient": "❌ <b>Insufficient balance!</b>\n\n💰 Balance: <b>{balance}</b>\n💵 Required: <b>{price}</b>\n\nDeposit via (💳 Deposit).",
        "my_info": "👤 <b>Info:</b>\n\n📛 {name}\n🆔 <code>{rid}</code>\n💰 Balance: <b>{balance} SYP</b>\n📅 {joined}\n🌐 {lang}\n\n🧾 <b>Orders:</b>\n{orders}",
        "no_orders": "No orders yet 😕",
        "wallet_info": "💰 <b>Your Wallet:</b>\n\nCurrent Balance: <b>{balance} SYP</b>",
        "deposit_caption": "💳 <b>Deposit via Sham Cash</b>\n\n📷 Scan the code above to transfer to:\n<code>{account}</code>\n\n💰 Amount: <b>{amount} SYP</b>\n\nAfter transfer, send <b>Transaction ID</b>:",
        "deposit_ask_amount": "💳 <b>Enter amount to deposit in SYP:</b>\n\nEx: 500",
        "deposit_verify": "⏳ Verifying...",
        "deposit_success": "✅ <b>Deposit successful!</b>\n\n💰 Added <b>{amount} SYP</b>.\n💳 New balance: <b>{balance} SYP</b>",
        "deposit_fail": "❌ <b>Verification failed:</b> {reason}",
        "deposit_used": "❌ This transaction ID is already used!",
        "deposit_expired": "❌ This transaction is too old! Must be within 5 minutes.",
        "deposit_invalid_amount": "❌ Please enter a valid amount.",
        "deposit_invalid_tx": "❌ Transaction ID must be digits only.",
        "admin_add_balance_usage": "⚠️ <b>Usage:</b>\n<code>/sendrasid [ID/Username] [Amount]</code>\n\n<b>Examples:</b>\n<code>/sendrasid 6382473367 500</code> (Telegram ID)\n<code>/sendrasid @Yamen 500</code> (Username)\n<code>/sendrasid 12345678 500</code> (Bot ID)",
        "admin_user_not_found": "❌ User not found.",
        "admin_balance_added": "✅ Added <b>{amount} SYP</b> to <b>{name}</b>.\n💰 New balance: <b>{balance} SYP</b>",
        "contest_disabled": "🚫 <b>Contest is disabled</b>",
        "contest_title": "🎁 <b>Contest!</b>\n\n📢 Invite <b>{REQUIRED_JOINS} people</b> to the channel via your link\n\n🔗 <b>Your link:</b>\n<code>{link}</code>\n\n📊 <b>Invites:</b> <b>{count}/{required}</b>\n🎯 Status: {status}",
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
        "contestant_item": "━━━━━━━━━━━━━━━━━━\n👤 <b>{name}</b>\n🆔 <code>{uid}</code>\n🌐 @{username}\n📊 <b>{count}/{required}</b>\n🎯 {status}\n🕒 {time}\n🕐 {last}\n🔗 <code>{link}</code>\n━━━━━━━━━━━━━━━━━━",
        "contestant_no_last": "No invites yet",
        "btn_view_details": "📋 Details",
        "btn_view_user": "👤 User",
        "contestant_full_details": "📋 <b>Contestant Details</b>\n\n👤 <b>{name}</b>\n🆔 <code>{uid}</code>\n🌐 @{username}\n\n📊 <b>{count}/{required}</b>\n🎯 {status}\n🕒 {created}\n🕐 {last}\n🔗 <code>{link}</code>\n\n👥 <b>Invited ({count}):</b>\n{referrals_list}",
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
        "support": "🆘 <b>Support Center</b>\n\n👨‍💻 Contact: {SUPPORT_USERNAME}\n\n📖 <b>How to use:</b>\n1️⃣ Choose game\n2️⃣ Choose package 💎\n3️⃣ Send ID 🆔\n4️⃣ Send name 📝\n5️⃣ Confirm order\n\n⏰ <b>Working: 12 PM - 10 PM</b> 🇸🇦\n\n👇 Send a complaint/suggestion:",
        "btn_complaint": "✉️ Send complaint/suggestion",
    }
}

# ============ قاعدة البيانات SQLite ============
DB_FILE = "/app/data/bot.db"

def db_connect():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db_connect()
    cur = conn.cursor()
    
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
        random_id TEXT, language TEXT DEFAULT 'ar', joined_at TEXT)""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, game TEXT, package TEXT,
        price REAL, game_id TEXT, player_name TEXT, payment_method TEXT,
        status TEXT, created_at TEXT)""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT)""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, full_name TEXT,
        message TEXT, is_read INTEGER DEFAULT 0, created_at TEXT)""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS contest (
        user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
        invite_link TEXT UNIQUE, invite_link_name TEXT,
        joins_count INTEGER DEFAULT 0, status TEXT DEFAULT 'active', created_at TEXT)""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, referred_id INTEGER UNIQUE,
        invite_link TEXT, joined_at TEXT)""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS wallets (
        user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)""")
        
    cur.execute("""CREATE TABLE IF NOT EXISTS deposits (
        tx_id TEXT PRIMARY KEY, user_id INTEGER, amount REAL, created_at TEXT)""")

    cur.execute("INSERT OR IGNORE INTO settings VALUES ('button_order', 'ff,pubg,jawaker,blood')")
    cur.execute("INSERT OR IGNORE INTO settings VALUES ('dev_mode', 'off')")
    cur.execute("INSERT OR IGNORE INTO settings VALUES ('contest_mode', 'on')")
    
    conn.commit()
    cur.close(); conn.close()
    print("✅ قاعدة بيانات SQLite جاهزة (/app/data/bot.db)")

init_db()

# ============ دوال مساعدة ============
def gen_random_id():
    return str(random.randint(10000000, 99999999))

def get_user(uid):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    u = cur.fetchone(); cur.close(); conn.close()
    return u

def ensure_user(message):
    uid = message.from_user.id
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, username, full_name, random_id, language, joined_at) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, message.from_user.username or "", message.from_user.full_name, gen_random_id(), "ar", datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
    cur.close(); conn.close()

def get_lang(uid):
    u = get_user(uid)
    return u["language"] if u and u["language"] else "ar"

def t(uid, key, **kwargs):
    lang = get_lang(uid)
    text = TEXTS.get(lang, TEXTS["ar"]).get(key, "")
    return text.format(**kwargs, CHANNEL_USERNAME=CHANNEL_USERNAME, SUPPORT_USERNAME=SUPPORT_USERNAME, REQUIRED_JOINS=REQUIRED_JOINS) if kwargs else text

def t_lang(lang, key, **kwargs):
    text = TEXTS.get(lang, TEXTS["ar"]).get(key, "")
    return text.format(**kwargs) if kwargs else text

def get_wallet_balance(uid):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT balance FROM wallets WHERE user_id = ?", (uid,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row["balance"] if row else 0.0

def update_wallet_balance(uid, amount):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("INSERT INTO wallets (user_id, balance) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?", (uid, amount, amount))
    conn.commit(); cur.close(); conn.close()

def deduct_wallet_balance(uid, amount):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE wallets SET balance = balance - ? WHERE user_id = ? AND balance >= ?", (amount, uid, amount))
    conn.commit(); cur.close(); conn.close()

# ============ التحقق من شام كاش عبر API SYRIA ============
def verify_sham_cash_tx(tx_id):
    url = f"https://apisyria.com/api/v1?resource=shamcash&action=find_tx&tx={tx_id}&account_address={API_SYRIA_ACCOUNT}"
    headers = {"X-Api-Key": API_SYRIA_KEY, "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        
        if data.get("success") and data.get("data", {}).get("found"):
            tx = data["data"]["transaction"]
            amount = float(tx.get("amount", 0))
            currency = tx.get("currency", "")
            tx_date_str = tx.get("datetime") # مثال: "2025-01-01 10:15:00"
            
            if currency != "SYP":
                return False, f"العملة غير مدعومة ({currency}). يرجى الدفع بالليرة السورية (SYP)."

            # ✅ التحقق من الوقت (صلاحية 6 دقائق كحد أقصى كهامش أمان)
            try:
                tx_time = datetime.strptime(tx_date_str, "%Y-%m-%d %H:%M:%S")
                # شام كاش يرسل الوقت بتوقيت سوريا (UTC+3). نستخدم نفس التوقيت للمقارنة.
                now_time = datetime.now(timezone(timedelta(hours=3))).replace(tzinfo=None)
                
                time_diff = (now_time - tx_time).total_seconds()
                
                if time_diff > 360: # 6 دقائق بالثواني
                    return False, "expired_date" # مفتاح خاص للترجمة
                if time_diff < -60: # إذا كان الوقت بالمستقبل (خطأ بالسيرفر)
                     return False, "تاريخ العملية غير صحيح."
            except Exception as e:
                print(f"⚠️ خطأ في قراءة التاريخ: {e}")
                return False, "تعذر قراءة تاريخ العملية."

            return True, amount
        return False, "رقم العملية غير موجود أو لم يتم العثور عليه."
    except Exception as e:
        return False, f"خطأ في الاتصال بالمنصة: {e}"

def get_button_order():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = 'button_order'")
    row = cur.fetchone(); cur.close(); conn.close()
    return row["value"] if row else "ff,pubg,jawaker,blood"

def set_button_order(value):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("UPDATE settings SET value = ? WHERE key = 'button_order'", (value,))
    conn.commit(); cur.close(); conn.close()

def get_setting(key, default=None):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row["value"] if row else default

def set_setting(key, value):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit(); cur.close(); conn.close()

def is_orders_open():
    if get_setting("dev_mode", "off") == "on": return True
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
    if not game_id.isdigit(): return False, "يجب أن يحتوي على أرقام فقط"
    if game_id.startswith("0"): return False, "لا يبدأ بـ 0"
    if game in ("ff", "ff_membership"):
        if len(game_id) < 5 or len(game_id) > 15: return False, "ID غير صالح (5-15 رقم)"
    elif game == "pubg":
        if len(game_id) < 9 or len(game_id) > 12: return False, "ID غير صالح (9-12 رقم)"
    elif game in ("jawaker", "jawaker_premium"):
        if len(game_id) < 6 or len(game_id) > 12: return False, "ID غير صالح (6-12 رقم)"
    elif game == "bs_global":
        if len(game_id) < 6 or len(game_id) > 15: return False, "ID غير صالح (6-15 رقم)"
    return True, game_id

# ============ دوال المسابقة ============
def create_user_invite_link(uid):
    try:
        link_name = f"ref_{uid}_{int(time.time())}"
        result = bot.create_chat_invite_link(chat_id=CHANNEL_USERNAME, name=link_name, creates_join_request=False)
        return result.invite_link, link_name
    except Exception as e:
        print(f"❌ create_user_invite_link: {e}")
        return None, None

def get_contest_entry(uid):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM contest WHERE user_id = ?", (uid,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row

def register_contest_user(uid, username, full_name):
    invite_link, link_name = create_user_invite_link(uid)
    if not invite_link: return None
    conn = db_connect(); cur = conn.cursor()
    cur.execute("INSERT INTO contest (user_id, username, full_name, invite_link, invite_link_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (uid, username, full_name, invite_link, link_name, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); cur.close(); conn.close()
    return get_contest_entry(uid)

def get_all_contestants():
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM contest ORDER BY joins_count DESC, created_at DESC")
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def get_last_referral_time(referrer_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT joined_at FROM referrals WHERE referrer_id = ? ORDER BY joined_at DESC LIMIT 1", (referrer_id,))
    row = cur.fetchone(); cur.close(); conn.close()
    return row["joined_at"] if row else None

def get_referrals_list(referrer_id):
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT r.referred_id, r.joined_at, u.full_name, u.username FROM referrals r LEFT JOIN users u ON u.user_id = r.referred_id WHERE r.referrer_id = ? ORDER BY r.joined_at ASC", (referrer_id,))
    rows = cur.fetchall(); cur.close(); conn.close()
    return rows

def contest_status_text(lang, status):
    if status == "qualified": return TEXTS[lang]["contest_status_qualified"]
    elif status == "rejected": return TEXTS[lang]["contest_status_rejected"]
    else: return TEXTS[lang]["contest_status_active"]

# ============ لوحات الأزرار ============
def games_row(uid):
    T = TEXTS[get_lang(uid)]
    order = get_button_order().split(",")
    game_map = {"ff": T["btn_ff"], "pubg": T["btn_pubg"], "jawaker": T["btn_jawaker"], "blood": T["btn_blood"]}
    return [game_map[g] for g in order if g in game_map]

def main_keyboard(uid):
    T = TEXTS[get_lang(uid)]; kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    games = games_row(uid)
    if len(games) == 4: kb.row(games[0], games[1]); kb.row(games[2], games[3])
    elif len(games) == 3: kb.row(games[0], games[1]); kb.row(games[2])
    else: kb.row(*games)
    kb.row(T["btn_info"], T["btn_settings"])
    kb.row(T["btn_deposit"], T["btn_wallet"])
    if uid == ADMIN_ID: kb.row(T["btn_support"], T["btn_inbox"]); kb.row(T["btn_contestants"])
    else: kb.row(T["btn_support"])
    return kb

def back_keyboard(uid):
    T = TEXTS[get_lang(uid)]; kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(T["btn_back"])
    games = games_row(uid)
    if len(games) == 4: kb.row(games[0], games[1]); kb.row(games[2], games[3])
    elif len(games) == 3: kb.row(games[0], games[1]); kb.row(games[2])
    else: kb.row(*games)
    kb.row(T["btn_info"], T["btn_settings"])
    kb.row(T["btn_deposit"], T["btn_wallet"])
    if uid == ADMIN_ID: kb.row(T["btn_support"], T["btn_inbox"]); kb.row(T["btn_contestants"])
    else: kb.row(T["btn_support"])
    return kb

# ============ رسائل ============
def send_welcome(chat_id, first_name, uid):
    balance = get_wallet_balance(uid)
    bot.send_message(chat_id, t(uid, "welcome", name=first_name, balance=balance), parse_mode="HTML", reply_markup=main_keyboard(uid))

def show_subscription_message(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_subscribe"), url=CHANNEL_LINK), types.InlineKeyboardButton(t(uid, "btn_check"), callback_data="check_sub"))
    bot.send_message(chat_id, t(uid, "subscribe_required"), parse_mode="HTML", reply_markup=kb)

def show_packages_for_game(chat_id, uid, game_key):
    lang = get_lang(uid); game_data = PACKAGES[game_key]
    kb = types.InlineKeyboardMarkup(row_width=1)
    for key, item in game_data["items"].items():
        kb.add(types.InlineKeyboardButton(text=f"{item[lang]} — {item['price']} ل.س", callback_data=f"pkg|{game_key}|{key}"))
    bot.send_message(chat_id, t(uid, "choose_package", game=game_data["title"][lang]), parse_mode="HTML", reply_markup=kb)
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {})["step"] = 3

def show_ff_types(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=2).add(types.InlineKeyboardButton(t(uid, "btn_ff_diamonds"), callback_data="ff_type|diamonds"), types.InlineKeyboardButton(t(uid, "btn_ff_membership"), callback_data="ff_type|membership"))
    bot.send_message(chat_id, t(uid, "choose_ff_type"), parse_mode="HTML", reply_markup=kb)
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {})["step"] = 2

def show_jw_types(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=2).add(types.InlineKeyboardButton(t(uid, "btn_jw_tokens"), callback_data="jw_type|tokens"), types.InlineKeyboardButton(t(uid, "btn_jw_premium"), callback_data="jw_type|premium"))
    bot.send_message(chat_id, t(uid, "choose_jw_type"), parse_mode="HTML", reply_markup=kb)
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {})["step"] = 2

def show_bs_servers(chat_id, uid):
    kb = types.InlineKeyboardMarkup(row_width=2).add(types.InlineKeyboardButton(t(uid, "btn_bs_global"), callback_data="bs_server|global"), types.InlineKeyboardButton(t(uid, "btn_bs_mena"), callback_data="bs_server|mena"))
    bot.send_message(chat_id, t(uid, "choose_bs_server"), parse_mode="HTML", reply_markup=kb)
    bot.send_message(chat_id, "🔽", reply_markup=back_keyboard(uid))
    USER_DATA.setdefault(uid, {})["step"] = 2

def go_back(message):
    uid = message.from_user.id; data = USER_DATA.get(uid, {}); step = data.get("step", 1)
    if step <= 2:
        bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid)); USER_DATA[uid] = {"step": 1}; return
    if step == 3:
        game = data.get("game", "")
        if game in ("ff", "ff_membership"): USER_DATA[uid] = {"game": "ff", "step": 2}; show_ff_types(message.chat.id, uid)
        elif game == "bs_global": USER_DATA[uid] = {"game": "blood", "step": 2}; show_bs_servers(message.chat.id, uid)
        elif game in ("jawaker", "jawaker_premium"): USER_DATA[uid] = {"game": "jawaker", "step": 2}; show_jw_types(message.chat.id, uid)
        else: bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid)); USER_DATA[uid] = {"step": 1}
        return
    if step == 4:
        game = data.get("game", "ff"); USER_DATA[uid]["step"] = 3; show_packages_for_game(message.chat.id, uid, game); return
    if step == 5:
        game = data.get("game", "ff"); game_title = PACKAGES[game]["title"][get_lang(uid)]; USER_DATA[uid]["step"] = 4
        msg = bot.send_message(message.chat.id, t(uid, "chosen", item=data.get("package_name", ""), price=data.get("price", ""), game=game_title), parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_game_id); return
    if step == 6:
        USER_DATA[uid]["step"] = 5
        msg = bot.send_message(message.chat.id, t(uid, "send_name"), parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_player_name); return
    bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid)); USER_DATA[uid] = {"step": 1}

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]])
def back_button_handler(message):
    try: ensure_user(message); go_back(message)
    except Exception as e: print(f"❌ back: {e}")

# ============ /start والإيداع ============
@bot.message_handler(commands=['start'])
def cmd_start(message):
    ensure_user(message); uid = message.from_user.id
    if is_subscribed(uid): send_welcome(message.chat.id, message.from_user.first_name, uid); USER_DATA[uid] = {"step": 1}
    else: show_subscription_message(message.chat.id, uid)

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def check_subscription(call):
    try:
        uid = call.from_user.id
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, t(uid, "check_success"))
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            send_welcome(call.message.chat.id, call.from_user.first_name, uid); USER_DATA[uid] = {"step": 1}
        else: bot.answer_callback_query(call.id, t(uid, "check_fail"), show_alert=True)
    except Exception as e: print(f"❌ {e}")

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_deposit"], TEXTS["en"]["btn_deposit"]])
def deposit_menu(message):
    uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    msg = bot.send_message(message.chat.id, t(uid, "deposit_ask_amount"), parse_mode="HTML")
    bot.register_next_step_handler(msg, process_deposit_amount)

def process_deposit_amount(message):
    uid = message.from_user.id
    try:
        amount = float(message.text.strip())
        if amount <= 0: raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, t(uid, "deposit_invalid_amount"), reply_markup=main_keyboard(uid))
        return
    
    USER_DATA.setdefault(uid, {})["deposit_amount"] = amount
    
    caption_text = t(uid, "deposit_caption", account=API_SYRIA_ACCOUNT, amount=amount)
    try:
        with open(SHAM_IMAGE_PATH, "rb") as photo:
            msg = bot.send_photo(message.chat.id, photo, caption=caption_text, parse_mode="HTML")
    except FileNotFoundError:
        msg = bot.send_message(message.chat.id, caption_text + "\n\n⚠️ (صورة sham.jpg غير موجودة)", parse_mode="HTML")
        
    bot.register_next_step_handler(msg, process_deposit_tx)

def process_deposit_tx(message):
    uid = message.from_user.id
    tx_id = message.text.strip()
    if not tx_id.isdigit():
        bot.send_message(message.chat.id, t(uid, "deposit_invalid_tx"), reply_markup=main_keyboard(uid))
        return
    
    amount = USER_DATA.get(uid, {}).get("deposit_amount", 0)
    if amount == 0:
        bot.send_message(message.chat.id, "⚠️ حدث خطأ، يرجى المحاولة من جديد.", reply_markup=main_keyboard(uid))
        return
        
    msg = bot.send_message(message.chat.id, t(uid, "deposit_verify"))
    
    # 1. التحقق من التكرار
    conn = db_connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM deposits WHERE tx_id = ?", (tx_id,))
    if cur.fetchone():
        cur.close(); conn.close()
        bot.edit_message_text(t(uid, "deposit_used"), chat_id=message.chat.id, message_id=msg.message_id)
        return
    cur.close(); conn.close()
    
    # 2. التحقق من API (المبلغ + التاريخ)
    success, result = verify_sham_cash_tx(tx_id)
    if success:
        api_amount = float(result)
        if api_amount >= amount:
            update_wallet_balance(uid, amount)
            
            conn = db_connect(); cur = conn.cursor()
            cur.execute("INSERT INTO deposits (tx_id, user_id, amount, created_at) VALUES (?, ?, ?, ?)", (tx_id, uid, amount, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit(); cur.close(); conn.close()
            
            new_balance = get_wallet_balance(uid)
            bot.edit_message_text(t(uid, "deposit_success", amount=amount, balance=new_balance), chat_id=message.chat.id, message_id=msg.message_id, parse_mode="HTML")
            try: bot.send_message(ADMIN_ID, f"💰 إيداع جديد!\nالمستخدم: {message.from_user.full_name}\nالمبلغ: {amount} ل.س\nرقم العملية: {tx_id}")
            except: pass
        else:
            bot.edit_message_text(t(uid, "deposit_fail", reason=f"المبلغ المحول ({api_amount}) أقل من المبلغ المطلوب ({amount})."), chat_id=message.chat.id, message_id=msg.message_id)
    else:
        if result == "expired_date":
            bot.edit_message_text(t(uid, "deposit_expired"), chat_id=message.chat.id, message_id=msg.message_id)
        else:
            bot.edit_message_text(t(uid, "deposit_fail", reason=result), chat_id=message.chat.id, message_id=msg.message_id)

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_wallet"], TEXTS["en"]["btn_wallet"]])
def show_wallet(message):
    uid = message.from_user.id
    balance = get_wallet_balance(uid)
    bot.send_message(message.chat.id, t(uid, "wallet_info", balance=balance), parse_mode="HTML")

# ============ أوامر المطور ============
@bot.message_handler(commands=['sendrasid'])
def admin_send_balance(message):
    if message.from_user.id != ADMIN_ID: return
    
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, t(ADMIN_ID, "admin_add_balance_usage"), parse_mode="HTML")
        return
        
    target = args[1].strip()
    try:
        amount = float(args[2].strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ المبلغ غير صالح.")
        return

    conn = db_connect(); cur = conn.cursor()
    
    query = "SELECT user_id, full_name FROM users WHERE user_id = ? OR random_id = ?"
    params = [target, target]
    
    if target.startswith("@"):
        query += " OR username = ?"
        params.append(target[1:])
    
    cur.execute(query, params)
    user = cur.fetchone()
    
    if not user:
        cur.close(); conn.close()
        bot.send_message(message.chat.id, t(ADMIN_ID, "admin_user_not_found"))
        return
        
    uid = user["user_id"]
    name = user["full_name"]
    cur.close(); conn.close()
    
    update_wallet_balance(uid, amount)
    new_balance = get_wallet_balance(uid)
    
    bot.send_message(message.chat.id, t(ADMIN_ID, "admin_balance_added", amount=amount, name=name, balance=new_balance), parse_mode="HTML")
    try: bot.send_message(uid, f"🎁 <b>تم إضافة {amount} ل.س إلى محفظتك من قِبَل الإدارة!</b>\n💰 رصيدك الجديد: <b>{new_balance} ل.س</b>", parse_mode="HTML")
    except: pass

# ============ الألعاب والشراء ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_ff"], TEXTS["en"]["btn_ff"]])
def show_ff(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    if not is_orders_open(): bot.send_message(message.chat.id, t(uid, "orders_closed_dev") if get_setting("dev_mode", "off") == "on" else t(uid, "orders_closed"), parse_mode="HTML"); return
    USER_DATA[uid] = {"game": "ff", "step": 2}; show_ff_types(message.chat.id, uid)

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_blood"], TEXTS["en"]["btn_blood"]])
def show_blood(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    if not is_orders_open(): bot.send_message(message.chat.id, t(uid, "orders_closed_dev") if get_setting("dev_mode", "off") == "on" else t(uid, "orders_closed"), parse_mode="HTML"); return
    USER_DATA[uid] = {"game": "blood", "step": 2}; show_bs_servers(message.chat.id, uid)

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_jawaker"], TEXTS["en"]["btn_jawaker"]])
def show_jawaker(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    if not is_orders_open(): bot.send_message(message.chat.id, t(uid, "orders_closed_dev") if get_setting("dev_mode", "off") == "on" else t(uid, "orders_closed"), parse_mode="HTML"); return
    USER_DATA[uid] = {"game": "jawaker", "step": 2}; show_jw_types(message.chat.id, uid)

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_pubg"], TEXTS["en"]["btn_pubg"]])
def show_pubg(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    if not is_orders_open(): bot.send_message(message.chat.id, t(uid, "orders_closed_dev") if get_setting("dev_mode", "off") == "on" else t(uid, "orders_closed"), parse_mode="HTML"); return
    USER_DATA[uid] = {"game": "pubg", "step": 3}; show_packages_for_game(message.chat.id, uid, "pubg")

@bot.callback_query_handler(func=lambda c: c.data.startswith("ff_type|"))
def choose_ff_type(call):
    ff_type = call.data.split("|")[1]; uid = call.from_user.id; bot.answer_callback_query(call.id, "✅")
    USER_DATA[uid] = {"game": "ff" if ff_type == "diamonds" else "ff_membership", "step": 3}
    show_packages_for_game(call.message.chat.id, uid, USER_DATA[uid]["game"])

@bot.callback_query_handler(func=lambda c: c.data.startswith("jw_type|"))
def choose_jw_type(call):
    jw_type = call.data.split("|")[1]; uid = call.from_user.id; bot.answer_callback_query(call.id, "✅")
    USER_DATA[uid] = {"game": "jawaker" if jw_type == "tokens" else "jawaker_premium", "step": 3}
    show_packages_for_game(call.message.chat.id, uid, USER_DATA[uid]["game"])

@bot.callback_query_handler(func=lambda c: c.data.startswith("bs_server|"))
def choose_bs_server(call):
    server = call.data.split("|")[1]; uid = call.from_user.id; bot.answer_callback_query(call.id, "✅")
    if server == "global": USER_DATA[uid] = {"game": "bs_global", "step": 3}; show_packages_for_game(call.message.chat.id, uid, "bs_global")
    else: bot.send_message(call.message.chat.id, t(uid, "bs_mena_soon"), parse_mode="HTML", reply_markup=main_keyboard(uid)); USER_DATA[uid] = {"step": 1}

@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg|"))
def choose_package(call):
    _, game, key = call.data.split("|"); uid = call.from_user.id; lang = get_lang(uid); item = PACKAGES[game]["items"][key]
    
    balance = get_wallet_balance(uid)
    if balance < item["price"]:
        bot.answer_callback_query(call.id, "❌ رصيدك غير كافي لهذا العرض!", show_alert=True)
        bot.send_message(call.message.chat.id, t(uid, "wallet_insufficient", balance=balance, price=item["price"]), parse_mode="HTML")
        return
        
    bot.answer_callback_query(call.id, "✅")
    USER_DATA[uid] = {"game": game, "package_key": key, "package_name": item[lang], "price": item["price"], "step": 4}
    msg = bot.send_message(call.message.chat.id, t(uid, "chosen", item=item[lang], price=item["price"], game=PACKAGES[game]["title"][lang]), parse_mode="HTML", reply_markup=back_keyboard(uid))
    bot.register_next_step_handler(msg, get_game_id)

def get_game_id(message):
    uid = message.from_user.id
    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]: go_back(message); return
    data = USER_DATA.get(uid)
    if not data: bot.send_message(message.chat.id, "⚠️ /start", reply_markup=main_keyboard(uid)); return
    game = data.get("game", "ff"); game_id = message.text.strip() if message.text else ""
    valid, result = validate_game_id(game_id, game)
    if not valid:
        key = "invalid_id_ff" if game in ("ff", "ff_membership") else ("invalid_id_pubg" if game == "pubg" else ("invalid_id_jawaker" if game in ("jawaker", "jawaker_premium") else "invalid_id_bs"))
        msg = bot.send_message(message.chat.id, t(uid, key, reason=result), parse_mode="HTML", reply_markup=back_keyboard(uid))
        bot.register_next_step_handler(msg, get_game_id); return
    USER_DATA[uid]["game_id"] = result; USER_DATA[uid]["step"] = 5
    msg = bot.send_message(message.chat.id, t(uid, "send_name"), parse_mode="HTML", reply_markup=back_keyboard(uid))
    bot.register_next_step_handler(msg, get_player_name)

def get_player_name(message):
    uid = message.from_user.id
    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]: go_back(message); return
    data = USER_DATA.get(uid)
    if not data: bot.send_message(message.chat.id, "⚠️ /start", reply_markup=main_keyboard(uid)); return
    player_name = message.text.strip() if message.text else ""
    if len(player_name) < 2:
        msg = bot.send_message(message.chat.id, t(uid, "invalid_name"), reply_markup=back_keyboard(uid)); bot.register_next_step_handler(msg, get_player_name); return
        
    price = data["price"]
    balance = get_wallet_balance(uid)
    
    if balance < price:
        bot.send_message(message.chat.id, t(uid, "wallet_insufficient", balance=balance, price=price), parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
        
    deduct_wallet_balance(uid, price)
    
    conn = db_connect(); cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, game, package, price, game_id, player_name, payment_method, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (uid, data["game"], data["package_name"], price, data["game_id"], player_name, "wallet", "pending", datetime.now().strftime("%Y-%m-%d %H:%M")))
    order_id = cur.lastrowid; conn.commit(); cur.close(); conn.close()
    
    bot.send_message(message.chat.id, t(uid, "wallet_paid", price=price), parse_mode="HTML", reply_markup=main_keyboard(uid))
    
    admin_text = f"🔔 <b>طلب جديد (محفظة)!</b>\n\n🔖 #{order_id}\n👤 {message.from_user.full_name}\n🆔 <code>{message.from_user.id}</code>\n\n🎮 {data['game'].upper()}\n💎 {data['package_name']}\n💰 {price} ل.س\n🎮 ID: <code>{data['game_id']}</code>\n📝 {player_name}\n💳 محفظة البوت"
    kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ قبول", callback_data=f"accept|{order_id}"), types.InlineKeyboardButton("❌ رفض", callback_data=f"reject|{order_id}"))
    bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML", reply_markup=kb)
    
    USER_DATA.pop(uid, None)

@bot.callback_query_handler(func=lambda c: c.data.startswith("accept|") or c.data.startswith("reject|"))
def handle_decision(call):
    action, oid = call.data.split("|"); oid = int(oid)
    conn = db_connect(); cur = conn.cursor(); cur.execute("SELECT user_id, package, price, payment_method FROM orders WHERE order_id = ?", (oid,)); row = cur.fetchone()
    if not row: bot.answer_callback_query(call.id, "⚠️"); cur.close(); conn.close(); return
    user_id, package, price, method = row["user_id"], row["package"], row["price"], row["payment_method"]
    
    if action == "accept":
        cur.execute("UPDATE orders SET status = 'accepted' WHERE order_id = ?", (oid,)); conn.commit()
        bot.send_message(user_id, t(user_id, "accepted", item=package), parse_mode="HTML"); bot.answer_callback_query(call.id, "✅")
    else:
        cur.execute("UPDATE orders SET status = 'rejected' WHERE order_id = ?", (oid,)); conn.commit()
        if method == "wallet":
            update_wallet_balance(user_id, price)
            bot.send_message(user_id, f"❌ تم رفض طلبك، وتم إرجاع {price} ل.س إلى محفظتك.")
        else:
            bot.send_message(user_id, t(user_id, "rejected"), parse_mode="HTML")
        bot.answer_callback_query(call.id, "❌")
    cur.close(); conn.close()
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except: pass

# ============ معلوماتي ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_info"], TEXTS["en"]["btn_info"]])
def my_info(message):
    ensure_user(message); uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    u = get_user(uid); lang = get_lang(uid); balance = get_wallet_balance(uid)
    conn = db_connect(); cur = conn.cursor(); cur.execute("SELECT order_id, package, price, status, created_at FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 5", (uid,)); orders = cur.fetchall(); cur.close(); conn.close()
    status_map = {"pending": "⏳", "accepted": "✅", "rejected": "❌", "expired": "⌛"}
    orders_text = "".join([f"\n🔖 #{o['order_id']} — {o['package']} ({o['price']})\n   {status_map.get(o['status'], o['status'])} | {o['created_at']}\n" for o in orders]) if orders else t(uid, "no_orders")
    bot.send_message(message.chat.id, t(uid, "my_info", name=message.from_user.full_name, rid=u["random_id"] if u else "-", balance=balance, joined=u["joined_at"] if u else "-", lang="العربية 🇸🇦" if lang == "ar" else "English 🇬🇧", orders=orders_text), parse_mode="HTML")
    kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_contest"), callback_data="contest_show"))
    bot.send_message(message.chat.id, "🎁 <b>هل تريد المشاركة في المسابقة؟</b>\n👇", parse_mode="HTML", reply_markup=kb)

# ============ المسابقة ============
@bot.callback_query_handler(func=lambda c: c.data == "contest_show")
def contest_show(call):
    uid = call.from_user.id; bot.answer_callback_query(call.id)
    if not is_contest_open(): bot.send_message(uid, t(uid, "contest_disabled"), parse_mode="HTML"); return
    entry = get_contest_entry(uid); lang = get_lang(uid)
    if entry:
        status = contest_status_text(lang, entry["status"])
        text = t(uid, "contest_title", link=entry["invite_link"], count=entry["joins_count"], required=REQUIRED_JOINS, status=status)
        kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_copy_link"), url=entry["invite_link"]))
        bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
    else:
        msg = bot.send_message(uid, t(uid, "contest_loading"))
        try: bot.delete_message(uid, msg.message_id)
        except: pass
        try:
            me = bot.get_me(); member = bot.get_chat_member(CHANNEL_USERNAME, me.id)
            if member.status not in ("administrator", "creator"): bot.send_message(uid, "⚠️ البوت غير مضاف كمشرف!\n👨‍💻 " + SUPPORT_USERNAME); return
        except Exception as e: print(f"❌ {e}")
        new_entry = register_contest_user(uid, call.from_user.username or "", call.from_user.full_name)
        if not new_entry: bot.send_message(uid, "⚠️ حدث خطأ في إنشاء الرابط."); return
        text = t(uid, "contest_created", link=new_entry["invite_link"], count=0, required=REQUIRED_JOINS)
        kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_copy_link"), url=new_entry["invite_link"]))
        bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)

# ============ قائمة المتسابقين ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_contestants"], TEXTS["en"]["btn_contestants"]] and m.from_user.id == ADMIN_ID)
def show_contestants(message):
    uid = message.from_user.id; contestants = get_all_contestants()
    if not contestants: bot.send_message(uid, t(uid, "contestants_empty")); return
    total = len(contestants); qualified = sum(1 for c in contestants if c["status"] == "qualified"); active = sum(1 for c in contestants if c["status"] == "active")
    bot.send_message(uid, t(uid, "contestants_title", total=total, qualified=qualified, active=active), parse_mode="HTML")
    for c in contestants:
        status_txt = contest_status_text(get_lang(uid), c["status"]); last_ref = get_last_referral_time(c["user_id"]); last_txt = last_ref if last_ref else t(uid, "contestant_no_last")
        text = t(uid, "contestant_item", name=c["full_name"] or "-", uid=c["user_id"], username=c["username"] or "لا يوجد", count=c["joins_count"], required=REQUIRED_JOINS, status=status_txt, time=c["created_at"] or "-", last=last_txt, link=c["invite_link"] or "-")
        kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_view_details"), callback_data=f"cdetails|{c['user_id']}"), types.InlineKeyboardButton(t(uid, "btn_view_user"), url=f"tg://user?id={c['user_id']}"))
        bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("cdetails|"))
def contestant_details(call):
    uid_admin = call.from_user.id
    if uid_admin != ADMIN_ID: bot.answer_callback_query(call.id, "🚫", show_alert=True); return
    target_uid = int(call.data.split("|")[1]); bot.answer_callback_query(call.id)
    conn = db_connect(); cur = conn.cursor(); cur.execute("SELECT * FROM contest WHERE user_id = ?", (target_uid,)); entry = cur.fetchone(); cur.close(); conn.close()
    if not entry: bot.send_message(uid_admin, "⚠️ غير موجود"); return
    last_ref = get_last_referral_time(target_uid); last_txt = last_ref if last_ref else "لا يوجد بعد"; refs = get_referrals_list(target_uid)
    refs_text = ""
    for i, r in enumerate(refs, 1): refs_text += f"   {i}. 👤 {r['full_name'] or 'مستخدم'} — <code>{r['referred_id']}</code> — {r['joined_at']}\n"
    if not refs: refs_text = "   لم يدعُ أحدًا بعد"
    status_txt = contest_status_text(get_lang(uid_admin), entry["status"])
    text = t(uid_admin, "contestant_full_details", name=entry["full_name"] or "-", uid=entry["user_id"], username=entry["username"] or "لا يوجد", count=entry["joins_count"], required=REQUIRED_JOINS, status=status_txt, created=entry["created_at"] or "-", last=last_txt, link=entry["invite_link"] or "-", referrals_list=refs_text)
    kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton("👤 فتح حساب", url=f"tg://user?id={entry['user_id']}"))
    bot.send_message(uid_admin, text, parse_mode="HTML", reply_markup=kb)

# ============ الدعم ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_support"], TEXTS["en"]["btn_support"]])
def support(message):
    uid = message.from_user.id
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_complaint"), callback_data="send_complaint"))
    bot.send_message(message.chat.id, t(uid, "support"), parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "send_complaint")
def ask_complaint(call):
    uid = call.from_user.id; bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, t(uid, "ask_message"), parse_mode="HTML", reply_markup=back_keyboard(uid))
    bot.register_next_step_handler(msg, receive_complaint)

def receive_complaint(message):
    uid = message.from_user.id
    if message.text in [TEXTS["ar"]["btn_back"], TEXTS["en"]["btn_back"]]: bot.send_message(message.chat.id, t(uid, "back_done"), reply_markup=main_keyboard(uid)); return
    text = message.text.strip() if message.text else ""
    if len(text) < 5:
        msg = bot.send_message(message.chat.id, t(uid, "message_too_short"), reply_markup=back_keyboard(uid)); bot.register_next_step_handler(msg, receive_complaint); return
    conn = db_connect(); cur = conn.cursor()
    cur.execute("INSERT INTO messages (user_id, username, full_name, message, created_at) VALUES (?, ?, ?, ?, ?)", (uid, message.from_user.username or "", message.from_user.full_name, text, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); cur.close(); conn.close()
    bot.send_message(message.chat.id, t(uid, "message_sent"), parse_mode="HTML", reply_markup=main_keyboard(uid))
    bot.send_message(ADMIN_ID, f"📩 <b>رسالة جديدة!</b>\n\n👤 {message.from_user.full_name}\n💬 {text}", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_inbox"], TEXTS["en"]["btn_inbox"]] and m.from_user.id == ADMIN_ID)
def show_inbox(message):
    uid = message.from_user.id; conn = db_connect(); cur = conn.cursor(); cur.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 10"); msgs = cur.fetchall(); cur.close(); conn.close()
    if not msgs: bot.send_message(message.chat.id, t(uid, "inbox_empty")); return
    bot.send_message(message.chat.id, t(uid, "inbox_title", count=len(msgs)), parse_mode="HTML")
    for m in msgs:
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👤 الرد", url=f"tg://user?id={m['user_id']}"))
        bot.send_message(message.chat.id, t(uid, "inbox_item", n=m["id"], name=m["full_name"], uid=m["user_id"], time=m["created_at"], msg=m["message"]), parse_mode="HTML", reply_markup=kb)

# ============ الإعدادات ============
@bot.message_handler(func=lambda m: m.text in [TEXTS["ar"]["btn_settings"], TEXTS["en"]["btn_settings"]])
def settings_menu(message):
    uid = message.from_user.id; ensure_user(message)
    if not is_subscribed(uid): show_subscription_message(message.chat.id, uid); return
    is_admin = (uid == ADMIN_ID); kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_change_lang"), callback_data="cfg_lang"))
    if is_admin: kb.add(types.InlineKeyboardButton(t(uid, "btn_change_order"), callback_data="cfg_order"), types.InlineKeyboardButton(t(uid, "btn_dev_mode"), callback_data="cfg_dev"), types.InlineKeyboardButton(t(uid, "btn_contest_toggle"), callback_data="cfg_contest"))
    kb.add(types.InlineKeyboardButton(t(uid, "btn_reset_data"), callback_data="cfg_reset"))
    bot.send_message(message.chat.id, t(uid, "settings_admin") if is_admin else t(uid, "settings_user"), parse_mode="HTML", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "cfg_lang")
def cfg_lang(call):
    kb = types.InlineKeyboardMarkup(row_width=2).add(types.InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang|ar"), types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang|en"))
    bot.edit_message_text(t(call.from_user.id, "lang_pick"), call.message.chat.id, call.message.message_id, reply_markup=kb); bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "cfg_order")
def cfg_order(call):
    uid = call.from_user.id
    if uid != ADMIN_ID: bot.answer_callback_query(call.id, "🚫", show_alert=True); return
    kb = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(t(uid, "btn_order_1"), callback_data="set_order|ff,pubg,jawaker,blood"), types.InlineKeyboardButton(t(uid, "btn_order_2"), callback_data="set_order|blood,ff,pubg,jawaker"), types.InlineKeyboardButton(t(uid, "btn_order_3"), callback_data="set_order|jawaker,blood,ff,pubg"))
    bot.edit_message_text(t(uid, "order_current", order=get_button_order()), call.message.chat.id, call.message.message_id, reply_markup=kb); bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "cfg_dev")
def cfg_dev(call):
    uid = call.from_user.id
    if uid != ADMIN_ID: bot.answer_callback_query(call.id, "🚫", show_alert=True); return
    cur = get_setting("dev_mode", "off"); text = t(uid, "dev_mode_current_on") if cur == "on" else t(uid, "dev_mode_current_off"); btn = t(uid, "btn_dev_off") if cur == "on" else t(uid, "btn_dev_on"); cb = "dev|off" if cur == "on" else "dev|on"
    kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(btn, callback_data=cb)); bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=kb); bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "cfg_contest")
def cfg_contest(call):
    uid = call.from_user.id
    if uid != ADMIN_ID: bot.answer_callback_query(call.id, "🚫", show_alert=True); return
    cur = get_setting("contest_mode", "on"); text = t(uid, "contest_toggle_current_on") if cur == "on" else t(uid, "contest_toggle_current_off"); btn = t(uid, "btn_contest_toggle_off") if cur == "on" else t(uid, "btn_contest_toggle_on"); cb = "contest|off" if cur == "on" else "contest|on"
    kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(btn, callback_data=cb)); bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=kb); bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("contest|"))
def contest_toggle(call):
    uid = call.from_user.id
    if uid != ADMIN_ID: bot.answer_callback_query(call.id, "🚫", show_alert=True); return
    act = call.data.split("|")[1]
    if act == "on": set_setting("contest_mode", "on"); bot.answer_callback_query(call.id, t(uid, "contest_enabled_msg"), show_alert=True)
    else: set_setting("contest_mode", "off"); bot.answer_callback_query(call.id, t(uid, "contest_disabled_msg"), show_alert=True)
    cfg_contest(call)

@bot.callback_query_handler(func=lambda c: c.data.startswith("dev|"))
def dev_toggle(call):
    uid = call.from_user.id
    if uid != ADMIN_ID: bot.answer_callback_query(call.id, "🚫", show_alert=True); return
    act = call.data.split("|")[1]
    if act == "on": set_setting("dev_mode", "on"); bot.answer_callback_query(call.id, t(uid, "dev_mode_enabled"), show_alert=True)
    else: set_setting("dev_mode", "off"); bot.answer_callback_query(call.id, t(uid, "dev_mode_disabled"), show_alert=True)
    cfg_dev(call)

@bot.callback_query_handler(func=lambda c: c.data == "cfg_reset")
def cfg_reset(call):
    kb = types.InlineKeyboardMarkup(row_width=2).add(types.InlineKeyboardButton(t(call.from_user.id, "btn_yes"), callback_data="do_reset"), types.InlineKeyboardButton(t(call.from_user.id, "btn_no"), callback_data="cancel_reset"))
    bot.edit_message_text(t(call.from_user.id, "reset_confirm"), call.message.chat.id, call.message.message_id, reply_markup=kb); bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_lang|"))
def set_lang(call):
    uid = call.from_user.id; new_lang = call.data.split("|")[1]
    conn = db_connect(); cur = conn.cursor(); cur.execute("UPDATE users SET language = ? WHERE user_id = ?", (new_lang, uid)); conn.commit(); cur.close(); conn.close()
    bot.answer_callback_query(call.id, t(uid, "lang_changed"))
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, t(uid, "lang_changed"), reply_markup=main_keyboard(uid))

@bot.callback_query_handler(func=lambda c: c.data.startswith("set_order|"))
def set_order(call):
    uid = call.from_user.id
    if uid != ADMIN_ID: bot.answer_callback_query(call.id, "🚫", show_alert=True); return
    set_button_order(call.data.split("|")[1]); bot.answer_callback_query(call.id, t(uid, "order_changed"))
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, t(uid, "order_changed"), reply_markup=main_keyboard(uid))

@bot.callback_query_handler(func=lambda c: c.data == "do_reset")
def do_reset(call):
    uid = call.from_user.id; conn = db_connect(); cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE user_id = ?", (uid,)); cur.execute("DELETE FROM users WHERE user_id = ?", (uid,)); conn.commit(); cur.close(); conn.close()
    bot.answer_callback_query(call.id, "🗑️")
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id, t(uid, "reset_done")); USER_DATA.pop(uid, None); cmd_start(call.message)

@bot.callback_query_handler(func=lambda c: c.data == "cancel_reset")
def cancel_reset(call):
    bot.answer_callback_query(call.id, "✅")
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass

@bot.message_handler(func=lambda m: True)
def unknown_message(message):
    try:
        uid = message.from_user.id; ensure_user(message)
        if is_subscribed(uid): bot.send_message(message.chat.id, t(uid, "unknown_msg"), reply_markup=main_keyboard(uid))
        else: show_subscription_message(message.chat.id, uid)
    except Exception as e: print(f"❌ {e}")

# ============ تشغيل ============
print("🤖 البوت يعمل الآن على SQLite (نظام المحفظة فقط)...")
bot.infinity_polling(
    allowed_updates=["message", "edited_message", "callback_query", "inline_query", "chosen_inline_result", "channel_post", "edited_channel_post", "chat_member", "my_chat_member", "chat_join_request"],
    skip_pending=True, timeout=30, long_polling_timeout=30
)
