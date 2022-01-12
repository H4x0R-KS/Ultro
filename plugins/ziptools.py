# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

• `{i}zip <reply to file>`
    zip the replied file
    To set password on zip: `{i}zip <password>` reply to file

• `{i}unzip <reply to zip file>`
    unzip the replied file.

• `{i}azip <reply to file>`
   add file to batch for batch upload zip

• `{i}dozip`
   upload batch zip the files u added from `{i}azip`
   To set Password: `{i}dozip <password>`

"""
import os
import time

from . import (
    HNDLR,
    asyncio,
    bash,
    downloader,
    get_all_files,
    get_string,
    ultroid_cmd,
    uploader,
)


@ultroid_cmd(pattern="zip ?(.*)")
async def zipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not reply:
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                reply.file.name, reply.media.document, xx, t, get_string("com_5")
            )
            file = image.name
        else:
            file = await event.download_media(reply)
    inp = file.replace(file.split(".")[-1], "zip")
    if event.pattern_match.group(1):
        await bash(f"zip -r --password {event.pattern_match.group(1)} {inp} {file}")
    else:
        await bash(f"zip -r {inp} {file}")
    k = time.time()
    xxx = await uploader(inp, inp, k, xx, get_string("com_6"))
    await event.client.send_file(
        event.chat_id,
        xxx,
        force_document=True,
        thumb="resources/extras/ultroid.jpg",
        caption=f"`{xxx.name}`",
        reply_to=reply,
    )
    os.remove(inp)
    os.remove(file)
    await xx.delete()


@ultroid_cmd(pattern="unzip$")
async def unzipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not reply:
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if reply.media:
        if not hasattr(reply.media, "document"):
            return await xx.edit(get_string("zip_3"))
        file = reply.media.document
        if not reply.file.name.endswith(("zip", "rar", "exe")):
            return await xx.edit(get_string("zip_3"))
        image = await downloader(
            reply.file.name, reply.media.document, xx, t, get_string("com_5")
        )
        file = image.name
    if os.path.isdir("unzip"):
        await bash("rm -rf unzip")
    os.mkdir("unzip")
    await bash(f"7z x {file} -aoa -ounzip")
    await asyncio.sleep(4)
    ok = get_all_files("unzip")
    for x in ok:
        k = time.time()
        xxx = await uploader(x, x, k, xx, get_string("com_6"))
        await event.client.send_file(
            event.chat_id,
            xxx,
            force_document=True,
            thumb="resources/extras/ultroid.jpg",
            caption=f"`{xxx.name}`",
        )
    await xx.delete()


@ultroid_cmd(pattern="addzip$")
async def azipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not reply:
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if not os.path.isdir("zip"):
        os.mkdir("zip")
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                "zip/" + reply.file.name,
                reply.media.document,
                xx,
                t,
                get_string("com_5"),
            )
            file = image.name
        else:
            file = await event.download_media(reply.media, "zip/")
    await xx.edit(
        f"Downloaded `{file}` succesfully\nNow Reply To Other Files To Add And Zip all at once"
    )


@ultroid_cmd(pattern="dozip ?(.*)")
async def do_zip(event):
    if not os.path.isdir("zip"):
        return await event.eor(get_string("zip_2").format(HNDLR))
    xx = await event.eor(get_string("com_1"))
    if event.pattern_match.group(1):
        await bash(
            f"zip -r --password {event.pattern_match.group(1)} ultroid.zip zip/*"
        )
    else:
        await bash("zip -r ultroid.zip zip/*")
    k = time.time()
    xxx = await uploader("ultroid.zip", "ultroid.zip", k, xx, get_string("com_6"))
    await event.client.send_file(
        event.chat_id,
        xxx,
        force_document=True,
        thumb="resources/extras/ultroid.jpg",
    )
    await bash("rm -rf zip")
    os.remove("ultroid.zip")
    await xx.delete()
