import discord
from discord.ext import commands
import random

class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # We add an alias so the user can type !8ball or !eightball
    @commands.command(name="8ball", aliases=["eightball"])
    async def magic_eightball(self, ctx, *, question: str = None):
        """Input a query for Mai to calculate its probability."""
        
        # Mai hates wasting time. If they don't ask a question, she calls them out.
        if question is None:
            await ctx.send("You didn't provide a parameter (question). Please don't waste my time.")
            return

        # Mai's custom probability matrix (Positive, Neutral, and Negative responses)
        responses = [
            # --- Positive / Yes ---
            "The probability approaches 1. Let's not waste time debating it.",
            "Calculated and confirmed. Yes.",
            "My data mining suggests a highly favorable outcome.",
            "It's as beautiful and true as a perfect mathematical equation. Yes.",
            "Logically speaking, yes. Now can I get back to my soldering?",
            "Boolean check returns: TRUE.",
            
            # --- Neutral / Try Again ---
            "Insufficient data. Provide better parameters next time.",
            "The algorithm is currently stuck in an infinite loop. Ask again later.",
            "My sisters are being loud and I can't concentrate on the calculation. Try again.",
            "Compiling... Error. Ask again when you have a more logical query.",
            "I'm too busy optimizing my Minecraft server to answer that right now.",
            
            # --- Negative / No ---
            "Probability is exactly 0. A complete waste of time.",
            "I ran a simulation. The answer is a definitive no.",
            "False. Even a simple script could have told you that.",
            "No. This query is as superficial as celebrity gossip.",
            "Negative. Don't make me explain the math to you, it would take too long.",
            "Absolutely not. I would rather listen to girl-to-girl talk than entertain this."
        ]
        
        # Pick a random response from Mai's list
        reply = random.choice(responses)
        
        # Format the output to look like a clean, logical readout
        formatted_response = (
            f"> {reply}"
        )
        
        await ctx.send(formatted_response)

async def setup(bot):
    await bot.add_cog(EightBall(bot))