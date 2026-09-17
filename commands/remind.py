import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re

class Remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="remind", description="Forces Mai to act as your unpaid secretary.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def remind(self, interaction: discord.Interaction, time: str, task: str):
        
        # Mai's regex parser extracts the number and the letter (s, m, h, d)
        match = re.match(r'^(\d+)([smhd])$', time.lower().strip())
        if not match:
            await interaction.response.send_message("invalid time format. use things like `10m`, `2h`, or `45s`. don't make this complicated.")
            return
        
        amount = int(match.group(1))
        unit = match.group(2)
        
        multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        total_seconds = amount * multipliers[unit]
        
        if total_seconds > 86400 * 7:
            await interaction.response.send_message("i am not keeping a background thread running for more than a week. my ram is for compiling, not your long-term memory.")
            return

        await interaction.response.send_message(f"timer set for {time}. i am not your personal secretary, but i will ping you when it's done.")
        
        # The background countdown thread
        async def background_reminder():
            await asyncio.sleep(total_seconds)
            try:
                # Mai tries to DM you directly first
                await interaction.user.send(f"hey {interaction.user.mention}, you told me to remind you to **{task}**. do it now before you interrupt my coding.")
            except discord.Forbidden:
                # If your DMs are closed, she falls back to pinging you in the channel you used
                try:
                    await interaction.channel.send(f"hey {interaction.user.mention}, your dms are locked so i have to ping you here. do your task: **{task}**.")
                except:
                    pass
                    
        self.bot.loop.create_task(background_reminder())

async def setup(bot):
    await bot.add_cog(Remind(bot))