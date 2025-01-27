import discord
from discord.ext import commands
from discord import app_commands
from util import Role, has_role
from models import reports, get_session, reports
from util import get_report_channel
from main import ReportView
import time

class searchPastReports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command()
    @has_role(Role.mod)
    async def searchReports(self, ctx, 
                            messageID:int=None, 
                            userID:int=None, userObject:discord.Member|discord.User=None, 
                            reporterID:int=None, reporterObject:discord.Member|discord.User=None,
                            claimerID:int=None, claimerObject:discord.Member|discord.User=None,
                            resolverID:int=None, resolverObject:discord.Member|discord.User=None,
                            reportType:app_commands.Choice[str]=None, status:bool=None, 
                            active:bool=None, 
                            before:float=None, after:float=None,
                            modActionsTaken:str="", reason:str="", contains:bool=None, exact:bool=None):
        pass
        

async def setup(bot):
    await bot.add_cog(searchPastReports(bot))