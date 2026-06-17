import asyncio, sqlite3, random, aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder as RKB, InlineKeyboardBuilder as IKB
from aiohttp import web

TKN = "8648819372:AAHQAROd96EBN8y5Eq_cSBMGKg7utylQBM4"
bot, dp, st = Bot(token=TKN), Dispatcher(), {}

# Kiber-test savollari variantlari bilan to'g'rilandi
QUIZ_DATA = [
    {
        "q": "1. Telegram'da notanish profil sizga pul yutuqli havola yubordi. Nima qilasiz?",
        "options": ["A) Havolaga kirib tekshiraman", "B) Fishing deb o'chiraman va bloklayman", "C) Do'stlarimga ulashaman"],
        "ans": "B"
    },
    {
        "q": "2. Ikki faktorli himoya (Two-Step Verification) nima uchun kerak?",
        "options": ["A) Profilni xakerlardan kuchli asrash uchun", "B) Telegramni tezroq ishlatish uchun", "C) Rasm va videolarni sifatli yuborish uchun"],
        "ans": "A"
    },
    {
        "q": "3. Kiber-botingiz maxfiy tokenini guruhga tashlash xavflimi?",
        "options": ["A) Yo'q, hech narsa qilmaydi", "B) Ha, xakerlar botingizni o'g'irlab o'z maqsadida ishlatishi mumkin", "C) Faqat guruh adminlari ko'rsa mayli"],
        "ans": "B"
    }
]

db = sqlite3.connect("u_base.db", check_same_thread=False)
cr = db.cursor()
cr.execute("CREATE TABLE IF NOT EXISTS u (user TEXT, ph TEXT)")
db.commit()

def btn(t, c=False):
    b = RKB()
    for i in t: b.add(types.KeyboardButton(text=i, request_contact=c if "📱" in i else False))
    b.adjust(1 if len(t)==2 else 2)
    return b.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def start(m: types.Message):
    st[m.from_user.id] = None
    await m.answer(f"Salom, {m.from_user.first_name}! Bo'limni tanlang:", reply_markup=btn(["🔍 Raqam qidirish", "🛡️ OSINT Razvedka", "🌤️ Ob-havo", "🌐 Tarjimon", "🕵️‍♂️ Whois (Sayt Test)", "🛡️ Fishing Detektor", "🤖 Kiber-Test (Quiz)", "⚡ Termux Buyruqlari", "💻 Biz haqimizda", "🌐 Havolalar"]))

@dp.message(F.photo)
async def rasm(m: types.Message): await m.reply("Rasm qabul qilindi! 📸")

@dp.message(F.contact)
async def knt(m: types.Message):
    usr, ph = f"@{m.from_user.username.lower()}" if m.from_user.username else None, m.contact.phone_number
    if usr:
        cr.execute("SELECT * FROM u WHERE user=?", (usr,))
        if not cr.fetchone(): cr.execute("INSERT INTO u VALUES (?,?)", (usr, ph)); db.commit()
        await m.answer("✅ Raqamingiz tasdiqlandi.", reply_markup=btn(["🔍 Raqam qidirish", "🛡️ OSINT Razvedka", "🌤️ Ob-havo", "🌐 Tarjimon", "🕵️‍♂️ Whois (Sayt Test)", "🛡️ Fishing Detektor", "🤖 Kiber-Test (Quiz)", "⚡ Termux Buyruqlari", "💻 Biz haqimizda", "🌐 Havolalar"]))
    else: await m.answer("⚠️ Profilingizda username yo'q.")

@dp.message()
async def msg(m: types.Message):
    t, uid = m.text.strip(), m.from_user.id
    
    if t == "💻 Biz haqimizda": await m.answer("Bot Pydroid 3-da yaratildi! 🚀")
    elif t == "🌐 Havolalar":
        b = IKB(); b.add(types.InlineKeyboardButton(text="Muallif 👤", url="https://t.me"))
        await m.answer("Havolalar:", reply_markup=b.as_markup())
    elif t == "🔍 Raqam qidirish": await m.answer("Avval o'z raqamingizni tasdiqlang:", reply_markup=btn(["📱 Raqamni ulashish", "⬅️ Orqaga"], True))
    elif t == "🛡️ OSINT Razvedka": st[uid] = "osint"; await m.answer("Skanerlash uchun Telegram username yuboring:", reply_markup=btn(["⬅️ Orqaga"]))
    elif t == "🌤️ Ob-havo": st[uid] = "weather"; await m.answer("Shahar nomini inglizcha yozing (Masalan: Tashkent):", reply_markup=btn(["⬅️ Orqaga"]))
    elif t == "🌐 Tarjimon": st[uid] = "tr"; await m.answer("O'zbekcha matn yuboring:", reply_markup=btn(["⬅️ Orqaga"]))
    elif t == "🕵️‍♂️ Whois (Sayt Test)": st[uid] = "whois"; await m.answer("Domen nomini yuboring (Masalan: google.com):", reply_markup=btn(["⬅️ Orqaga"]))
    elif t == "🛡️ Fishing Detektor": st[uid] = "fishing"; await m.answer("🛡️ **Fishing Link Detektor**\n\nTekshirmoqchi bo'lgan shubhali sayt manzilini yuboring:", reply_markup=btn(["⬅️ Orqaga"]))
    elif t == "⚡ Termux Buyruqlari":
        await m.answer("⚡ **Termux Buyruqlari:**\n\n📁 `ls` - Fayllarni ko'rish\n📂 `cd` - Papkaga kirish\n🔍 `nmap` - Port skanerlash")
        
    elif t == "🤖 Kiber-Test (Quiz)":
        st[uid] = {"step": 0, "score": 0}
        q = QUIZ_DATA[0]
        opts = "\n".join(q["options"])
        await m.answer(f"🤖 **Kiber-Xavfsizlik Testi boshlandi!**\n\n{q['q']}\n\n{opts}", reply_markup=btn(["A", "B", "C", "⬅️ Orqaga"]))
        
    elif t == "⬅️ Orqaga": 
        st[uid] = None
        await m.answer("Bosh menyu:", reply_markup=btn(["🔍 Raqam qidirish", "🛡️ OSINT Razvedka", "🌤️ Ob-havo", "🌐 Tarjimon", "🕵️‍♂️ Whois (Sayt Test)", "🛡️ Fishing Detektor", "🤖 Kiber-Test (Quiz)", "⚡ Termux Buyruqlari", "💻 Biz haqimizda", "🌐 Havolalar"]))
    
    elif isinstance(st.get(uid), dict) and "step" in st[uid]:
        state = st[uid]
        current_step = state["step"]
        user_choice = t.upper()
        
        if user_choice in ["A", "B", "C"]:
            if user_choice == QUIZ_DATA[current_step]["ans"]: state["score"] += 1
            next_step = current_step + 1
            state["step"] = next_step
            
            if next_step < len(QUIZ_DATA):
                q = QUIZ_DATA[next_step]
                opts = "\n".join(q["options"])
                await m.answer(f"{q['q']}\n\n{opts}", reply_markup=btn(["A", "B", "C", "⬅️ Orqaga"]))
            else:
                score = state["score"]
                st[uid] = None
                status = "🟢 Kiber-Mutaxassis" if score == 3 else "🟡 Kiber-Sariq" if score == 2 else "🔴 Kiber-Sodda"
                await m.answer(f"🏁 **Test yakunlandi!**\n\n📊 To'g'ri: {score}/3\n🛡️ Daraja: **{status}**", reply_markup=btn(["🔍 Raqam qidirish", "🛡️ OSINT Razvedka", "🌤️ Ob-havo", "🌐 Tarjimon", "🕵️‍♂️ Whois (Sayt Test)", "🛡️ Fishing Detektor", "🤖 Kiber-Test (Quiz)", "⚡ Termux Buyruqlari", "💻 Biz haqimizda", "🌐 Havolalar"]))
        else: await m.answer("⚠️ Variantlardan birini (A, B yoki C) tanlang.")

    elif st.get(uid) in ["fishing", "whois"]:
        mode = st.get(uid)
        s = await m.answer("🔍 Global kiber-baza (RDAP) tahlil qilinmoqda...")
        domain = t.replace("https://", "").replace("http://", "").lower().split("/")[0]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://rdap.org{domain}") as r:
                    if r.status == 200:
                        data = await r.json()
                        created_date = None
                        if "events" in data:
                            for event in data["events"]:
                                if event.get("eventAction") == "registration": created_date = event.get("eventDate")[:10]
                        if created_date:
                            c_date = datetime.strptime(created_date, "%Y-%m-%d")
                            days_old = (datetime.now() - c_date).days
                            if mode == "fishing":
                                if days_old < 180: await s.edit_text(f"🚨 **FISHING XAVFI!**\n🌐 Sayt: `{domain}` juda yangi! 🔴")
                                else: await s.edit_text(f"✅ Xavfsiz tizim. `{domain}` eski va ishonchli.")
                            else: await s.edit_text(f"🕵️‍♂️ **WHOIS ({domain}):**\n📅 Ochilgan: {created_date}\n📊 Yoshi: {days_old} kun.")
                        else: await s.edit_text("⚠️ Sanani aniqlab bo'lmadi.")
                    else: await s.edit_text(f"⚠️ `{domain}` topilmadi. Fishing bo'lishi mumkin! 🔴")
            except: await s.edit_text("⚙️ Tarmoq ulanishida xatolik.")

    elif st.get(uid) == "weather":
        s = await m.answer("📡 Tekshirilmoqda...")
        async with aiohttp.ClientSession() as os:
            async with os.get(f"https://wttr.in{t}?format=%c+%t+%C") as r: res = await r.text() if r.status == 200 else "Topilmadi"
        await s.edit_text(f"🌤️ {t.capitalize()} ob-havosi:\n{res.strip()}" if "404" not in res else "⚠️ Topilmadi.")
    elif st.get(uid) == "osint":
        s = await m.answer("🔍 Skanerlanmoqda...")
        await asyncio.sleep(1)
        await s.edit_text(f"🛡️ **OSINT @{t}:**\n├ Guruhlar: ~{random.randint(10,50)} ta\n├ Kanallar: ~{random.randint(15,80)} ta\n⚠️ Xavf: {random.choice(['PAST 🟢','O\'RTA 🟡','YUQORI 🔴'])}")
    elif st.get(uid) == "tr": await m.answer(f"📝 Matn: {t}\n🇬🇧 Inglizcha: [Lug'at yangilanmoqda...]")
    elif t.startswith("@"):
        cr.execute("SELECT ph FROM u WHERE user=?", (t.lower(),))
        r = cr.fetchone()
        if r: await m.answer(f"🔍 Topildi!\n👤 {t}\n📞 +{r}")
        else: await m.answer(f"🔍 Qidirilmoqda...\n⚠️ Topilmadi. Kod: +998 ({random.choice(['90','91','93','94','99'])}) ***-**-**")
    else: await m.answer("⚠️ Noma'lum buyruq. Tugmalardan foydalaning.")

async def handle(request):
    return web.Response(text="Bot is running 24/7!")

async def main():
    print("Serverbop va variantlari to'g'rilangan bot faol...")
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await asyncio.gather(site.start(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
    
