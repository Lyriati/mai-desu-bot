import discord
from discord.ext import commands
import urllib.parse
import re

class WikiMiner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wiki", aliases=["mine", "data"])
    async def mine_wiki(self, ctx, *, query: str = None):
        """Mines the Love Live! Wiki for data."""
        
        # Mai hates wasting time on empty queries
        if not query:
            await ctx.send("You didn't specify a search parameter. I can't mine data from nothing.")
            return

        # Step 1: Use the Fandom API to search for the exact page title
        search_url = f"https://love-live.fandom.com/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json&srlimit=1"

        try:
            async with self.bot.session.get(search_url) as resp:
                if resp.status != 200:
                    await ctx.send("The wiki database is currently throwing HTTP errors. Try again later.")
                    return
                search_data = await resp.json()

            # If the search returns absolutely nothing
            if not search_data['query']['search']:
                await ctx.send(f"My query for `{query}` returned 0 results. Check your spelling and stop wasting my time.")
                return

            title = search_data['query']['search'][0]['title']

            # Step 2: Fetch the clean introductory text AND the raw page code (to find the release date)
            content_url = f"https://love-live.fandom.com/api.php?action=query&prop=extracts|revisions&exintro=true&explaintext=true&rvprop=content&rvslots=main&titles={urllib.parse.quote(title)}&format=json"

            async with self.bot.session.get(content_url) as resp:
                content_data = await resp.json()

            pages = content_data['query']['pages']
            page_id = list(pages.keys())[0]
            page_info = pages[page_id]

            # Grab the clean summary paragraph provided by the API
            summary = page_info.get('extract', 'No summary data found in the database.').strip()

            # Prevent massive walls of text if the intro is too long for Discord Embeds
            summary = re.sub(r'\n+', '\n\n', summary)
            if len(summary) > 1000:
                summary = summary[:997] + "..."

            # Step 3: Dig into the raw code (Wikitext) to find the release date
            release_date = None
            if 'revisions' in page_info:
                wikitext = page_info['revisions'][0]['slots']['main']['*']
                
                # Use Regular Expressions (Regex) to search for the "released =" parameter in the wiki's Infobox
                match = re.search(r'\|\s*released?\s*=\s*(.*?)(?=\n\||\n}})', wikitext, re.IGNORECASE)
                
                if match:
                    # Fandom wiki dates often have link brackets like [[September 2]], [[2020]]
                    # This cleans the brackets out so it just reads "September 2, 2020"
                    raw_date = match.group(1).strip()
                    clean_date = re.sub(r'\[\[(.*?)\]\]', lambda m: m.group(1).split('|')[-1], raw_date)
                    release_date = clean_date.strip()

            # Step 4: Build a beautiful, logical UI box for the data (Discord Embed)
            embed = discord.Embed(
                title=f"Data Extraction: {title}",
                url=f"https://love-live.fandom.com/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                description=summary,
                color=0x1abc9c # A clean, computerized teal color
            )

            # If our data miner found a release date, add it to the bottom of the embed
            if release_date:
                embed.add_field(name="Release Date", value=release_date, inline=False)

            embed.set_footer(text="Data efficiently mined from Love Live! Wiki.")

            # Send Mai's dialogue and the formatted data box
            await ctx.send("Query complete. I bypassed the superficial fluff and extracted the data. Read it quickly.", embed=embed)

        except Exception as e:
            print(f"Wiki Miner Error: {e}")
            await ctx.send("A critical error occurred while parsing the wiki data. My algorithms have been interrupted.")

async def setup(bot):
    await bot.add_cog(WikiMiner(bot))