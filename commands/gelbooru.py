import discord
from discord.ext import commands
from discord import app_commands
import urllib.parse
import random
import os
from collections import deque

class GelbooruMiner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_images = deque(maxlen=3)
        
        # Mai securely loads her clearance codes from the .env file
        self.api_key = os.getenv('GELBOORU_API_KEY')
        self.user_id = os.getenv('GELBOORU_USER_ID')

    @app_commands.command(name="gelbooru", description="Mine the image database using custom tags.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fetch_image(self, interaction: discord.Interaction, tags: str):
        
        await interaction.response.defer()

        # Failsafe: Mai complains if you forgot to add the keys to the .env file
        if not self.api_key or not self.user_id:
            await interaction.followup.send("i'm throwing a 401 because you didn't give me an api key. update the .env file or i literally cannot do this.")
            return

        safe_tags = f"{tags} rating:general sort:random"
        encoded_tags = urllib.parse.quote_plus(safe_tags)
        
        # Mai injects her VIP credentials into the URL so Gelbooru lets her in
        url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=50&tags={encoded_tags}&api_key={self.api_key}&user_id={self.user_id}"

        headers = {
            "User-Agent": "Mai-desu/1.0 Discord Bot (Personal Project)"
        }

        try:
            async with self.bot.session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"api is throwing a fit (HTTP {resp.status}). try again later.")
                    return
                
                data = await resp.json(content_type=None)

            posts = data.get('post', [])

            if not posts:
                await interaction.followup.send(f"my query for `{tags}` returned zero safe results. either it doesn't exist or your tags are weird.")
                return

            valid_posts = [p for p in posts if p.get('file_url') not in self.recent_images]

            if not valid_posts:
                valid_posts = posts

            chosen_post = random.choice(valid_posts)
            image_url = chosen_post.get('file_url')
            post_id = chosen_post.get('id')

            self.recent_images.append(image_url)

            embed = discord.Embed(
                title="Image Extraction Complete",
                url=f"https://gelbooru.com/index.php?page=post&s=view&id={post_id}",
                color=0x1abc9c
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Tags: {tags} | Memory Cache: {len(self.recent_images)}/3")

            dialogue_options = [
                "bypassed the firewall and mined this. sfw filter is on.",
                "found one. if it looks weird, blame your tags, not my algorithm.",
                "database clearance accepted. here is your randomly sorted query.",
                "image extracted. taking up my bandwidth for this... honestly typical."
            ]

            await interaction.followup.send(content=random.choice(dialogue_options), embed=embed)

        except Exception as e:
            print(f"Gelbooru Fetch Error: {e}")
            await interaction.followup.send("critical error in my image scraper. server probably timed out.")

async def setup(bot):
    await bot.add_cog(GelbooruMiner(bot))