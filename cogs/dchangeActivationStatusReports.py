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
        """
        Takes a report object, fetches the associated message from the channel,
        and attaches a new ReportView to it.
        """
        if report.embed_message_id:
            try:
                report_channel_id = int(get_report_channel())
                report_channel = self.bot.get_channel(report_channel_id)
                report_message = await report_channel.fetch_message(report.embed_message_id)

                # Get the embed from the newly-created message
                embed = report_message.embeds[0]
                view = ReportView(embed=embed, report_message=report_message, reportObject=report)
                await report_message.edit(view=view)
            except discord.HTTPException as e:
                print(f"Failed to load active report (ID {report.id}): {e}")

    async def deactivate_buttons(self, report):
        """
        Disables buttons on an existing report embed (for 'deactivating' a report).
        """
        if report.embed_message_id:
            try:
                report_channel_id = int(get_report_channel())
                report_channel = self.bot.get_channel(report_channel_id)
                report_message = await report_channel.fetch_message(report.embed_message_id)

                view = ReportView(
                    embed=report_message.embeds[0],
                    report_message=report_message,
                    reportObject=report
                )

                for item in view.children:
                    item.disabled = True

                await report_message.edit(view=view)
            except discord.HTTPException as e:
                print(f"Failed to deactivate buttons for report (ID {report.id}): {e}")

    @commands.command()
    @has_role(Role.mod)
    async def reactivateReport(self, ctx, messageID: int):
        """
        Reactivate a report by message ID by making a new copy of the old embed
        and storing that new message's ID in the database.
        Usage: !reactivateReport <messageID>
        """
        session = get_session()
        # Fetch the report by old message ID
        report = session.query(reports).filter_by(embed_message_id=messageID).first()
        if report is None:
            await ctx.send("Report embed not found.")
            return

        # Mark the report as active again
        report.active = True
        report.last_updated = time.time()

        # Fetch the old embed
        report_channel_id = int(get_report_channel())
        report_channel = self.bot.get_channel(report_channel_id)

        try:
            old_message = await report_channel.fetch_message(messageID)
        except discord.NotFound:
            await ctx.send("Old report message not found in the channel.")
            return

        # Make a copy of the old embed
        if not old_message.embeds:
            await ctx.send("Old report had no embed to copy.")
            return
        old_embed = old_message.embeds[0]

        # Send a new message with the exact same embed
        new_message = await report_channel.send(embed=old_embed)

        # Update the report to reference this new message
        report.embed_message_id = str(new_message.id)
        session.commit()

        # Attach a fresh view to the new embed
        await self.load_report_view(report)

        await ctx.send("Report successfully reactivated with a new embed message.")

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

        # Mark the report inactive
        report.active = False
        report.last_updated = time.time()
        session.commit()

        # Disable the buttons on the existing message
        await self.deactivate_buttons(report)

        await ctx.send("Report deactivated.")

async def setup(bot):
    await bot.add_cog(reactivateReports(bot))
