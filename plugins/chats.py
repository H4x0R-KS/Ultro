# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}delchat <optional- username/id>`
    Delete the group this cmd is used in.

• `{i}getlink`
    Get link of group this cmd is used in.

• `{i}create (g|b|c) <group_name> ; <optional-username>`
    Create group woth a specific name.
    g - megagroup/supergroup
    b - small group
    c - channel

• `{i}setgpic <reply to Photo><chat username>`
    Set Profile photo of Group.

• `{i}delgpic <chat username -optional>`
    Delete Profile photo of Group.

• `{i}unbanall`
    Unban all Members of a group.

• `{i}rmusers`
    Remove users specifically.
"""

from telethon.errors import ChatAdminRequiredError as no_admin
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    DeleteChannelRequest,
    EditPhotoRequest,
    GetFullChannelRequest,
    UpdateUsernameRequest,
)
from telethon.tl.functions.messages import (
    CreateChatRequest,
    ExportChatInviteRequest,
    GetFullChatRequest,
)
from telethon.tl.types import (
    ChannelParticipantsKicked,
    User,
    UserStatusEmpty,
    UserStatusLastMonth,
    UserStatusLastWeek,
    UserStatusOffline,
    UserStatusOnline,
    UserStatusRecently,
)

from . import HNDLR, LOGS, asst, get_string, mediainfo, os, types, udB, ultroid_cmd


@ultroid_cmd(
    pattern="delchat",
    groups_only=True,
)
async def _(e):
    xx = await e.eor(get_string("com_1"))
    try:
        match = e.text.split(" ", maxsplit=1)[1]
        chat = await e.client.parse_id(match)
    except IndexError:
        chat = e.chat_id
    try:
        await e.client(DeleteChannelRequest(chat))
    except TypeError:
        return await xx.eor(get_string("chats_1"), time=10)
    except no_admin:
        return await xx.eor(get_string("chats_2"), time=10)
    await e.client.send_message(
        int(udB.get_key("LOG_CHANNEL")), get_string("chats_6").format(e.chat_id)
    )


@ultroid_cmd(
    pattern="getlink$",
    groups_only=True,
    manager=True,
)
async def _(e):
    reply = await e.get_reply_message()
    if reply and not isinstance(reply.sender, User):
        chat = await reply.get_sender()
    else:
        chat = await e.get_chat()
    if hasattr(chat, "username") and chat.username:
        return await e.eor(f"Username: @{chat.username}")
    if isinstance(chat, types.Chat):
        FC = await e.client(GetFullChatRequest(chat.id))
    elif isinstance(chat, types.Channel):
        FC = await e.client(GetFullChannelRequest(chat.id))
    Inv = FC.full_chat.exported_invite
    if Inv and not Inv.revoked:
        link = Inv.link
    else:
        try:
            r = await e.client(
                ExportChatInviteRequest(e.chat_id),
            )
        except no_admin:
            return await e.eor(get_string("chats_2"), time=10)
        link = r.link
    await e.eor(f"Link:- {link}")


@ultroid_cmd(
    pattern="create (b|g|c)(?: |$)(.*)",
)
async def _(e):
    type_of_group = e.pattern_match.group(1)
    group_name = e.pattern_match.group(2)
    username = None
    if " ; " in group_name:
        group_ = group_name.split(" ; ", maxsplit=1)
        group_name = group_[0]
        username = group_[1]
    xx = await e.eor(get_string("com_1"))
    if type_of_group == "b":
        try:
            r = await e.client(
                CreateChatRequest(
                    users=[asst.me.username],
                    title=group_name,
                ),
            )
            created_chat_id = r.chats[0].id
            result = await e.client(
                ExportChatInviteRequest(
                    peer=created_chat_id,
                ),
            )
            await xx.edit(
                get_string("chats_4").format(group_name, result.link),
                link_preview=False,
            )
        except Exception as ex:
            await xx.edit(str(ex))
    elif type_of_group in ["g", "c"]:
        try:
            r = await e.client(
                CreateChannelRequest(
                    title=group_name,
                    about=get_string("chats_5"),
                    megagroup=type_of_group != "c",
                )
            )

            created_chat_id = r.chats[0].id
            if username:
                await e.client(UpdateUsernameRequest(created_chat_id, username))
                result = "https://t.me/" + username
            else:
                result = (
                    await e.client(
                        ExportChatInviteRequest(
                            peer=created_chat_id,
                        ),
                    )
                ).link
            await xx.edit(
                get_string("chats_6").format(f"[{group_name}]({result})"),
                link_preview=False,
            )
        except Exception as ex:
            await xx.edit(str(ex))


# ---------------------------------------------------------------- #


@ultroid_cmd(
    pattern="setgpic ?(.*)", admins_only=True, manager=True, require="change_info"
)
async def _(ult):
    if not ult.is_reply:
        return await ult.eor("`Reply to a Media..`", time=5)
    match = ult.pattern_match.group(1)
    if not ult.client._bot and match:
        try:
            chat = await ult.client.parse_id(match)
        except Exception as ok:
            return await ult.eor(str(ok))
    else:
        chat = ult.chat_id
    reply_message = await ult.get_reply_message()
    if reply_message.media:
        replfile = await reply_message.download_media()
    else:
        return await ult.eor("Reply to a Photo or Video..")
    file = await ult.client.upload_file(replfile)
    mediain = mediainfo(reply_message.media)
    try:
        if "pic" not in mediain:
            file = types.InputChatUploadedPhoto(video=file)
        await ult.client(EditPhotoRequest(chat, file))
        await ult.eor("`Group Photo has Successfully Changed !`", time=5)
    except Exception as ex:
        await ult.eor("Error occured.\n`{}`".format(str(ex)), time=5)
    os.remove(replfile)


@ultroid_cmd(
    pattern="delgpic ?(.*)", admins_only=True, manager=True, require="change_info"
)
async def _(ult):
    match = ult.pattern_match.group(1)
    chat = ult.chat_id
    if not ult.client._bot and match:
        chat = match
    try:
        await ult.client(EditPhotoRequest(chat, types.InputChatPhotoEmpty()))
        text = "`Removed Chat Photo..`"
    except Exception as E:
        text = str(E)
    return await ult.eor(text, time=5)


@ultroid_cmd(pattern="unbanall$", manager=True, admins_only=True, require="ban_users")
async def _(event):
    xx = await event.eor("Searching Participant Lists.")
    p = 0
    title = (await event.get_chat()).title
    async for i in event.client.iter_participants(
        event.chat_id,
        filter=ChannelParticipantsKicked,
        aggressive=True,
    ):
        try:
            await event.client.edit_permissions(event.chat_id, i, view_messages=True)
            p += 1
        except no_admin:
            pass
        except BaseException as er:
            LOGS.exception(er)
    await xx.eor(f"{title}: {p} unbanned", time=5)


@ultroid_cmd(
    pattern="rmusers ?(.*)",
    groups_only=True,
    admins_only=True,
    fullsudo=True,
)
async def _(event):
    xx = await event.eor(get_string("com_1"))
    input_str = event.pattern_match.group(1)
    p, a, b, c, d, m, n, y, w, o, q, r = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    async for i in event.client.iter_participants(event.chat_id):
        p += 1  # Total Count
        if isinstance(i.status, UserStatusEmpty):
            if "empty" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                y += 1
        if isinstance(i.status, UserStatusLastMonth):
            if "month" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                m += 1
        if isinstance(i.status, UserStatusLastWeek):
            if "week" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                w += 1
        if isinstance(i.status, UserStatusOffline):
            if "offline" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                o += 1
        if isinstance(i.status, UserStatusOnline):
            if "online" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                q += 1
        if isinstance(i.status, UserStatusRecently):
            if "recently" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                r += 1
        if i.bot:
            if "bot" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                b += 1
        elif i.deleted:
            if "deleted" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                d += 1
        elif i.status is None:
            if "none" in input_str:
                try:
                    await event.client.kick_participant(event.chat_id, i)
                    c += 1
                except BaseException:
                    pass
            else:
                n += 1
    if input_str:
        required_string = f"**>> Kicked** `{c} / {p}` **users**\n\n"
    else:
        required_string = f"**>> Total** `{p}` **users**\n\n"
    required_string += f"  `{HNDLR}rmusers deleted`  **••**  `{d}`\n"
    required_string += f"  `{HNDLR}rmusers empty`  **••**  `{y}`\n"
    required_string += f"  `{HNDLR}rmusers month`  **••**  `{m}`\n"
    required_string += f"  `{HNDLR}rmusers week`  **••**  `{w}`\n"
    required_string += f"  `{HNDLR}rmusers offline`  **••**  `{o}`\n"
    required_string += f"  `{HNDLR}rmusers online`  **••**  `{q}`\n"
    required_string += f"  `{HNDLR}rmusers recently`  **••**  `{r}`\n"
    required_string += f"  `{HNDLR}rmusers bot`  **••**  `{b}`\n"
    required_string += f"  `{HNDLR}rmusers none`  **••**  `{n}`"
    await xx.eor(required_string)
