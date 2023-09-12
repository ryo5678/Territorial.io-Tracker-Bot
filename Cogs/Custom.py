import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, discord.utils, subprocess, statistics, typing, functools
from discord.ext import commands, tasks
from discord.ext.commands import bot
from discord import Embed
from firebase_admin import db
from urllib.request import Request, urlopen
from datetime import datetime, timedelta, timezone
from discord.utils import get

#English
textfile = open('/Strings/en-errors.txt', 'r')
english = textfile.read().splitlines()
textfile.close()

class Custom(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# Thread
	def to_thread(func: typing.Callable) -> typing.Coroutine:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			return await asyncio.to_thread(func, *args, **kwargs)
		return wrapper
	
	# Random Troll command
	@commands.command()
	@commands.cooldown(1, 180, commands.BucketType.user)
	async def gaysex(self,ctx):
		#await ctx.send("Pong")
		if ctx.author.id == 759859163282669578:
			await ctx.send("Woah I didn't know you liked gay sex. Thats pretty cool.")
		else:
			await ctx.send("<@{0}> likes gay sex.".format("759859163282669578"))

	# Custom Command for Xesphor
	@commands.command()
	@commands.cooldown(1, 180, commands.BucketType.user)
	async def x(self,ctx):
		# Download the webpage as text
		req = Request(
			url = "https://territorial.io/clans",
			headers={'User-Agent': 'Mozilla/5.0'}
		)
		with urlopen(req) as webpage:
			content = webpage.read().decode()
		# print(content)
		# Convert webpage text to string list by lines
		content = content.splitlines()
		content.pop(3)
		content.pop(2)
		content.pop(1)
		content.pop(0)
		clans = list()
		# Grab only top 100 clans
		for i in range(100):
			# Split string to extract clan name
			text = content[i].split(', ')
			clans.append(text[1])
		#print(clans)
		x = random.randint(0,99)
		await ctx.send(f'X loves {clans[x]}!')
		
		if(ctx.author.id == 314969222516047872):
			ctx.command.reset_cooldown(ctx)

async def setup(bot):
	await bot.add_cog(Profile(bot))