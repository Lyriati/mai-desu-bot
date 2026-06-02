import discord
from discord.ext import commands
import random
import os

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.normal_file = os.path.join(os.getcwd(), 'responses', 'responses.txt')
        self.chaotic_file = os.path.join(os.getcwd(), 'responses', 'chaotic_responses.txt')
        
        # Mai's memory variable to track her last sent message
        self.last_reply = None 

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if "hi mai-desu" in message.content.lower():
            # 10% chance for a chaotic response
            is_chaotic = random.random() < 0.10
            target_file = self.chaotic_file if is_chaotic else self.normal_file
            
            try:
                with open(target_file, 'r', encoding='utf-8') as file:
                    responses = [line.strip() for line in file if line.strip()]
                
                if responses:
                    reply = random.choice(responses)
                    
                    # Prevent back-to-back duplicates (Safety check: ensures we have at least 2 lines to choose from)
                    if len(responses) > 1:
                        while reply == self.last_reply:
                            reply = random.choice(responses)
                    
                    # Save the new reply into Mai's memory before sending it
                    self.last_reply = reply
                    await message.channel.send(reply)
                else:
                    print(f"Warning: {target_file} is empty.")
                    
            except FileNotFoundError:
                print(f"Error: Could not find {target_file}")

async def setup(bot):
    await bot.add_cog(AutoResponder(bot))