import discord
from discord.ext import commands
from discord import app_commands
import random

class Decide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="decide", description="Eliminates human indecision by picking an option for you.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def decide(self, interaction: discord.Interaction, options: str):
        
        # Split by comma. If they didn't use commas, split by spaces instead.
        choices = [opt.strip() for opt in options.split(',')] if ',' in options else options.split()
        
        if len(choices) < 2:
            await interaction.response.send_message("you need to give me at least two options separated by commas. i can't run a selection algorithm on a single variable.")
            return
        
        picked = random.choice(choices)
        
        reply = (
            "polka spent 45 minutes deciding what snack to buy yesterday. i wrote this script to eliminate human indecision.\n\n"
            f"you are doing **{picked}**. don't argue with the algorithm."
        )
        await interaction.response.send_message(reply)

async def setup(bot):
    await bot.add_cog(Decide(bot))