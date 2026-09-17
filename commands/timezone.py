import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import urllib.parse
import re
from datetime import datetime
from zoneinfo import ZoneInfo

class TimezoneConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def resolve_location(self, query: str):
        query_lower = query.lower().strip()
        
        # 1. First, check if they used a common timezone abbreviation
        common_tz = {
            "jst": "Asia/Tokyo", "est": "America/New_York", "edt": "America/New_York",
            "cst": "America/Chicago", "cdt": "America/Chicago",
            "pst": "America/Los_Angeles", "pdt": "America/Los_Angeles",
            "mst": "America/Denver", "mdt": "America/Denver",
            "gmt": "UTC", "utc": "UTC", "bst": "Europe/London",
            "aest": "Australia/Sydney", "cet": "Europe/Paris"
        }
        if query_lower in common_tz:
            return common_tz[query_lower], query.upper()
            
        # 2. If it's a city/country, Mai uses OpenStreetMap to find its coordinates
        nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
        headers = {"User-Agent": "Mai-desu/1.0 Discord Bot"}
        
        try:
            async with self.bot.session.get(nom_url, headers=headers) as resp:
                if resp.status != 200: return None, None
                data = await resp.json()
                if not data: return None, None
                
                lat = data[0]['lat']
                lon = data[0]['lon']
                
                # Grab just the primary city/name for clean UI display (e.g., "Kyoto" instead of "Kyoto, Japan")
                location_name = data[0]['display_name'].split(',')[0]
                
            # 3. She passes the coordinates to TimeAPI to get the exact TimeZone name
            tz_url = f"https://timeapi.io/api/TimeZone/coordinate?latitude={lat}&longitude={lon}"
            async with self.bot.session.get(tz_url) as resp:
                if resp.status != 200: return None, None
                tz_data = await resp.json()
                return tz_data['timeZone'], location_name
                
        except Exception as e:
            print(f"Timezone Resolver Error: {e}")
            return None, None

    @app_commands.command(name="timezone", description="Convert time between any two locations or timezones.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def timezone_cmd(self, interaction: discord.Interaction, origin: str, destination: str, time: str = "now"):
        await interaction.response.defer()
        
        # Resolve both inputs into proper timezones
        src_tz_str, src_name = await self.resolve_location(origin)
        dest_tz_str, dest_name = await self.resolve_location(destination)
        
        if not src_tz_str:
            await interaction.followup.send(f"my geocoding algorithms failed on `{origin}`. are you sure that's a real place?")
            return
        if not dest_tz_str:
            await interaction.followup.send(f"my geocoding algorithms failed on `{destination}`. are you sure that's a real place?")
            return
            
        # Initialize Python's built-in timezone handler (Requires Python 3.9+)
        src_tz = ZoneInfo(src_tz_str)
        dest_tz = ZoneInfo(dest_tz_str)
        
        # Parse the requested time
        if time.lower() == "now":
            src_dt = datetime.now(src_tz)
        else:
            # Mai's custom regex can parse logic like "10am", "10:30am", "3 pm", or "15:00"
            match = re.match(r'^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$', time.lower().replace(" ", ""))
            if not match:
                await interaction.followup.send("i literally cannot parse that time format. try something logical like `10:30am` or `15:00`.")
                return
                
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            ampm = match.group(3)
            
            if ampm == 'pm' and hour < 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
                
            if hour > 23 or minute > 59:
                await interaction.followup.send("time out of bounds. learn to read a clock.")
                return
                
            # Construct a datetime object using today's date but the user's requested time
            now = datetime.now(src_tz)
            src_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        # Do the conversion
        dest_dt = src_dt.astimezone(dest_tz)
        
        # Format perfectly (e.g., "10:30 AM")
        src_time_str = src_dt.strftime("%I:%M %p").lstrip("0")
        dest_time_str = dest_dt.strftime("%I:%M %p").lstrip("0")
        
        # If the conversion jumps forward or backward a full calendar day, note it
        day_diff = dest_dt.date() - src_dt.date()
        day_str = ""
        if day_diff.days == 1:
            day_str = " *(the next day)*"
        elif day_diff.days == -1:
            day_str = " *(the previous day)*"
        
        # Output exactly as requested
        reply = (
            "here's what time that would be. have you tried memorizing the time zones you care about? "
            "i would do that for polka.\n\n"
            f"> **{src_time_str}** in **{src_name}** is **{dest_time_str}** in **{dest_name}**{day_str}."
        )
        
        await interaction.followup.send(reply)

async def setup(bot):
    await bot.add_cog(TimezoneConverter(bot))