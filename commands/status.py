import discord
from discord.ext import commands
from discord import app_commands
import psutil
import time

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Records the exact timestamp when Mai boots up
        self.start_time = time.time()

    @app_commands.command(name="status", description="Check Mai's physical server hardware diagnostics.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Ping the physical Ubuntu hardware
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        
        # Calculate uptime
        uptime_seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"
        
        # Calculate Discord WebSocket latency
        ping = round(self.bot.latency * 1000)
        
        embed = discord.Embed(title="System Diagnostics", color=0x1abc9c)
        embed.add_field(name="CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="RAM Usage", value=f"{ram_usage}%", inline=True)
        embed.add_field(name="WebSocket Ping", value=f"{ping}ms", inline=True)
        embed.add_field(name="Process Uptime", value=uptime_str, inline=True)
        
        reply = f"diagnostics run. cpu is at {cpu_usage}%, ram is at {ram_usage}%. if i'm responding slowly, it's because discord's api is trash (ping is {ping}ms), not my code."
        
        await interaction.followup.send(content=reply, embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))