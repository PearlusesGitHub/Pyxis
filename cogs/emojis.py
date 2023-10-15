import enum
import logging
from os import environ
from typing import NamedTuple

class Emojis:
    cross_mark = "\u274C"
    check = "\u2611"
    envelope = "\U0001F4E8"
    trashcan = environ.get("TRASHCAN_EMOJI", "<:trashcan:637136429717389331>")
    ok_hand = ":ok_hand:"
    hand_raised = "\U0001F64B"

    dice_1 = "<:dice_1:755891608859443290>"
    dice_2 = "<:dice_2:755891608741740635>"
    dice_3 = "<:dice_3:755891608251138158>"
    dice_4 = "<:dice_4:755891607882039327>"
    dice_5 = "<:dice_5:755891608091885627>"
    dice_6 = "<:dice_6:755891607680843838>"

    # These icons are from Github's repo https://github.com/primer/octicons/
    issue_open = "<:IssueOpen:852596024777506817>"
    issue_closed = "<:IssueClosed:927326162861039626>"
    issue_draft = "<:IssueDraft:852596025147523102>"  # Not currently used by Github, but here for future.
    pull_request_open = "<:PROpen:852596471505223781>"
    pull_request_closed = "<:PRClosed:852596024732286976>"
    pull_request_draft = "<:PRDraft:852596025045680218>"
    pull_request_merged = "<:PRMerged:852596100301193227>"

    number_emojis = {
        1: "\u0031\ufe0f\u20e3",
        2: "\u0032\ufe0f\u20e3",
        3: "\u0033\ufe0f\u20e3",
        4: "\u0034\ufe0f\u20e3",
        5: "\u0035\ufe0f\u20e3",
        6: "\u0036\ufe0f\u20e3",
        7: "\u0037\ufe0f\u20e3",
        8: "\u0038\ufe0f\u20e3",
        9: "\u0039\ufe0f\u20e3"
    }

    confirmation = "\u2705"
    decline = "\u274c"
    incident_unactioned = "<:incident_unactioned:719645583245180960>"

    x = "\U0001f1fd"
    o = "\U0001f1f4"

    x_square = "<:x_square:632278427260682281>"
    o_square = "<:o_square:632278452413661214>"

    status_online = "<:status_online:470326272351010816>"
    status_idle = "<:status_idle:470326266625785866>"
    status_dnd = "<:status_dnd:470326272082313216>"
    status_offline = "<:status_offline:470326266537705472>"

    stackoverflow_tag = "<:stack_tag:870926975307501570>"
    stackoverflow_views = "<:stack_eye:870926992692879371>"

    # Reddit emojis
    reddit = "<:reddit:676030265734332427>"
    reddit_post_text = "<:reddit_post_text:676030265910493204>"
    reddit_post_video = "<:reddit_post_video:676030265839190047>"
    reddit_post_photo = "<:reddit_post_photo:676030265734201344>"
    reddit_upvote = "<:reddit_upvote:755845219890757644>"
    reddit_comments = "<:reddit_comments:755845255001014384>"
    reddit_users = "<:reddit_users:755845303822974997>"

    lemon_hyperpleased = "<:lemon_hyperpleased:754441879822663811>"
    lemon_pensive = "<:lemon_pensive:754441880246419486>"


class Icons:
    questionmark = "https://cdn.discordapp.com/emojis/512367613339369475.png"
    bookmark = (
        "https://images-ext-2.discordapp.net/external/zl4oDwcmxUILY7sD9ZWE2fU5R7n6QcxEmPYSE5eddbg/"
        "%3Fv%3D1/https/cdn.discordapp.com/emojis/654080405988966419.png?width=20&height=20"
    )
