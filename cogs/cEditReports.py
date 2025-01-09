import discord
from discord.ext import commands
import json
from util import update_reports_json, Role, has_role
from cogs.aReportStringCustomization import ReportStringCustomization

class EditReports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_role(Role.senior)
    async def editReportTitle(self, ctx, report_type: str, *, new_value: str):
        """
        Edit the title for a report type.
        Usage: !editReportTitle <user|message> <new_value>
        """
        if report_type not in ["user", "message"]:
            await ctx.send("Invalid report type. Use `user` or `message`.")
            return

        key = f"title-{report_type}"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editReportTitle(self, ctx):
        embed = discord.Embed(
            title="Report String Customization",
            description=(
                "Use the buttons below to view and edit the current report strings in `reports.json`."
            ),
            color=discord.Color.blue()
        )
        view = ReportStringCustomization.CustomizationView(ctx)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @has_role(Role.senior)
    async def editReportDescription(self, ctx, report_type: str, *, new_value: str):
        """
        Edit the description for a report type.
        Usage: !editReportDescription <user|message> <new_value>
        """
        if report_type not in ["user", "message"]:
            await ctx.send("Invalid report type. Use `user` or `message`.")
            return

        key = f"description-{report_type}"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editReportDescription(self, ctx):
        embed = discord.Embed(
            title="Report String Customization",
            description=(
                "Use the buttons below to view and edit the current report strings in `reports.json`."
            ),
            color=discord.Color.blue()
        )
        view = ReportStringCustomization.CustomizationView(ctx)
        await ctx.send(embed=embed, view=view)
    
    @commands.command()
    @has_role(Role.senior)
    async def editMaxReasonLength(self, ctx, new_value: int):
        """
        Edit the maximum length for a reason.
        Usage: !editMaxReasonLength <new_value>
        """
        key = "max-reason-length"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editUserReportTimeout(self, ctx, new_value: int):
        """
        Edit the timeout for user reports.
        Usage: !editUserReportTimeout <new_value>
        """
        key = "user-report-timeout"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editReportsColor(self, ctx, type: str, new_value: str):
        """
        Edit the color for reports.
        Usage: !editReportsColor <new_value>
        """
        if type not in ["color", "claimed", "resolved"]:
            await ctx.send("Invalid color type. Use `color`, `claimed`, or `resolved`.")
        if type == "color":
            key = "color"
        else:
            key = f"{type}_color"
        with open("reports.json", "r") as f:
            data = json.load(f)
        new_value = new_value.replace(" ", ",")
        new_value = new_value.replace("(", "")
        new_value = new_value.replace(")", "")
        data[key]['r'] = int(new_value.split(",")[0])
        data[key]['g'] = int(new_value.split(",")[1])
        data[key]['b'] = int(new_value.split(",")[2])
        with open("reports.json", "w") as f:
            json.dump(data, f, indent=4)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editReportFailureMessage(self, ctx, new_value: str):
        """
        Edit the failure message for reports.
        Usage: !editReportFailureMessage <new_value>
        """
        key = "report-failure-message"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editReportModalReasonLabel(self, ctx, new_value: str):
        """
        Edit the reason label for the report modal.
        Usage: !editReportModalReasonLabel <new_value>
        """
        key = "report-modal-reason-label"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editReportModalReasonPlaceholder(self, ctx, new_value: str):
        """
        Edit the reason placeholder for the report modal.
        Usage: !editReportModalReasonPlaceholder <new_value>
        """
        key = "report-modal-reason-placeholder"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editDuplicateReportModalReasonLabel(self, ctx, new_value: str):
        """
        Edit the reason label for the duplicate report modal.
        Usage: !editDuplicateReportModalReasonLabel <new_value>
        """
        key = "duplicate-report-modal-reason-label"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    @commands.command()
    @has_role(Role.senior)
    async def editDuplicateReportModalReasonPlaceholder(self, ctx, new_value: str):
        """
        Edit the reason placeholder for the duplicate report modal.
        Usage: !editDuplicateReportModalReasonPlaceholder <new_value>
        """
        key = "duplicate-report-modal-reason-placeholder"
        update_reports_json(key, new_value)
        await ctx.send(f"Updated `{key}` to: `{new_value}`")
    
    

async def setup(bot):
    await bot.add_cog(EditReports(bot))
