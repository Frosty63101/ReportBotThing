import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
from matplotlib.artist import get
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
    def __init__(self, embed: discord.Embed, report_message: discord.Message):
        # 172800 seconds = 48 hours
        super().__init__(timeout=172800)
        
        # Save the embed and the original report message so we can edit later
        self.embed = embed
        self.reportMessage = report_message
        
        # Store the status so it can be updated as buttons are pressed
        self.status = "Pending"
    
    async def on_timeout(self):
        """
        This is automatically called when the view's timeout is reached (after 48 hours).
        Here, you can disable the buttons or modify the embed/message as needed.
        """
        # Disable all buttons
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        # Optionally, edit the message to indicate it timed out
        await self.reportMessage.edit(
            content="This report is no longer active (timed out).",
            view=self
        )
    
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
        # Disable this button
        button.disabled = True
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
        
        # Also disable the 'Claim' button if it isn't already
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.label == "Claim":
                child.disabled = True
        
        # Ask for moderator action via the modal
        modAction = modActionModal()
        action = await modAction.get_action(interaction)
        
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

    # Send the embed to the report channel
    try:
        report_message = await report_channel.send(content=mod_role.mention, embed=embed)
        view = ReportView(embed=embed, report_message=report_message)
        await report_message.edit(view=view)
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"Failed to send the report due to an error: {e}", ephemeral=True
        )

@app_commands.context_menu(name="Report Message")
async def report_message(interaction: discord.Interaction, message: discord.Message):
    await handle_report(interaction, message, "message")

@app_commands.context_menu(name="Report User")
async def report_user(interaction: discord.Interaction, user: discord.User):
    await handle_report(interaction, user, "user")

if __name__ == "__main__":
    token = get_token()
    if token:
        bot.run(token)
    else:
        print("Failed to get token.")
