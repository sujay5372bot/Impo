import logging, re, asyncio
from utils import temp
from info import ADMINS
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, MessageIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")

    _, raju, chat, lst_msg_id, from_user = query.data.split("#")

    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(
            int(from_user),
            f'Your Submission for indexing {chat} has been declined by our moderators.',
            reply_to_message_id=int(lst_msg_id)
        )
        return

    if lock.locked():
        await query.answer('Wait until previous process complete.', show_alert=True)
        return

    await query.answer('Processing...⏳', show_alert=True)

    if int(from_user) not in ADMINS:
        await bot.send_message(
            int(from_user),
            f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
            reply_to_message_id=int(lst_msg_id)
        )

    msg = query.message  # This was missing; needed for further usage

    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )

    try:
        chat = int(chat)
    except ValueError:
        pass  # keep chat as string if not convertible

    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    batch_size = 20

    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False

            while current <= lst_msg_id:
                if temp.CANCEL:
                    break

                batch_ids = list(range(current + 1, min(current + batch_size + 1, lst_msg_id + 1)))

                try:
                    messages = await bot.get_messages(chat, batch_ids)
                except MessageIdInvalid:
                    current += batch_size
                    continue

                async def process_message(message):
                    nonlocal total_files, duplicate, errors, deleted, no_media, unsupported

                    if not message or message.date is None:
                        deleted += 1
                        return
                    elif not message.media:
                        no_media += 1
                        return
                    elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                        unsupported += 1
                        return

                    media = getattr(message, message.media.value, None)
                    if not media:
                        unsupported += 1
                        return

                    file_info = {
                        "file_type": message.media.value,
                        "caption": message.caption,
                        "media": media
                    }

                    aynav, vnay = await save_file(file_info)
                    if aynav:
                        total_files += 1
                    elif vnay == 0:
                        duplicate += 1
                    elif vnay == 2:
                        errors += 1

                await asyncio.gather(*(process_message(m) for m in messages if m))

                current += batch_size
                temp.CURRENT = current

                await msg.edit_text(
                    f"Total fetched: <code>{current}</code>\n"
                    f"Saved: <code>{total_files}</code>\n"
                    f"Duplicate: <code>{duplicate}</code>\n"
                    f"Deleted: <code>{deleted}</code>\n"
                    f"Non-Media: <code>{no_media + unsupported}</code> (Unsupported: {unsupported})\n"
                    f"Errors: <code>{errors}</code>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]])
                )

        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
        else:
            await msg.edit(
                f'\u2705 Indexing Complete!\n\nSaved: <code>{total_files}</code>\n'
                f'Duplicates: <code>{duplicate}</code>\n'
                f'Deleted: <code>{deleted}</code>\n'
                f'Skipped (non-media): <code>{no_media + unsupported}</code>\n'
                f'Errors: <code>{errors}</code>'
                )
