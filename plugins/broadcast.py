#Don't Remove Credit @SUJAY
#Ask Doubt on telegram @onefighterarmy

import datetime, time, asyncio 
from pyrogram import Client, filters 
from database.users_chats_db import db 
from info import ADMINS 
from utils import broadcast_messages, broadcast_messages_group

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message): 
    b_msg = await bot.ask(chat_id=message.from_user.id, text="Now Send Me Your Broadcast Message") 
    pin_msg = await bot.ask(chat_id=message.from_user.id, text="Do you want to pin the message? (yes/no)") 
    should_pin = pin_msg.text.lower() in ["yes", "y"]

try:
    users = await db.get_all_users()
    sts = await message.reply_text('Broadcasting your messages...')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = blocked = deleted = failed = success = 0

    async for user in users:
        if 'id' in user:
            pti, sh = await broadcast_messages(int(user['id']), b_msg, should_pin)
            if pti:
                success += 1
            elif pti == False:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "Error":
                    failed += 1
            done += 1
        else:
            done += 1
            failed += 1
        await asyncio.sleep(0.5)  # 0.5 second delay

        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
except Exception as e:
    print(f"error: {e}")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS)) 
async def broadcast_group(bot, message): 
    b_msg = await bot.ask(chat_id=message.from_user.id, text="Now Send Me Your Broadcast Message") 
    pin_msg = await bot.ask(chat_id=message.from_user.id, text="Do you want to pin the message? (yes/no)") 
    should_pin = pin_msg.text.lower() in ["yes", "y"]

groups = await db.get_all_chats()
sts = await message.reply_text("Broadcasting your messages To Groups...")
start_time = time.time()
total_groups = await db.total_chat_count()
done = failed = success = 0

async for group in groups:
    pti, sh = await broadcast_messages_group(int(group['id']), b_msg, should_pin)
    await asyncio.sleep(0.5)  # 0.5 second delay
    if pti:
        success += 1
    elif sh == "Error":
        failed += 1
    done += 1

    if not done % 20:
        await sts.edit(f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")

time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}") #Update these utility functions in utils.py:

async def broadcast_messages(user_id, message, should_pin=False): 
try: 
    sent_msg = await message.copy(chat_id=user_id) 
    if should_pin: 
try: 
    await message._client.pin_chat_message(chat_id=user_id, message_id=sent_msg.id, disable_notification=True) 
    except: 
        pass  # ignore pin error return True, "Success" except Exception as e: if "bot was blocked by the user" in str(e): return False, "Blocked" elif "chat not found" in str(e): return False, "Deleted" else: return False, "Error"

async def broadcast_messages_group(chat_id, message, should_pin=False): 
try: 
    sent_msg = await message.copy(chat_id=chat_id) 
if should_pin: 
try: 
    await message._client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, disable_notification=True) 
except: 
pass  # ignore pin error return True, "Success" except: return False, "Error"
                           
