import discord
from discord.ext import commands

from util import get_report_channel, get_report_title, get_report_description, get_reports_color, get_mod_role

class ctx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.contextmenu(name="Report Message", target=discord.Message)
    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        modRoleID = int(get_mod_role())
        modRole = interaction.guild.get_role(modRoleID)
        ReportChannelID = int(get_report_channel())
        ReportChannel = ctx.guild.get_channel(ReportChannelID)
        reporter = interaction.user
        messageAuthor = message.author
        messageContent = message.content
        messageChannel = message.channel
        messageGuild = message.guild
        messageID = message.id
        rgb = get_reports_color()
        embed = discord.Embed(
            title = get_report_title(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
            description = get_report_description(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
            color = discord.Color.from_rgb(rgb[0], rgb[1], rgb[2])
        )
        await ReportChannel.send(f"{modRole.mention}", embed=embed)

    @commands.contextmenu(name="Report User", target=discord.User)
    async def report_user(self, interaction: discord.Interaction, user: discord.User):
        modRoleID = int(get_mod_role())
        modRole = interaction.guild.get_role(modRoleID)
        ReportChannelID = int(get_report_channel())
        ReportChannel = ctx.guild.get_channel(ReportChannelID)
        reporter = interaction.user
        messageAuthor = user
        messageContent = "User"
        messageChannel = None
        messageGuild = interaction.guild
        messageID = None
        rgb = get_reports_color()
        embed = discord.Embed(
            title = get_report_title(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
            description = get_report_description(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
            color = discord.Color.from_rgb(rgb[0], rgb[1], rgb[2])
        )
        await ReportChannel.send(f"{modRole.mention}", embed=embed)

async def setup(bot):
    await bot.add_cog(ctx(bot))