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
        
        if not query:
            await ctx.send("You didn't specify a search parameter. I can't mine data from nothing.")
            return

        search_url = f"https://love-live.fandom.com/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json&srlimit=1"

        try:
            async with self.bot.session.get(search_url) as resp:
                if resp.status != 200:
                    await ctx.send("The wiki database is currently throwing HTTP errors. Try again later.")
                    return
                search_data = await resp.json()

            if not search_data['query']['search']:
                await ctx.send(f"My query for `{query}` returned 0 results. Check your spelling and stop wasting my time.")
                return

            title = search_data['query']['search'][0]['title']

            # Note: Changed 'true' to '1' as MediaWiki API prefers integers for booleans
            content_url = f"https://love-live.fandom.com/api.php?action=query&prop=extracts|revisions&exintro=1&explaintext=1&rvprop=content&rvslots=main&titles={urllib.parse.quote(title)}&format=json"

            async with self.bot.session.get(content_url) as resp:
                content_data = await resp.json()

            pages = content_data['query']['pages']
            page_id = list(pages.keys())[0]
            page_info = pages[page_id]

            # 1. Try to politely ask the API for the extract first
            summary = page_info.get('extract', '').strip()

            # 2. Dig into the raw code (Wikitext)
            release_date = None
            if 'revisions' in page_info:
                wikitext = page_info['revisions'][0]['slots']['main']['*']
                
                # --- MAI'S CUSTOM OVERRIDE ---
                # If the API gave us nothing, we bypass it and parse the raw code ourselves
                if not summary:
                    clean_text = wikitext
                    
                    # Recursively strip out all messy {{Infoboxes}} and templates
                    while re.search(r'\{\{[^{}]*\}\}', clean_text):
                        clean_text = re.sub(r'\{\{[^{}]*\}\}', '', clean_text)
                    
                    # Read the page line by line to find the first actual sentence
                    for line in clean_text.split('\n'):
                        line = line.strip()
                        # Skip empty lines, table rows, and leftover formatting junk
                        if line and not line.startswith(('|', '{', '<', '!', '=', '[[File:')):
                            # Clean up bold/italics
                            line = re.sub(r"''+", "", line)
                            # Clean up wiki links (e.g., [[Target|Text]] becomes just Text)
                            line = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', line)
                            # Remove stray HTML tags
                            line = re.sub(r'<[^>]+>', '', line)
                            
                            summary = line
                            break # We found the intro, stop reading!

                # 3. Look for the Release Date
                match = re.search(r'\|\s*released?\s*=\s*(.*?)(?=\n\||\n}})', wikitext, re.IGNORECASE)
                if match:
                    raw_date = match.group(1).strip()
                    clean_date = re.sub(r'\[\[(.*?)\]\]', lambda m: m.group(1).split('|')[-1], raw_date)
                    release_date = clean_date.strip()

            # Fallback if the page is completely broken
            if not summary:
                summary = "Error: Fandom's database formatting is completely illogical. My manual override failed to find a summary."
            
            # Format massive text blocks
            summary = re.sub(r'\n+', '\n\n', summary)
            if len(summary) > 1000:
                summary = summary[:997] + "..."

            # 4. Build the Output Box
            embed = discord.Embed(
                title=f"Data Extraction: {title}",
                url=f"https://love-live.fandom.com/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                description=summary,
                color=0x1abc9c
            )

            if release_date:
                embed.add_field(name="Release Date", value=release_date, inline=False)

            embed.set_footer(text="Data efficiently mined from Love Live! Wiki.")

            # Mai's Dialogue
            await ctx.send("Query complete. I bypassed the superficial fluff and extracted the data. Read it quickly.", embed=embed)

        except Exception as e:
            print(f"Wiki Miner Error: {e}")
            await ctx.send("A critical error occurred while parsing the wiki data. My algorithms have been interrupted.")

async def setup(bot):
    await bot.add_cog(WikiMiner(bot))