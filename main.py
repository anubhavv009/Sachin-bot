import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URL, ADMIN, FSUB_CHANNEL
from database import add_user, get_all_users, total_users

logging.basicConfig(level=logging.INFO)
app = Client("KalakaarBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Force Subscribe Check Helper
async def is_subscribed(client, user_id):
    if not FSUB_CHANNEL:
        return True
    try:
        member = await client.get_chat_member(FSUB_CHANNEL.replace("@", ""), user_id)
        return member.status not in ["kicked", "left"]
    except Exception:
        return False

# /start Command Handler
@app.on_message(filters.private & filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    await add_user(user_id)

    if not await is_subscribed(client, user_id):
        ch = FSUB_CHANNEL.replace("@", "")
        btn = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{ch}")],
            [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.me.username}?start=start")]
        ]
        return await message.reply_text("⚠️ Bot use karne ke liye pehle channel join karein!", reply_markup=InlineKeyboardMarkup(btn))

    welcome_text = (
        f"👋 Namaste {message.from_user.first_name}!\n\n"
        f"Welcome to my official custom Telegram Bot!\n"
        f"Main aapke groups aur channels ko 24/7 automate kar sakta hoon."
    )

    buttons = [
        [
            InlineKeyboardButton("📢 Updates Channel", url="https://t.me/telegram"),
            InlineKeyboardButton("💬 Support Group", url="https://t.me/telegram")
        ],
        [InlineKeyboardButton("👤 Developer", url=f"tg://user?id={ADMIN}")]
    ]
    await message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons))


# 🎯 AUTO ACCEPT JOIN REQUEST + TEXT & VIDEO MESSAGE
@app.on_chat_join_request()
async def auto_accept(client: Client, request: ChatJoinRequest):
    try:
        # 1. Join Request Auto-Approve Karein
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)
        await add_user(request.from_user.id)

        user_name = request.from_user.first_name

        # 2. 💬 PEHLA TEXT MESSAGE (Yahan aap greeting message badal sakte hain):
        msg1 = (
            f"HELLO {user_name.upper()} 🖐️\n"
            f"APKI REQUEST HAMEN MIL GAI HAI JALDI ACCEPT HO JAYEGI 😃\n\n"
            f"T AB TAK AAP NICHE DI GAI HUI VIDEO DEKH LO 📣📣"
        )
        await client.send_message(request.from_user.id, msg1)

        # 3. 📹 DOOSRA VIDEO MESSAGE:
        # ✏️ CHANGE 1: Apni Video ka Link yahan daalein
        VIDEO_URL = "https://files.catbox.moe/sal3dp.mp4"

        # ✏️ CHANGE 2: Video ke niche wala text/links yahan badlein
        caption_text = (
            f"👈NEWPLATFORM H GUYSS✔️\n\n"
            f"⚠️WATCH THE FULL VEDIO ⚠️\n\n"
            f"✔️ पैसे कमाओ दोस्तों नीचे लिंक से ID बनालो और deposit करके ready रहो next season soon ⭐️\n\n"
            f"📎CREATE ID FAST 🔝✅\n\n"
            f"https://www.veergame9.com/#/register?invitationCode=97298414754\n\n"
            f"अगर Daily के 4000-5000 कमाना हो  चैनल के लिंक से ID बना लो सारे भाई✅\n\n"
            f"DEPOSIT NOW -500-/5000🍀 "
        )

        await client.send_video(
            chat_id=request.from_user.id,
            video=VIDEO_URL,
            caption=caption_text
        )

    except Exception as e:
        print(f"Error in Join Request: {e}")


# TagAll Command for Groups
@app.on_message(filters.group & filters.command("tagall"))
async def tag_all(client: Client, message: Message):
    text = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else "Attention Everyone! 📢"
    mentions = ""
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot:
            mentions += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
            if len(mentions) > 3000:
                await message.reply_text(f"{text}\n\n{mentions}")
                mentions = ""
    if mentions:
        await message.reply_text(f"{text}\n\n{mentions}")

# Admin Stats Command
@app.on_message(filters.private & filters.command("stats") & filters.user(ADMIN))
async def stats_cmd(client: Client, message: Message):
    count = await total_users()
    await message.reply_text(f"📊 Total Bot Users: {count}")

# Admin Broadcast Command
@app.on_message(filters.private & filters.command("broadcast") & filters.user(ADMIN))
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Kisi Message/Video ko reply karke /broadcast likhein!")
    
    msg = await message.reply_text("📢 Broadcast shuru ho raha hai...")
    users = await get_all_users()
    succ, fail = 0, 0

    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            succ += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail += 1

    await msg.edit_text(f"✅ Broadcast Done!\n• Success: {succ}\n• Failed: {fail}")

print("⚡ Bot Running...")
app.run()
