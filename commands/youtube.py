import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import sqlite3
import re
import os

class YouTubeNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'youtube_subs.db')
        self.init_db()
        self.check_youtube_feeds.start() # Starts the background loop

    def init_db(self):
        # Creates a local database file on your Ubuntu server to track everything permanently
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER,
                channel_id TEXT,
                channel_name TEXT,
                last_video_id TEXT,
                PRIMARY KEY (user_id, channel_id)
            )
        ''')
        conn.commit()
        conn.close()

async def get_channel_info(self, url: str):
        # Mai's failsafe: if you don't give her a real URL, she builds one assuming it's a channel handle
        if not url.startswith(('http://', 'https://')):
            clean_handle = url.lstrip('@')
            url = f"https://www.youtube.com/@{clean_handle}"

        # Mai forcefully rips the hidden channel ID out of the webpage's source code
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        try:
            async with self.bot.session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return None, None
                html = await resp.text()
                
                # Scrape the unique 24-character Channel ID and the channel's display name
                id_match = re.search(r'itemprop="channelId" content="(UC[a-zA-Z0-9_-]{22})"', html)
                name_match = re.search(r'itemprop="name" content="(.*?)"', html)
                
                if not id_match:
                    return None, None
                    
                return id_match.group(1), (name_match.group(1) if name_match else "Unknown Channel")
        except Exception as e:
            print(f"YouTube Scraper Error: {e}")
            return None, None

    async def get_latest_video(self, channel_id: str):
        # Ping YouTube's hidden RSS feed to bypass the official API quotas
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        async with self.bot.session.get(rss_url) as resp:
            if resp.status != 200:
                return None, None
            xml_data = await resp.text()
            
            # Extract the newest video ID and Title using regex
            vid_match = re.search(r'<yt:videoId>(.*?)</yt:videoId>', xml_data)
            title_match = re.search(r'<title>(.*?)</title>', xml_data)
            
            if vid_match and title_match:
                return vid_match.group(1), title_match.group(1)
            return None, None

    # --- COMMAND GROUP ---
    youtube_group = app_commands.Group(name="youtube", description="Manage YouTube DM notifications.")

    @youtube_group.command(name="subscribe", description="Subscribe to a YouTube channel's uploads.")
    async def yt_subscribe(self, interaction: discord.Interaction, channel_url: str):
        await interaction.response.defer()
        
        channel_id, channel_name = await self.get_channel_info(channel_url)
        if not channel_id:
            await interaction.followup.send("i couldn't parse a channel id from that link. give me a raw channel URL or a video link from the channel.")
            return

        # Fetch the current newest video so Mai doesn't instantly ping you with an old upload
        latest_vid, _ = await self.get_latest_video(channel_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO subscriptions (user_id, channel_id, channel_name, last_video_id)
                VALUES (?, ?, ?, ?)
            ''', (interaction.user.id, channel_id, channel_name, latest_vid or "NONE"))
            conn.commit()
            await interaction.followup.send(f"fine. i will monitor **{channel_name}** and ping your dms when they upload. i am not a notification bell, but whatever.")
        except sqlite3.IntegrityError:
            await interaction.followup.send(f"you are already subscribed to **{channel_name}**. my database doesn't need duplicates.")
        finally:
            conn.close()

    @youtube_group.command(name="unsubscribe", description="Stop receiving notifications for a channel.")
    async def yt_unsubscribe(self, interaction: discord.Interaction, channel_url: str):
        await interaction.response.defer()
        
        channel_id, _ = await self.get_channel_info(channel_url)
        if not channel_id:
            await interaction.followup.send("couldn't extract the channel id. just drop a link to their page.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM subscriptions WHERE user_id = ? AND channel_id = ?', (interaction.user.id, channel_id))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted > 0:
            await interaction.followup.send("unsubscribed. one less background process taking up my ram.")
        else:
            await interaction.followup.send("you weren't even subscribed to them in my database.")

    @youtube_group.command(name="list", description="See all channels you are currently subscribed to.")
    async def yt_list(self, interaction: discord.Interaction):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT channel_name FROM subscriptions WHERE user_id = ?', (interaction.user.id,))
        subs = cursor.fetchall()
        conn.close()

        if not subs:
            await interaction.response.send_message("you aren't tracking any channels. my processing queue is peacefully empty.")
            return
            
        sub_list = "\n".join([f"- **{sub[0]}**" for sub in subs])
        await interaction.response.send_message(f"here is who you are forcing me to monitor:\n{sub_list}")

    # --- BACKGROUND TASK ---
    @tasks.loop(minutes=15.0)
    async def check_youtube_feeds(self):
        # Mai scans the database every 15 minutes in the background
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT channel_id, channel_name, last_video_id FROM subscriptions')
        channels = cursor.fetchall()

        for channel_id, channel_name, last_video_id in channels:
            latest_vid, latest_title = await self.get_latest_video(channel_id)
            
            if latest_vid and latest_vid != last_video_id:
                # Update the database so she doesn't spam it next loop
                cursor.execute('UPDATE subscriptions SET last_video_id = ? WHERE channel_id = ?', (latest_vid, channel_id))
                conn.commit()
                
                # Fetch all users tracking this channel
                cursor.execute('SELECT user_id FROM subscriptions WHERE channel_id = ?', (channel_id,))
                users = cursor.fetchall()
                
                for (user_id,) in users:
                    try:
                        user = await self.bot.fetch_user(user_id)
                        video_url = f"https://www.youtube.com/watch?v={latest_vid}"
                        # Mai drops the notification directly in DMs
                        await user.send(f"**{channel_name}** uploaded a new video. watch it so i can clear my cache.\n{video_url}")
                    except discord.Forbidden:
                        print(f"Failed to DM user {user_id} for YouTube notification.")
                        
        conn.close()

    @check_youtube_feeds.before_loop
    async def before_check(self):
        # Wait until Mai is fully logged into Discord before starting the 15-minute loop
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(YouTubeNotifier(bot))