import discord
from discord.ext import commands
from discord import ui
from util import Role, has_role

class ReportCustomizationHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class HelpView(ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            
            # Add buttons to the view
            self.add_item(ReportCustomizationHelp.ReportUserTitleButton())
            self.add_item(ReportCustomizationHelp.ReportUserDescriptionButton())
            self.add_item(ReportCustomizationHelp.ReportMessageTitleButton())
            self.add_item(ReportCustomizationHelp.ReportMessageDescriptionButton())

    class ReportUserTitleButton(ui.Button):
        def __init__(self):
            super().__init__(label="Report User Title", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(
                title="Customizing Report User Title",
                description=(
                    "You can customize the report user title using the '' command. "
                    "to separate the fields in the title use '???' for inline fields and '!!!' for non-inline fields. "
                    "The following keys are available for the format string:\n\n"
                    " - '{reporter}' : This is the user object of the person who initiated the report.\n"
                    " - '{reporterMention}' : This is the mention of the person who initiated the report.\n"
                    " - '{reporterID}' : This is the ID of the person who initiated the report.\n"
                    " - '{userMention}' : This is the mention of the user being reported.\n"
                    " - '{userTag}' : This is the tag of the user being reported.\n"
                    " - '{userID}' : This is the ID of the user being reported.\n"
                    " - '{userCreated}' : This is the timestamp of the user's account creation in the markdown format (e.g. December 26, 2024 11:13 PM).\n"
                    " - '{time}' : This is the timestamp of the report in the markdown format (e.g. December 26, 2024 11:13 PM).\n"
                    " - '{reason}' : This is the reason provided by the reporter for the report.\n"
                    "\nUse these keys in the `` command to define your custom title."
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    class ReportUserDescriptionButton(ui.Button):
        def __init__(self):
            super().__init__(label="Report User Description", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(
                title="Customizing Report User Description",
                description=(
                    "You can customize the report user description using the '' command. "
                    "to separate the fields in the description use '???' for inline fields and '!!!' for non-inline fields. "
                    "The following keys are available for the format string:\n\n"
                    " - '{reporter}' : This is the user object of the person who initiated the report.\n"
                    " - '{reporterMention}' : This is the mention of the person who initiated the report.\n"
                    " - '{reporterID}' : This is the ID of the person who initiated the report.\n"
                    " - '{userMention}' : This is the mention of the user being reported.\n"
                    " - '{userTag}' : This is the tag of the user being reported.\n"
                    " - '{userID}' : This is the ID of the user being reported.\n"
                    " - '{userCreated}' : This is the timestamp of the user's account creation in the markdown format (e.g. December 26, 2024 11:13 PM).\n"
                    " - '{time}' : This is the timestamp of the report in the markdown format (e.g. December 26, 2024 11:13 PM).\n"
                    " - '{reason}' : This is the reason provided by the reporter for the report.\n"
                    "\nUse these keys in the `` command to define your custom description."
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    class ReportMessageTitleButton(ui.Button):
        def __init__(self):
            super().__init__(label="Report Message Title", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(
                title="Customizing Report Message Title",
                description=(
                    "You can customize the report message title using the '' command. "
                    "to separate the fields in the description use '???' for inline fields and '!!!' for non-inline fields. "
                    "The following keys are available for the format string:\n\n"
                    " - '{reporter}' : This is the user object of the person who initiated the report.\n"
                    " - '{reporterMention}' : This is the mention of the person who initiated the report.\n"
                    " - '{reporterID}' : This is the ID of the person who initiated the report.\n"
                    " - '{messageAuthor}' : This is the user object of the author of the reported message.\n"
                    " - '{messageAuthorMention}' : This is the mention of the author of the reported message.\n"
                    " - '{messageContent}' : This is the content of the reported message.\n"
                    " - '{messageChannel}' : This is the channel object where the message was reported.\n"
                    " - '{messageGuild}' : This is the guild object where the message was reported.\n"
                    " - '{messageID}' : This is the ID of the reported message.\n"
                    " - '{messageLink}' : This is a link to the reported message.\n"
                    " - '{channel}' : This is the channel object where the message was reported.\n"
                    " - '{channelName}' : This is the name of the channel where the message was reported.\n"
                    " - '{channelMention}' : This is the mention of the channel where the message was reported.\n"
                    " - '{time}' : This is the timestamp of the report in the markdown format (e.g. December 26, 2024 11:13 PM).\n"
                    " - '{reason}' : This is the reason provided by the reporter for the report.\n"
                    "\nUse these keys in the `` command to define your custom title."
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    class ReportMessageDescriptionButton(ui.Button):
        def __init__(self):
            super().__init__(label="Report Message Description", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(
                title="Customizing Report Message Description",
                description=(
                    "You can customize the report message description using the '' command. "
                    "to separate the fields in the description use '???' for inline fields and '!!!' for non-inline fields. "
                    "The following keys are available for the format string:\n\n"
                    " - '{reporter}' : This is the user object of the person who initiated the report.\n"
                    " - '{reporterMention}' : This is the mention of the person who initiated the report.\n"
                    " - '{reporterID}' : This is the ID of the person who initiated the report.\n"
                    " - '{messageAuthor}' : This is the user object of the author of the reported message.\n"
                    " - '{messageAuthorMention}' : This is the mention of the author of the reported message.\n"
                    " - '{messageContent}' : This is the content of the reported message.\n"
                    " - '{messageChannel}' : This is the channel object where the message was reported.\n"
                    " - '{messageGuild}' : This is the guild object where the message was reported.\n"
                    " - '{messageID}' : This is the ID of the reported message.\n"
                    " - '{messageLink}' : This is a link to the reported message.\n"
                    " - '{channel}' : This is the channel object where the message was reported.\n"
                    " - '{channelName}' : This is the name of the channel where the message was reported.\n"
                    " - '{channelMention}' : This is the mention of the channel where the message was reported.\n"
                    " - '{time}' : This is the timestamp of the report in the markdown format (e.g. December 26, 2024 11:13 PM).\n"
                    " - '{reason}' : This is the reason provided by the reporter for the report.\n"
                    "\nUse these keys in the `` command to define your custom description."
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    @commands.command()
    @has_role(Role.senior)
    async def reportHelp(self, ctx):
        embed = discord.Embed(
            title="Report Customization Help",
            description=(
                "This guide explains how to customize the responses in `reports.json`. "
                "Use the buttons below to navigate to specific sections."
            ),
            color=discord.Color.blue()
        )
        view = self.HelpView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ReportCustomizationHelp(bot))
