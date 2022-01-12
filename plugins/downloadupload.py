# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}ul <path/to/file>`
    Upload files on telegram.
    Use following arguments before or after filename as per requirement:
      `--allow-stream` to upload as stream.
      `--delete` to delete file after uploading.
      `--no-thumb` to upload without thumbnail.

• `{i}dl <filename(optional)>`
    Reply to file to download.

• `{i}download <DDL> (| filename)`
    Download using DDL. Will autogenerate filename if not given.
"""

import asyncio
import os
import time
from datetime import datetime as dt

from aiohttp.client_exceptions import InvalidURL
from pyUltroid.functions.helper import time_formatter
from pyUltroid.functions.tools import set_attributes
from telethon.errors.rpcerrorlist import MessageNotModifiedError

from . import (
    downloader,
    eor,
    fast_download,
    get_string,
    progress,
    time_formatter,
    ultroid_cmd,
)


@ultroid_cmd(
    pattern="download( (.*)|$)",
)
async def down(event):
    matched = event.pattern_match.group(1).strip()
    msg = await event.eor(get_string("udl_4"))
    if not matched:
        return await eor(msg, get_string("udl_5"), time=5)
    try:
        splited = matched.split(" | ")
        link = splited[0]
        filename = splited[1]
    except IndexError:
        filename = None
    s_time = time.time()
    try:
        filename, d = await fast_download(
            link,
            filename,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    msg,
                    s_time,
                    f"Downloading from {link}",
                )
            ),
        )
    except InvalidURL:
        return await msg.eor("`Invalid URL provided :(`", time=5)
    await msg.eor(f"`{filename}` `downloaded in {time_formatter(d*1000)}.`")


@ultroid_cmd(
    pattern="dl( (.*)|$)",
)
async def download(event):
    if not event.reply_to_msg_id:
        return await event.eor(get_string("cvt_3"))
    xx = await event.eor(get_string("com_1"))
    s = dt.now()
    k = time.time()
    if event.reply_to_msg_id:
        ok = await event.get_reply_message()
        if not ok.media:
            return await xx.eor(get_string("udl_1"), time=5)
        if hasattr(ok.media, "document"):
            file = ok.media.document
            mime_type = file.mime_type
            filename = event.pattern_match.group(1).strip() or ok.file.name
            if not filename:
                if "audio" in mime_type:
                    filename = "audio_" + dt.now().isoformat("_", "seconds") + ".ogg"
                elif "video" in mime_type:
                    filename = "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
            try:
                result = await downloader(
                    "resources/downloads/" + filename,
                    file,
                    xx,
                    k,
                    "Downloading " + filename + "...",
                )
            except MessageNotModifiedError as err:
                return await xx.edit(str(err))
            file_name = result.name
        else:
            d = "resources/downloads/"
            file_name = await event.client.download_media(
                ok,
                d,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d,
                        t,
                        xx,
                        k,
                        get_string("com_5"),
                    ),
                ),
            )
    e = dt.now()
    t = time_formatter(((e - s).seconds) * 1000)
    await xx.eor(get_string("udl_2").format(file_name, t))


@ultroid_cmd(
    pattern="ul( (.*)|$)",
)
async def _(event):
    if len(event.text) >= 8:
        if "ultroid" in event.text[:7]:
            return
    msg = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1)
    if match:
        match = match.strip()
    stream, force_doc, delete, thumb = (
        False,
        True,
        False,
        "resources/extras/ultroid.jpg",
    )
    if "--allow-stream" in match:
        stream = True
        force_doc = False
    if "--delete" in match:
        delete = True
    if "--no-thumb" in match:
        thumb = None
    arguments = ["--allow-stream", "--delete", "--no-thumb"]
    if any(item in match for item in arguments):
        match = (
            match.replace("--allow-stream", "")
            .replace("--delete", "")
            .replace("--no-thumb", "")
            .strip()
        )
    if not os.path.exists(match):
        return await msg.eor("`File doesn't exist or path is incorrect!`")
    if os.path.isdir(match):
        c, s = 0, 0
        for files in sorted(os.listdir(match)):
            attributes = None
            if stream:
                attributes = await set_attributes(files)
            try:
                file, _ = await event.client.fast_uploader(
                    match + "/" + files, show_progress=True, event=msg, to_delete=delete
                )
                await event.client.send_file(
                    event.chat_id,
                    file,
                    supports_streaming=stream,
                    force_document=force_doc,
                    thumb=thumb,
                    attributes=attributes,
                    caption=f"`Uploaded` `{match}/{files}` `in {time_formatter(_*1000)}`",
                    reply_to=event.reply_to_msg_id or event,
                )
                s += 1
            except (ValueError, IsADirectoryError):
                c += 1
        return await msg.eor(f"`Uploaded {s} files, failed to upload {c}.`")
    attributes = None
    if stream:
        attributes = await set_attributes(match)
    file, _ = await event.client.fast_uploader(
        match, show_progress=True, event=msg, to_delete=delete
    )
    await event.client.send_file(
        event.chat_id,
        file,
        supports_streaming=stream,
        force_document=force_doc,
        thumb=thumb,
        attributes=attributes,
        caption=f"`Uploaded` `{match}` `in {time_formatter(_*1000)}`",
        reply_to=event.reply_to_msg_id or event,
    )
    await msg.try_delete()


"""


@ultroid_cmd(
    pattern="ul( (.*)|$)",
)
async def download(event):
    if event.text[1:].startswith("ultroid"):
        return
    xx = await event.eor(get_string("com_1"))
    hmm = event.pattern_match.group(1).strip()
    try:
        kk = hmm.split(" | stream")[0]
    except BaseException:
        pass
    try:
        title = kk.split("/")[-1]
    except BaseException:
        title = hmm
    s = dt.now()
    tt = time.time()
    ko = kk
    if not kk:
        return await xx.eor(get_string("udl_3"), time=5)
    if kk == ".env" or ".session" in kk:
        return await eod(xx, get_string("udl_7"), time=5)
    if not os.path.exists(kk):
        try:
            await event.client.send_file(
                event.chat_id, file=kk, reply_to=event.reply_to_msg_id
            )
            await xx.try_delete()
            return
        except Exception as er:
            LOGS.exception(er)
            return await xx.eor("File doesn't exists or path is incorrect!", time=5)
    if os.path.isdir(kk):
        if not os.listdir(kk):
            return await xx.eor(get_string("udl_6"), time=5)
        ok = glob.glob(f"{kk}/*")
        kk = [*sorted(ok)]
        for kk in kk:
            tt = time.time()
            try:
                try:
                    res = await uploader(kk, kk, tt, xx, f"Uploading {kk}...")
                except MessageNotModifiedError as err:
                    return await xx.edit(str(err))
                title = kk.split("/")[-1]
                if " | stream" in hmm:
                    data = await metadata(res.name)
                    wi = data["width"]
                    hi = data["height"]
                    duration = data["duration"]
                    artist = data["performer"]
                    if res.name.endswith((".mkv", ".mp4", ".avi", "webm")):
                        attributes = [
                            DocumentAttributeVideo(
                                w=wi, h=hi, duration=duration, supports_streaming=True
                            )
                        ]
                    elif res.name.endswith((".mp3", ".m4a", ".opus", ".ogg", ".flac")):
                        attributes = [
                            DocumentAttributeAudio(
                                duration=duration,
                                title=".".join(title.split(".")[:-1]),
                                performer=artist,
                            )
                        ]

                    else:
                        attributes = []
                    try:
                        await event.client.send_file(
                            event.chat_id,
                            res,
                            caption=f"`{title}`",
                            reply_to=event.reply_to_msg_id,
                            attributes=attributes,
                            supports_streaming=True,
                            thumb="resources/extras/ultroid.jpg",
                        )
                    except BaseException as er:
                        LOGS.exception(er)
                        await event.client.send_file(
                            event.chat_id,
                            res,
                            caption=f"`{title}`",
                            reply_to=event.reply_to_msg_id,
                            thumb="resources/extras/ultroid.jpg",
                        )
                else:
                    await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=f"`{title}`",
                        reply_to=event.reply_to_msg_id,
                        force_document=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
            except Exception as ve:
                return await xx.eor(str(ve))
    else:
        try:
            try:
                res = await uploader(kk, kk, tt, xx, f"Uploading {kk}...")
            except MessageNotModifiedError as err:
                return await xx.edit(str(err))
            if title.endswith((".mp3", ".m4a", ".opus", ".ogg", ".flac")):
                hmm = " | stream"
            if " | stream" in hmm:
                data = await metadata(res.name)
                wi = data["width"]
                hi = data["height"]
                duration = data["duration"]
                artist = data["performer"]
                if res.name.endswith((".mkv", ".mp4", ".avi", "webm")):
                    attributes = [
                        DocumentAttributeVideo(
                            w=wi, h=hi, duration=duration, supports_streaming=True
                        )
                    ]
                elif res.name.endswith((".mp3", ".m4a", ".opus", ".ogg", ".flac")):
                    attributes = [
                        DocumentAttributeAudio(
                            duration=duration,
                            title=title.split(".")[0],
                            performer=artist,
                        )
                    ]
                else:
                    attributes = None
                try:
                    await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=f"`{title}`",
                        attributes=attributes,
                        reply_to=event.reply_to_msg_id,
                        supports_streaming=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
                except BaseException as er:
                    LOGS.exception(er)
                    await event.client.send_file(
                        event.chat_id,
                        res,
                        caption=f"`{title}`",
                        reply_to=event.reply_to_msg_id,
                        force_document=True,
                        thumb="resources/extras/ultroid.jpg",
                    )
            else:
                await event.client.send_file(
                    event.chat_id,
                    res,
                    caption=f"`{title}`",
                    reply_to=event.reply_to_msg_id,
                    force_document=True,
                    thumb="resources/extras/ultroid.jpg",
                )
        except Exception as ve:
            return await xx.eor(str(ve))
    e = dt.now()
    t = time_formatter(((e - s).seconds) * 1000)
    if os.path.isdir(ko):
        size = 0
        for path, dirs, files in os.walk(ko):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
        c = len(os.listdir(ko))
        await xx.delete()
        await event.client.send_message(
            event.chat_id,
            f"Uploaded `{ko}` Folder, Total - `{c}` files of `{humanbytes(size)}` in `{t}`",
        )
    else:
        await xx.eor(f"Uploaded `{ko}` in `{t}`")
"""
