# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}destroy <reply to animated sticker>`
    To destroy the sticker.

• `{i}tiny <reply to media>`
    To create Tiny stickers.

• `{i}convert <gif/img/sticker>`
    Reply to animated sticker to convert it into gif or image or normal sticker.

• `{i}kang <reply to image/sticker>`
    Kang the sticker (add to your pack).

• `{i}packkang <pack name>`
    Kang the Complete sticker set (with custom name).

• `{i}round <reply to any media>`
    To extract round sticker.
"""
import io
import os
import random
from os import remove

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw
from pyUltroid.functions.misc import create_quotly
from telethon.errors import PeerIdInvalidError, YouBlockedUserError
from telethon.tl.types import DocumentAttributeFilename, DocumentAttributeSticker
from telethon.utils import get_input_document

from . import (
    KANGING_STR,
    LOGS,
    asst,
    bash,
    functions,
    get_string,
    inline_mention,
    mediainfo,
    resize_photo,
    types,
    udB,
    ultroid_cmd,
)


@ultroid_cmd(
    pattern="convert ?(.*)",
)
async def uconverter(event):
    xx = await event.eor(get_string("com_1"))
    a = await event.get_reply_message()
    if not (a and a.media and "animated" in mediainfo(a.media)):
        return await event.eor(get_string("sts_2"))
    input_ = event.pattern_match.group(1)
    b = await a.download_media("resources/downloads/")
    if "gif" in input_:
        file = "something.gif"
    elif "img" in input_:
        file = "something.png"
    elif "sticker" in input_:
        file = "something.webp"
    else:
        return await xx.edit(get_string("sts_3").format("gif/img/sticker"))
    await bash(f"lottie_convert.py '{b}' {file}")
    await event.client.send_file(event.chat_id, file, force_document=False)
    await xx.delete()
    os.remove(file)
    os.remove(b)


@ultroid_cmd(pattern="packkang")
async def pack_kangish(_):
    _e = await _.get_reply_message()
    if not (_e and _e.sticker and _e.file.mime_type == "image/webp"):
        return await _.eor(get_string("sts_4"))
    if len(_.text) > 9:
        _packname = _.text.split(" ", maxsplit=1)[1]
    else:
        _packname = f"Ultroid Kang Pack By {_.sender_id}"
    _id = _e.media.document.attributes[1].stickerset.id
    _hash = _e.media.document.attributes[1].stickerset.access_hash
    _get_stiks = await _.client(
        functions.messages.GetStickerSetRequest(
            stickerset=types.InputStickerSetID(id=_id, access_hash=_hash), hash=0
        )
    )
    stiks = []
    for i in _get_stiks.documents:
        x = get_input_document(i)
        stiks.append(
            types.InputStickerSetItem(
                document=x,
                emoji=(i.attributes[1]).alt,
            )
        )
    try:
        short_name = "ult_" + _packname.replace(" ", "_") + str(_.id)
        _r_e_s = await asst(
            functions.stickers.CreateStickerSetRequest(
                user_id=_.sender_id,
                title=_packname,
                short_name=f"{short_name}_by_{asst.me.username}",
                stickers=stiks,
            )
        )
    except PeerIdInvalidError:
        return await _.eor(
            f"Hey {inline_mention(_.sender)} send `/start` to @{asst.me.username} and later try this command again.."
        )
    except BaseException as er:
        LOGS.exception(er)
        return await _.eor(str(er))
    await _.eor(
        get_string("sts_5").format(f"https://t.me/addstickers/{_r_e_s.set.short_name}"),
    )


@ultroid_cmd(
    pattern="kang",
)
async def hehe(args):
    ultroid_bot = args.client
    xx = await args.eor(get_string("com_1"))
    user = ultroid_bot.me
    if not user.username:
        user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    is_anim = False
    emoji = None
    if not message:
        return await xx.eor(get_string("sts_6"))
    if message.photo:
        photo = io.BytesIO()
        photo = await ultroid_bot.download_media(message.photo, photo)
    elif message.file and "image" in message.file.mime_type.split("/"):
        photo = io.BytesIO()
        await ultroid_bot.download_file(message.media.document, photo)
        if (
            DocumentAttributeFilename(file_name="sticker.webp")
            in message.media.document.attributes
        ):
            emoji = message.media.document.attributes[1].alt

    elif message.file and "video" in message.file.mime_type.split("/"):
        xy = await message.download_media()
        y = cv2.VideoCapture(xy)
        heh, lol = y.read()
        cv2.imwrite("ult.webp", lol)
        photo = "ult.webp"
    elif message.file and "tgsticker" in message.file.mime_type:
        await ultroid_bot.download_file(
            message.media.document,
            "AnimatedSticker.tgs",
        )
        attributes = message.media.document.attributes
        for attribute in attributes:
            if isinstance(attribute, DocumentAttributeSticker):
                emoji = attribute.alt
        is_anim = True
        photo = 1
    elif message.message:
        photo = await create_quotly(message)
    else:
        return await xx.edit(get_string("com_4"))
    if not udB.get_key("language") or udB.get_key("language") == "en":
        ra = random.choice(KANGING_STR)
    else:
        ra = get_string("sts_11")
    await xx.edit(f"`{ra}`")
    if photo:
        splat = args.text.split()
        pack = 1
        if not emoji:
            emoji = "🏵"
        if len(splat) == 3:
            pack = splat[2]  # User sent ultroid_both
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                pack = int(splat[1])
            else:
                emoji = splat[1]

        packname = f"ult_{user.id}_{pack}"
        packnick = f"@{user.username}'s Pack {pack}"
        cmd = "/newpack"
        file = io.BytesIO()

        if not is_anim:
            image = resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"

        response = requests.get(f"http://t.me/addstickers/{packname}")
        htmlstr = response.text.split("\n")

        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with ultroid_bot.conversation("@Stickers") as conv:
                try:
                    await conv.send_message("/addsticker")
                except YouBlockedUserError:
                    LOGS.info("Unblocking @Stickers for kang...")
                    await ultroid_bot(functions.contacts.UnblockRequest("stickers"))
                    await conv.send_message("/addsticker")
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                t = "50" if is_anim else "120"
                while t in x.text:
                    pack += 1
                    packname = f"ult_{user.id}_{pack}"
                    if is_anim:
                        packname += "_anim"
                    packnick = f"@{user.username}'s Pack {pack}"
                    await xx.edit(get_string("sts_13").format(pack))
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file("AnimatedSticker.tgs")
                            remove("AnimatedSticker.tgs")
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await ultroid_bot.send_read_acknowledge(conv.chat_id)
                        await xx.edit(
                            get_string("sts_7").format(packname),
                            parse_mode="md",
                        )
                        return
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await xx.edit(
                        get_string("sts_8"),
                    )
                    return
                await conv.send_message(emoji)
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/done")
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
        else:
            await xx.edit("`Brewing a new Pack...`")
            async with ultroid_bot.conversation("Stickers") as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await xx.edit(
                        get_string("sts_8"),
                    )
                    return
                await conv.send_message(emoji)
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")

                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await ultroid_bot.send_read_acknowledge(conv.chat_id)
        await xx.edit(
            get_string("sts_12").format(emoji, packname),
            parse_mode="md",
        )
        try:
            os.remove(photo)
        except BaseException:
            pass


@ultroid_cmd(
    pattern="round$",
)
async def ultdround(event):
    ureply = await event.get_reply_message()
    xx = await event.eor(get_string("com_1"))
    if not (ureply and (ureply.media)):
        await xx.edit(get_string("sts_10"))
        return
    ultt = await ureply.download_media()
    if ultt.endswith(".tgs"):
        await xx.edit(get_string("sts_9"))
        file = "ult.png"
        await bash(f"lottie_convert.py '{ultt}' {file}")
    elif ultt.endswith((".gif", ".mp4", ".mkv")):
        await xx.edit(get_string("com_1"))
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite("ult.png", lol)
        file = "ult.png"
    else:
        file = ultt
    img = Image.open(file).convert("RGB")
    npImage = np.array(img)
    h, w = img.size
    alpha = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0, 0, h, w], 0, 360, fill=255)
    npAlpha = np.array(alpha)
    npImage = np.dstack((npImage, npAlpha))
    Image.fromarray(npImage).save("ult.webp")
    await event.client.send_file(
        event.chat_id,
        "ult.webp",
        force_document=False,
        reply_to=event.reply_to_msg_id,
    )
    await xx.delete()
    os.remove(file)
    os.remove("ult.webp")


@ultroid_cmd(
    pattern="destroy$",
)
async def ultdestroy(event):
    ult = await event.get_reply_message()
    if not (ult and ult.media and "animated" in mediainfo(ult.media)):
        return await event.eor(get_string("sts_2"))
    await event.client.download_media(ult, "ultroid.tgs")
    xx = await event.eor(get_string("com_1"))
    await bash("lottie_convert.py ultroid.tgs json.json")
    with open("json.json") as json:
        jsn = json.read()
    jsn = (
        jsn.replace("[100]", "[200]")
        .replace("[10]", "[40]")
        .replace("[-1]", "[-10]")
        .replace("[0]", "[15]")
        .replace("[1]", "[20]")
        .replace("[2]", "[17]")
        .replace("[3]", "[40]")
        .replace("[4]", "[37]")
        .replace("[5]", "[60]")
        .replace("[6]", "[70]")
        .replace("[7]", "[40]")
        .replace("[8]", "[37]")
        .replace("[9]", "[110]")
    )
    open("json.json", "w").write(jsn)
    await bash("lottie_convert.py json.json ultroid.tgs")
    await event.client.send_file(
        event.chat_id,
        file="ultroid.tgs",
        force_document=False,
        reply_to=event.reply_to_msg_id,
    )
    await xx.delete()
    os.remove("json.json")


@ultroid_cmd(
    pattern="tiny$",
)
async def ultiny(event):
    reply = await event.get_reply_message()
    if not (reply and (reply.media)):
        await event.eor(get_string("sts_10"))
        return
    xx = await event.eor(get_string("com_1"))
    ik = await event.client.download_media(reply)
    im1 = Image.open("resources/extras/ultroid_blank.png")
    if ik.endswith(".tgs"):
        await event.client.download_media(reply, "ult.tgs")
        await bash("lottie_convert.py ult.tgs json.json")
        with open("json.json") as json:
            jsn = json.read()
        jsn = jsn.replace("512", "2000")
        open("json.json", "w").write(jsn)
        await bash("lottie_convert.py json.json ult.tgs")
        file = "ult.tgs"
        os.remove("json.json")
    elif ik.endswith((".gif", ".mp4")):
        iik = cv2.VideoCapture(ik)
        dani, busy = iik.read()
        cv2.imwrite("i.png", busy)
        fil = "i.png"
        im = Image.open(fil)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove(fil)
        os.remove("k.png")
    else:
        im = Image.open(ik)
        z, d = im.size
        if z == d:
            xxx, yyy = 200, 200
        else:
            t = z + d
            a = z / t
            b = d / t
            aa = (a * 100) - 50
            bb = (b * 100) - 50
            xxx = 200 + 5 * aa
            yyy = 200 + 5 * bb
        k = im.resize((int(xxx), int(yyy)))
        k.save("k.png", format="PNG", optimize=True)
        im2 = Image.open("k.png")
        back_im = im1.copy()
        back_im.paste(im2, (150, 0))
        back_im.save("o.webp", "WEBP", quality=95)
        file = "o.webp"
        os.remove("k.png")
    await event.client.send_file(event.chat_id, file, reply_to=event.reply_to_msg_id)
    await xx.delete()
    os.remove(file)
    os.remove(ik)
