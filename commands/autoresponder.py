import discord
from discord.ext import commands
import random
import os

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Define paths for both files
        self.normal_file = os.path.join(os.getcwd(), 'responses', 'responses.txt')
        self.chaotic_file = os.path.join(os.getcwd(), 'responses', 'chaotic_responses.txt')

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        if "hi mai-desu" in message.content.lower():
            # Roll a random number between 0.0 and 1.0
            # A 0.10 means there is a 10% chance for a chaotic response
            is_chaotic = random.random() < 0.10
            
            # Select which file to open based on the roll
            target_file = self.chaotic_file if is_chaotic else self.normal_file
            
            try:
                # Read the chosen file dynamically
                with open(target_file, 'r', encoding='utf-8') as file:
                    responses = [line.strip() for line in file if line.strip()]
                
                if responses:
                    reply = random.choice(responses)
                    await message.channel.send(reply)
                else:
                    print(f"Warning: {target_file} is empty.")
                    
            except FileNotFoundError:
                print(f"Error: Could not find {target_file}")

async def setup(bot):
    await bot.add_cog(AutoResponder(bot))