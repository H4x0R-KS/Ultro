# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}setname <first name // last name>`
    Change your profile name.

• `{i}setbio <bio>`
    Change your profile bio.

• `{i}setpic <reply to pic>`
    Change your profile pic.

• `{i}delpfp <n>(optional)`
    Delete one profile pic, if no value given, else delete n number of pics.

• `{i}poto <username>`
    Upload the photo of Chat/User if Available.
"""
import os

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest

from . import eod, eor, get_string, mediainfo, ultroid_cmd

TMP_DOWNLOAD_DIRECTORY = "resources/downloads/"

# bio changer


@ultroid_cmd(pattern="setbio ?(.*)", fullsudo=True)
async def _(ult):
    ok = await ult.eor("...")
    set = ult.pattern_match.group(1)
    try:
        await ult.client(UpdateProfileRequest(about=set))
        await eod(ok, f"Profile bio changed to\n`{set}`")
    except Exception as ex:
        await eod(ok, "Error occured.\n`{}`".format(str(ex)))


# name changer


@ultroid_cmd(pattern="setname ?((.|//)*)", fullsudo=True)
async def _(ult):
    ok = await ult.eor("...")
    names = ult.pattern_match.group(1)
    first_name = names
    last_name = ""
    if "//" in names:
        first_name, last_name = names.split("//", 1)
    try:
        await ult.client(
            UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name,
            ),
        )
        await eod(ok, f"Name changed to `{names}`")
    except Exception as ex:
        await eod(ok, "Error occured.\n`{}`".format(str(ex)))


# profile pic


@ultroid_cmd(pattern="setpic$", fullsudo=True)
async def _(ult):
    if not ult.is_reply:
        return await ult.eor("`Reply to a Media..`", time=5)
    reply_message = await ult.get_reply_message()
    ok = await ult.eor(get_string("com_1"))
    replfile = await reply_message.download_media()
    file = await ult.client.upload_file(replfile)
    try:
        if "pic" in mediainfo(reply_message.media):
            await ult.client(UploadProfilePhotoRequest(file))
        else:
            await ult.client(UploadProfilePhotoRequest(video=file))
        await eod(ok, "`My Profile Photo has Successfully Changed !`")
    except Exception as ex:
        await eod(ok, "Error occured.\n`{}`".format(str(ex)))
    os.remove(replfile)


# delete profile pic(s)


@ultroid_cmd(pattern="delpfp ?(.*)", fullsudo=True)
async def remove_profilepic(delpfp):
    ok = await eor(delpfp, "`...`")
    group = delpfp.text[8:]
    if group == "all":
        lim = 0
    elif group.isdigit():
        lim = int(group)
    else:
        lim = 1
    pfplist = await delpfp.client.get_profile_photos("me", limit=lim)
    await delpfp.client(DeletePhotosRequest(pfplist))
    await eod(ok, f"`Successfully deleted {len(pfplist)} profile picture(s).`")


@ultroid_cmd(pattern="poto ?(.*)")
async def gpoto(e):
    ult = e.pattern_match.group(1)
    a = await e.eor(get_string("com_1"))
    if not ult:
        if e.is_reply:
            gs = await e.get_reply_message()
            ult = gs.sender_id
        else:
            ult = e.chat_id
    okla = await e.client.download_profile_photo(ult)
    if not okla:
        return await eor(a, "`Pfp Not Found...`")
    await a.delete()
    await e.reply(file=okla)
    os.remove(okla)
