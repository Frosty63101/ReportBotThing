from email import message
import os
from dotenv import load_dotenv
from enum import Enum as PyEnum
from typing import Union
import discord
from discord.ext import commands
import json


envVars = {
    "TOKEN",
    "REPORT_CHANNEL_ID",
    "MOD_ROLE",
    "ADMIN_ROLE"
}

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
                f.write('{"title": "Report by {reporter} on {messageAuthor}", \n"description": "Message: {messageContent}\nChannel: {messageChannel}\nGuild: {messageGuild}\nMessage ID: {messageID}",\n "color": {\n"r": 255, \n"g": 0, \n"b": 0\n},\n "max_reason_length": 300}')
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

def get_report_title(reporter: discord.User, messageAuthor: discord.User, messageContent: str, messageChannel: discord.TextChannel, messageGuild: discord.Guild, messageID: int):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    return reportFormats["title"].format(reporter=reporter, messageAuthor=messageAuthor, messageContent=messageContent, messageChannel=messageChannel, messageGuild=messageGuild, messageID=messageID)

def get_report_description(
    type: str,
    reporter: discord.User,
    messageAuthor: discord.User,
    messageContent: str,
    messageChannel: discord.TextChannel,
    messageID: int,
    messageLink: str,
    user: discord.User,
    userID: int,
    reason: str
):
    verify_file("reports.json")
    with open("reports.json", "r") as f:
        reportFormats = json.load(f)
    if type == "message":
        return reportFormats["description-message"].format(
            reporter=reporter,
            messageAuthor=messageAuthor,
            messageContent=messageContent,
            messageChannel=messageChannel.name if messageChannel else "Direct Message",
            messageChannelMention=messageChannel.mention if messageChannel else "Direct Message",
            messageID=messageID or "N/A",
            messageLink=messageLink or "N/A",
            userID=userID or "N/A",
            user=user,
            reason=reason
        )
    elif type == "user":
        return reportFormats["description-user"].format(
            reporter=reporter,
            messageAuthor=messageAuthor,
            messageContent=messageContent,
            messageChannel=messageChannel.name if messageChannel else "Direct Message",
            messageChannelMention=messageChannel.mention if messageChannel else "Direct Message",
            messageID=messageID or "N/A",
            messageLink=messageLink or "N/A",
            userID=userID or "N/A",
            user=user,
            reason=reason
        )

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

def has_role(role: Role):
    def predicate(ctx: commands.context):
        if role == Role.owner:
            return ctx.author.id == ctx.guild.owner_id
        if role == Role.admin:
            return any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_admin_role()))
        if role == Role.mod:
            return any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_mod_role()))
        if role == Role.senior:
            return any(role.id in [r.id for r in ctx.author.roles] for role in ctx.guild.roles if role.id == int(get_senior_role()))
        return False
    return commands.check(predicate)