import discord
from discord.ext import commands
import os
import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MaiDesuBot(commands.Bot):
    def __init__(self):
        # Set up intents (Message Content intent is REQUIRED for reading messages)
        intents = discord.Intents.default()
        intents.message_content = True
        
        # Initialize the bot with a prefix (e.g., "!")
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        """This runs once when the bot starts. Perfect for loading commands and creating sessions."""
        # Create a shared web session for future HTML/API requests
        self.session = aiohttp.ClientSession()

        # Dynamically load all python files in the /commands/ directory
        for filename in os.listdir('./commands'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'commands.{filename[:-3]}')
                    print(f"Loaded extension: {filename}")
                except Exception as e:
                    print(f"Failed to load extension {filename}: {e}")

    async def close(self):
        """Cleanup when the bot shuts down."""
        # Safety check: Only close the session if it was successfully created
        if hasattr(self, 'session'):
            await self.session.close()
        await super().close()

    async def on_ready(self):
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('Ready to serve!')

# Instantiate and run the bot
bot = MaiDesuBot()

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))