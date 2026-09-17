import discord
from discord.ext import commands
from discord import app_commands
import urllib.parse

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Defines the slash command and allows it in private DMs
    @app_commands.command(name="weather", description="Extract atmospheric data for a specific location.")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def weather_check(self, interaction: discord.Interaction, location: str):
        
        # Mai defers the response while waiting for the weather API
        await interaction.response.defer()

        # wttr.in is a free weather API that doesn't require an API key (format=j1 returns JSON data)
        url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"

        try:
            async with self.bot.session.get(url) as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"HTTP Error {resp.status}. The meteorological database is currently unresponsive.")
                    return
                
                data = await resp.json(content_type=None)

            # Extract the core data from the JSON response
            current = data['current_condition'][0]
            temp_c = current['temp_C']
            temp_f = current['temp_F']
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            wind_kph = current['windspeedKmph']
            wind_mph = current['windspeedMiles']
            
            # Extract the actual location name parsed by the API
            area = data['nearest_area'][0]
            city = area['areaName'][0]['value']
            region = area['region'][0]['value']
            country = area['country'][0]['value']
            
            # Clean up the location string
            full_location = f"{city}, {region}, {country}".strip(', ')

            # Build Mai's logical UI box
            embed = discord.Embed(
                title=f"Atmospheric Scan: {full_location}",
                color=0x1abc9c
            )
            
            # Display both Celsius and Fahrenheit for maximum efficiency
            embed.add_field(name="Temperature", value=f"{temp_c}°C / {temp_f}°F", inline=True)
            embed.add_field(name="Conditions", value=desc, inline=True)
            embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
            embed.add_field(name="Wind Speed", value=f"{wind_kph} km/h / {wind_mph} mph", inline=True)
            
            embed.set_footer(text="Data efficiently parsed by Mai-desu.")

            # Mai's in-character dialogue
            mai_dialogue = "Meteorological data extracted. Why you need this when you should be inside optimizing your code is beyond my logical comprehension."

            await interaction.followup.send(content=mai_dialogue, embed=embed)

        except Exception as e:
            print(f"Weather Fetch Error: {e}")
            await interaction.followup.send(f"My query failed. The location `{location}` likely does not exist in the database, or your spelling is highly illogical.")

async def setup(bot):
    await bot.add_cog(Weather(bot))