import discord
from discord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="weather")
    async def weather_command(self, ctx, *, city: str):
        """Fetches the current weather for a specified city."""
        
        # Replace spaces with plus signs for the URL (e.g., "New York" -> "New+York")
        formatted_city = city.replace(" ", "+")
        
        # The ?format=j1 parameter tells wttr.in to send us a JSON dictionary back
        url = f"https://wttr.in/{formatted_city}?format=j1"
        
        try:
            # Open an asynchronous network request using the session from main.py
            async with self.bot.session.get(url) as response:
                
                # Check if the website actually found the city (Status 200 means OK)
                if response.status == 200:
                    # content_type=None forces it to ignore the 'text/plain' warning
                    data = await response.json(content_type=None)
                    
                    # 1. Parse the specific data points from the JSON dictionary
                    current = data['current_condition'][0]
                    # Sometimes the API finds a nearby area instead of the exact string, so we grab its official name
                    location = data['nearest_area'][0]['areaName'][0]['value'] 
                    
                    temp_c = current['temp_C']
                    temp_f = current['temp_F']
                    desc = current['weatherDesc'][0]['value']
                    humidity = current['humidity']
                    
                    # 2. Format the text exactly to your requested layout
                    reply = (
                        f"**{location}**\n"
                        f"{temp_f}°F / {temp_c}°C\n"
                        f"{desc}\n"
                        f"{humidity}% Humidity"
                    )
                    
                    # 3. Send the message back to Discord
                    await ctx.send(reply)
                else:
                    await ctx.send(f"I'm sorry, I couldn't find weather data for `{city}`.")
                    
        except Exception as e:
            await ctx.send("An error occurred while reaching out to the weather service.")
            print(f"Weather API Error: {e}")

async def setup(bot):
    await bot.add_cog(Weather(bot))