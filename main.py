#main.py
import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
from util import get_token
from util import get_report_channel, get_report_title, get_report_description, get_reports_color, get_mod_role, get_max_reason_length



bot = commands.AutoShardedBot(intents=discord.Intents.all(), command_prefix="!")

# Load cogs
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
    commandString = "\n".join(commandList)
    print(f"Registered commands:\n{commandString}")

@bot.event
async def on_ready():
    await load_cogs()
    print(f"Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

class reportReason(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
    async def ask_reason(interaction: discord.Interaction) -> str:
        """
        Prompt the user to provide a reason for the report if they choose to.

        Returns:
            str: The reason provided by the user, or "No reason provided." if they skip.
        """
        modal = discord.ui.Modal(title="Add a Reason for the Report")

        reason_input = discord.ui.TextInput(
            label="Reason (Optional)",
            style=discord.TextStyle.long,
            placeholder="Provide a reason for this report...",
            required=False,
            max_length=int(get_max_reason_length())
        )

        modal.add_item(reason_input)

        await interaction.response.send_modal(modal)

        await modal.wait()  # Wait for the user to complete the modal

        return reason_input.value or "No reason provided."
    
    def callback(self, interaction: discord.Interaction):
        self.value = interaction.data["values"][0]
        self.stop()

@app_commands.context_menu(name="Report Message")
@app_commands.allowed_installs(guilds=True)
async def report_message(interaction: discord.Interaction, message: discord.Message):
    modRoleID = int(get_mod_role())
    modRole = interaction.guild.get_role(modRoleID)
    ReportChannelID = int(get_report_channel())
    ReportChannel = interaction.guild.get_channel(ReportChannelID)
    reporter = interaction.user
    messageAuthor = message.author
    messageContent = message.content
    messageChannel = message.channel
    messageGuild = message.guild
    messageID = message.id
    rgb = get_reports_color()

    # Ask the user for a reason
    reason = await reportReason.ask_reason(interaction)
    
    print(discord.Color.from_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2])))

    embed = discord.Embed(
        title=get_report_title(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
        description=f"{get_report_description(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID)}\n\n**Reason:** {reason}",
        color=discord.Color.from_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    )

    await ReportChannel.send(f"{modRole.mention}", embed=embed)

@app_commands.context_menu(name="Report User")
@app_commands.allowed_installs(guilds=True)
async def report_user(interaction: discord.Interaction, user: discord.User):
    modRoleID = int(get_mod_role())
    modRole = interaction.guild.get_role(modRoleID)
    ReportChannelID = int(get_report_channel())
    ReportChannel = interaction.guild.get_channel(ReportChannelID)
    reporter = interaction.user
    messageAuthor = user
    messageContent = "User"
    messageChannel = None
    messageGuild = interaction.guild
    messageID = None
    rgb = get_reports_color()

    # Ask the user for a reason
    reason = await reportReason.ask_reason(interaction)
    
    print(discord.Color.from_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2])))

    embed = discord.Embed(
        title=get_report_title(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID),
        description=f"{get_report_description(reporter, messageAuthor, messageContent, messageChannel, messageGuild, messageID)}\n\n**Reason:** {reason}",
        color=discord.Color.from_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    )

    await ReportChannel.send(f"{modRole.mention}", embed=embed)

if __name__ == "__main__":
    token = get_token()
    if token:
        bot.run(token)
    else:
        print("Failed to get token.")