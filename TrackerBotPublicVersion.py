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

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="Rebooting, please wait..."), status=discord.Status.online,help_command=None,intents=intents)
	
database_url = "database url goes here"

cred = firebase_admin.credentials.Certificate('database credentials json file goes here')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

counter = 1

#English
textfile = open('Strings/en-strings.txt', 'r')
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
	if counter == 1:
		try:
			clanRanker.start()
			clanLogSender.start()
			# Error Cog
			await bot.load_extension("Cogs.Error")
			print("Error loaded")
			# Clan Cog
			# NEEDS REWORK
			await bot.load_extension("Cogs.Clans")
			print("Clans loaded")
			# Profile Cog
			# NEEDS REWORK
			await bot.load_extension("Cogs.Profile")
			print("Profile is online")
			# Win Cog
			# NEEDS REWORK
			await bot.load_extension("Cogs.Wins")
			print("Wins loaded")
			# Help Cog
			# NEEDS REWORK
			await bot.load_extension("Cogs.Help")
			print("Help is online")
			# Admin Cog
			#await bot.load_extension("Cogs.Admin")
			#print("Admin loaded")
			# Custom Cog
			await bot.load_extension("Cogs.Custom")
			print("Custom loaded")
			# Switch Cog
			await bot.load_extension("Cogs.Switch")
			print("Switch is online")
			
			WinsCog = bot.get_cog("Wins")
			WinsCog.topPlayer.start()
			
			await bot.change_presence(activity=discord.Game(name="t!help for commands"))
			
		except Exception as e:
			print(".start() or cog error")
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
		await bot.load_extension("Cogs.Switch")
		await ctx.send("Switch is online")
	except commands.ExtensionAlreadyLoaded:
		await bot.unload_extension("Cogs.Switch")
		await ctx.send("Switch is offline")
		
#-------------------------------------------------------------------------------
#------------------------------ Clan Ranking Tracking --------------------------
#-------------------------------------------------------------------------------
def to_thread(func: typing.Callable) -> typing.Coroutine:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			return await asyncio.to_thread(func, *args, **kwargs)
		return wrapper


@to_thread
def clanExtra(text3,clan,players,map,message):

	# Have code 
	points = text3[1]
	points = points.split("->")
	points = points[1]
	points = re.sub(r'[^\d.]+', '', points)
	points.strip("[]")
	# Fix clan for database
	clan = clan.replace('.', 'period5')
	clan = clan.replace('$', 'dollar5')
	clan = clan.replace('#', 'htag5')
	clan = clan.replace('[', 'lbracket5')
	clan = clan.replace('/', 'slash5')
	clan = clan.replace(']', 'rbracket5')
	clan = clan.replace('?', 'qmark5')
	time = message.created_at
	try:
		year = time.year
		month = time.month
		day = time.day
		time = time.isoformat()
	except Exception as e:
		print("year/month/day issue")
		print(e)
	# Upload the game if it doesn't already exist
	ref5 = db.reference(f'/gameDataFinal/{year}/{month}/{day}/{clan}/{map}/{message.id}')
	if(ref5.get() == None):
		ref5.update({
		'Players': players,
		'Score': float(points),
		'Time': time
		})
		# Set clan data, either create or update.
		ref = db.reference('/780723109128962070/clans/{0}'.format(clan))
		if(ref.get() == None):
			ref.set({
			'score': float(points),
			'wins': 1,
			'wins2023': 1
			})
		else:
			clanData = ref.get()
			try:
				total = clanData['wins'] + 1
				ref.update({
				'score': float(points),
				'wins': total
				})
			except:
				ref.update({
				'score': float(points),
				'wins': 1
				})
			try:
				total2 = clanData['wins2023'] + 1
				ref.update({
				'wins2023': total2
				})
			except:
				ref.update({
				'wins2023': 1
				})

@loop(seconds=30.0,count=None,reconnect=True)
async def clanRanker():
	channel = bot.get_channel(917537295261913159)
	try:
		# Grab most recent 5 messages
		# Loop code to run through each message
		messages = [msg async for msg in channel.history(limit=5)]
		
		for message in messages:
			text = message.content
			# Split message into parts
			textList = text.split(4*' ')
			# Set map
			text2 = textList[0].split()
			if len(text2) == 2:
				map = text2[0] + text2[1]
				try:
					map.strip("**")
				except:
					print("Error in clanR")
			else:
				map = text2[0]
				try:
					map.strip("**")
				except:
					print("Error in clanR")
			# Set Players
			players = textList[1]
			# Set clan
			clan = ""
			text3 = textList[2].rsplit(' ',1)
			clan = text3[0]
			# Run new thread to finish game upload
			await clanExtra(text3,clan,players,map,message)
			
	except Exception as e:
		# if message != none crashes bot if try/catch failed on message = await
		print("An erorr occured in clanRanker, previous message null")
		print(e)
#-------------------------------------------------------------------------------
#--------------------------------- Clan Log Sender  ----------------------------
#-------------------------------------------------------------------------------
@loop(seconds=20.0,count=None,reconnect=True)
async def clanLogSender():
	channel = bot.get_channel(917537295261913159)
	try:
		# Grab most recent 3 messages
		# Loop code to run through each message
		messages = [msg async for msg in channel.history(limit=3)]
		
		for message in messages:
			verify = 1
			text = message.content
			# Send game to new clan log channel
			channel2 = bot.get_channel(1048347071637364876)
			messages2 = [msg async for msg in channel2.history(limit=5)]
			for message2 in messages2:
				text2 = message2.content
				if(text2 == text):
					verify = 0
					#print("Verify equals 0")
			if verify == 1:
				await channel2.send(text)
				# Send contest to new clan contest channel
				channel3 = bot.get_channel(1067189652785725521)
				if text.startswith('**'):
					await channel3.send(text)
				
				textList = text.split(4*' ')
				clan = ""
				# Set clan
				text3 = textList[2].rsplit(' ',1)
				clan = text3[0]
				
				# Discord channel update for specific clans
				if clan == "X" or clan == "x":
					channel4 = bot.get_channel(1001628256518291606)
					await channel4.send(text)
				if clan == "ARCTIC" or clan == "arctic":
					channel9 = bot.get_channel(1094955638674698322)
					await channel9.send(text)
				if clan == "PEACE" or clan == "peace":
					channel5 = bot.get_channel(1063858717927424011)
					await channel5.send(text)
				if clan == "ZEN" or clan == "zen":
					channel6 = bot.get_channel(1023973455592439868)
					await channel6.send(text)
				if clan == "SPADES" or clan == "spades":
					channel7 = bot.get_channel(1066674369687994428)
					await channel7.send(text)
				if clan == "VOID" or clan == "void":
					channel8 = bot.get_channel(955664863454199889)
					await channel8.send(text)
				if clan == "ELITE" or clan == "elite":
					channel11 = bot.get_channel(1127009439854112821)
					await channel11.send(text)
	except Exception as e:
		# if message != none crashes bot if try/catch failed on message = await
		print("An erorr occured in clanLogSender, previous message null")
		print(e)
@bot.command()
@commands.is_owner()
async def say(ctx,*,text):
	await ctx.message.delete()
	
	# Get update channels
	ref = db.reference('/channels')
	info = ref.get()
	channels = list(info.items())
	
	# Get Image Channels
	ref = db.reference('/imageChannels')
	info = ref.get()
	channels2 = list(info.items())
	channels3 = []
	# Image channels warning
	for i in range(len(channels)):
		try:
			channels3.append(int(channels[i][1]))
			channel = bot.get_channel(int(channels[i][1]))
			# Check if channel still exists, if not, delete from database
			if channel == None:
				ref = db.reference('/channels/{0}/'.format(int(channels[i][0])))
				ref.delete()
			else:
				try:
					await channel.send(text)
				except Exception as e:
					if isinstance(e, discord.ext.commands.BotMissingPermissions):
						print("A channel {0} has blocked updates in {1}").format(channel.id,channel.guild)
		#await channel.send("Image Tracking Rebooted! You may now post again.")
		except Exception as e:
			if isinstance(e, discord.ext.commands.BotMissingPermissions):
				try:
					await channel.send("The bot does not have access to use this command here.")
					print("A channel {0} has blocked permissions in {1}").format(channel.id,channel.guild)
				except:
					print("A channel {0} has blocked sending permissions in {1}").format(channel.id,channel.guild)
			

	# Announcement channels warning
	for i in range(len(channels3)):
		# Not fixed, still messages same channel twice!
		if int(channels2[i][1]['channelID']) in channels3:
			x = "Do Nothing"
		else:
			channel = bot.get_channel(int(channels2[i][1]['channelID']))
			if channel == None:
				ref = db.reference('/imageChannels/{0}/'.format(int(channels2[i][0]['channelID'])))
				ref.delete()
			else:
				# Try to send message
				try:
					await channel.send(text)
				except Exception as e:
					if isinstance(e, discord.ext.commands.BotMissingPermissions):
						print("A channel {0} has blocked updates in {1}").format(channel.id,channel.guild)
#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
bot.run('bot token goes here', reconnect=True)