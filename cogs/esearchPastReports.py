from discord.ext import commands
import discord
from discord import app_commands, Interaction, Embed, ui
from typing import Optional
import re
import time

from util import Role, has_role
from models import reports, get_session

class ReportsPaginationView(ui.View):
    """
    This view provides pagination for a list of reports.
    """
    def __init__(self, reportList, author, ephemeral, pageSize=5):
        super().__init__(timeout=180)  # Timeout for the view (in seconds)
        self.reportList = reportList         # The full list of report objects from the DB
        self.author = author                 # The user who initiated the command
        self.ephemeral = ephemeral           # Whether the results should be ephemeral
        self.pageSize = pageSize             # Number of reports per page
        self.currentPageIndex = 0            # Tracks the current page index

        # Calculate how many pages we need based on number of reports and pageSize
        self.totalPages = (len(reportList) // self.pageSize) + (
            1 if len(reportList) % self.pageSize != 0 else 0
        )

        # Disable buttons if there's only one page
        if self.totalPages <= 1:
            for child in self.children:
                if isinstance(child, ui.Button):
                    child.disabled = True

    def create_embed_for_page(self, pageIndex: int) -> Embed:
        """
        Creates an embed containing the reports for the given page index.
        """
        startIndex = pageIndex * self.pageSize
        endIndex = startIndex + self.pageSize
        pageItems = self.reportList[startIndex:endIndex]

        embed = Embed(title="Search Reports Results")
        embed.set_footer(
            text=f"Page {pageIndex + 1}/{self.totalPages} | "
                 f"Showing {len(pageItems)} of {len(self.reportList)} total"
        )

        if not pageItems:
            embed.description = "No reports found on this page."
            return embed

        for reportObj in pageItems:
            # We'll show some basic info for each report.
            reportId = reportObj.id
            report_type = reportObj.report_type or "N/A"
            messageId = reportObj.message_id if reportObj.message_id else "N/A"
            userId = reportObj.user_id if reportObj.user_id else "N/A"
            reason = (
                reportObj.reason[:100] + "..."
                if reportObj.reason and len(reportObj.reason) > 100
                else (reportObj.reason or "")
            )
            modAction = (
                reportObj.mod_action[:100] + "..."
                if reportObj.mod_action and len(reportObj.mod_action) > 100
                else (reportObj.mod_action or "")
            )
            status = reportObj.status
            activeFlag = reportObj.active
            reportTime = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(reportObj.report_time)
            )

            embed.add_field(
                name=f"Report ID #{reportId} - {report_type}",
                value=(
                    f"**Message ID**: {messageId}\n"
                    f"**User ID**: {userId}\n"
                    f"**Reason**: {reason}\n"
                    f"**Mod Action**: {modAction}\n"
                    f"**Status**: {status}\n"
                    f"**Active**: {activeFlag}\n"
                    f"**Report Time**: {reportTime}\n"
                ),
                inline=False
            )

        return embed

    async def update_page(self, interaction: Interaction):
        """
        Re-compute and display the embed for the current page index.
        """
        embed = self.create_embed_for_page(self.currentPageIndex)
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: Interaction, button: ui.Button):
        # Only the original invoker can use the pagination buttons
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                "You are not the invoker of this command.",
                ephemeral=True
            )
        if self.currentPageIndex > 0:
            self.currentPageIndex -= 1
        await self.update_page(interaction)

    @ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: Interaction, button: ui.Button):
        # Only the original invoker can use the pagination buttons
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                "You are not the invoker of this command.",
                ephemeral=True
            )
        if self.currentPageIndex < self.totalPages - 1:
            self.currentPageIndex += 1
        await self.update_page(interaction)


class searchPastReports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="search_reports",
        description="Search past reports in the database using various filters."
    )
    @has_role(Role.mod)
    async def search_reports(
        self,
        interaction: Interaction,
        # Accept as strings so we can parse them ourselves.
        message: Optional[str] = None,
        # Let user pick a mention from the slash UI. If you want IDs, switch to str and parse.
        user: Optional[discord.User] = None,
        reporter: Optional[discord.User] = None,
        claimer: Optional[discord.User] = None,
        resolver: Optional[discord.User] = None,
        # 'report_type' can remain an app_commands.Choice[str], which is valid for slash commands
        report_type: Optional[app_commands.Choice[str]] = None,
        # bool works fine in slash commands for True/False
        status: Optional[bool] = None,     
        active: Optional[bool] = None,     
        before: Optional[float] = None,    
        after: Optional[float] = None,     
        mod_actions_taken: str = "",        
        reason: str = "",
        # Booleans are also valid. If you want them as a single "mode", keep them. 
        # If you want to unify them into one param, that's also possible.
        contains: Optional[bool] = None,   
        exact: Optional[bool] = None,      
        ephemeral: Optional[bool] = None   
    ):
        """
        Search past reports with optional filters. 
        All parameters are combined (AND logic).

        - message (str): Could be a numeric ID or a link to a message.
        - user (discord.User): The reported user (mention).
        - reporter (discord.User): The user who made the report.
        - claimer (discord.User): The user who claimed the report.
        - resolver (discord.User): The user who resolved the report.
        - report_type (Choice[str]): The type of the report.
        - status (bool): True => 'Resolved', False => 'Pending'
        - active (bool): True => active only, False => inactive
        - before (float): Filter by report_time <= before
        - after (float): Filter by report_time >= after
        - mod_actions_taken (str): Text to match in mod_action field
        - reason (str): Text to match in reason field
        - contains (bool): partial substring match for text fields
        - exact (bool): exact match for text fields
        - ephemeral (bool): show results only to you
        """
        # Default ephemeral to True if user doesn't specify
        if ephemeral is None:
            ephemeral = True

        dbSession = get_session()
        searchQuery = dbSession.query(reports)

        # Handle 'message' as a string. Could be link or numeric string.
        if message:
            # Attempt to parse out the numeric message ID from a link
            match = re.search(r"/channels/(\d+)/(\d+)/(\d+)", message)
            if match:
                try:
                    parsedId = int(match.group(3))
                    searchQuery = searchQuery.filter_by(message_id=parsedId)
                except ValueError:
                    # If can't parse, no results
                    searchQuery = searchQuery.filter_by(message_id=-1)
            else:
                # Otherwise, see if it's just an integer
                try:
                    messageId = int(message)
                    searchQuery = searchQuery.filter_by(message_id=messageId)
                except ValueError:
                    # If not a valid integer, no results
                    searchQuery = searchQuery.filter_by(message_id=-1)

        # Filter by 'user' if provided (use user.id)
        if user:
            searchQuery = searchQuery.filter_by(user_id=user.id)

        # Filter by 'reporter' if provided (reporter.id)
        if reporter:
            searchQuery = searchQuery.filter_by(reporter_id=reporter.id)

        # Filter by 'claimer' if provided
        if claimer:
            searchQuery = searchQuery.filter_by(claimer_id=claimer.id)

        # Filter by 'resolver' if provided
        if resolver:
            searchQuery = searchQuery.filter_by(resolver_id=resolver.id)

        # report_type => an app_commands.Choice[str], so filter by report_type.value
        if report_type:
            searchQuery = searchQuery.filter_by(report_type=report_type.value)

        # status => True => "Resolved", False => "Pending"
        if status is True:
            searchQuery = searchQuery.filter_by(status="Resolved")
        elif status is False:
            searchQuery = searchQuery.filter_by(status="Pending")

        # active => True => active, False => inactive
        if active is True:
            searchQuery = searchQuery.filter_by(active=True)
        elif active is False:
            searchQuery = searchQuery.filter_by(active=False)

        # before/after => compare with report_time
        if before is not None:
            searchQuery = searchQuery.filter(reports.report_time <= before)
        if after is not None:
            searchQuery = searchQuery.filter(reports.report_time >= after)

        # reason / mod_actions_taken => partial or exact matching
        if reason:
            if exact:
                searchQuery = searchQuery.filter(reports.reason == reason)
            elif contains:
                searchQuery = searchQuery.filter(reports.reason.ilike(f"%{reason}%"))
            else:
                searchQuery = searchQuery.filter(reports.reason == reason)

        if mod_actions_taken:
            if exact:
                searchQuery = searchQuery.filter(reports.mod_action == mod_actions_taken)
            elif contains:
                searchQuery = searchQuery.filter(
                    reports.mod_action.ilike(f"%{mod_actions_taken}%")
                )
            else:
                searchQuery = searchQuery.filter(
                    reports.mod_action == mod_actions_taken
                )

        reportList = searchQuery.all()
        if not reportList:
            return await interaction.response.send_message(
                content="No matching reports found.",
                ephemeral=ephemeral
            )

        # Paginate the results
        paginationView = ReportsPaginationView(reportList, interaction.user, ephemeral)
        firstEmbed = paginationView.create_embed_for_page(0)
        await interaction.response.send_message(
            embed=firstEmbed,
            view=paginationView,
            ephemeral=ephemeral
        )

async def setup(bot):
    await bot.add_cog(searchPastReports(bot))
