# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}bash <cmds>`
    Run linux commands on telegram.

• `{i}eval <code>`
    Evaluate python commands on telegram.
    Shortcuts:
        client = bot = event.client
        e = event
        p = print
        reply = await event.get_reply_message()
        chat = event.chat_id

• `{i}cpp <code>`
    Run c++ code from Telegram.

• `{i}sysinfo`
    Shows System Info.
"""

import sys
import traceback
from io import BytesIO, StringIO
from os import remove
from pprint import pprint

from telethon.utils import get_display_name

# Used for Formatting Eval Code, if installed
try:
    import black
except ImportError:
    black = None

from . import *


@ultroid_cmd(
    pattern="sysinfo$",
)
async def _(e):
    xx = await e.eor(get_string("com_1"))
    x, y = await bash("neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g' >> neo.txt")
    with open("neo.txt", "r") as neo:
        p = (neo.read()).replace("\n\n", "")
    haa = await Carbon(code=p, file_name="neofetch")
    await e.reply(file=haa)
    await xx.delete()
    remove("neo.txt")


@ultroid_cmd(pattern="bash", fullsudo=True, only_devs=True)
async def _(event):
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await event.eor(get_string("devs_1"), time=10)
    xx = await event.eor(get_string("com_1"))
    reply_to_id = event.reply_to_msg_id or event.id
    stdout, stderr = await bash(cmd)
    OUT = f"**☞ BASH\n\n• COMMAND:**\n`{cmd}` \n\n"
    if stderr:
        OUT += f"**• ERROR:** \n`{stderr}`\n\n"
    if stdout:
        _o = stdout.split("\n")
        o = "\n".join(_o)
        OUT += f"**• OUTPUT:**\n`{o}`"
    if not stderr and not stdout:
        OUT += "**• OUTPUT:**\n`Success`"
    if len(OUT) > 4096:
        ultd = OUT.replace("`", "").replace("**", "").replace("__", "")
        with BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb="resources/extras/ultroid.jpg",
                allow_cache=False,
                caption=f"`{cmd}`" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )

            await xx.delete()
    else:
        await xx.edit(OUT)


pp = pprint  # ignore: pylint
bot = ultroid = ultroid_bot

_ignore_eval = []


def _parse_eval(value):
    if value is None:
        return
    if hasattr(value, "stringify"):
        try:
            return value.stringify()
        except TypeError:
            pass
    elif isinstance(value, dict):
        try:
            return json_parser(value, indent=1)
        except BaseException:
            pass
    # is to_dict is also Good option to format?
    return str(value)


@ultroid_cmd(pattern="eval", fullsudo=True, only_devs=True)
async def _(event):
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await event.eor(get_string("devs_2"), time=5)
    silent = False
    if cmd.split()[0] in ["-s", "--silent"]:
        try:
            cmd = cmd.split(maxsplit=1)[1]
        except IndexError:
            return await event.eor("->> Wrong Format <<-")
        await event.delete()
        silent = True
    elif cmd.split()[0] in ["-n", "-noedit"]:
        try:
            cmd = cmd.split(maxsplit=1)[1]
        except IndexError:
            return await event.eor("->> Wrong Format <<-")
        xx = await event.reply(get_string("com_1"))
    else:
        xx = await event.eor(get_string("com_1"))
    if black:
        try:
            cmd = black.format_str(cmd, mode=black.Mode())
        except BaseException:
            # Consider it as Code Error, and move on to be shown ahead.
            pass
    reply_to_id = event.reply_to_msg_id or event.id
    if any(item in cmd for item in KEEP_SAFE().All) and (
        not (event.out or event.sender_id == ultroid_bot.uid)
    ):
        if event.sender_id in _ignore_eval:
            return await xx.edit(
                "`You cannot use this command now. Contact owner of this bot!`"
            )
        warning = await event.forward_to(udB.get_key("LOG_CHANNEL"))
        await warning.reply(
            f"Malicious Activities suspected by {inline_mention(await event.get_sender())}"
        )
        _ignore_eval.append(event.sender_id)
        return await xx.edit(
            "`Malicious Activities suspected⚠️!\nReported to owner. Aborted this request!`"
        )
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        value = await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = exc or stderr or stdout or _parse_eval(value) or get_string("instu_4")
    if silent:
        if exc:
            msg = f"• <b>EVAL ERROR\n\n• CHAT:</b> <code>{get_display_name(event.chat)}</code> [<code>{event.chat_id}</code>]"
            msg += f"\n\n∆ <b>CODE:</b>\n<code>{cmd}</code>\n\n∆ <b>ERROR:</b>\n<code>{exc}</code>"
            log_chat = udB.get_key("LOG_CHANNEL")
            if len(msg) > 4000:
                with BytesIO(msg.encode()) as out_file:
                    out_file.name = "Eval-Error.txt"
                return await event.client.send_message(
                    log_chat, f"`{cmd}`", file=out_file
                )
            await event.client.send_message(log_chat, msg, parse_mode="html")
        return
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            cmd,
            evaluation,
        )
    )
    if len(final_output) > 4096:
        ultd = final_output.replace("`", "").replace("**", "").replace("__", "")
        with BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "eval.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb="resources/extras/ultroid.jpg",
                allow_cache=False,
                caption=f"```{cmd}```" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )
        return await xx.delete()
    await xx.edit(final_output)


def _stringified(text, *args, **kwargs):
    text = _parse_eval(text)
    print(text, *args, **kwargs)


async def aexec(code, event):
    exec(
        (
            (
                ("async def __aexec(e, client): " + "\n message = event = e")
                + "\n reply = await event.get_reply_message()"
            )
            + "\n chat = event.chat_id"
            + "\n print = p = _stringified"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )

    return await locals()["__aexec"](event, event.client)


DUMMY_CPP = """#include <iostream>
using namespace std;

int main(){
!code
}
"""


@ultroid_cmd(pattern="cpp", only_devs=True)
async def doie(e):
    match = e.text.split(" ", maxsplit=1)
    try:
        match = match[1]
    except IndexError:
        return await e.eor(get_string("devs_3"))
    msg = await e.eor(get_string("com_1"))
    if "main(" not in match:
        new_m = "".join(" " * 4 + i + "\n" for i in match.split("\n"))
        match = DUMMY_CPP.replace("!code", new_m)
    open("cpp-ultroid.cpp", "w").write(match)
    m = await bash("g++ -o CppUltroid cpp-ultroid.cpp")
    o_cpp = f"• **Eval-Cpp**\n`{match}`"
    if m[1] != "":
        o_cpp += f"\n\n**• Error :**\n`{m[1]}`"
        if len(o_cpp) > 3000:
            os.remove("cpp-ultroid.cpp")
            if os.path.exists("CppUltroid"):
                os.remove("CppUltroid")
            with BytesIO(str.encode(o_cpp)) as out_file:
                out_file.name = "error.txt"
                return await msg.reply(f"`{match}`", file=out_file)
        return await eor(msg, o_cpp)
    m = await bash("./CppUltroid")
    if m[0] != "":
        o_cpp += f"\n\n**• Output :**\n`{m[0]}`"
    if m[1] != "":
        o_cpp += f"\n\n**• Error :**\n`{m[1]}`"
    if len(o_cpp) > 3000:
        with BytesIO(str.encode(o_cpp)) as out_file:
            out_file.name = "eval.txt"
            await msg.reply(f"`{match}`", file=out_file)
    else:
        await eor(msg, o_cpp)
    os.remove("CppUltroid")
    os.remove("cpp-ultroid.cpp")
