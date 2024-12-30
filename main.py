import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
import time

from flask import session
from models import get_claim_button_id, get_resolve_button_id, get_edit_reason_button_id, get_report_by_id, get_report_by_message_id, get_report_by_user_id, get_session, reports
from util import (
    get_token, get_report_channel, get_report_title,
    get_report_description, get_reports_color, 
    get_mod_role, get_max_reason_length
)

bot = commands.AutoShardedBot(intents=discord.Intents.all(), command_prefix="!")

async def load_cogs():
    for cog in os.listdir("cogs"):
        if cog.endswith(".py"):
            cog = cog[:-3]
            try:
                await bot.load_extension(f"cogs.{cog}")
                print(f"Loaded {cog} cog.")
            except Exception as e:
                print(f"Failed to load {cog} cog: {e}")
    
    bot.tree.add_command(report_message)
    bot.tree.add_command(report_user)
    
    commandList = [command.name for command in bot.commands]
    commandList += [command.name for command in bot.tree.walk_commands()]
    commandList.sort()
    print(f"Registered commands:\n{commandList}")

@bot.event
async def on_ready():
    await load_cogs()
    print(f"Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    check_active()
    # load past views that are active
    session = get_session()
    active_reports = session.query(reports).filter_by(active=True).all()
    for report in active_reports:
        if report.embed_message_id:
            try:
                report_channel_id = int(get_report_channel())
                report_channel = bot.get_channel(report_channel_id)
                report_message = await report_channel.fetch_message(report.embed_message_id)
                embed = report_message.embeds[0]
                view = ReportView(embed=embed, report_message=report_message, reportObject=report)
                await report_message.edit(view=view)
            except discord.HTTPException as e:
                print(f"Failed to load active report: {e}")
    session.close()

class ReportReasonModal(discord.ui.Modal):
    def __init__(self, max_length: int):
        super().__init__(title="Add a Reason for the Report")
        self.reason = discord.ui.TextInput(
            label="Reason (Optional)",
            style=discord.TextStyle.long,
            placeholder="Provide a reason for this report...",
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
        session.close()
        if not self.reportObject.claim_button_active:
            self.claimButton.disabled = True
        if not self.reportObject.resolve_button_active:
            self.resolveButton.disabled = True
        
    
    async def update_embed(self, interaction: discord.Interaction, newStatus: str):
        """
        Updates the embed description with the latest status and changes the color.
        """
        # Replace the status text
        print("updating embed")
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
        session.close()
        
        # (Example) set color based on status
        if "Claimed" in newStatus:
            rgb = get_reports_color("claimed_color")
        elif "Resolved" in newStatus:
            rgb = get_reports_color("resolved_color")
        else:
            rgb = get_reports_color()
        self.embed.color = discord.Color.from_rgb(*rgb)
        
        # Apply updates by editing the message
        await self.reportMessage.edit(embed=self.embed, view=self)
    
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary)
    async def claimButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Marks this report as claimed by whoever pressed the button.
        Disables the 'Claim' button to prevent it from being pressed again.
        """
        check_active()
        # Disable this button
        button.disabled = True
        session = get_session()
        self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
        self.reportObject.claimer_id = interaction.user.id
        self.reportObject.last_updated = time.time()
        self.reportObject.claim_button_active = False
        session.commit()
        session.close()
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
        check_active()
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
        self.reportObject.status = action
        self.reportObject = session.query(reports).filter_by(id=self.reportObject.id).first()
        self.reportObject.resolver_id = interaction.user.id
        self.reportObject.last_updated = time.time()
        self.reportObject.status = "Resolved"
        session.commit()
        session.close()
        
        # Update the embed with the resolution status
        await self.update_embed(
            interaction,
            f"Resolved by {interaction.user.mention} \nwith action: {action}"
        )
        
        # Edit the message with the final state
        await self.reportMessage.edit(embed=self.embed, view=self)


async def handle_report(
    interaction: discord.Interaction,
    target: discord.User | discord.Message,
    report_type: str,
):
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
        description = get_report_description(reporter, target, None, reason)
        title = get_report_title(reporter, target, None, reason)
    else:
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
        user_id=target.id if isinstance(target, discord.User) else None,
        reason=reason,
        status="Pending",
        claim_button_id=None,
        resolve_button_id=None,
        edit_reason_button_id=None,
        claimer_id=None,
        resolver_id=None,
        reporter_id=reporter.id,
        embed_message_id=None,
        last_updated=time.time()
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
            f"Failed to send the report due to an error: {e}", ephemeral=True
        )
    session.close()

def check_active():
    session = get_session()
    active_reports = session.query(reports).filter_by(active=True).all()
    curent_time = time.time()
    for report in active_reports:
        if report.last_updated + 172800 < curent_time:
            report.active = False
            session.commit()
    session.close()

@app_commands.context_menu(name="Report Message")
async def report_message(interaction: discord.Interaction, message: discord.Message):
    check_active()
    await handle_report(interaction, message, "message")

@app_commands.context_menu(name="Report User")
async def report_user(interaction: discord.Interaction, user: discord.User):
    check_active()
    await handle_report(interaction, user, "user")

if __name__ == "__main__":
    token = get_token()
    if token:
        bot.run(token)
    else:
        print("Failed to get token.")
