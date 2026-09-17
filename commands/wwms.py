import discord
from discord.ext import commands
from discord import app_commands
import random

class WhatWouldMaiSay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="whatwouldmaisay", description="Summon Mai for a random, unprompted thought.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def wwms(self, interaction: discord.Interaction):
        
        # Casual, deadpan teen-programmer thoughts
        unprompted_thoughts = [
            "polka lost her phone again. if anyone asks i didn't see it",
            "bro who left a whole ass kimono on my secondary monitor...",
            "my sisters are screaming over a gacha pull im locking my bedroom door",
            "akira is literally scaling the outside wall of the building right now. use the stairs man",
            "why is the club room so loud i just want to optimize my redstone tick rate in peace",
            "if yukuri tries to drag me to another overpriced cafe im faking a system crash",
            "currently hiding under the desk until everyone leaves. do not perceive me",
            "i love math but trying to explain basic algebra to polka is making my brain bleed",
            "shion is supposed to be sleeping but her steam status says otherwise... interesting",
            "my social battery is at 4%. logging off to go solder things",
            "the urge to reformat the shared club drive because the folder structure gives me physical pain",
            "i am deducting polka's snack budget for every spontaneous dance move she does today",
            "minecraft server is lagging again someone gave the sheep too much dedotated wam",
            "miracle please stop touching my soldering iron you are going to burn your fingers off",
            "why do people talk so much when we could literally just send code snippets",
            "noriko disappeared again. honestly valid strategy im doing that next",
            "i got 100 on the test. no i will not tutor you, time is money"
        ]
        
        reply = random.choice(unprompted_thoughts)
        await interaction.response.send_message(reply)

async def setup(bot):
    await bot.add_cog(WhatWouldMaiSay(bot))