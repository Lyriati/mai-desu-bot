import discord
from discord.ext import commands
from discord import app_commands
import random

class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Defines the slash command and its description in the Discord UI
    @app_commands.command(name="8ball", description="Input a query for Mai to calculate its probability.")
    # These two lines allow the bot to be installed to a user's account and used in DMs!
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def magic_eightball(self, interaction: discord.Interaction, question: str):
        
        # Mai's custom probability matrix
        responses = [
            # Positive
            "The probability approaches 1. Let's not waste time debating it.",
            "Calculated and confirmed. Yes.",
            "My data mining suggests a highly favorable outcome.",
            "Logically speaking, yes. Now can I get back to my soldering?",
            "Boolean check returns: TRUE.",
            
            # Neutral
            "Insufficient data. Provide better parameters next time.",
            "The algorithm is currently stuck in an infinite loop. Ask again later.",
            "My sisters are being loud and I can't concentrate on the calculation. Try again.",
            
            # Negative
            "Probability is exactly 0. A complete waste of time.",
            "I ran a simulation. The answer is a definitive no.",
            "False. Even a simple script could have told you that.",
            "Negative. Don't make me explain the math to you, it would take too long."
        ]
        
        reply = random.choice(responses)
        
        formatted_response = (
            f"> **Query Input:** {question}\n"
            f"> **Mai's Output:** {reply}"
        )
        
        # With slash commands, you reply to the 'interaction' object
        await interaction.response.send_message(formatted_response)

async def setup(bot):
    await bot.add_cog(EightBall(bot))