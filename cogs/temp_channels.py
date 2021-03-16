import discord
from discord.ext import commands
from util.logger import logger
from util.colors import colors
from util.emojis import *
import oyaml as yaml

class TempChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setup',
        desc='Setup for the temporary voice channels',
        help='Setup for the temporary voice channels')
    async def setup(self, ctx):
        author = ctx.message.author
        guild = ctx.message.guild
        id = guild.id

        cats = [c.name for c in guild.categories]
        cats_list = [numEmojis[i] + " " + c for i, c in enumerate(cats)]
        cats_str = '\n'.join(cats_list)

        embed = discord.Embed(title='Setup - Category',
            description=f'Please select a category for the temporary voice channels',
            color=colors["InProgress"])
        embed.add_field(name="Please select one category", value=cats_str)
        msg = await ctx.send(embed=embed)
        selection = await self.addNumReactions(msg, len(cats_list))

        def check(r, u):
            return (r.message.id == msg.id
                and r.emoji in selection.keys()
                and u == author)
        reaction, _ = await self.bot.wait_for('reaction_add', check=check)
        cat = cats[selection[reaction.emoji]]

        embed = discord.Embed(title='Setup - Name',
            description=f'`{cat}` was chosen for the temporary voice channel category\n\n\
                Please type the name of the temporary voice channels',
            color=colors["InProgress"])
        await msg.clear_reactions()
        await msg.edit(embed=embed)

        def check(m):
            return m.channel == msg.channel and m.author == author
        message = await self.bot.wait_for('message', check=check)

        name = message.content

        embed = discord.Embed(title='Setup',
            description=f'Setup complete.\n\
                `{name}` was chosen for the temporary voice channel name\n\
                `{cat}` was chosen for the temporary voice channel category.',
            color=colors['OK'])
        await msg.edit(embed=embed)

        with open('config.yaml', 'r+') as stream:
            data = yaml.safe_load(stream)
            if data is None:
                data = {}
            if id not in data.keys():
                data[id] = {}

            data[id]['temp_vc_category'] = cat
            data[id]['temp_vc_name'] = name

            stream.seek(0)
            stream.truncate()
            yaml.safe_dump(data, stream)

        logger.info(f'{author.name} completed the setup for temporary voice\
            channels on {guild.name}')


    @commands.command(name='open', aliases=['new', 'create'],
        desc='Open a new temporary voice channel with a member limit',
        help='Open a new temporary voice channel with a member limit')
    async def open_table(self, ctx, *, limit: int):
        author = ctx.message.author
        guild = ctx.message.guild
        id = guild.id
        try:
            limit = int(limit)
        except ValueError:
            embed = discord.Embed(title='Error',
                description=f'Your limit is {limit} is invalid.\
                    Please specify an integer number.',
                color=colors['Error'])
            await ctx.send(embed=embed)
            return

        cats = {c.name: c for c in guild.categories}

        with open('config.yaml', 'r') as stream:
            data = yaml.safe_load(stream)
            try:
                if data is None or id not in data:
                    raise ValueError
                cat = data[id]['temp_vc_category']
                name = data[id]['temp_vc_name']
            except KeyError:
                embed = discord.Embed(title='Error',
                description='There was no configuration found for this server.\
                    Please use "setup" first.',
                color=colors['Error'])
                await ctx.send(embed=embed)
                return

        cat = cats[cat]
        await cat.create_voice_channel(f'{name}', user_limit=limit)

        embed = discord.Embed(title='Done', description='Enjoy your time.\
            The channel will be deleted when there are no members left in it.',
            color=colors['OK'])
        await ctx.send(embed=embed)

        logger.info(f'{author.name} created the temporary voice channel \"{name}\"\
            for {limit} people')

    @commands.command(name='resize', aliases=['expand','shrink','extend'],
        desc='Change the user limit for your current temporary voice channel',
        help='Change the user limit for your current temporary voice channel')
    async def expand(self, ctx, *, limit: int):
        guild = ctx.message.guild
        author = ctx.message.author
        id = guild.id
        with open('config.yaml' , 'r') as stream:
            data = yaml.safe_load(stream)
            if data is None or id not in data.keys():
                embed = discord.Embed(title='Error',
                    description='There was no configuration found for this server.\
                        Please use "setup" first.',
                    color=colors['Error'])
                await ctx.send(embed=embed)
                return
            try:
                cat = data[id]['temp_vc_category']
                name = data[id]['temp_vc_name']
            except (KeyError, TypeError) as e:
                embed = discord.Embed(title='Error',
                    description='Something unexpected happened.\
                        Cancelling channel resizing.',
                    color=colors['Error'])
                await ctx.send(embed=embed)
                logger.error(e)
                return

        if (author.voice is None
            or author.voice.channel is None
            or not author.voice.channel.name.startswith(name)):
            embed = discord.Embed(title='Error',
                description='You must be in a temporary channel voice channel\
                    to use this command.',
                color=colors['Error'])
            await ctx.send(embed=embed)
            return

        channel = author.voice.channel
        await channel.edit(user_limit=limit)
        embed = discord.Embed(title='Done',
            description='The user limit was changed as you asked.',
            color=colors['OK'])
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None:
            channel = before.channel
        else:
            channel = after.channel
        if channel is None:
            return

        id = channel.guild.id

        with open('config.yaml', 'r') as stream:
            data = yaml.safe_load(stream)
            if data is None or id not in data.keys():
                return
            cat = data[id]['temp_vc_category']
            name = data[id]['temp_vc_name']

        if (channel.category.name == cat
                and channel.name.startswith(name)
                and len(channel.members) == 0):
            await channel.delete()


    async def addNumReactions(self, msg, max):
        selection = {}
        for i in range(max):
            await msg.add_reaction(numEmojis[i])
            selection[numEmojis[i]] = i
        return selection

def setup(bot):
    bot.add_cog(TempChannels(bot))
