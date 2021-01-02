import os

import discord
from discord.ext import commands

from dotenv import load_dotenv
from util.logger import logger

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = 't!'
extensions = ['cogs.bar_tables']

bot = commands.Bot(command_prefix=PREFIX)
if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)
        logger.debug(f'{extension} loaded')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Spilling the Tea'))
    logger.info(f'{bot.user} has connected to Discord!')

logger.info("Starting bot")
bot.run(TOKEN)
