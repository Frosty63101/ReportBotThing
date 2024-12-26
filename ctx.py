# I forgot that ctx menus don't work in cogs


import discord
from discord.ext import commands
from discord import app_commands

from util import get_report_channel, get_report_title, get_report_description, get_reports_color, get_mod_role

class ctx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ask_reason(self, interaction: discord.Interaction) -> str:
        """
        Prompt the user to provide a reason for the report if they choose to.

        Returns:
            str: The reason provided by the user, or "No reason provided." if they skip.
        """
        modal = discord.ui.Modal(title="Add a Reason for the Report")

        reason_input = discord.ui.TextInput(
            label="Reason (Optional)",
            style=discord.TextStyle.long,
            placeholder="Provide a reason for this report...",
            required=False,
            max_length=300
        )

        modal.add_item(reason_input)

        await interaction.response.send_modal(modal)

        await modal.wait()  # Wait for the user to complete the modal

        return reason_input.value or "No reason provided."

    @app_commands.context_menu(name="Report Message")
    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        modRoleID = int(get_mod_role())
        modRole = interaction.guild.get_role(modRoleID)
        ReportChannelID = int(get_report_channel())
        ReportChannel = interaction.guild.get_channel(ReportChannelID)
        reporter = interaction.user
        messageAuthor = message.author
        messageContent = message.content
        messageChannel = message.channel
        messageGuild = message.guild
        messageID = message.id
        rgb = get_reports_color()

        # Ask the user for a reason
        reason = await self.ask_reason(interaction)

        embed = discord.Embed(
            title=get_report_title(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
            description=f"{get_report_description(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID)}\n\n**Reason:** {reason}",
            color=discord.Color.from_rgb(rgb[0], rgb[1], rgb[2])
        )

        await ReportChannel.send(f"{modRole.mention}", embed=embed)

    @app_commands.context_menu(name="Report User")
    async def report_user(self, interaction: discord.Interaction, user: discord.User):
        modRoleID = int(get_mod_role())
        modRole = interaction.guild.get_role(modRoleID)
        ReportChannelID = int(get_report_channel())
        ReportChannel = interaction.guild.get_channel(ReportChannelID)
        reporter = interaction.user
        messageAuthor = user
        messageContent = "User"
        messageChannel = None
        messageGuild = interaction.guild
        messageID = None
        rgb = get_reports_color()

        # Ask the user for a reason
        reason = await self.ask_reason(interaction)

        embed = discord.Embed(
            title=get_report_title(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
            description=f"{get_report_description(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID)}\n\n**Reason:** {reason}",
            color=discord.Color.from_rgb(rgb[0], rgb[1], rgb[2])
        )

        await ReportChannel.send(f"{modRole.mention}", embed=embed)

async def setup(bot):
    await bot.add_cog(ctx(bot))
