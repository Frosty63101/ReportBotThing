import discord
from discord.ext import commands
from discord import ui
import json
from util import Role, has_role
from util import (
    get_reports_color, 
    get_max_reason_length,
    get_user_report_timeout, rgbToHex
)
import time

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
            time.sleep(0.1)
            self.add_item(ReportStringCustomization.ReportMessageDescriptionButton(ctx))
            self.add_item(ReportStringCustomization.DuplicateReportMessageMessage(ctx))
            self.add_item(ReportStringCustomization.DuplicateReportUserMessage(ctx))
            time.sleep(0.1)
            self.add_item(ReportStringCustomization.OtherSettings(ctx))
            self.add_item(ReportStringCustomization.report_failure_message(ctx))
            self.add_item(ReportStringCustomization.report_modal_reason_label(ctx))
            time.sleep(0.1)
            self.add_item(ReportStringCustomization.report_modal_reason_placeholder(ctx))
            self.add_item(ReportStringCustomization.duplicate_report_modal_reason_label(ctx))
            self.add_item(ReportStringCustomization.duplicate_report_modal_reason_placeholder(ctx))

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
    
    class DuplicateReportMessageMessage(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Duplicate Report Message Message", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("duplicate_message_report_message", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editDuplaicateReportMessage message {current_value}"

            embed = discord.Embed(
                title="Current Duplicate Report Message Message",
                description=(
                    f"Below is the current string for the `duplicate_message_report_message`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)

    class DuplicateReportUserMessage(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Duplicate Report User Message", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("duplicate_user_report_message", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editDuplaicateReportMessage user {current_value}"

            embed = discord.Embed(
                title="Current Duplicate Report User Message",
                description=(
                    f"Below is the current string for the `duplicate_user_report_message`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
    
    class report_failure_message(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Report Failure Message", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("report_failure_message", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editReportFailureMessage {current_value}"

            embed = discord.Embed(
                title="Current Report Failure Message",
                description=(
                    f"Below is the current string for the `report_failure_message`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
    
    class report_modal_reason_label(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Report Modal Reason Label", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("report_modal_reason_label", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editReportModalReasonLabel {current_value}"

            embed = discord.Embed(
                title="Current Report Modal Reason Label",
                description=(
                    f"Below is the current string for the `report_modal_reason_label`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
    
    class report_modal_reason_placeholder(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Report Modal Reason Placeholder", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("report_modal_reason_placeholder", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editReportModalReasonPlaceholder {current_value}"

            embed = discord.Embed(
                title="Current Report Modal Reason Placeholder",
                description=(
                    f"Below is the current string for the `report_modal_reason_placeholder`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
    
    class duplicate_report_modal_reason_label(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Duplicate Report Modal Reason Label", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("duplicate_report_modal_reason_label", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editDuplicateReportModalReasonLabel {current_value}"

            embed = discord.Embed(
                title="Current Duplicate Report Modal Reason Label",
                description=(
                    f"Below is the current string for the `duplicate_report_modal_reason_label`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
    
    class duplicate_report_modal_reason_placeholder(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Duplicate Report Modal Reason Placeholder", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            with open("reports.json", "r") as f:
                report_formats = json.load(f)

            current_value = report_formats.get("duplicate_report_modal_reason_placeholder", "Not set")
            current_value = current_value.replace("\n", "\\n")
            command = f"!editDuplicateReportModalReasonPlaceholder {current_value}"

            embed = discord.Embed(
                title="Current Duplicate Report Modal Reason Placeholder",
                description=(
                    f"Below is the current string for the `duplicate_report_modal_reason_placeholder`.\n\n"
                    f"```{current_value}```\n"
                    f"Use the command below to edit it:\n\n"
                    f"```{command}```"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
    
    class OtherSettings(ui.Button):
        def __init__(self, ctx):
            self.ctx = ctx
            super().__init__(label="Other Settings", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):

            embed = discord.Embed(
                title="Current Other Settings",
                description=(
                    f"Below is the current settings for the max reason length.\n\n"
                    f"```{get_max_reason_length()}```\n"
                    f"```{f'!editMaxReasonLength {get_max_reason_length()}'}```\n"
                    f"Below is the current settings for the duplicate user report timeout.\n\n"
                    f"```{get_user_report_timeout()}```\n"
                    f"```!editUserReportTimeout {get_user_report_timeout()}```\n"
                    f"Below is the current settings for the report embed color.\n\n"
                    f"```{get_reports_color('color')} // {rgbToHex(get_reports_color('color'))}```\n"
                    f"```!editReportsColor color {get_reports_color('color')}```"
                    f"```!editReportsColor color {rgbToHex(get_reports_color('color'))}```\n"
                    f"Below is the current settings for the claimed report embed color.\n\n"
                    f"```{get_reports_color('claimed_color')} // {rgbToHex(get_reports_color('claimed_color'))}```\n"
                    f"```!editReportsColor claimed {get_reports_color('claimed_color')}```"
                    f"```!editReportsColor claimed {rgbToHex(get_reports_color('claimed_color'))}```\n"
                    f"Below is the current settings for the resolved report embed color.\n\n"
                    f"```{get_reports_color('resolved_color')} // {rgbToHex(get_reports_color('resolved_color'))}```\n"
                    f"```!editReportsColor resolved {get_reports_color('resolved_color')}```"
                    f"```!editReportsColor resolved {rgbToHex(get_reports_color('resolved_color'))}```\n"
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
