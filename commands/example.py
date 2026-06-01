from discord.ext import commands

class ExampleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping_command(self, ctx):
        """A simple test command."""
        # Because we set up self.session in main.py, you can access it anywhere like this:
        # async with self.bot.session.get('https://some-api.com/data') as response:
        #     ...
        await ctx.send(f'Pong! Latency: {round(self.bot.latency * 1000)}ms')

async def setup(bot):
    await bot.add_cog(ExampleCommands(bot))