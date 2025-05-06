#Don't Remove Credit @SUJAY
#Ask Doubt on telegram @onefighterarmy

import datetime, time, asyncio 
from pyrogram import Client, filters 
from database.users_chats_db import db 
from info import ADMINS 
from utils import broadcast_messages, broadcast_messages_group

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    try:
        b_msg = await bot.ask(chat_id=message.from_user.id, text="Now Send Me Your Broadcast Message", timeout=60)
        if not b_msg:
            return await message.reply("Koi message nahi mila broadcast ke liye.")

        pin_msg = await bot.ask(chat_id=message.from_user.id, text="Do you want to pin the message? (yes/no)", timeout=30)
        if not pin_msg:
            return await message.reply("Aapne pin karne ke liye koi jawab nahi diya.")
        
        should_pin = pin_msg.text.lower() in ["yes", "y"]

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
                elif sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                else:
                    failed += 1
            else:
                failed += 1
            done += 1
            await asyncio.sleep(0.5)

            if not done % 20:
                await sts.edit(f"Broadcast in progress:\n\nTotal Users: {total_users}\nCompleted: {done}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

    except asyncio.TimeoutError:
        return await message.reply("Time ho gaya, aapne koi message nahi bheja.")
    except Exception as e:
        print(f"error: {e}")


@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS)) 
async def broadcast_group(bot, message): 
    try:
        b_msg = await bot.ask(chat_id=message.from_user.id, text="Now Send Me Your Broadcast Message", timeout=60)
        if not b_msg:
            return await message.reply("Koi message nahi mila group broadcast ke liye.")

        pin_msg = await bot.ask(chat_id=message.from_user.id, text="Do you want to pin the message? (yes/no)", timeout=30)
        if not pin_msg:
            return await message.reply("Aapne pin karne ke liye koi jawab nahi diya.")

        should_pin = pin_msg.text.lower() in ["yes", "y"]

        groups = await db.get_all_chats()
        sts = await message.reply_text("Broadcasting your messages To Groups...")
        start_time = time.time()
        total_groups = await db.total_chat_count()
        done = failed = success = 0

        async for group in groups:
            pti, sh = await broadcast_messages_group(int(group['id']), b_msg, should_pin)
            await asyncio.sleep(0.5)
            if pti:
                success += 1
            else:
                failed += 1
            done += 1

            if not done % 20:
                await sts.edit(f"Broadcast in progress:\n\nTotal Groups: {total_groups}\nCompleted: {done}\nSuccess: {success}")

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups: {total_groups}\nCompleted: {done}\nSuccess: {success}")

    except asyncio.TimeoutError:
        return await message.reply("Time ho gaya, aapne koi message nahi bheja.")
    except Exception as e:
        print(f"error: {e}")


async def broadcast_messages(user_id, message, should_pin=False): 
    try: 
        sent_msg = await message.copy(chat_id=user_id) 
        if should_pin: 
            try: 
                await message._client.pin_chat_message(chat_id=user_id, message_id=sent_msg.id, disable_notification=True) 
            except: 
                pass 
        return True, "Success"
    except Exception as e: 
        if "bot was blocked by the user" in str(e): 
            return False, "Blocked"
        elif "chat not found" in str(e): 
            return False, "Deleted"
        else: 
            return False, "Error"

async def broadcast_messages_group(chat_id, message, should_pin=False): 
    try: 
        sent_msg = await message.copy(chat_id=chat_id) 
        if should_pin: 
            try: 
                await message._client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, disable_notification=True) 
            except: 
                pass 
        return True, "Success"
    except: 
        return False, "Error"
