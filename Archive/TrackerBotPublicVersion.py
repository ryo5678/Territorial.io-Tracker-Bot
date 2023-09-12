import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
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
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from PIL import Image, ImageOps
from pytesseract import pytesseract
import numpy as np
from matplotlib import pyplot as plt, ticker as ticker, dates as mdates
from discord.ext.commands import CommandNotFound, MissingPermissions, MessageNotFound, NotOwner, BotMissingPermissions, CommandOnCooldown, ExtensionAlreadyLoaded
path_to_tesseract = r"File path to tesseract.exe goes here"
#from threading import Thread
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

creds = service_account.Credentials.from_service_account_file(
    'Google credentials json file goes here')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'spreadsheet ID goes here'
RANGE_NAME = 'A2'

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="t!help for commands"), status=discord.Status.online,help_command=None,intents=intents)
	
database_url = "Database url goes here"

cred = firebase_admin.credentials.Certificate('Firebase database credentials json goes here')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

counter = 1

#English
textfile = open('en-strings.txt', 'r')
english = textfile.read().splitlines()
textfile.close()
    


##########################
# Problem found, imageTrack loop, images not deleted are ones that failed or are irelevant to bot
##########################
#-------------------------------------------------------------------------------
#------------------------------ ON READY EVENT ---------------------------------
#-------------------------------------------------------------------------------		

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	global LangCog
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
			# Language Cog
			await bot.load_extension("LangCog")
			LangCog = bot.get_cog("LangCog")
			print("Lang loaded")
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
			# Poll Cog
			await bot.load_extension("Poll")
			PollCog = bot.get_cog("Poll")
			await PollCog.pollStart()
			print("Poll loaded")
			# Switch Cog
			await bot.load_extension("Switch")
			print("Switch is online")
			
			WinsCog = bot.get_cog("Wins")
			WinsCog.bestPlayer.start()
			WinsCog.bestClan.start()
			WinsCog.topPlayer.start()
			WinsCog.userCount.start()
			
		except Exception as e:
			print(".start() error")
			print(e)
		#ref = db.reference('/imageChannels')
		#info = ref.get()
		#channels = list(info.items())
		print("Tasks starting")
		# REVISIT AND DELETE STUFF DOESNT WORK PROPERLY
		#try:
			#channel = bot.get_channel(int(900982254287855688))
			#elite_task = tasks.loop(seconds=5.0,count=None,reconnect=True)(imagelooper)
			#Thread(new_task.start(channel))
			#elite_task.start(channel)
		#except Exception as e:
			#print(e)
			
		#for i in range(len(channels)):
				#print(int(channels[i][1]['channelID']))
			#try:
				#if int(channels[i][1]['channelID']) == 900982254287855688:
				#	do = "nothing"
				#else:
					#channel = bot.get_channel(int(channels[i][1]['channelID']))
					#Check if channel still exists, if not, delete from database
					#if channel == None:
					#	ref = db.reference('/imageChannels/{0}/'.format(int(channels[i][0])))
					#	ref.delete()
					#else:
						#new_task = tasks.loop(seconds=20.0,count=None,reconnect=True)(imagelooper)
						#Thread(new_task.start(channel))
					#	new_task.start(channel)
					#	testLine = "test"
			#await channel.send("Image Tracking Rebooted! You may now post again.")
			#except Exception as e:
				#print(e)
				#if isinstance(e, discord.ext.commands.BotMissingPermissions):
					#try:
					#	language = english
					#	await channel.send(language[0])
						#print("test")
					#except Exception as e:
					#	print("Exception error in Exception of on_ready")
					#	print(e)
					#	if str(e) == "object Nonetype can't be used in 'await' expression":
						#	print("found")
		
	counter = 2
# Plans for future updates
# Make a search method to display other clans leaderboards.
# Example !leaderboard cum   searches all discord databases for name attribute cum

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
#----------------------------- Spreadsheet Filler ------------------------------
#-------------------------------------------------------------------------------

@bot.command(pass_context = True)
@commands.cooldown(1, 604800, commands.BucketType.user)
async def joinEvent(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	# Gather discord user and server information
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	channel = ctx.message.channel.id
	if guild == 780723109128962070 and channel == 939841267213422672:	
		name = '{0}#{1}'.format(ctx.message.author.name,ctx.message.author.discriminator)
		#print("Before role = get")
		try:
			role = get(ctx.guild.roles, id=941970444653850654)
			await ctx.author.add_roles(role)
			#print("after bot.add")
			# Log into the google sheet
			service = build('sheets', 'v4', credentials=creds)
			
			# Set the entry value for sheet
			values = [
				[
				name
				],
			]
			body = {
				'values': values
			}
			#print("after service = build")
			# Send the update to the live google sheet
			result = service.spreadsheets().values().append(
				spreadsheetId=SPREADSHEET_ID,range=RANGE_NAME,
				valueInputOption="RAW",body=body).execute()
			#print("after result =")
			# Provide feedback to user on success
			await ctx.send(language[1].format(name))
		except Exception as e:
			print(e)
	else:
		try:
			await ctx.send(language[2])
			await joinEvent.reset_cooldown(ctx)
		except Exception as e:
			print("JoinEvent called in wrong server")
			print(e)
#-------------------------------------------------------------------------------
#------------------------------ Set Announcement Channel -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def updates(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
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
#------------------------------ Clan Ranking Tracking --------------------------
#-------------------------------------------------------------------------------	
# NEW VERSION OF COMMAND LOOP
@loop(seconds=3.0,count=None,reconnect=True)
async def clanRanker():
	channel = bot.get_channel(917537295261913159)
	try:
		message = await channel.fetch_message(
				channel.last_message_id)
				
		mRef = db.reference('/780723109128962070/lastMessage')
		message2 = int(mRef.get())
		
		if message2 != message.id:
			message2 = message
			text = message.content
			
			channel2 = bot.get_channel(1048347071637364876)
			await channel2.send(text)
			
			textList = text.split(4*' ')
			clan = ""
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
			# original code before potential fix
			#text3 = textList[2].split()
			#for i in range(len(text3) - 1):
			#	clan += text3[i]
			#points = text3[len(text3) - 1]
			# New code
			text3 = textList[2].rsplit(' ',1)
			clan = text3[0]
			
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
			time = message.created_at.isoformat()
			# Set clan data, either create or update.
			ref = db.reference('/780723109128962070/clans/{0}'.format(clan))
			if(ref.get() == None):
				ref.set({
				'score': float(points)
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
					'score': float(points)
					})
			ref5 = db.reference('/gameData5')
			ref5.push({
			'Map': map,
			'Players': players,
			'Clan': clan,
			'Score': float(points),
			'Time': time
			})
			mRef = db.reference('/780723109128962070')
			mRef.update({
			'lastMessage': str(message.id)
			})
	except Exception as e:
		# if message != none crashes bot if try/catch failed on message = await
		print("An erorr occured in clanRanker, previous message null")
		print(e)

#-------------------------------------------------------------------------------
#------------------------------ Change bot status ------------------------------
#-------------------------------------------------------------------------------	
@commands.is_owner()
@bot.command(pass_context = True)
async def botstatus(ctx,*,text):
	await bot.change_presence(activity=discord.Game(name=text))
	await ctx.message.delete()

#-------------------------------------------------------------------------------
#------------------------------ PING CRASH TEST --------------------------------
#-------------------------------------------------------------------------------
@bot.command()
@commands.is_owner()
async def ping(ctx):
	#await ctx.send("Pong")
	await ctx.send('Pong! {}ms'.format(round(bot.latency, 1)))

@bot.command()
@commands.is_owner()
async def historyGrab(ctx):
	channel = bot.get_channel(917537295261913159)
	try:
		x = datetime(2022,1,25,8,49,00)
		messages = await channel.history(limit=None,after=x).flatten()
		print("Finished discord list gathering")
		for msg in messages:
			text = msg.content
			#print(text)
			textList = text.split()
			if len(textList) == 6:
				map = textList[0] + textList[1]
				players = textList[2]
				clan = textList[3] + textList[4]
				points = textList[5]
				points = re.sub(r'[^\d.]+', '', points)
				points.strip("[]")
			elif len(textList) == 5:
				map = textList[0] + textList[1]
				players = textList[2]
				clan = textList[3]
				points = textList[4]
				points = re.sub(r'[^\d.]+', '', points)
				points.strip("[]")
			elif len(textList) == 4:
				map = textList[0]
				players = textList[1]
				clan = textList[2]
				points = textList[3]
				points = re.sub(r'[^\d.]+', '', points)
				points.strip("[]")
			else:
				map = textList[0]
				players = textList[1]
				clan = " "
				points = textList[2]
				points = re.sub(r'[^\d.]+', '', points)
				points.strip("[]")
			#print(points)
			# Temp fix, might not work
			clan = clan.replace('.', 'period5')
			clan = clan.replace('$', 'dollar5')
			clan = clan.replace('#', 'htag5')
			clan = clan.replace('[', 'lbracket5')
			clan = clan.replace('/', 'slash5')
			clan = clan.replace(']', 'rbracket5')
			clan = clan.replace('?', 'qmark5')
			time = msg.created_at.isoformat()
				
			ref2 = db.reference('/gameDataHistory')
			ref2.push({
			'Map': map,
			'Players': players,
			'Clan': clan,
			'Score': float(points),
			'Time': time
			})
		print("Finished discord list posting")
	except Exception as e:
		# if message != none crashes bot if try/catch failed on message = await
		print("An erorr occured in gameDataHistory, previous message null")
		print(e)
#-------------------------------------------------------------------------------
#------------------------------ SAY COMMAND -------------------------------
#-------------------------------------------------------------------------------
# Shutdown the bot!
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
#------------------------------ add COMMAND -------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def add(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	await ctx.send(language[166])
	await ctx.send(language[167])
		
#-------------------------------------------------------------------------------
#------------------------------ LCEVENTSTATS COMMAND -------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def lc(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	# Post to channel
	await ctx.send(language[168],file=discord.File("StatisticsLCEvent.pdf"))

#-------------------------------------------------------------------------------
#------------------------------ SCOPE COMMAND ---------------------------
#-------------------------------------------------------------------------------		
@bot.command(pass_context = True)
@commands.is_owner()
async def scope(ctx):
	# Check if all users still in scope
	try:
		# Retrieve user id list stored by bot
		users = []
		#ref = db.reference('/userIDs')
		ref = db.reference('/users')
		snapshot = ref.get()
		for key in snapshot:
			users.append(key)
		#print(users)
		# Retrieve user list bot can get from discord
		for guild in bot.guilds:
			print(guild)
			for member in guild.members:
				#print(member.id)
				if str(member.id) in users:
					# If user has rejoined scope, update to True
					ref = db.reference('/userIDs/{0}/time'.format(str(member.id)))
					ref.delete()
					ref = db.reference('/userIDs/{0}'.format(str(member.id)))
					ref.update({
					'scope': True
					})
					# Remove user from list
					users.remove(str(member.id))
		# Update database user list to reflect users no longer in discord scope
		print(len(users))
		for i in range(len(users)):
			ref2 = db.reference('/userIDs/{0}/scope'.format(users[i]))
			if ref2.get() == True:
				ref = db.reference('/userIDs/{0}'.format(users[i]))
				ref.update({
				'scope': False,
				'time': str(datetime.now())
				})
		print("Update complete, checking to delete users next")		
	except Exception as e:
		print("Scope check error")
		print(e)
	# Remove users who have been outside scope for 30 days
	try:
		# Get times
		timeDif = timedelta(30)
		cTime = datetime.now() - timeDif
		ref = db.reference('userIDs')
		snapshot = ref.order_by_child('scope').equal_to(False).get()
		users = list(snapshot.items())
		
		# Compare times
		for i in range(len(users)):
			if datetime.strptime(users[i][1]['time'],"%Y-%m-%d %H:%M:%S.%f") < cTime:
				# Remove user if time exceeds 30 days**
				ref = db.reference('/userIDs/{0}'.format(users[i][0]))
				ref.delete()
				ref = db.reference('/users/{0}'.format(users[i][0]))
				ref.delete()
				print("User {0} deleted from system".format(users[i][0]))
	except Exception as e:
		print("Error in user data removal")
		print(e)
#-------------------------------------------------------------------------------
#------------------------------ DATA REMOVAL COMMAND ---------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def data(ctx):
	# Note to self: Add a double check confirmation method 
	ref = db.reference('/users/{0}/'.format(ctx.author.id))
	ref.delete()
#-------------------------------------------------------------------------------
#------------------------- OPT IN AND OUT OF DATA STORAGE ----------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 1800, commands.BucketType.user)
async def disable(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	# Check for existing opt status
	opt = db.reference('/users/{0}/opt'.format(user))
	if (opt.get() == True):
		await ctx.send(language[170])
		return
	ref = db.reference('/users/{0}'.format(ctx.author.id))
	ref.update({
	'opt': True
	})
	await ctx.send(language[171])
		
@bot.command(pass_context = True)
@commands.cooldown(1, 1800, commands.BucketType.user)
async def enable(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	# Check for existing opt status
	opt = db.reference('/users/{0}/opt'.format(user))
	if (opt.get() == False):
		await ctx.send(language[172])
		return
	ref = db.reference('/users/{0}/opt'.format(ctx.author.id))
	ref.update({
	'opt': False
	})
	await ctx.send(language[173])

#-------------------------------------------------------------------------------
#------------------------------- Donate link command ---------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 180, commands.BucketType.user)
async def donate(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	try:
		await ctx.send(language[174])
	except:
		print(ctx.message.guild.id + ctx.message.guild.name + " guild id and name, no send permissions")
#-------------------------------------------------------------------------------
#------------------------------ Set Language Command ---------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def setlanguage(ctx, lang):
	# List of accepted languages
	languages = ['english','french','russian','turkish','german']
	# Get user ID
	user = ctx.author.id
	# Get guild
	guild = ctx.message.guild.id
	guild = bot.get_guild(guild)
	# Set reference
	ref = db.reference('/users/{0}'.format(user))
	# Get username/nickname
	username = ((await guild.fetch_member(user)).nick)
	if username == None:
		username = ((await guild.fetch_member(user)).name)
	# Create profile is none exists for user ID
	try:
		if ref.get() == None:
			# Add to scope list
			newRef = db.reference('/userIDs/{0}'.format(user))
			newRef.set({
			'scope': True
			})
			# Add to user list
			ref.set({
			'brwins': 0,
			'clans': {
				'currentclan': "none"
			},
			'lang': 'english',
			'name': username,
			'onevsone': 0
			})
			language = english
			lang = lang.lower()
			if lang not in languages:
				try:
					return await ctx.send(language[165])
				except:
					return await ctx.author.send(language[165])
			# Update language setting in database
			ref.update({
			'lang': lang
			})
			
		else:
			# Check for existing language
			language = LangCog.languagePicker(user)
			lang = lang.lower()
			#print(lang)
			if lang not in languages:
				try:
					return await ctx.send(language[165])
				except:
					return await ctx.author.send(language[165])
			# Update language setting in database
			ref.update({
			'lang': lang
			})
			language = LangCog.languagePicker(user)
			print("Issue check, string index of out range")
			return await ctx.send(language[175].format(lang))
	except Exception as e:
		print(e)
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
bot.run('Bot Token Goes Here', reconnect=True)
