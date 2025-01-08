import discord
from discord.ext import commands
from util import Role, has_role
from models import reports, get_session, reports
from util import get_report_channel
from main import ReportView
import time

class reactivateReports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def load_report_view(self, report):
        if report.embed_message_id:
            try:
                report_channel_id = int(get_report_channel())
                report_channel = self.bot.get_channel(report_channel_id)
                report_message = await report_channel.fetch_message(report.embed_message_id)
                embed = report_message.embeds[0]
                view = ReportView(embed=embed, report_message=report_message, reportObject=report)
                await report_message.edit(view=view)
            except discord.HTTPException as e:
                print(f"Failed to load active report (ID {report.id}): {e}")
    
    async def deactivate_buttons(self, report):
        if report.embed_message_id:
            try:
                report_channel_id = int(get_report_channel())
                report_channel = self.bot.get_channel(report_channel_id)
                report_message = await report_channel.fetch_message(report.embed_message_id)

                view = ReportView(embed=report_message.embeds[0], report_message=report_message, reportObject=report)

                for item in view.children:
                    item.disabled = True

                await report_message.edit(view=view)
            except discord.HTTPException as e:
                print(f"Failed to deactivate buttons for report (ID {report.id}): {e}")
    
    @commands.command()
    @has_role(Role.mod)
    async def reactivateReport(self, ctx, messageID: int):
        """
        Reactivate a report by message ID.
        Usage: !reactivateReport <messageID>
        """
        session = get_session()
        report = session.query(reports).filter_by(embed_message_id=messageID).first()
        if report is None:
            await ctx.send("Report embed not found.")
            return
        
        report.active = True
        report.last_updated = time.time()
        session.commit()
        
        await self.load_report_view(report)
        
        await ctx.send("Report reactivated.")
    
    @commands.command()
    @has_role(Role.mod)
    async def deactivateReport(self, ctx, messageID: int):
        """
        Deactivate a report by message ID.
        Usage: !deactivateReport <messageID>
        """
        session = get_session()
        report = session.query(reports).filter_by(embed_message_id=messageID).first()
        if report is None:
            await ctx.send("Report embed not found.")
            return
        
        report.active = False
        report.last_updated = time.time()
        session.commit()
        
        await self.deactivate_buttons(report)
        
        await ctx.send("Report deactivated.")

async def setup(bot):
    await bot.add_cog(reactivateReports(bot))