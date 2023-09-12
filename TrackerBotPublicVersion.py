import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, discord.utils, subprocess, statistics, typing, functools
from discord.ext import commands
from discord.ext.commands import bot, Cog
from firebase_admin import credentials
from firebase_admin import db
from discord import Embed, Emoji
from discord.ext import tasks
from discord.ext.tasks import loop
from discord.utils import get
from datetime import datetime, timedelta
from collections import defaultdict
owner_id = 138752093308583936
import numpy as np
from matplotlib import pyplot as plt, ticker as ticker, dates as mdates
from discord.ext.commands import CommandNotFound, MissingPermissions, MessageNotFound, NotOwner, BotMissingPermissions, CommandOnCooldown, ExtensionAlreadyLoaded

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="t!help for commands"), status=discord.Status.online,help_command=None,intents=intents)
	
database_url = "database url"

cred = firebase_admin.credentials.Certificate('JSON credentials file')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

counter = 1

#English
textfile = open('en-strings.txt', 'r')
english = textfile.read().splitlines()
textfile.close()
    
lastMessageID = None

#-------------------------------------------------------------------------------
#------------------------------ ON READY EVENT ---------------------------------
#-------------------------------------------------------------------------------		

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	global counter
	#counter = counter + 1
	# if counter == 1:
	# 	clanRanker.start()
	if counter == 1:
		try:
			clanRanker.start()
			# Error Cog
			await bot.load_extension("Error")
			print("Error loaded")
			# Clan Cog
			await bot.load_extension("Clans")
			print("Clans loaded")
			# Profile Cog
			await bot.load_extension("Profile")
			print("Profile is online")
			# Win Cog
			await bot.load_extension("Wins")
			print("Wins loaded")
			# Help Cog
			await bot.load_extension("Help")
			print("Help is online")
			# Admin Cog
			await bot.load_extension("Admin")
			print("Admin loaded")
			# Custom Cog
			await bot.load_extension("Custom")
			print("Custom loaded")
			# Switch Cog
			await bot.load_extension("Switch")
			print("Switch is online")
			
			WinsCog = bot.get_cog("Wins")
			#WinsCog.bestPlayer.start()
			WinsCog.topPlayer.start()
			WinsCog.userCount.start()
			WinsCog.userStatCheck.start()
			
		except Exception as e:
			print(".start() error")
			print(e)
		print("Tasks starting")
	counter = 2
	
# Plans for future updates? Ooutdated, not sure if I did these already or will do them still
# Make a search method to display other clans leaderboards.
# Example !leaderboard cum searches all discord databases for name attribute cum

@bot.event
async def on_resumed():
	print('We have resumed as {0.user}'.format(bot))

#-------------------------------------------------------------------------------
#--------------------------- Switch for the Switches ---------------------------
#-------------------------------------------------------------------------------
@commands.command(pass_context = True)
@commands.is_owner()
async def switchSwitch(ctx):
	try:
		await bot.load_extension("Switch")
		await ctx.send("Switch is online")
	except commands.ExtensionAlreadyLoaded:
		await bot.unload_extension("Switch")
		await ctx.send("Switch is offline")
#-------------------------------------------------------------------------------
#----------------------------------- LAG TEST ----------------------------------
#-------------------------------------------------------------------------------
		
@bot.command(pass_context = True)
@commands.is_owner()
async def lag(ctx):
	print("lag")
	await asyncio.sleep(5)
	print("lag")

#-------------------------------------------------------------------------------
#--------------------------- Submit Suggestions Command ------------------------
#-------------------------------------------------------------------------------
		
@bot.command(pass_context = True)
@commands.cooldown(1, 86400, commands.BucketType.user)
async def suggest(ctx):
	# Check correct channel
	def check(c):
		return c.channel == ctx.author.dm_channel and c.author == ctx.author
	# Send user the request
	await ctx.author.send("Please enter your suggestion to improve the bot.")
	try:
		# Wait for suggestion
		suggestion = await bot.wait_for('message', check=check, timeout = 180)
		suggestion = suggestion.content
		# Submit suggestion
		if(suggestion != None):
			with open('suggestions.txt', 'a') as textfile:
				textfile.write(f"\n{suggestion} {ctx.author.id} {ctx.author.name}")
	# Catch timeout
	except asyncio.TimeoutError:
		await ctx.author.send("You took too long to respond.")
	# Catch anything else
	except Exception as e:
		print(e)
		print("Error occured in suggest command")

#-------------------------------------------------------------------------------
#------------------------------ Set Announcement Channel -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def updates(ctx):
	# Set language
	language = english
	# Set user
	user = ctx.message.author.id
	# Get guild id
	guild = ctx.message.guild.id
	ref = db.reference('/channels/{0}'.format(guild))
	if ref.get() != None:
		await ctx.send(language[115])
	else:
		ref = db.reference('/channels'.format(guild))
		ref.update({
		guild: "{0}".format(ctx.channel.id)
		})
		await ctx.send(language[116])
	await ctx.message.delete()

#-------------------------------------------------------------------------------
#------------------------------ Change bot status ------------------------------
#-------------------------------------------------------------------------------	
@commands.is_owner()
@bot.command(pass_context = True)
async def botstatus(ctx,*,text):
	await bot.change_presence(activity=discord.Game(name=text))
	await ctx.message.delete()

#-------------------------------------------------------------------------------
#---------------------------------- PING TEST ----------------------------------
#-------------------------------------------------------------------------------
@bot.command()
@commands.is_owner()
async def ping(ctx):
	await ctx.send('Pong! {}ms'.format(round(bot.latency, 1)))

#-------------------------------------------------------------------------------
#------------------------------ add COMMAND -------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def add(ctx):
	# Set language
	language = english
	# Set user
	user = ctx.message.author.id
	await ctx.send(language[166])
	await ctx.send(language[167])

#-------------------------------------------------------------------------------
#----------------------------- Load/Unload Switch Cog ---------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.is_owner()
async def switch(ctx):
	try:
		await bot.load_extension("Switch")
		await ctx.send("Switch is online")
	except commands.ExtensionAlreadyLoaded:
		await bot.unload_extension("Switch")
		await ctx.send("Switch is offline")

#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
bot.run('bot token', reconnect=True)