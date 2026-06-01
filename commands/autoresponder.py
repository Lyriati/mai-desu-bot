import discord
from discord.ext import commands
import random
import os

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dynamically build the path to the responses file
        self.responses_file = os.path.join(os.getcwd(), 'responses', 'responses.txt')

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself to prevent infinite loops
        if message.author == self.bot.user:
            return

        # Check for the trigger phrase (converted to lowercase for easier matching)
        if "hi mai-desu" in message.content.lower():
            try:
                # Read the file every time so it updates without restarting the bot
                with open(self.responses_file, 'r', encoding='utf-8') as file:
                    # Strip whitespace and ignore empty lines
                    responses = [line.strip() for line in file if line.strip()]
                
                if responses:
                    # Choose a perfectly random response and send it
                    reply = random.choice(responses)
                    await message.channel.send(reply)
                else:
                    print("Warning: responses.txt is empty.")
                    
            except FileNotFoundError:
                print(f"Error: Could not find {self.responses_file}")

# This setup function is required for discord.py to load the Cog
async def setup(bot):
    await bot.add_cog(AutoResponder(bot))