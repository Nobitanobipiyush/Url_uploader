from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from pyromod import listen

import requests
import subprocess
import time
import asyncio
import re
import os
import sys

from subprocess import getstatusoutput
from aiohttp import ClientSession

import helper


# ================== CONFIG ==================

BOT_TOKEN = "add"
API_ID = add
API_HASH = "add"

owner_id = [8440950205]
auth_users = [8440950205]

token_cp = "your cp token"

# If you use PW / UTKASH / etc
api_url = ""     # example: https://your-api.vercel.app/
api_token = ""   # your token

photo1 = "https://envs.sh/PQ_.jpg"
getstatusoutput(f"wget {photo1} -O 'photo.jpg'")
photo = "photo.jpg"


bot = Client(
    "bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)


# ================== START ==================

@bot.on_message(filters.command("start") & filters.user(owner_id))
async def start_cmd(_, m: Message):
    await m.reply_text(
        f"**Hello Bruh** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n"
        ">> I am TXT file Downloader Bot.\n"
        ">> Send me /txt Command And Follow Steps\n\n"
        "If You Want To Stop Me Just Send /stop 😎"
    )


# ================== STOP / RESTART ==================

@bot.on_message(filters.command("stop") & filters.user(owner_id))
async def stop_cmd(_, m: Message):
    await m.reply_text("🛑 Bot Stopped!")
    os._exit(0)


@bot.on_message(filters.command("restart") & filters.user(owner_id))
async def restart_cmd(_, m: Message):
    await m.reply_text("♻️ Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)


# ================== TXT MAIN ==================

@bot.on_message(filters.command("txt") & filters.user(owner_id))
async def txt_handler(bot: Client, m: Message):
    editable = await m.reply_text("**Please Send TXT file for download**")

    input_file: Message = await bot.listen(editable.chat.id)
    txt_path = await input_file.download()

    file_name, ext = os.path.splitext(os.path.basename(txt_path))

    # Read txt
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().splitlines()

        os.remove(txt_path)

        links = []
        for line in content:
            line = line.strip()
            if not line:
                continue
            # format:  Title://link
            links.append(line.split("://", 1))

        if not links:
            await editable.edit("❌ No links found in TXT.")
            return

    except Exception as e:
        await editable.edit(f"❌ Invalid file input.\n\n{e}")
        return

    # Ask starting number
    await editable.edit(
        f"Total links found are **{len(links)}**\n\n"
        "Send From where you want to download.\nInitial is **1**"
    )
    input0: Message = await bot.listen(editable.chat.id)
    start_from = input0.text.strip()
    await input0.delete(True)

    # Ask batch name
    await editable.edit("**Send Me Your Batch Name or send `df` for grabing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    batch_name_in = input1.text.strip()
    await input1.delete(True)

    if batch_name_in.lower() == "df":
        b_name = file_name
    else:
        b_name = batch_name_in

    # Ask resolution
    await editable.edit("**Enter resolution** `1080` , `720` , `480` , `360` , `240` , `144`")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text.strip()
    await input2.delete(True)

    res_map = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080",
    }
    res = res_map.get(raw_text2, "1280x720")

    # Ask caption
    await editable.edit("**Now Enter A Caption\n\n>>OR Send `df` for use default**")
    input3: Message = await bot.listen(editable.chat.id)
    MR = input3.text.strip()
    await input3.delete(True)

    if MR.lower() == "df":
        MR = "Group Admin:)™"

    # Ask token for PW mpd
    await editable.edit("**If pw mpd links enter working token !**")
    input11: Message = await bot.listen(editable.chat.id)
    token = input11.text.strip()
    await input11.delete(True)

    # Ask thumb
    await editable.edit(
        "Now send the Thumb url For Custom Thumbnail.\n"
        "Example » `https://envs.sh/Hlb.jpg`\n"
        "Or if don't want Custom Thumbnail send = `no`"
    )
    input6: Message = await bot.listen(editable.chat.id)
    thumb = input6.text.strip()
    await input6.delete(True)
    await editable.delete()

    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    # Start count
    try:
        if len(links) == 1:
            count = 1
        else:
            count = int(start_from)
    except:
        count = 1

    path = f"./downloads/{m.chat.id}"
    os.makedirs(path, exist_ok=True)

    # ================== DOWNLOAD LOOP ==================

    for i in range(count - 1, len(links)):

        try:
            # Clean url
            V = links[i][1].replace("file/d/", "uc?export=download&id=")\
                           .replace("www.youtube-nocookie.com/embed", "youtu.be")\
                           .replace("?modestbranding=1", "")\
                           .replace("/view?usp=sharing", "")

            url = "https://" + V

            keys_string = ""
            mpd = ""
            appxkey = ""

            # ----------- URL HANDLING -----------

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/", "https://media-cdn.classplusapp.com/drm/")
                url = "https://dragoapi.vercel.app/classplus?link=" + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = "https://dragoapi.vercel.app/classplus?link=" + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "edge.api.brightcove.com" in url:
                bcov = "bcov_auth=YOURTOKEN#YOURCVTOKEN"
                url = url.split("bcov_auth")[0] + bcov

            elif "tencdn.classplusapp" in url:
                headers = {
                    "Host": "api.classplusapp.com",
                    "x-access-token": f"{token_cp}",
                    "user-agent": "Mobile-Android",
                    "X-CDN-Tag": "empty"
                }
                params = {"url": url}
                response = requests.get(
                    "https://api.classplusapp.com/cams/uploader/video/jw-signed-url",
                    headers=headers,
                    params=params,
                    timeout=60
                )
                url = response.json()["url"]

            elif "videos.classplusapp" in url:
                url = requests.get(
                    f"https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}",
                    headers={"x-access-token": f"{token_cp}"},
                    timeout=60
                ).json()["url"]

            elif "media-cdn.classplusapp.com" in url or "media-cdn-alisg.classplusapp.com" in url or "media-cdn-a.classplusapp.com" in url:
                headers = {"x-access-token": f"{token_cp}", "X-CDN-Tag": "empty"}
                url = requests.get(
                    f"https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}",
                    headers=headers,
                    timeout=60
                ).json()["url"]

            elif "encrypted.m" in url:
                appxkey = url.split("*")[1]
                url = url.split("*")[0]

            elif url.startswith("https://videotest.adda247.com/"):
                if url.split("/")[3] != "demo":
                    url = f"https://videotest.adda247.com/demo/{url.split('https://videotest.adda247.com/')[1]}"

            elif "master.mpd" in url:
                url = f"{api_url}pw-dl?url={url}&token={token}&authorization={api_token}&q={raw_text2}"

            # ----------- NAME -----------

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "")\
                .replace("+", "").replace("#", "").replace("|", "").replace("@", "")\
                .replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()

            if not name1:
                name1 = f"Video_{str(count).zfill(3)}"

            name = f"{name1[:60]} 𝐃𝐈𝐋𝐉𝐀𝐋𝐄 ❤️"

            # ----------- FORMAT -----------

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            # ----------- CAPTIONS -----------

            cc = (
                f"**╭── ⋆⋅☆⋅⋆ ──╮**\n"
                f"✦ **{str(count).zfill(3)}** ✦\n"
                f"**╰── ⋆⋅☆⋅⋆ ──╯**\n\n"
                f"🎭 **Title:** `{name1}.mkv`\n"
                f"🖥️ **Resolution:** [{res}]\n\n"
                f"📘 **Course:** `{b_name}`\n\n"
                f"🚀 **Extracted By:** `{MR}`"
            )

            cc1 = (
                f"**╭── ⋆⋅☆⋅⋆ ──╮**\n"
                f"✦ **{str(count).zfill(3)}** ✦\n"
                f"**╰── ⋆⋅☆⋅⋆ ──╯**\n\n"
                f"🎭 **Title:** `{name1}.pdf`\n\n"
                f"📘 **Course:** `{b_name}`\n\n"
                f"🚀 **Extracted By:** `{MR}`"
            )

            cc2 = (
                f"**╭── ⋆⋅☆⋅⋆ ──╮**\n"
                f"✦ **{str(count).zfill(3)}** ✦\n"
                f"**╰── ⋆⋅☆⋅⋆ ──╯**\n\n"
                f"🎭 **Title:** `{name1}.jpg`\n\n"
                f"📘 **Course:** `{b_name}`\n\n"
                f"🚀 **Extracted By:** `{MR}`"
            )

            ccyt = (
                f"**╭── ⋆⋅☆⋅⋆ ──╮**\n"
                f"✦ **{str(count).zfill(3)}** ✦\n"
                f"**╰── ⋆⋅☆⋅⋆ ──╯**\n\n"
                f"🎭 **Title:** `{name1}.mkv`\n"
                f"🎬 **Video Link:** {url}\n"
                f"🖥️ **Resolution:** [{res}]\n\n"
                f"📘 **Course:** `{b_name}`\n\n"
                f"🚀 **Extracted By:** `{MR}`"
            )

            # ================== FILE TYPES ==================

            # Google drive
            if "drive" in url:
                ka = await helper.download(url, name)
                await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc1)
                count += 1
                os.remove(ka)
                await asyncio.sleep(1)
                continue

            # Encrypted PDF
            if "pdf*" in url:
                pdf_key = url.split("*")[1]
                pdf_url = url.split("*")[0]
                pdf_enc = await helper.download_and_decrypt_pdf(pdf_url, name, pdf_key)
                await bot.send_document(chat_id=m.chat.id, document=pdf_enc, caption=cc1)
                count += 1
                os.remove(pdf_enc)
                continue

            # Normal PDF
            if ".pdf" in url:
                cmd_pdf = f'yt-dlp -o "{name}.pdf" "{url}" -R 25 --fragment-retries 25'
                os.system(cmd_pdf)
                await bot.send_document(chat_id=m.chat.id, document=f"{name}.pdf", caption=cc1)
                count += 1
                os.remove(f"{name}.pdf")
                continue

            # Images
            if any(img in url.lower() for img in [".jpeg", ".png", ".jpg"]):
                subprocess.run(["wget", url, "-O", f"{name}.jpg"], check=True)
                await bot.send_photo(chat_id=m.chat.id, caption=cc2, photo=f"{name}.jpg")
                count += 1
                os.remove(f"{name}.jpg")
                continue

            # Youtube only send link poster
            if "youtu" in url:
                await bot.send_photo(chat_id=m.chat.id, photo=photo, caption=ccyt)
                count += 1
                continue

            # WS HTML
            if ".ws" in url and url.endswith(".ws"):
                await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}", f"{name}.html")
                await bot.send_document(chat_id=m.chat.id, document=f"{name}.html", caption=cc1)
                count += 1
                os.remove(f"{name}.html")
                continue

            # Encrypted M
            if "encrypted.m" in url:
                prog = await m.reply_text(f"⬇️ Downloading: `{name}`")
                res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)
                await prog.delete(True)
                await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                count += 1
                await asyncio.sleep(1)
                continue

            # DRM
            if "drmcdni" in url or "drm/wv" in url:
                prog = await m.reply_text(f"⬇️ Decrypting DRM: `{name}`")
                res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                await prog.delete(True)
                await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                count += 1
                await asyncio.sleep(1)
                continue

            # Normal video
            prog = await m.reply_text(f"⬇️ Downloading: `{name}`")
            res_file = await helper.download_video(url, cmd, name)
            await prog.delete(True)
            await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
            count += 1
            await asyncio.sleep(1)

        except FloodWait as e:
            await m.reply_text(f"⏳ FloodWait: {e.x} sec")
            await asyncio.sleep(e.x)
            continue

        except Exception as e:
            await m.reply_text(
                f"**downloading failed**\n\n"
                f"{str(e)}\n\n"
                f"**Name** - {name}\n"
                f"**Link** - {url}"
            )
            count += 1
            continue

    await m.reply_text("**🔥 Successfully Downloaded All Lectures SIR 🔥**")


bot.run()
