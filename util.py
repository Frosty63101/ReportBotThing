import os
import time
from dotenv import load_dotenv
from enum import Enum as PyEnum
import discord
from discord.ext import commands
import json
import string

envVars = {
    "TOKEN",
    "REPORT_CHANNEL_ID",
    "MOD_ROLE",
    "ADMIN_ROLE"
}

class SafeFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, "{" + key + "}")
        return super().get_value(key, args, kwargs)

class Role(PyEnum):
    admin = "Admin"
    mod = "Moderator"
    owner = "Owner"
    senior = "Senior Moderator"

envLoaded = False

def verify_file(filePath):
    if not os.path.exists(filePath):
        with open(filePath, "w") as f:
            if filePath == "reports.json":
                with open("reports.json.example", "r") as e:
                    f.write(e.read())
            elif filePath == ".env":
                with open(".env.example", "r") as e:
                    f.write(e.read())
            else:
                f.write("")

def ensure_env_loaded():
    global envLoaded
    if not envLoaded:
        load_dotenv()
        envLoaded = True

def reload_env():
    global envLoaded
    envLoaded = False
    ensure_env_loaded()

def get_token():
    ensure_env_loaded()
    token = os.getenv('TOKEN')
    return token

def get_report_channel():
    ensure_env_loaded()
    channel = os.getenv('REPORT_CHANNEL_ID')
    return channel

def get_mod_role():
    ensure_env_loaded()
    role = os.getenv('MOD_ROLE')
    return role

def get_senior_role():
    ensure_env_loaded()
    role = os.getenv('SENIOR_ROLE')
    return role

def get_admin_role():
    ensure_env_loaded()
    role = os.getenv('ADMIN_ROLE')
    return role

def get_report_title(
    reporter: discord.User,
    message: discord.Message,
    user: discord.User,
    reason: str
):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    
    formatter = SafeFormatter()

    if message:
        context = {
            "reporter": reporter,
            "reporterMention": reporter.mention,
            "reporterID": reporter.id,
            "messageAuthor": message.author,
            "messageAuthorMention": message.author.mention,
            "messageContent": message.content,
            "messageChannel": message.channel,
            "messageGuild": message.guild,
            "messageID": message.id,
            "messageLink": message.jump_url,
            "channel": message.channel,
            "channelName": message.channel.name,
            "channelMention": message.channel.mention,
            "time": f"<t:{int(time.time())}:f>",
            "reason": reason,
        }
        return formatter.format(reportFormats["title-message"], **context)
    
    elif user:
        context = {
            "reporter": reporter,
            "reporterMention": reporter.mention,
            "reporterID": reporter.id,
            "userMention": user.mention,
            "userTag": user.discriminator,
            "userID": user.id,
            "userCreated": f"<t:{int(user.created_at.timestamp())}:f>",
            "time": f"<t:{int(time.time())}:f>",
            "reason": reason,
        }
        return formatter.format(reportFormats["title-user"], **context)

def get_report_description(
    reporter: discord.User,
    message: discord.Message,
    user: discord.User,
    reason: str
):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    
    formatter = SafeFormatter()

    if (
        message and message.guild and message.author and \
        message.channel and message.content and message.id and \
        message.jump_url and reason
    ):
        context = {
            "reporter": reporter,
            "reporterMention": reporter.mention,
            "reporterID": reporter.id,
            "messageAuthor": message.author,
            "messageAuthorMention": message.author.mention,
            "messageContent": message.content,
            "messageChannel": message.channel,
            "messageGuild": message.guild,
            "messageID": message.id,
            "messageLink": message.jump_url,
            "channel": message.channel,
            "channelName": message.channel.name,
            "channelMention": message.channel.mention,
            "time": f"<t:{int(time.time())}:f>",
            "reason": reason,
        }
        return formatter.format(reportFormats["description-message"], **context)
    
    elif (
        user and user.id and user.mention and user.discriminator and \
        user.created_at and user.joined_at and reason
    ):
        context = {
            "reporter": reporter,
            "reporterMention": reporter.mention,
            "reporterID": reporter.id,
            "userMention": user.mention,
            "userTag": user.discriminator,
            "userID": user.id,
            "userCreated": f"<t:{int(user.created_at.timestamp())}:f>",
            "time": f"<t:{int(time.time())}:f>",
            "reason": reason,
        }
        return formatter.format(reportFormats["description-user"], **context)



def get_reports_color():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return (reportFormats["color"]["r"], reportFormats["color"]["g"], reportFormats["color"]["b"])

def get_max_reason_length():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["max_reason_length"]

def get_reports_color(color_key: str = "color"):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        report_formats = json.load(f)
    color = report_formats.get(color_key, report_formats["color"])
    return (color["r"], color["g"], color["b"])

def get_user_report_timeout():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["user_report_timeout"]

def get_duplicate_user_report_message():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["duplicate_user_report_message"]

def get_duplicate_message_report_message():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["duplicate_message_report_message"]

def get_message_report_message():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["message_report_message"]

def get_user_report_message():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["user_report_message"]

def get_report_failure_message():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["report_failure_message"]

def get_report_modal_reason_label():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["report_modal_reason_label"]

def get_report_modal_reason_placeholder():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["report_modal_reason_placeholder"]

def get_duplicate_report_modal_reason_label():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["duplicate_report_modal_reason_label"]

def get_duplicate_report_modal_reason_placeholder():
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["duplicate_report_modal_reason_placeholder"]

### EDIT FUNCTIONS ###

def edit_message_report_message(value: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["message_report_message"] = value
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_user_report_message(value: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["user_report_message"] = value
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_report_failure_message(value: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["report_failure_message"] = value
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_report_modal_reason_label(value: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["report_modal_reason_label"] = value
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_report_modal_reason_placeholder(value: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["report_modal_reason_placeholder"] = value
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_duplicate_report_modal_reason_label(value: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["duplicate_report_modal_reason_label"] = value
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_duplicate_report_modal_reason_placeholder(value: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["duplicate_report_modal_reason_placeholder"] = value
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_duplicate_user_report_message(new_message: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["duplicate_user_report_message"] = new_message
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_duplicate_message_report_message(new_message: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["duplicate_message_report_message"] = new_message
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_user_report_timeout(timeout: int):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["user_report_timeout"] = timeout
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_reports_title(title: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["title"] = title
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_reports_description(description: str):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["description"] = description
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def edit_reports_color(r: int, g: int, b: int):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    reportFormats["color"] = {"r": r, "g": g, "b": b}
    with open("reports.json", "w") as f:
        json.dump(reportFormats, f, indent=4)

def update_reports_json(self, key: str, new_value: str):
        """Helper function to update a specific key in reports.json."""
        with open("reports.json", "r") as f:
            report_formats = json.load(f)

        report_formats[key] = new_value

        with open("reports.json", "w") as f:
            json.dump(report_formats, f, indent=4)

def edit_env(key, value):
    ensure_env_loaded()
    with open(".env", "r") as f:
        lines = f.readlines()
    edited = False
    for i, line in enumerate(lines):
        if line.startswith(key):
            lines[i] = f"{key}={value}\n"
            edited = True
            break
    if not edited:
        lines.append(f"{key}={value}\n")
    
    with open(".env", "w") as f:
        f.writelines(lines)
    reload_env()

def get_stored_prefix():
    verify_file(".env")
    ensure_env_loaded()
    return str(os.getenv("PREFIX"))

def edit_prefix(new_prefix: str):
    verify_file(".env")
    edit_env("PREFIX", new_prefix)

def rgbToHex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])

def has_role(role: Role):
    def predicate(ctx: commands.context):
        if role == Role.owner:
            return ctx.author.id == ctx.guild.owner_id
        if role == Role.admin:
            return any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_admin_role())) or ctx.author.id == ctx.guild.owner_id
        if role == Role.senior:
            return any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_senior_role())) or any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_admin_role())) or ctx.author.id == ctx.guild.owner_id
        if role == Role.mod:
            return any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_mod_role())) or any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_senior_role())) or any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_admin_role())) or ctx.author.id == ctx.guild.owner_id
        return False
    return commands.check(predicate)