import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import time
from models import get_claim_button_id, get_resolve_button_id, get_edit_reason_button_id, get_session, reports
from util import (
    get_token, get_report_channel, get_report_title,
    get_report_description, get_reports_color, 
    get_mod_role, get_max_reason_length,
    get_user_report_timeout, get_duplicate_user_report_message,
    get_duplicate_message_report_message, get_report_failure_message,
    get_user_report_message, get_message_report_message,
    get_report_modal_reason_label, get_report_modal_reason_placeholder,
    get_duplicate_report_modal_reason_label, get_duplicate_report_modal_reason_placeholder,
    get_stored_prefix, edit_prefix
)

prefix = get_stored_prefix()

# Function to dynamically get the prefix
async def get_prefix(bot, message):
    global prefix
    return prefix

bot = commands.AutoShardedBot(intents=discord.Intents.all(), command_prefix=get_prefix)

@bot.command(name="changeprefix")
@commands.has_permissions(administrator=True)
async def change_prefix(ctx, new_prefix: str):
    """
    Change the bot's command prefix.
    Only users with administrator permission can use this command.
    """
    global prefix
    if len(new_prefix) > 3:  # Limit the prefix length for usability
        await ctx.send("The prefix is too long! Please use a shorter prefix (max 3 characters).")
        return

    prefix = new_prefix
    edit_prefix(new_prefix)
    await ctx.send(f"Prefix successfully changed to `{prefix}`")

@change_prefix.error
async def change_prefix_error(ctx, error):
    """
    Handle errors for the change_prefix command.
    """
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to change the prefix!")

async def load_cogs():
    """
    Load all cogs in the 'cogs' directory.
    """
    for cog in os.listdir("cogs"):
        if cog.endswith(".py"):
            cog = cog[:-3]
            try:
                await bot.load_extension(f"cogs.{cog}")
                time.sleep(1)  # Prevent API spam
                print(f"Loaded {cog} cog.")
            except Exception as e:
                print(f"Failed to load {cog} cog: {e}")
    
    bot.tree.add_command(report_message)
    bot.tree.add_command(report_user)
    
    commandList = [command.name for command in bot.commands]
    commandList += [command.name for command in bot.tree.walk_commands()]
    commandList.sort()
    print(f"Registered commands:\n{commandList}")

executor = ThreadPoolExecutor()

@bot.event
async def on_ready():
    """ 
    Load cogs and sync commands when the bot is ready.
    """
    await load_cogs()
    print(f"Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Load active views concurrently
    session = get_session()
    active_reports = session.query(reports).filter_by(active=True).all()

    if not check_active_reports.is_running():
        check_active_reports.start()

    async def load_report_view(report):
        """ 
        Load the view for an active report.
        """
        await asyncio.sleep(1)  # Prevent API spam
        if report.embed_message_id:
            try:
                report_channel_id = int(get_report_channel())
                report_channel = bot.get_channel(report_channel_id)
                report_message = await report_channel.fetch_message(report.embed_message_id)
                embed = report_message.embeds[0]
                await asyncio.sleep(1)  # Prevent API spam
                view = ReportView(embed=embed, report_message=report_message, reportObject=report)
                await asyncio.sleep(1)  # Prevent API spam
                try:
                    await report_message.edit(view=view)
                except discord.HTTPException as e:
                    if e.code == 30046:
                        print("Cannot edit this old message anymore. Skipping.")
                        session = get_session()
                        report = session.query(reports).filter_by(id=report.id).first()
                        report.active = False
                        report.claim_button_active = False
                        report.resolve_button_active = False
                        session.commit()
                    else:
                        raise 
            except discord.HTTPException as e:
                print(f"Failed to load active report (ID {report.id}): {e}")

    # Define a task to process reports in a separate thread
    async def process_reports():
        """
        Load all active report views with asyncio.
        """
        for i, report in enumerate(active_reports):
            await asyncio.sleep(2)  # Prevent API spam
            asyncio.run_coroutine_threadsafe(load_report_view(report), bot.loop)
            if i % 5 == 0:  # Add a delay after every 5 reports
                await asyncio.sleep(5)

    # Run the processing task
    await process_reports()
    print("Loaded all active report views.")

class ReportReasonModal(discord.ui.Modal):
    def __init__(self, max_length: int, duplicate=False):
        super().__init__(title="Add a Reason for the Report")
        if not duplicate:
            self.reason = discord.ui.TextInput(
                label=get_report_modal_reason_label(),
                style=discord.TextStyle.long,
                placeholder=get_report_modal_reason_placeholder(),
                required=False,
                max_length=max_length
            )
        else:
            self.reason = discord.ui.TextInput(
                label=get_duplicate_report_modal_reason_label(),
                style=discord.TextStyle.long,
                placeholder=get_duplicate_report_modal_reason_placeholder(),
                required=False,
                max_length=max_length
            )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

    async def get_reason(self, interaction: discord.Interaction) -> str:
        """Show the modal and return the user's input."""
        await interaction.response.send_modal(self)
        await self.wait()  # Wait until the modal is submitted
        return self.reason.value or "No reason provided."

class modActionModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Add a summary of the moderation action taken")
        self.action = discord.ui.TextInput(
            label="Mod action (Optional)",
            style=discord.TextStyle.long,
            placeholder="Provide a summary of moderation action taken if needed...",
            required=False
        )
        self.add_item(self.action)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

    async def get_action(self, interaction: discord.Interaction) -> str:
        """Show the modal and return the user's input."""
        await interaction.response.send_modal(self)
        await self.wait()  # Wait until the modal is submitted
        return self.action.value or "No action provided."

class ReportView(discord.ui.View):
    def __init__(self, embed: discord.Embed, report_message: discord.Message, reportObject: reports):
        super().__init__()
        
        # Save the embed and the original report message so we can edit later
        self.embed = embed
        self.reportMessage = report_message
        self.reportObject = reportObject
        
        # Store the status so it can be updated as buttons are pressed
        self.status = reportObject.status
        
        self.claimButton.custom_id = get_claim_button_id(self.reportObject.id)
        self.resolveButton.custom_id = get_resolve_button_id(self.reportObject.id)
        
        session = get_session()
        self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
        
        if not self.reportObject.claim_button_active:
            self.claimButton.disabled = True
        if not self.reportObject.resolve_button_active:
            self.resolveButton.disabled = True
        
    
    async def update_embed(self, interaction: discord.Interaction, newStatus: str):
        """
        Updates the embed description with the latest status and changes the color.
        """
        # Replace the status text
        updatedDescription = self.embed.description.replace(
            f"**Status:** {self.status}",
            f"**Status:** {newStatus}"
        )
        self.status = newStatus
        self.embed.description = updatedDescription
        
        session = get_session()
        self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
        self.reportObject.status = newStatus
        self.reportObject.last_updated = time.time()
        session.commit()
        
        # (Example) set color based on status
        if "Claimed" in newStatus:
            rgb = get_reports_color("claimed_color")
        elif "Resolved" in newStatus:
            rgb = get_reports_color("resolved_color")
        else:
            rgb = get_reports_color()
        self.embed.color = discord.Color.from_rgb(*rgb)
        
        # Apply updates by editing the message
        time.sleep(2)  # Prevent API spam
        await self.reportMessage.edit(embed=self.embed, view=self)
    
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary)
    async def claimButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Marks this report as claimed by whoever pressed the button.
        Disables the 'Claim' button to prevent it from being pressed again.
        """
        # Disable this button
        button.disabled = True
        session = get_session()
        self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
        self.reportObject.claimer_id = interaction.user.id
        self.reportObject.last_updated = time.time()
        self.reportObject.claim_button_active = False
        session.commit()
        
        # Update the embed to reflect the claimed status
        await self.update_embed(interaction, f"Claimed by {interaction.user.mention}")
        # Edit the message to apply the updated view
        await interaction.response.edit_message(embed=self.embed, view=self)
    
    @discord.ui.button(label="Resolve", style=discord.ButtonStyle.success)
    async def resolveButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Prompts the moderator to provide an action/summary, then marks this report
        as resolved and disables the buttons.
        """
        # Disable the 'Resolve' button
        button.disabled = True
        session = get_session()
        self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
        self.reportObject.resolve_button_active = False
        session.commit()
        
        # Also disable the 'Claim' button if it isn't already
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.label == "Claim":
                child.disabled = True
                session = get_session()
                self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
                self.reportObject.claim_button_active = False
                session.commit()
        
        # Ask for moderator action via the modal
        modAction = modActionModal()
        action = await modAction.get_action(interaction)
        
        session = get_session()
        self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
        self.reportObject.resolver_id = interaction.user.id
        self.reportObject.last_updated = time.time()
        self.reportObject.status = "Resolved"
        session.commit()
        
        # Update the embed with the resolution status
        await self.update_embed(
            interaction,
            f"Resolved by {interaction.user.mention} \nwith action: {action}"
        )
        
        # Edit the message with the final state
        await self.reportMessage.edit(embed=self.embed, view=self)


async def handle_report(
    interaction: discord.Interaction,
    target: discord.Member | discord.Message,
    report_type: str,
):
    """ 
    handles the report command
    """
    print(type(target))
    mod_role_id = int(get_mod_role())
    mod_role = interaction.guild.get_role(mod_role_id)
    report_channel_id = int(get_report_channel())
    report_channel = interaction.guild.get_channel(report_channel_id)

    reporter = interaction.user
    rgb = get_reports_color()
    embed_color = discord.Color.from_rgb(*rgb)

    reason_modal = ReportReasonModal(max_length=int(get_max_reason_length()))
    reason = await reason_modal.get_reason(interaction)

    if isinstance(target, discord.Message):
        await interaction.followup.send(get_message_report_message(), ephemeral=True)
        description = get_report_description(reporter, target, None, reason)
        title = get_report_title(reporter, target, None, reason)
    else:
        await interaction.followup.send(get_user_report_message(), ephemeral=True)
        description = get_report_description(reporter, None, target, reason)
        title = get_report_title(reporter, None, target, reason)
    
    description = description.split("!!!")
    
    descriptionMatrix = []
    for i in range(len(description)):
        descriptionMatrix.append(description[i].split("???"))

    embed = discord.Embed(
        title=title,
        description="**Status:** Pending",
        color=embed_color
    )
    
    for i in range(len(descriptionMatrix)):
        embed.add_field(name=descriptionMatrix[i][0].split("\n")[0], value=descriptionMatrix[i][0].split("\n")[1] if len(descriptionMatrix[i][0].split("\n")) == 2 else "", inline=(False if i > 0 else True))
        for j in range(1, len(descriptionMatrix[i])):
            embed.add_field(name=descriptionMatrix[i][j].split("\n")[0], value=descriptionMatrix[i][j].split("\n")[1] if len(descriptionMatrix[i][j].split("\n")) == 2 else "", inline=True)

    session = get_session()
    reportObject = reports(
        report_type=report_type,
        message_id=target.id if isinstance(target, discord.Message) else None,
        user_id=target.id if isinstance(target, discord.Member) else None,
        reason=reason,
        status="Pending",
        claim_button_id=None,
        resolve_button_id=None,
        edit_reason_button_id=None,
        claimer_id=None,
        resolver_id=None,
        reporter_id=reporter.id,
        embed_message_id=None,
        last_updated=time.time(),
        report_time=time.time()
    )
    session.add(reportObject)
    session.flush()
    reportObject.claim_button_id = get_claim_button_id(int(reportObject.id))
    reportObject.resolve_button_id = get_resolve_button_id(int(reportObject.id))
    reportObject.edit_reason_button_id = get_edit_reason_button_id(int(reportObject.id))
    session.commit()

    # Send the embed to the report channel
    try:
        report_message = await report_channel.send(content=mod_role.mention, embed=embed)
        reportObject.embed_message_id = str(report_message.id)
        session.commit()
        view = ReportView(embed=embed, report_message=report_message, reportObject=reportObject)
        await report_message.edit(view=view)
    except discord.HTTPException as e:
        await interaction.response.send_message(
            get_report_failure_message(), ephemeral=True
        )

@tasks.loop(seconds=3600)  # Runs every hour (adjust as needed)
async def check_active_reports():
    """ 
    Check active reports and disable
    them if they are older than 48 hours.
    """
    await check_active() 

@check_active_reports.before_loop
async def before_check_active_reports():
    """ 
    Wait until the bot is ready before starting the loop.
    """
    await bot.wait_until_ready() 

async def check_active():
    """ 
    Check active reports and disable
    them if they are older than 48 hours.
    """
    session = get_session()
    active_reports = session.query(reports).filter_by(active=True).all()
    current_time = time.time()
    report_channel_id = int(get_report_channel())
    report_channel = bot.get_channel(report_channel_id)

    for report in active_reports:
        time.sleep(1)  # Prevent API spam
        if report.last_updated + 172800 < current_time:
            report.active = False

            # Fetch the report message
            if report.embed_message_id:
                report_message_id = int(report.embed_message_id)
                report_message = await report_channel.fetch_message(report_message_id)

                # Create a new view and disable buttons
                view = ReportView(embed=report_message.embeds[0], report_message=report_message, reportObject=report)
                for child in view.children:
                    time.sleep(0.2)
                    if isinstance(child, discord.ui.Button):
                        child.disabled = True

                # Commit changes to the database
                session.commit()

                # Edit the message with the updated view
                await report_message.edit(embed=report_message.embeds[0], view=view)
    
    session.commit()

@app_commands.context_menu(name="Report Message")
async def report_message(interaction: discord.Interaction, message: discord.Message):
    """ 
    Handle the 'Report Message' context menu command.
    """
    session = get_session()
    if session.query(reports).filter_by(message_id=message.id).first():
        await interaction.response.send_message(get_duplicate_message_report_message(), ephemeral=True)
        return
    await handle_report(interaction, message, "message")

@app_commands.context_menu(name="Report User")
async def report_user(interaction: discord.Interaction, user: discord.User):
    """ 
    Handle the 'Report User' context menu command.
    """
    session = get_session()
    report_object = session.query(reports).filter(reports.user_id == user.id, reports.report_time + int(get_user_report_timeout()) > time.time()).first()
    if report_object: # if the report has already been filed
        reason_modal = ReportReasonModal(max_length=int(get_max_reason_length()), duplicate=True)
        reason = await reason_modal.get_reason(interaction)
        report_channel_id = int(get_report_channel())
        report_channel = bot.get_channel(report_channel_id)
        report_message = await report_channel.fetch_message(report_object.embed_message_id)
        embed = report_message.embeds[0]
        for field in embed.fields:
            if field.value == report_object.reason:
                new_reason = f"{field.value}\n\n{reason}"
                embed.set_field_at(embed.fields.index(field), name=field.name, value=new_reason, inline=field.inline)
                report_object.reason = new_reason
                await report_message.edit(embed=embed)
                session.commit()
        await interaction.followup.send(get_duplicate_user_report_message(), ephemeral=True)
        return
    await handle_report(interaction, user, "user")

if __name__ == "__main__":
    token = get_token()
    if token:
        bot.run(token)
    else:
        print("Failed to get token.")
