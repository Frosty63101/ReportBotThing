import discord
from discord.ext import commands
import json
from util import update_reports_json, Role, has_role
from ReportStringCustomization import ReportStringCustomization

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

async def setup(bot):
    await bot.add_cog(EditReports(bot))
