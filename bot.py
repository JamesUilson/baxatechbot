import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import config

# Bot va dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# JSON faylni yuklash
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 🔹 Asosiy menyu
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Kompaniya haqida"), KeyboardButton(text="🖼 Portfolio")],
        [KeyboardButton(text="📞 Operator bilan bog‘lanish"), KeyboardButton(text="🛠 Xizmatlar")],
        [KeyboardButton(text="⁉️ Savol yoki shikoyat qoldirish")]
    ],
    resize_keyboard=True
)

# 🔹 Xizmatlar menyusi
services_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💻 Dasturlash xizmatlari"), KeyboardButton(text="🎨 Dizayn xizmatlari")],
        [KeyboardButton(text="🔐 Pentesting & Cyber Security")],
        [KeyboardButton(text="🔙 Orqaga")]
    ],
    resize_keyboard=True
)

# 🔹 Kanalga obuna bo‘lish uchun inline tugmalar
def check_channel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Kanalga obuna bo‘lish", url=f"https://t.me/{config.REQUIRED_CHANNEL}")],
            [InlineKeyboardButton(text="🔄 Tekshirish", callback_data="check_channel")]
        ]
    )

# 🔹 Kanal obunasini tekshirish funksiyasi
async def check_user_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(chat_id=f"@{config.REQUIRED_CHANNEL}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print("Subscription check error:", e)
        return False

# 🔹 Savol uchun state
class ComplaintState(StatesGroup):
    waiting_for_text = State()

# 🔹 Start komandasi
@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    subscribed = await check_user_subscription(message.from_user.id)
    if not subscribed:
        await message.answer(
            "❌ Botdan foydalanish uchun avval kanalga obuna bo‘ling.",
            reply_markup=check_channel_keyboard()
        )
        return

    await message.answer(
        "Assalomu alaykum 👋\n"
        "Siz *BaxaTech Professional Computer Services* support botidasiz.\n"
        "Qaysi yo‘nalishda yordam kerak?",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# 🔹 Callback tugma tekshiruvi
@dp.callback_query(lambda c: c.data == "check_channel")
async def check_channel_callback(callback_query: types.CallbackQuery):
    try:
        subscribed = await check_user_subscription(callback_query.from_user.id)
        if subscribed:
            await bot.send_message(
                callback_query.from_user.id,
                "✅ Siz kanalga obuna bo‘lgansiz! Botdan foydalanishingiz mumkin.",
                reply_markup=main_menu
            )
            await callback_query.message.delete()
        else:
            await callback_query.answer("❌ Siz hali kanalga obuna bo‘lmadingiz.", show_alert=True)
    except Exception as e:
        print("Callback error:", e)
        await callback_query.answer("❌ Xatolik yuz berdi, qayta urinib ko‘ring.", show_alert=True)

# 🔹 Kompaniya haqida
async def about(message: types.Message):
    text = (
        "🌟 *BaxaTech Professional Computer Services*\n\n"
        "📅 Biz 2023-yilda BDesign nomi bilan xizmat ko‘rsatishni boshlaganmiz.\n"
        "2025-yilda esa BaxaTech nomi bilan qayta tashkil etildik va faqat dizayn emas, \n"
        "dasturchilik va kiberxavfsizlik (hackerlik) sohalarini ham integratsiya qildik.\n\n"
        "🎯 *Missiyamiz:* mijozlarimizning biznesini raqamli texnologiyalar orqali rivojlantirish.\n\n"
        "👥 *Jamoamiz:* Asoschi Bahodirov Baxtiyorjon Baxromjon o‘g‘li boshchiligida kuchli va malakali mutaxassislar jamoasi.\n"
        "Kompaniya shaxs nomiga umumiylashgan bo‘lsa-da, kuchli jamoani tashkil etadi.\n\n"
        "🛠 *Loyihalar:* 100+ muvaffaqiyatli loyiha, jumladan web, mobil ilovalar, dizayn ishlari va kiberxavfsizlik loyihalari.\n\n"
        "🌐 Sayt: {data['contacts']['website']}\n"
        "📧 Email: {data['contacts']['email']}\n"
        "☎️ Telefon: {data['contacts']['phone']}"
    )
    await message.answer(text, reply_markup=main_menu, parse_mode="Markdown")


# 🔹 Portfolio
async def portfolio(message: types.Message):
    await message.answer(f"Bizning portfolio saytimiz 👇\n{config.PORTFOLIO_URL}", reply_markup=main_menu)

# 🔹 Operator bilan bog‘lanish
async def operator(message: types.Message):
    contacts = data["contacts"]
    text = (f"☎️ Telefon: {contacts['phone']}\n"
            f"💬 Telegram: {contacts['telegram']}\n"
            f"📧 Email: {contacts['email']}")
    await message.answer(text, reply_markup=main_menu)

# 🔹 Xizmatlar
async def services(message: types.Message):
    await message.answer("Biz quyidagi xizmatlarni taklif qilamiz:", reply_markup=services_menu)

# 🔹 Har bir xizmat
async def service_detail(message: types.Message):
    if message.text == "💻 Dasturlash xizmatlari":
        await message.answer(data["services"]["programming"], reply_markup=services_menu)
    elif message.text == "🎨 Dizayn xizmatlari":
        await message.answer(data["services"]["design"], reply_markup=services_menu)
    elif message.text == "🔐 Pentesting & Cyber Security":
        await message.answer(data["services"]["pentest"], reply_markup=services_menu)

# 🔹 Savol tugmasi bosilganda
async def complaint(message: types.Message, state: FSMContext):
    await message.answer(
        "Savolingiz yoki shikoyatingizni yozib yuboring. Biz uni adminlarga jo‘natamiz.",
        reply_markup=main_menu
    )
    await state.set_state(ComplaintState.waiting_for_text)

# 🔹 Foydalanuvchi Savol yozganda
@dp.message(ComplaintState.waiting_for_text)
async def handle_complaint(message: types.Message, state: FSMContext):
    admin_id = int(config.ADMIN_ID)  # Telegram ID
    user_name = message.from_user.username or message.from_user.full_name
    try:
        await bot.send_message(
            chat_id=admin_id,
            text=f"📩 Yangi Savol:\n\n{message.text}\n\n👤 {user_name}"
        )
        # Foydalanuvchiga javob
        await message.answer("✅ Rahmat! Savolingiz/shikoyatingiz qabul qilindi. Tez orada javob olasiz", reply_markup=main_menu)
    except Exception as e:
        print("Savol yuborishda xatolik:", e)
        await message.answer("❌ Savol yuborishda xatolik yuz berdi.", reply_markup=main_menu)
    finally:
        await state.clear()

# 🔹 Barcha matnli xabarlarni ushlash va yo‘naltirish (FSM bo‘lmaganlar uchun)
@dp.message(lambda m: True)
async def handle_all_messages(message: types.Message, state: FSMContext):
    if await state.get_state() is not None:
        return  # agar state-da bo‘lsa, bu handler ishlamasin

    subscribed = await check_user_subscription(message.from_user.id)
    if not subscribed:
        await message.answer(
            "❌ Botdan foydalanish uchun avval kanalga obuna bo‘ling.",
            reply_markup=check_channel_keyboard()
        )
        return

    if message.text == "ℹ️ Kompaniya haqida":
        await about(message)
    elif message.text == "🖼 Portfolio":
        await portfolio(message)
    elif message.text == "📞 Operator bilan bog‘lanish":
        await operator(message)
    elif message.text == "🛠 Xizmatlar":
        await services(message)
    elif message.text == "⁉️ Savol yoki shikoyat qoldirish":
        await complaint(message, state)
    elif message.text in ["💻 Dasturlash xizmatlari", "🎨 Dizayn xizmatlari", "🔐 Pentesting & Cyber Security"]:
        await service_detail(message)
    elif message.text == "🔙 Orqaga":
        await start(message)

# 🔹 Botni ishga tushirish
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
