# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}meaning <word>`
    Get the meaning of the word.

• `{i}synonym <word>`
    Get all synonyms.

• `{i}antonym <word>`
    Get all antonyms.

• `{i}ud <word>`
    Fetch word defenition from urbandictionary.
"""
import io

from pyUltroid.functions.misc import get_synonyms_or_antonyms
from pyUltroid.functions.tools import async_searcher

from . import get_string, ultroid_cmd


@ultroid_cmd(pattern="meaning( (.*)|$)", manager=True)
async def mean(event):
    wrd = event.pattern_match.group(1).strip()
    if not wrd:
        return await event.eor(get_string("wrd_4"))
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + wrd
    out = await async_searcher(url, re_json=True)
    try:
        return await event.eor(f'**{out["title"]}**')
    except (KeyError, TypeError):
        pass
    defi = out[0]["meanings"][0]["definitions"][0]
    ex = "None" if not defi.get("example") else defi["example"]
    text = get_string("wrd_1").format(wrd, defi["definition"], ex)
    if defi["synonyms"]:
        text += (
            f"\n\n• **{get_string('wrd_5')} :**"
            + "".join(f" {a}," for a in defi["synonyms"])[:-1][:10]
        )
    if defi["antonyms"]:
        text += (
            f"\n\n**{get_string('wrd_6')} :**"
            + "".join(f" {a}," for a in defi["antonyms"])[:-1][:10]
        )
    if len(text) > 4096:
        with io.BytesIO(str.encode(text)) as fle:
            fle.name = f"{wrd}-meanings.txt"
            await event.reply(
                file=fle,
                force_document=True,
                caption=f"Meanings of {wrd}",
            )
            await event.delete()
    else:
        await event.eor(text)


@ultroid_cmd(
    pattern="synonym",
)
async def mean(event):
    wrd = event.text.split(" ", maxsplit=1)[1]
    ok = await get_synonyms_or_antonyms(wrd, "synonyms")
    x = get_string("wrd_2").format(wrd)
    try:
        for c, i in enumerate(ok, start=1):
            x += f"**{c}.** `{i}`\n"
        if len(x) > 4096:
            with io.BytesIO(str.encode(x)) as fle:
                fle.name = f"{wrd}-synonyms.txt"
                await event.client.send_file(
                    event.chat_id,
                    fle,
                    force_document=True,
                    allow_cache=False,
                    caption=f"Synonyms of {wrd}",
                    reply_to=event.reply_to_msg_id,
                )
                await event.delete()
        else:
            await event.eor(x)
    except Exception as e:
        await event.eor(get_string("wrd_7").format(e))


@ultroid_cmd(
    pattern="antonym",
)
async def mean(event):
    evid = event.message.id
    wrd = event.text.split(" ", maxsplit=1)[1]
    ok = await get_synonyms_or_antonyms(wrd, "antonyms")
    x = get_string("wrd_3").format(wrd)
    c = 1
    try:
        for c, i in enumerate(ok, start=1):
            x += f"**{c}.** `{i}`\n"
        if len(x) > 4096:
            with io.BytesIO(str.encode(x)) as fle:
                fle.name = f"{wrd}-antonyms.txt"
                await event.client.send_file(
                    event.chat_id,
                    fle,
                    force_document=True,
                    allow_cache=False,
                    caption=f"Antonyms of {wrd}",
                    reply_to=evid,
                )
                await event.delete()
        else:
            await event.eor(x)
    except Exception as e:
        await event.eor(get_string("wrd_8").format(e))


@ultroid_cmd(pattern="ud (.*)")
async def _(event):
    word = event.pattern_match.group(1).strip()
    if not word:
        return await event.eor(get_string("autopic_1"))
    out = await async_searcher(
        "http://api.urbandictionary.com/v0/define", params={"term": word}, re_json=True
    )
    try:
        out = out["list"][0]
    except IndexError:
        return await event.eor(get_string("autopic_2").format(word))
    await event.eor(
        get_string("wrd_1").format(out["word"], out["definition"], out["example"]),
    )
