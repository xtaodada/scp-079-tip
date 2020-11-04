# SCP-079-TIP - Here's a tip
# Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-TIP.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re
from copy import deepcopy
from string import ascii_lowercase
from typing import Match, Optional, Union

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, User

from .. import glovar
from .etc import get_filename, get_forward_name, get_full_name, get_now, get_text, t2t
from .file import save, save_regex_timeout
from .ids import init_group_id
from .telegram import get_user_full

# Enable logging
logger = logging.getLogger(__name__)


def is_aio(_, __, ___) -> bool:
    # Check if the program is under all-in-one mode
    result = False

    try:
        result = glovar.aio
    except Exception as e:
        logger.warning(f"Is aio error: {e}", exc_info=True)

    return result


def is_authorized_group(_, __, update: Union[CallbackQuery, Message]) -> bool:
    # Check if the message is send from the authorized group
    result = False

    try:
        if isinstance(update, CallbackQuery):
            message = update.message
        else:
            message = update

        if not message.chat or message.chat.type != "supergroup":
            return False

        cid = message.chat.id

        if cid > 0:
            return False

        if init_group_id(cid):
            return True
    except Exception as e:
        logger.warning(f"Is authorized group error: {e}", exc_info=True)

    return result


def is_class_c(_, __, message: Message) -> bool:
    # Check if the message is sent from Class C personnel
    result = False

    try:
        if not message.from_user:
            return False

        # Basic data
        uid = message.from_user.id
        gid = message.chat.id

        # Check permission
        if uid in glovar.admin_ids[gid] or uid in glovar.bot_ids or message.from_user.is_self:
            return True
    except Exception as e:
        logger.warning(f"Is class c error: {e}", exc_info=True)

    return result


def is_class_d(_, __, message: Message) -> bool:
    # Check if the message is Class D object
    result = False

    try:
        if not message.from_user:
            return False

        if is_class_d_user(message.from_user):
            return True
    except Exception as e:
        logger.warning(f"Is class d error: {e}", exc_info=True)

    return result


def is_class_e(_, __, message: Message, test: bool = False) -> bool:
    # Check if the message is Class E personnel
    result = False

    try:
        if not message.from_user:
            return False

        if not test and is_class_e_user(message.from_user):
            return True
    except Exception as e:
        logger.warning(f"Is class e error: {e}", exc_info=True)

    return result


def is_declared_message(_, __, message: Message) -> bool:
    # Check if the message is declared by other bots
    result = False

    try:
        if not message.chat:
            return False

        gid = message.chat.id
        mid = message.message_id
        result = is_declared_message_id(gid, mid)
    except Exception as e:
        logger.warning(f"Is declared message error: {e}", exc_info=True)

    return result


def is_exchange_channel(_, __, message: Message) -> bool:
    # Check if the message is sent from the exchange channel
    result = False

    try:
        if not message.chat:
            return False

        cid = message.chat.id

        if glovar.should_hide:
            result = cid == glovar.hide_channel_id
        else:
            result = cid == glovar.exchange_channel_id
    except Exception as e:
        logger.warning(f"Is exchange channel error: {e}", exc_info=True)

    return result


def is_from_user(_, __, update: Union[CallbackQuery, Message]) -> bool:
    # Check if the message is sent from a user, or the callback is sent from a private chat
    result = False

    try:
        if (isinstance(update, CallbackQuery)
                and (not update.message or not update.message.chat or update.message.chat.id < 0)):
            return False

        if update.from_user and update.from_user.id != 777000:
            return True
    except Exception as e:
        logger.warning(f"Is from user error: {e}", exc_info=True)

    return result


def is_hide_channel(_, __, message: Message) -> bool:
    # Check if the message is sent from the hide channel
    result = False

    try:
        if not message.chat:
            return False

        cid = message.chat.id

        if cid == glovar.hide_channel_id:
            return True
    except Exception as e:
        logger.warning(f"Is hide channel error: {e}", exc_info=True)

    return result


def is_new_group(_, __, message: Message) -> bool:
    # Check if the bot joined a new group
    result = False

    try:
        new_users = message.new_chat_members

        if new_users:
            result = any(user.is_self for user in new_users)
        elif message.group_chat_created or message.supergroup_chat_created:
            result = True
    except Exception as e:
        logger.warning(f"Is new group error: {e}", exc_info=True)

    return result


def is_test_group(_, __, update: Union[CallbackQuery, Message]) -> bool:
    # Check if the message is sent from the test group
    result = False

    try:
        if isinstance(update, CallbackQuery):
            message = update.message
        else:
            message = update

        if not message.chat or message.chat.type != "supergroup":
            return False

        cid = message.chat.id

        if cid == glovar.test_group_id:
            return True
    except Exception as e:
        logger.warning(f"Is test group error: {e}", exc_info=True)

    return result


aio = filters.create(
    func=is_aio,
    name="AIO"
)

authorized_group = filters.create(
    func=is_authorized_group,
    name="Authorized Group"
)

class_c = filters.create(
    func=is_class_c,
    name="Class C"
)

class_d = filters.create(
    func=is_class_d,
    name="Class D"
)

class_e = filters.create(
    func=is_class_e,
    name="Class E"
)

declared_message = filters.create(
    func=is_declared_message,
    name="Declared message"
)

exchange_channel = filters.create(
    func=is_exchange_channel,
    name="Exchange Channel"
)

from_user = filters.create(
    func=is_from_user,
    name="From User"
)

hide_channel = filters.create(
    func=is_hide_channel,
    name="Hide Channel"
)

new_group = filters.create(
    func=is_new_group,
    name="New Group"
)

test_group = filters.create(
    func=is_test_group,
    name="Test Group"
)


def get_words(words: set, exact: bool) -> dict:
    # Get words dict
    result = {}

    try:
        for word in words:
            if word.startswith("{{") and word.endswith("}}"):
                word = word[2:-2]

                if not word:
                    continue

                result[word] = True
            elif exact:
                result[word] = True
            else:
                result[word] = False
    except Exception as e:
        logger.warning(f"Get words error: {e}", exc_info=True)

    return result


def is_ad_text(text: str, ocr: bool, matched: str = "") -> str:
    # Check if the text is ad text
    result = ""

    try:
        if not text:
            return ""

        for c in ascii_lowercase:
            if c == matched:
                continue

            if not is_regex_text(f"ad{c}", text, ocr):
                continue

            result = c
            break
    except Exception as e:
        logger.warning(f"Is ad text error: {e}", exc_info=True)

    return result


def is_ban_text(text: str, ocr: bool, message: Message = None) -> bool:
    # Check if the text is ban text
    result = False

    try:
        if is_regex_text("ban", text, ocr):
            return True

        # ad + con
        ad = is_regex_text("ad", text, ocr)
        con = is_con_text(text, ocr)

        if ad and con:
            return True

        # emoji + con
        emoji = is_emoji("ad", text, message)

        if emoji and con:
            return True

        # ad_ + con
        ad = is_ad_text(text, ocr)

        if ad and con:
            return True

        # ad_ + emoji
        if ad and emoji:
            return True

        # ad_ + ad_
        if not ad:
            return False

        ad = is_ad_text(text, ocr, ad)
        result = bool(ad)
    except Exception as e:
        logger.warning(f"Is ban text error: {e}", exc_info=True)

    return result


def is_bio_text(text: str) -> bool:
    # Check if the text is bio text
    result = False

    try:
        if (is_regex_text("bio", text)
                or is_ban_text(text, False)):
            return True
    except Exception as e:
        logger.warning(f"Is bio text error: {e}", exc_info=True)

    return result


def is_class_d_user(user: Union[int, User]) -> bool:
    # Check if the user is a Class D personnel
    result = False

    try:
        if isinstance(user, int):
            uid = user
        else:
            uid = user.id

        if uid in glovar.bad_ids["users"]:
            return True
    except Exception as e:
        logger.warning(f"Is class d user error: {e}", exc_info=True)

    return result


def is_class_e_user(user: Union[int, User]) -> bool:
    # Check if the user is a Class E personnel
    result = False

    try:
        if isinstance(user, int):
            uid = user
        else:
            uid = user.id

        if uid in glovar.bot_ids:
            return True

        group_list = list(glovar.trust_ids)
        result = any(uid in glovar.trust_ids.get(gid, set()) for gid in group_list)
    except Exception as e:
        logger.warning(f"Is class e user error: {e}", exc_info=True)

    return result


def is_con_text(text: str, ocr: bool) -> bool:
    # Check if the text is con text
    result = False

    try:
        if (is_regex_text("con", text, ocr)
                or is_regex_text("iml", text, ocr)
                or is_regex_text("pho", text, ocr)):
            return True
    except Exception as e:
        logger.warning(f"Is con text error: {e}", exc_info=True)

    return result


def is_declared_message_id(gid: int, mid: int) -> bool:
    # Check if the message's ID is declared by other bots
    result = False

    try:
        result = mid in glovar.declared_message_ids.get(gid, set())
    except Exception as e:
        logger.warning(f"Is declared message id error: {e}", exc_info=True)

    return result


def is_emoji(the_type: str, text: str, message: Message = None) -> bool:
    # Check the emoji type
    result = False

    try:
        if message:
            text = get_text(message)

        emoji_dict = {}
        emoji_set = {emoji for emoji in glovar.emoji_set if emoji in text and emoji not in glovar.emoji_protect}
        emoji_old_set = deepcopy(emoji_set)

        for emoji in emoji_old_set:
            if any(emoji in emoji_old and emoji != emoji_old for emoji_old in emoji_old_set):
                emoji_set.discard(emoji)

        for emoji in emoji_set:
            emoji_dict[emoji] = text.count(emoji)

        # Check ad
        if the_type == "ad":
            if any(emoji_dict[emoji] >= glovar.emoji_ad_single for emoji in emoji_dict):
                return True

            if sum(emoji_dict.values()) >= glovar.emoji_ad_total:
                return True

        # Check many
        elif the_type == "many":
            if sum(emoji_dict.values()) >= glovar.emoji_many:
                return True

        # Check wb
        elif the_type == "wb":
            if any(emoji_dict[emoji] >= glovar.emoji_wb_single for emoji in emoji_dict):
                return True

            if sum(emoji_dict.values()) >= glovar.emoji_wb_total:
                return True
    except Exception as e:
        logger.warning(f"Is emoji error: {e}", exc_info=True)

    return result


def is_high_score_user(user: Union[int, User], high: bool = True) -> float:
    # Check if the message is sent by a high score user
    result = 0.0

    try:
        if is_class_e_user(user):
            return 0.0

        if isinstance(user, int):
            uid = user
        else:
            uid = user.id

        user_status = glovar.user_ids.get(uid, {})

        if not user_status:
            return 0.0

        score = sum(user_status["score"].values())

        if not high:
            return score

        if score >= 3.0:
            return score
    except Exception as e:
        logger.warning(f"Is high score user error: {e}", exc_info=True)

    return result


def is_keyword_message(message: Message) -> dict:
    # Check if the message includes keywords
    result = {}

    try:
        # Basic data
        gid = message.chat.id

        # Check config
        if not glovar.configs[gid].get("keyword", True):
            return {}

        # Check message sender:
        if message.forward_from and message.forward_from.is_self:
            return {}

        # Get the keywords
        keywords = glovar.keywords[gid].get("kws", {})

        # Check keywords
        if not keywords:
            return {}

        # Loop keywords
        for key in keywords:
            # Config data
            modes = keywords[key]["modes"]
            actions = keywords[key]["actions"]
            target = keywords[key]["target"]
            class_c_message = is_class_c(None, None, message)
            should_pass = is_should_pass(message, False)
            should_pass_terminate = is_should_pass(message, True)

            # Check target
            if target == "member" and class_c_message:
                continue
            elif target == "admin" and not class_c_message:
                continue
            elif is_terminate_actions(actions) and is_should_pass(message):
                continue

            # Get result
            if ((should_pass_terminate and "name" in modes and "forward" not in modes and not message.forward_date)
                    or (should_pass and "forward" in modes)):
                continue
            elif "name" in modes or "join" in modes:
                result = is_keyword_name(message, key)
            elif "forward" in modes:
                result = is_keyword_text(message, key, True)
            else:
                result = is_keyword_text(message, key)

            # Check result
            if result:
                return result
    except Exception as e:
        logger.warning(f"Is keyword text error: {e}", exc_info=True)

    return result


def is_keyword_name(message: Message, key: str) -> dict:
    # Check if the message's sender name includes keywords
    result = {}

    try:
        # Basic data
        gid = message.chat.id
        match = ""

        # Get keywords
        keyword = glovar.keywords[gid]["kws"].get(key, {})

        # Check the keyword
        if not keyword:
            return {}

        # Get modes
        modes = keyword["modes"]
        exact = "exact" in modes
        case = "case" in modes
        join = "join" in modes
        pure = "pure" in modes
        forward = "forward" in modes
        regex = "regex" in modes

        # Check join status
        if join and not message.new_chat_members:
            return {}

        # Get names
        user_name = get_full_name(message.from_user, True, pure, pure)
        forward_name = get_forward_name(message, True, pure, pure)

        # Check the forward name
        if forward and not forward_name:
            return {}

        # Get words
        words = get_words(keyword["words"], exact)

        # Get name list
        if forward:
            names = [forward_name]
        else:
            names = [user_name, forward_name]

        # Get match result
        for name in names:
            if not name:
                continue

            for word in words:
                match = is_keyword_string(word, name, words[word], case, regex)

                if match:
                    break

            if match:
                break

        # Check the match
        if not match:
            return {}

        result = {
            "key": key,
            "mid": None,
            "word": match,
            "reply": keyword["reply"],
            "actions": keyword["actions"],
            "destruct": keyword["destruct"],
            "forward": forward,
            "name": True
        }
    except Exception as e:
        logger.warning(f"Is keyword name error: {e}", exc_info=True)

    return result


def is_keyword_string(word: str, text: str, exact: bool, case: bool, regex: bool) -> str:
    # Check if the keyword match the string
    result = ""

    try:
        if not text or not text.strip():
            return ""

        text = text.strip()
        origin = word

        if regex:
            return ""

        if not case:
            word = word.lower()
            text = text.lower()

        if exact and word == text:
            return origin
        elif not exact and word in text:
            return origin
    except Exception as e:
        logger.warning(f"Is keyword string error: {e}", exc_info=True)

    return result


def is_keyword_text(message: Message, key: str, forward: bool = False) -> dict:
    # Check if the message includes keywords
    result = {}

    try:
        # Basic data
        gid = message.chat.id
        mid = None
        class_c_message = is_class_c(None, None, message)
        match = ""

        # Check the message
        if forward and not message.forward_date:
            return {}

        # Get keywords
        keyword = glovar.keywords[gid]["kws"].get(key, {})

        # Check the keyword
        if not keyword:
            return {}

        # Get config
        equal_mode = glovar.configs[gid].get("equal", False)

        # Get modes
        modes = keyword["modes"]
        exact = "exact" in modes or (class_c_message and not equal_mode)
        case = "case" in modes
        regex = "regex" in modes

        # Get text
        message_text = get_text(message, True)

        # Check the text
        if not message_text:
            return {}

        # Get words
        words = get_words(keyword["words"], exact)

        # Get match result
        for word in words:
            match = is_keyword_string(word, message_text, words[word], case, regex)

            if match and not equal_mode and class_c_message and regex and message_text.lower() != word.lower():
                match = ""
            elif match and not equal_mode and not forward and class_c_message and message_text.lower() == word.lower():
                mid = (message.reply_to_message and message.reply_to_message.message_id) or message.message_id
                break
            elif match:
                break

        # Check the match
        if not match:
            return {}

        result = {
            "key": key,
            "mid": mid,
            "word": match,
            "reply": keyword["reply"],
            "actions": keyword["actions"],
            "destruct": keyword["destruct"],
            "forward": forward,
            "name": False
        }
    except Exception as e:
        logger.warning(f"Is keyword text error: {e}", exc_info=True)

    return result


def is_keyworded_user(gid: int, key: str, uid: int) -> bool:
    # Check if the user is keyworded user
    result = False

    try:
        if key in glovar.keyworded_ids[gid].get(uid, set()):
            return True

        if not glovar.keyworded_ids[gid].get(uid, set()):
            glovar.keyworded_ids[gid][uid] = set()

        glovar.keyworded_ids[gid][uid].add(key)

        result = False
    except Exception as e:
        logger.warning(f"Is keyworded user error: {e}", exc_info=True)

    return result


def is_nm_text(text: str) -> bool:
    # Check if the text is nm text
    result = False

    try:
        if (is_regex_text("nm", text)
                or is_regex_text("bio", text)
                or is_ban_text(text, False)):
            return True
    except Exception as e:
        logger.warning(f"Is nm text error: {e}", exc_info=True)

    return result


def is_nospam_message(message: Message) -> bool:
    # Check if the message will be processed by NOSPAM
    result = False

    try:
        # Basic data
        gid = message.chat.id

        # Check nospam status
        if glovar.nospam_id not in glovar.admin_ids[gid]:
            return False

        # Check the forward from name
        forward_name = get_forward_name(message, True, True, True)

        if forward_name and is_nm_text(forward_name):
            return True

        # Check the user's name
        name = get_full_name(message.from_user, True, True, True)

        if name and is_nm_text(name):
            return True

        # Check the text
        message_text = get_text(message, True, True)

        if is_ban_text(message_text, False):
            return True

        if is_regex_text("del", message_text):
            return True

        # File name
        filename = get_filename(message, True, True)

        if is_ban_text(filename, False):
            return True

        if is_regex_text("fil", filename):
            return True

        if is_regex_text("del", filename):
            return True
    except Exception as e:
        logger.warning(f"Is nospam message error: {e}", exc_info=True)

    return result


def is_nospam_join(client: Client, gid: int, user: User) -> bool:
    # Check if the joined message will be processed by NOSPAM
    result = False

    try:
        # Basic data
        uid = user.id

        # Check nospam status
        if glovar.nospam_id not in glovar.admin_ids[gid]:
            return False

        # Check nospam ignore status
        if gid in glovar.ignore_ids["nospam"]:
            return False

        # Check name
        name = get_full_name(user, True, True, True)

        if name and is_nm_text(name):
            return True

        # Check bio
        user = get_user_full(client, uid)

        if not user or not user.about:
            bio = ""
        else:
            bio = t2t(user.about, True, True, True)

        if bio and is_bio_text(bio):
            return True
    except Exception as e:
        logger.warning(f"Is nospam join error: {e}", exc_info=True)

    return result


def is_user_class_d(gid: int, user: User) -> bool:
    # Check if the class d user will be processed by USER
    result = False

    try:
        # Check nospam ignore status
        if gid in glovar.ignore_ids["user"]:
            return False

        # Check class D status
        if is_class_d_user(user):
            return True
    except Exception as e:
        logger.warning(f"Is user class d error: {e}", exc_info=True)

    return result


def is_regex_text(word_type: str, text: str, ocr: bool = False, again: bool = False) -> Optional[Match]:
    # Check if the text hit the regex rules
    result = None

    try:
        if text:
            if not again:
                text = re.sub(r"\s{2,}", " ", text)
            elif " " in text:
                text = re.sub(r"\s", "", text)
            else:
                return None
        else:
            return None

        with glovar.locks["regex"]:
            words = list(eval(f"glovar.{word_type}_words"))

        for word in words:
            if word in glovar.timeout_words:
                continue

            if ocr and "(?# nocr)" in word:
                continue

            try:
                result = is_regex_string(word, text)
            except TimeoutError:
                save_regex_timeout(word)

            # Count and return
            if not result:
                continue

            count = eval(f"glovar.{word_type}_words").get(word, 0)
            count += 1
            eval(f"glovar.{word_type}_words")[word] = count
            save(f"{word_type}_words")

            return result

        # Try again
        return is_regex_text(word_type, text, ocr, True)
    except Exception as e:
        logger.warning(f"Is regex text error: {e}", exc_info=True)

    return result


def is_regex_string(word: str, text: str) -> Optional[Match]:
    # Check if the text hit the regex rules
    result = None

    try:
        begin = get_now()
        result = re.search(word, text, re.I | re.S | re.M)
        end = get_now()

        if end - begin < 5:
            return result

        raise TimeoutError
    except Exception as e:
        logger.warning(f"Is regex string error: {e}", exc_info=True)

    return result


def is_rm_text(message: Message) -> bool:
    # Check if the text is rm text
    result = False

    try:
        # Basic data
        gid = message.chat.id

        # Check admin
        if is_class_c(None, None, message):
            return False

        # Check config
        if not glovar.configs[gid].get("rm", True) or not glovar.rms[gid].get("reply", ""):
            return False

        # Get the message text
        message_text = get_text(message)

        # Check the message_text
        if not is_regex_text("rm", message_text):
            return False

        result = True
    except Exception as e:
        logger.warning(f"Is rm text error: {e}", exc_info=True)

    return result


def is_should_pass(message: Message, terminate: bool = False) -> bool:
    # Check if should pass the keyword detection
    result = False

    try:
        # Basic data
        gid = message.chat.id
        uid = message.from_user.id

        # Check config
        if not terminate and glovar.configs[gid].get("equal", False):
            return False

        # Check admins
        if is_class_c(None, None, message):
            return True

        # Check white users
        if glovar.configs[gid].get("white", False) and uid in glovar.white_ids:
            return True
    except Exception as e:
        logger.warning(f"Is should pass error: {e}", exc_info=True)

    return result


def is_should_terminate(message: Message, actions: set) -> bool:
    # Check if should terminate the user
    result = False

    try:
        # Check terminate actions
        if not is_terminate_actions(actions):
            return False

        # Check if should pass
        if is_should_pass(message):
            return False

        result = True
    except Exception as e:
        logger.warning(f"Is should terminate error: {e}", exc_info=True)

    return result


def is_terminate_actions(actions: set) -> bool:
    # Check if actions have terminate action
    result = False

    try:
        result = any(a in {"delete", "kick"} or a.startswith("ban") or a.startswith("restrict") for a in actions)
    except Exception as e:
        logger.warning(f"Is terminate actions error: {e}", exc_info=True)

    return result


def is_watch_user(user: Union[int, User], the_type: str, now: int = 0) -> bool:
    # Check if the message is sent by a watch user
    result = False

    try:
        if is_class_e_user(user):
            return False

        if isinstance(user, int):
            uid = user
        else:
            uid = user.id

        now = now or get_now()
        until = glovar.watch_ids[the_type].get(uid, 0)
        result = now < until
    except Exception as e:
        logger.warning(f"Is watch user error: {e}", exc_info=True)

    return result


def is_wb_text(text: str, ocr: bool) -> bool:
    # Check if the text is wb text
    result = False

    try:
        if (is_regex_text("wb", text, ocr)
                or is_regex_text("ad", text, ocr)
                or is_regex_text("iml", text, ocr)
                or is_regex_text("pho", text, ocr)
                or is_regex_text("sho", text, ocr)
                or is_regex_text("spc", text, ocr)):
            return True

        result = any(c not in {"i"} and is_regex_text(f"ad{c}", text, ocr)
                     for c in ascii_lowercase)
    except Exception as e:
        logger.warning(f"Is wb text error: {e}", exc_info=True)

    return result
