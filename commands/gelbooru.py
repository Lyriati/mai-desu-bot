import discord
from discord.ext import commands
from discord import app_commands
import urllib.parse
import random
import aiohttp
from collections import deque

class GelbooruMiner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Mai's memory cache. It holds exactly 3 URLs. 
        # When a 4th is added, the oldest one is forgotten.
        self.recent_images = deque(maxlen=3)

    @app_commands.command(name="gelbooru", description="Mine the image database using custom tags.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def fetch_image(self, interaction: discord.Interaction, tags: str):
        
        # Defer so the API has time to respond without timing out
        await interaction.response.defer()

        # Hardcode the safety filter and add sort:random to get a different batch every time
        safe_tags = f"{tags} rating:general sort:random"
        encoded_tags = urllib.parse.quote(safe_tags)
        
        # Gelbooru JSON API endpoint
        url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=50&tags={encoded_tags}"

        try:
            async with self.bot.session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send("api is throwing a fit. try again later.")
                    return
                
                # Some APIs return plain text even if it's JSON format, so we force parse it
                data = await resp.json(content_type=None)

            # Gelbooru returns a dictionary with a 'post' list
            posts = data.get('post', [])

            if not posts:
                await interaction.followup.send(f"my query for `{tags}` returned zero safe results. either it doesn't exist or your tags are weird.")
                return

            # Filter out images that are currently in Mai's short-term memory
            valid_posts = [p for p in posts if p.get('file_url') not in self.recent_images]

            # Failsafe: if the search only has like 2 results total, ignore the memory so it doesn't crash
            if not valid_posts:
                valid_posts = posts

            # Pick a random image from the valid list
            chosen_post = random.choice(valid_posts)
            image_url = chosen_post.get('file_url')
            post_id = chosen_post.get('id')

            # Add the chosen image to Mai's memory cache
            self.recent_images.append(image_url)

            # Build the visual output
            embed = discord.Embed(
                title="Image Extraction Complete",
                url=f"https://gelbooru.com/index.php?page=post&s=view&id={post_id}",
                color=0x1abc9c
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Tags: {tags} | Memory Cache: {len(self.recent_images)}/3")

            # Mai's casual dialogue options
            dialogue_options = [
                "mined this from the database. sfw filter is on so discord doesn't smite us.",
                "found one. if it looks weird, blame your tags, not my algorithm.",
                "here. i added a randomizer so you don't keep staring at the same image.",
                "database query successful. back to coding now.",
                "image extracted. taking up my bandwidth for this... honestly typical."
            ]

            await interaction.followup.send(content=random.choice(dialogue_options), embed=embed)

        except Exception as e:
            print(f"Gelbooru Fetch Error: {e}")
            await interaction.followup.send("critical error in my image scraper. server probably timed out.")

async def setup(bot):
    await bot.add_cog(GelbooruMiner(bot))