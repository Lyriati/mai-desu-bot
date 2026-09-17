import discord
from discord.ext import commands
from discord import app_commands
import urllib.parse
import re

class WikiMiner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command setup and User App permissions
    @app_commands.command(name="wiki", description="Mines the Love Live! Wiki for character or song data.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mine_wiki(self, interaction: discord.Interaction, query: str):
        
        # Mai immediately tells Discord she is calculating, preventing timeout errors
        await interaction.response.defer()

        search_url = f"https://love-live.fandom.com/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json&srlimit=1"

        try:
            async with self.bot.session.get(search_url) as resp:
                if resp.status != 200:
                    # Because we deferred, we MUST use followup.send instead of response.send_message
                    await interaction.followup.send("The wiki database is currently throwing HTTP errors. Try again later.")
                    return
                search_data = await resp.json()

            if not search_data['query']['search']:
                await interaction.followup.send(f"My query for `{query}` returned 0 results. Check your spelling and stop wasting my time.")
                return

            title = search_data['query']['search'][0]['title']

            content_url = f"https://love-live.fandom.com/api.php?action=query&prop=extracts|revisions&exintro=1&explaintext=1&rvprop=content&rvslots=main&titles={urllib.parse.quote(title)}&format=json"

            async with self.bot.session.get(content_url) as resp:
                content_data = await resp.json()

            pages = content_data['query']['pages']
            page_id = list(pages.keys())[0]
            page_info = pages[page_id]

            summary = page_info.get('extract', '').strip()
            release_date = None
            
            if 'revisions' in page_info:
                wikitext = page_info['revisions'][0]['slots']['main']['*']
                
                # Mai's custom regex override
                if not summary:
                    clean_text = wikitext
                    
                    # 1. Strip out citation footnotes (<ref> tags) completely
                    clean_text = re.sub(r'<ref[^>]*>.*?</ref>', '', clean_text, flags=re.DOTALL)
                    clean_text = re.sub(r'<ref[^>]*/>', '', clean_text)
                    
                    # 2. Recursively strip out all messy {{Infoboxes}} and templates
                    while re.search(r'\{\{[^{}]*\}\}', clean_text):
                        clean_text = re.sub(r'\{\{[^{}]*\}\}', '', clean_text)
                    
                    # Read the page line by line to find the first actual sentence
                    for line in clean_text.split('\n'):
                        line = line.strip()
                        if line and not line.startswith(('|', '{', '<', '!', '=', '[[File:')):
                            line = re.sub(r"''+", "", line)
                            line = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', line)
                            line = re.sub(r'<[^>]+>', '', line)
                            
                            summary = line
                            break 

                # Look for the Release Date
                match = re.search(r'\|\s*released?\s*=\s*(.*?)(?=\n\||\n}})', wikitext, re.IGNORECASE)
                if match:
                    raw_date = match.group(1).strip()
                    clean_date = re.sub(r'\[\[(.*?)\]\]', lambda m: m.group(1).split('|')[-1], raw_date)
                    release_date = clean_date.strip()

            if not summary:
                summary = "Error: Fandom's database formatting is completely illogical. My manual override failed to find a summary."
            
            summary = re.sub(r'\n+', '\n\n', summary)
            if len(summary) > 1000:
                summary = summary[:997] + "..."

            embed = discord.Embed(
                title=f"Data Extraction: {title}",
                url=f"https://love-live.fandom.com/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                description=summary,
                color=0x1abc9c
            )

            if release_date:
                embed.add_field(name="Release Date", value=release_date, inline=False)

            embed.set_footer(text="Data efficiently mined from Love Live! Wiki.")

            # Send the final result
            await interaction.followup.send(content="Query complete. I bypassed the superficial fluff and extracted the data. Read it quickly.", embed=embed)

        except Exception as e:
            print(f"Wiki Miner Error: {e}")
            await interaction.followup.send("A critical error occurred while parsing the wiki data. My algorithms have been interrupted.")

async def setup(bot):
    await bot.add_cog(WikiMiner(bot))