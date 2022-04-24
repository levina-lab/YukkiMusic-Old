import os
import time
import shutil
import random
import asyncio
import yt_dlp
import shutil
import psutil
import subprocess

from os import path
from typing import Union
from .. import converter
from pytube import YouTube
from yt_dlp import YoutubeDL
from asyncio import QueueEmpty
from pytgcalls import StreamType
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, Audio
from pytgcalls.exceptions import NoActiveGroupCall, GroupCallNotFound
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from Yukki import dbb, app, BOT_USERNAME, BOT_ID, ASSID, ASSNAME, ASSUSERNAME, ASSMENTION
from ..YukkiUtilities.tgcallsrun import (yukki, convert, download, clear, get, is_empty, put, task_done, ASS_ACC)
from Yukki.YukkiUtilities.database.queue import (get_active_chats, is_active_chat, add_active_chat, remove_active_chat, music_on, is_music_playing, music_off)
from Yukki.YukkiUtilities.database.onoff import (is_on_off, add_on, add_off)
from Yukki.YukkiUtilities.database.chats import (get_served_chats, is_served_chat, add_served_chat, get_served_chats)
from ..YukkiUtilities.helpers.inline import (play_keyboard, search_markup, play_markup, playlist_markup, audio_markup, play_list_keyboard, close_keyboard)
from Yukki.YukkiUtilities.database.blacklistchat import (blacklisted_chats, blacklist_chat, whitelist_chat)
from Yukki.YukkiUtilities.database.gbanned import (get_gbans_count, is_gbanned_user, add_gban_user, add_gban_user)
from Yukki.YukkiUtilities.database.theme import (_get_theme, get_theme, save_theme)
from Yukki.YukkiUtilities.database.assistant import (_get_assistant, get_assistant, save_assistant)
from ..config import DURATION_LIMIT
from ..YukkiUtilities.helpers.decorators import errors
from ..YukkiUtilities.helpers.filters import command, other_filters
from ..YukkiUtilities.helpers.gets import (get_url, themes, random_assistant, ass_det)
from ..YukkiUtilities.helpers.logger import LOG_CHAT
from ..YukkiUtilities.helpers.thumbnails import gen_thumb
from ..YukkiUtilities.helpers.chattitle import CHAT_TITLE
from ..YukkiUtilities.helpers.ytdl import ytdl_opts 
from ..YukkiUtilities.helpers.inline import (play_keyboard, search_markup2, search_markup)
from youtubesearchpython import VideosSearch
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message)


flex = {}
chat_watcher_group = 3


def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":")))
    )

def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


@Client.on_message(command(["play", "play@VeezMegaBot"]) & other_filters)
async def play(_, message: Message):
    await message.delete()
    chat_id = message.chat.id  
    if message.sender_chat:
        return await message.reply_text("You'll need to switch to a user account to play music.")  
    user_id = message.from_user.id
    chat_title = message.chat.title
    username = message.from_user.first_name
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_on_off(1):
        LOG_ID = "-1001306851903"
        if int(chat_id) != int(LOG_ID):
            return await message.reply_text("❌ The bot is under maintenance you're not able to play music for a while !\n\n• we're sorry for the inconveniences.")
        return await message.reply_text("❌ The bot is under maintenance you're not able to play music for a while !\n\n• we're sorry for the inconveniences.")
    a = await app.get_chat_member(message.chat.id, BOT_ID)
    if a.status != "administrator":
        await message.reply_text(f"💡 To use me, I need to be an Administrator with the following permissions:\n\n» ❌ __Delete messages__\n» ❌ __Add users__\n» ❌ __Manage video chat__\n\nData is **updated** automatically after you **promote me**")
        return
    if not a.can_manage_voice_chats:
        await message.reply_text(
        "💡 To use me, Give me the following permission below:"
        + "\n\n» ❌ __Manage video chat__\n\nOnce done, try again.")
        return
    if not a.can_delete_messages:
        await message.reply_text(
        "💡 To use me, Give me the following permission below:"
        + "\n\n» ❌ __Delete messages__\n\nOnce done, try again.")
        return
    if not a.can_invite_users:
        await message.reply_text(
        "💡 To use me, Give me the following permission below:"
        + "\n\n» ❌ __Add users__\n\nOnce done, try again.")
        return
    try:
        b = await app.get_chat_member(message.chat.id, ASSID)
        if b.status == "banned":
            try:
                await message.reply_text("❌ The userbot is banned in this chat, unban the userbot first to be able to play music !")
                await remove_active_chat(message.chat.id)
            except BaseException:
                pass
            invitelink = (await app.get_chat(message.chat.id)).invite_link
            if not invitelink:
                await app.export_chat_invite_link(message.chat.id)
                invitelink = (await app.get_chat(message.chat.id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await ASS_ACC.join_chat(invitelink)
            await remove_active_chat(message.chat.id)
    except UserNotParticipant:
        try:
            invitelink = (await app.get_chat(message.chat.id)).invite_link
            if not invitelink:
                await app.export_chat_invite_link(message.chat.id)
                invitelink = (await app.get_chat(message.chat.id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await ASS_ACC.join_chat(invitelink)
            await remove_active_chat(message.chat.id)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            return await message.reply_text(f"❌ **userbot failed to join**\n\n**reason**: `{e}`")
    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)
    fucksemx = 0
    if audio:
        fucksemx = 1
        mystic = await message.reply_text("🔄 Converting audio...")
        if audio.file_size > 157286400:
            await mystic.edit_text("audio file size must be less than `150 mb`") 
            return
        duration = round(audio.duration / 60)
        if duration > DURATION_LIMIT:
            return await mystic.edit_text(f"❌ duration error\n\nallowed duration: {DURATION_LIMIT} minute\nreceived duration:** {duration} minute")
        file_name = audio.file_unique_id + '.' + (
            (
                audio.file_name.split('.')[-1]
            ) if (
                not isinstance(audio, Voice)
            ) else 'ogg'
        )
        file_name = path.join(path.realpath('downloads'), file_name)
        file = await convert(
            (
                await message.reply_to_message.download(file_name)
            )
            if (
                not path.isfile(file_name)
            )
            else file_name,
        )
        
        num = message.reply_to_message
        if num.audio:
           title = audio.title
        elif num.voice:
           title = "telegram audio"
        link = message.reply_to_message.link
        thumbnail = "https://telegra.ph/file/82862f0af1d599cdea127.jpg"
        videoid = "smex1"
        message.chat.title
        if len(message.chat.title) > 10:
            ctitle = message.chat.title[:10] + "..."
        else:
            ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle) 
        duration = convert_seconds(audio.duration)
        theme = random.choice(themes)
        userid = message.from_user.id 
        thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
        
    elif url:
        query = " ".join(message.command[1:])
        mystic = await _.send_message(chat_id, "🔍 **Searching...**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        try:
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = (result["title"])
                duration = (result["duration"])
                views = (result["viewCount"]["short"])  
                thumbnail = (result["thumbnails"][0]["url"])
                link = (result["link"])
                idxz = (result["id"])
                videoid = (result["id"])
        except Exception as e:
            return await mystic.edit_text(f"song not found.\n\n**reason:** {e}")    
        smex = int(time_to_seconds(duration))
        if smex > DURATION_LIMIT:
            return await mystic.edit_text(f"❌ duration error\n\nallowed duration: {DURATION_LIMIT} minute\nreceived duration:** {duration} minute")
        if duration == "None":
            return await mystic.edit_text("❌ live stream not supported")
        if views == "None":
            return await mystic.edit_text("❌ live stream not supported")
        semxbabes = (f"📥 downloading: {title[:55]}")
        await mystic.edit(semxbabes)
        theme = random.choice(themes)
        ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        userid = message.from_user.id
        thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
        def my_hook(d): 
            if d['status'] == 'downloading':
                percentage = d['_percent_str']
                per = (str(percentage)).replace(".","", 1).replace("%","", 1)
                per = int(per)
                eta = d['eta']
                speed = d['_speed_str']
                size = d['_total_bytes_str']
                bytesx = d['total_bytes']
                if str(bytesx) in flex:
                    pass
                else:
                    flex[str(bytesx)] = 1
                if flex[str(bytesx)] == 1:
                    flex[str(bytesx)] += 1
                    try:
                        if eta > 2:
                            mystic.edit(f"Downloading {title[:50]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                    except Exception as e:
                        pass
                if per > 250:    
                    if flex[str(bytesx)] == 2:
                        flex[str(bytesx)] += 1
                        if eta > 2:     
                            mystic.edit(f"Downloading {title[:50]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                        print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                if per > 500:    
                    if flex[str(bytesx)] == 3:
                        flex[str(bytesx)] += 1
                        if eta > 2:     
                            mystic.edit(f"Downloading {title[:50]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                        print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                if per > 800:    
                    if flex[str(bytesx)] == 4:
                        flex[str(bytesx)] += 1
                        if eta > 2:    
                            mystic.edit(f"Downloading {title[:50]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                        print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
            if d['status'] == 'finished': 
                try:
                    taken = d['_elapsed_str']
                except Exception as e:
                    taken = "00:00"
                size = d['_total_bytes_str']
                mystic.edit(f"**Downloaded {title[:55]}...**\n\n**size:** `{size}`\n**time:** {taken} sec\n\n**Converting file** [ffmpeg process]")
                print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")  
        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, download, link, my_hook)
        file = await convert(x)
        
    else:
        if len(message.command) < 2:
            user_name = message.from_user.first_name
            thumb ="cache/playlist.png"
            buttons = playlist_markup(user_name, user_id)
            hmo = await message.reply_photo(
            photo=thumb, 
            caption=("**usage:** /play (music name/youtube url/audio file)\n\nIf you want to play from playlist, select one from below."),    
            reply_markup=InlineKeyboardMarkup(buttons),
            ) 
            return
        
        query = " ".join(message.command[1:])
        mystic = await _.send_message(chat_id, "🔍 **Searching...**")
        try:
            a = VideosSearch(query, limit=5)
            result = (a.result()).get("result")
            title1 = (result[0]["title"])
            duration1 = (result[0]["duration"])
            title2 = (result[1]["title"])
            duration2 = (result[1]["duration"])      
            title3 = (result[2]["title"])
            duration3 = (result[2]["duration"])
            title4 = (result[3]["title"])
            duration4 = (result[3]["duration"])
            title5 = (result[4]["title"])
            duration5 = (result[4]["duration"])
            ID1 = (result[0]["id"])
            ID2 = (result[1]["id"])
            ID3 = (result[2]["id"])
            ID4 = (result[3]["id"])
            ID5 = (result[4]["id"])
        except Exception as e:
            return await mystic.edit_text(f"😕 Sorry, we **couldn't** find the song you were looking for\n\n• Check that the **name is correct** or **try by searching the artist.**", reply_markup=close_keyboard)
        thumb = "cache/results.png"
        url = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await mystic.edit(
            f"• Choose the results to play !\n\n1️⃣ <b>[{title1[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n\n2️⃣ <b>[{title2[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n\n3️⃣ <b>[{title3[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n\n4️⃣ <b>[{title4[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n\n5️⃣ <b>[{title5[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID5})",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return   
    if await is_active_chat(chat_id):
        position = await put(chat_id, file=file)
        _chat_ = ((str(file)).replace("_","", 1).replace("/","", 1).replace(".","", 1))
        cpl=(f"downloads/{_chat_}final.png")     
        shutil.copyfile(thumb, cpl) 
        f20 = open(f'search/{_chat_}title.txt', 'w')
        f20.write(f"{title}") 
        f20.close()
        f111 = open(f'search/{_chat_}duration.txt', 'w')
        f111.write(f"{duration}") 
        f111.close()
        f27 = open(f'search/{_chat_}username.txt', 'w')
        f27.write(f"{checking}") 
        f27.close()
        if fucksemx != 1:
            f28 = open(f'search/{_chat_}videoid.txt', 'w')
            f28.write(f"{videoid}") 
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f'search/{_chat_}videoid.txt', 'w')
            f28.write(f"{videoid}") 
            f28.close()
            buttons = audio_markup(videoid, user_id)
        checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        await message.reply_photo(
            photo=thumb,
            caption=(f"💡 **Track added to queue »** {position}\n\n🗂 **Name:** [{title[:35]}...]({link}) \n⏱ **Duration:** `{duration}` \n🧸 **Request by:** {checking}"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return await mystic.delete()     
    else:
        try:
            await music_on(chat_id)
            await yukki.pytgcalls.join_group_call(
                chat_id,
                InputStream(
                    InputAudioStream(
                        file,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
        except (NoActiveGroupCall, GroupCallNotFound):
            return await app.send_message(chat_id, "😕 Sorry, **no** active video chat!\n\n• to use me, **start one.**", reply_markup=close_keyboard)
        await add_active_chat(chat_id)
        _chat_ = ((str(file)).replace("_","", 1).replace("/","", 1).replace(".","", 1))                                                                                           
        checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        if fucksemx != 1:
            f28 = open(f'search/{_chat_}videoid.txt', 'w')
            f28.write(f"{videoid}") 
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f'search/{_chat_}videoid.txt', 'w')
            f28.write(f"{videoid}") 
            f28.close()
            buttons = audio_markup(videoid, user_id)
        await message.reply_photo(
        photo=thumb,
        reply_markup=InlineKeyboardMarkup(buttons),    
        caption=(f"🗂 **Name:** [{title[:95]}]({link})\n⏱ Duration: `{duration}`\n🧸 Request by:** {checking}")
    )   
        return await mystic.delete()
         
    
@Client.on_callback_query(filters.regex(pattern=r"yukki"))
async def start_stream(_, CallbackQuery): 
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id 
    try:
        id, duration, user_id = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"an error occured\n\n**reason**:{e}")
    if duration == "None":
        return await CallbackQuery.answer("❌ live stream not supported", show_alert=True)      
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer("💡 sorry this not your request", show_alert=True)
    await CallbackQuery.message.delete()
    checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    url = (f"https://www.youtube.com/watch?v={id}")
    videoid = id
    idx = id
    smex = int(time_to_seconds(duration))
    if smex > DURATION_LIMIT:
        await CallbackQuery.message.reply_text(f"❌ duration error\n\nallowed duration: {DURATION_LIMIT} minute\nreceived duration:** {duration} minute")
        return 
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            x = ytdl.extract_info(url, download=False)
    except Exception as e:
        return await CallbackQuery.message.reply_text(f"❌ failed to download video.\n\n**reason**: `{e}`") 
    title = (x["title"])
    mystic = await CallbackQuery.message.reply_text(f"📥 downloading: {title[:55]}")
    thumbnail = (x["thumbnail"])
    idx = (x["id"])
    videoid = (x["id"])
    def my_hook(d): 
        if d['status'] == 'downloading':
            percentage = d['_percent_str']
            per = (str(percentage)).replace(".","", 1).replace("%","", 1)
            per = int(per)
            eta = d['eta']
            speed = d['_speed_str']
            size = d['_total_bytes_str']
            bytesx = d['total_bytes']
            if str(bytesx) in flex:
                pass
            else:
                flex[str(bytesx)] = 1
            if flex[str(bytesx)] == 1:
                flex[str(bytesx)] += 1
                try:
                    if eta > 2:
                        mystic.edit(f"Downloading {title[:50]}\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                except Exception as e:
                    pass
            if per > 250:    
                if flex[str(bytesx)] == 2:
                    flex[str(bytesx)] += 1
                    if eta > 2:     
                        mystic.edit(f"Downloading {title[:50]}..\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
            if per > 500:    
                if flex[str(bytesx)] == 3:
                    flex[str(bytesx)] += 1
                    if eta > 2:     
                        mystic.edit(f"Downloading {title[:50]}...\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
            if per > 800:    
                if flex[str(bytesx)] == 4:
                    flex[str(bytesx)] += 1
                    if eta > 2:    
                        mystic.edit(f"Downloading {title[:50]}....\n\n**FileSize:** {size}\n**Downloaded:** {percentage}\n**Speed:** {speed}\n**ETA:** {eta} sec")
                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
        if d['status'] == 'finished': 
            try:
                taken = d['_elapsed_str']
            except Exception as e:
                taken = "00:00"
            size = d['_total_bytes_str']
            mystic.edit(f"**Downloaded: {title[:55]}...**\n\n**size:** `{size}`\n**time:** `{taken}` sec\n\n**Converting file [ffmpeg process]")
            print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")    
    loop = asyncio.get_event_loop()
    x = await loop.run_in_executor(None, download, url, my_hook)
    file = await convert(x)
    theme = random.choice(themes)
    ctitle = CallbackQuery.message.chat.title
    ctitle = await CHAT_TITLE(ctitle)
    thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
    await mystic.delete()
    if await is_active_chat(chat_id):
        position = await put(chat_id, file=file)
        buttons = play_markup(videoid, user_id)
        _chat_ = ((str(file)).replace("_","", 1).replace("/","", 1).replace(".","", 1))
        cpl=(f"downloads/{_chat_}final.png")     
        shutil.copyfile(thumb, cpl) 
        f20 = open(f'search/{_chat_}title.txt', 'w')
        f20.write(f"{title}") 
        f20.close()
        f111 = open(f'search/{_chat_}duration.txt', 'w')
        f111.write(f"{duration}") 
        f111.close()
        f27 = open(f'search/{_chat_}username.txt', 'w')
        f27.write(f"{checking}") 
        f27.close()
        f28 = open(f'search/{_chat_}videoid.txt', 'w')
        f28.write(f"{videoid}") 
        f28.close()
        await mystic.delete()
        m = await CallbackQuery.message.reply_photo(
        photo=thumb,
        caption=(f"💡 **Track added to queue »** `{position}`\n\n🗂 **Name:** [{title[:35]}...]({url})\n⏱ **Duration:** `{duration}`\n🧸 **Request by:** {checking}"),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
        os.remove(thumb)
        await CallbackQuery.message.delete()       
    else:
        try:
            await music_on(chat_id)
            await yukki.pytgcalls.join_group_call(
                chat_id,
                InputStream(
                    InputAudioStream(
                        file,
                    ),
                ),
                stream_type=StreamType().local_stream,
            ) 
        except (NoActiveGroupCall, GroupCallNotFound):
            return await app.send_message(chat_id, "😕 Sorry, **no** active video chat!\n\n• to use me, **start one.**", reply_markup=close_keyboard)
        await add_active_chat(chat_id)
        buttons = play_markup(videoid, user_id)
        await mystic.delete()
        m = await CallbackQuery.message.reply_photo(
        photo=thumb,
        reply_markup=InlineKeyboardMarkup(buttons),    
        caption=(f"🗂 **Name:** [{title[:95]}]({url}) \n⏱ **Duration:** `{duration}`\n🧸 **Request by:** {checking}")
    )   
        os.remove(thumb)
        await CallbackQuery.message.delete()


@Client.on_callback_query(filters.regex(pattern=r"popat"))
async def popat(_, CallbackQuery): 
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    print(callback_request)
    userid = CallbackQuery.from_user.id 
    try:
        id, query, user_id = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"an error occured\n\n**reason**: {e}")       
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer("💡 sorry this not your request", show_alert=True)
    i=int(id)
    query = str(query)
    try:
        a = VideosSearch(query, limit=10)
        result = (a.result()).get("result")
        title1 = (result[0]["title"])
        duration1 = (result[0]["duration"])
        title2 = (result[1]["title"])
        duration2 = (result[1]["duration"])      
        title3 = (result[2]["title"])
        duration3 = (result[2]["duration"])
        title4 = (result[3]["title"])
        duration4 = (result[3]["duration"])
        title5 = (result[4]["title"])
        duration5 = (result[4]["duration"])
        title6 = (result[5]["title"])
        duration6 = (result[5]["duration"])
        title7= (result[6]["title"])
        duration7 = (result[6]["duration"])      
        title8 = (result[7]["title"])
        duration8 = (result[7]["duration"])
        title9 = (result[8]["title"])
        duration9 = (result[8]["duration"])
        title10 = (result[9]["title"])
        duration10 = (result[9]["duration"])
        ID1 = (result[0]["id"])
        ID2 = (result[1]["id"])
        ID3 = (result[2]["id"])
        ID4 = (result[3]["id"])
        ID5 = (result[4]["id"])
        ID6 = (result[5]["id"])
        ID7 = (result[6]["id"])
        ID8 = (result[7]["id"])
        ID9 = (result[8]["id"])
        ID10 = (result[9]["id"])                    
    except Exception as e:
        return await mystic.edit_text("😕 Sorry, we **couldn't** find the song you were looking for\n\n• Check that the **name is correct** or **try by searching the artist.**", reply_markup=close_keyboard)
    if i == 1:
        url = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10 ,user_id, query)
        await CallbackQuery.edit_message_text(
            f"• Choose the results to play !\n\n6️⃣ <b>[{title6[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID6})\n\n7️⃣ <b>[{title7[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID7})\n\n8️⃣ <b>[{title8[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID8})\n\n9️⃣ <b>[{title9[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID9})\n\n🔟 <b>[{title10[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID10})",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return    
    if i == 2:
        url = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await CallbackQuery.edit_message_text(
            f"• Choose the results to play !\n\n1️⃣ <b>[{title1[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n\n2️⃣ <b>[{title2[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n\n3️⃣ <b>[{title3[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n\n4️⃣ <b>[{title4[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n\n5️⃣ <b>[{title5[:35]}...]({url})</b>\n └ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID5})",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return


@Client.on_message(command(["playplaylist", "playplaylist@VeezMegaBot"]) & other_filters)
async def start_playlist_stream(_, message):
    thumb ="cache/playlist.png"
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    buttons = playlist_markup(user_name, user_id)
    await app.send_photo(
        chat_id,
        photo=thumb,
        caption=("**❓ Which playlist do you want to play?**"),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return
