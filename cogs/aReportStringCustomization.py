import discord
from discord.ext import commands
from discord import ui
import json
from util import Role, has_role

class ReportStringCustomization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class CustomizationView(ui.View):
        def __init__(self, ctx):
            super().__init__(timeout=None)
            self.ctx = ctx
            
            # Add buttons to the view
            self.add_item(ReportStringCustomization.ReportUserTitleButton(ctx))
            self.add_item(ReportStringCustomization.ReportUserDescriptionButton(ctx))
            self.add_item(ReportStringCustomization.ReportMessageTitleButton(ctx))
            self.add_item(ReportStringCustomization.ReportMessageDescriptionButton(ctx))

    class ReportUserTitleButton(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Report User Title", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("title-user", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editReportTitle user {current_value}"

            embed = discord.Embed(
                title="Current Report User Title",
                description=(
                    f"Below is the current string for the `title-user`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    class ReportUserDescriptionButton(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Report User Description", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("description-user", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editReportDescription user {current_value}"

            embed = discord.Embed(
                title="Current Report User Description",
                description=(
                    f"Below is the current string for the `description-user`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    class ReportMessageTitleButton(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Report Message Title", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("title-message", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editReportTitle message {current_value}"

            embed = discord.Embed(
                title="Current Report Message Title",
                description=(
                    f"Below is the current string for the `title-message`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    class ReportMessageDescriptionButton(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Report Message Description", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("description-message", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editReportDescription message {current_value}"

            embed = discord.Embed(
                title="Current Report Message Description",
                description=(
                    f"Below is the current string for the `description-message`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    @commands.command()
    @has_role(Role.senior)
    async def customizeReports(self, ctx):
        embed = discord.Embed(
            title="Report String Customization",
            description=(
                "Use the buttons below to view and edit the current report strings in `reports.json`."
            ),
            color=discord.Color.blue()
        )
        view = self.CustomizationView(ctx)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ReportStringCustomization(bot))
