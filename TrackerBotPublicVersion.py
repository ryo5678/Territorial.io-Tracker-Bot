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
path_to_tesseract = r"Tesseract exe location here"
#from threading import Thread
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

creds = service_account.Credentials.from_service_account_file(
    'Google credentials json here')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'Google sheets id here'
RANGE_NAME = 'A2'

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="t!help for commands"), status=discord.Status.online,help_command=None,intents=intents)
	
database_url = "Firebase database url here"

cred = firebase_admin.credentials.Certificate('Firebase admin credentials json here')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

counter = 1

#English
textfile = open('en-strings.txt', 'r')
english = textfile.read().splitlines()
textfile.close()
    
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
		except Exception as e:
			print(".start() error")
			print(e)
		ref = db.reference('/imageChannels')
		info = ref.get()
		channels = list(info.items())
		print("Tasks starting")
		# REVISIT AND DELETE STUFF DOESNT WORK PROPERLY
		try:
			channel = bot.get_channel(int(900982254287855688))
			elite_task = tasks.loop(seconds=5.0,count=None,reconnect=True)(imagelooper)
			#Thread(new_task.start(channel))
			elite_task.start(channel)
		except Exception as e:
			print(e)
			
		for i in range(len(channels)):
				#print(int(channels[i][1]['channelID']))
			try:
				if int(channels[i][1]['channelID']) == 900982254287855688:
					do = "nothing"
				else:
					channel = bot.get_channel(int(channels[i][1]['channelID']))
					# Check if channel still exists, if not, delete from database
					if channel == None:
						ref = db.reference('/imageChannels/{0}/'.format(int(channels[i][0])))
						ref.delete()
					else:
						new_task = tasks.loop(seconds=15.0,count=None,reconnect=True)(imagelooper)
						#Thread(new_task.start(channel))
						new_task.start(channel)
						testLine = "test"
			#await channel.send("Image Tracking Rebooted! You may now post again.")
			except Exception as e:
				print(e)
				if isinstance(e, discord.ext.commands.BotMissingPermissions):
					try:
						language = english
						await channel.send(language[0])
						print("test")
					except Exception as e:
						print("Exception error in Exception of on_ready")
						print(e)
						if str(e) == "object Nonetype can't be used in 'await' expression":
							print("found")
		
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
#------------------------- 1v1 LEADERBOARD COMMAND -----------------------------
#-------------------------------------------------------------------------------
@loop(seconds=30,count=None,reconnect=True)
async def sololoop(ctx,clan,user):
	try:
		# Get/Set language
		language = LangCog.languagePicker(user)
		# Get references
		ref = db.reference('/users')
		refList = ref.order_by_child('onevsone').limit_to_last(25).get()
		scores = list(refList.items())
		scores.reverse()
		ladder = discord.Embed(title=language[148], description=language[136], color=0x33DDFF)
		# First Ladder
		for i in range(25):
			ladder.add_field(name=language[149].format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
		msg = await ctx.send(embed=ladder)
	except Exception as e:
		print(e)
		await ctx.send(language[146].format('<@138752093308583936>'))
		check = False
		print("Soloboard command call failed before loop started.")

@bot.command(pass_context = True)
@commands.is_owner()
async def soloboard(ctx,clan):
	# Get/Set Language
	user = ctx.message.author.id
	# Get guild ID
	guild = ctx.message.guild.id
	sololoop.start(ctx,clan,user)

@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def oneboard(ctx,x):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	try:
		x = int(x)
		guild = ctx.message.guild.id
		if x <= 50:
			try:
				ref = db.reference('/users')
				refList = ref.order_by_child('onevsone').limit_to_last(x).get()
				scores = list(refList.items())
				scores.reverse()
				ladder = discord.Embed(title=language[148], description=language[136], color=0x33DDFF)
				ladder2 = discord.Embed(title=language[148], description=language[137], color=0x33DDFF)
				ladder3 = discord.Embed(title=language[148], description=language[138], color=0x33DDFF)
				ladder4 = discord.Embed(title=language[148], description=language[139], color=0x33DDFF)
				# First Ladder
				if x <= 25:
					for i in range(x):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value="Elo: {0} Clan: {1}".format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentclan']), inline=True)
					msg = await ctx.send(embed=ladder)
				elif x <= 50:
					for i in range(25):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value="Elo: {0} Clan: {1}".format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentclan']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(x-25):
						name = await bot.fetch_user(scores[i+25][0])
						ladder2.add_field(name=language[140].format(i+26,name.name), value="Elo: {0} Clan: {1}".format(scores[i+25][1]['onevsone'],scores[i+25][1]['clans']['currentclan']), inline=True)
					msg2 = await ctx.send(embed=ladder2)
				elif x <= 75:
					for i in range(25):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value=language[150].format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentClan']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(50):
						name = await bot.fetch_user(scores[i+25][0])
						ladder2.add_field(name=language[140].format(i+26,name.name), value=scores[i+25][1]['onevsone'], inline=True)
					msg2 = await ctx.send(embed=ladder2)
					for i in range(x-50):
						name = await bot.fetch_user(scores[i+50][0])
						ladder3.add_field(name=language[140].format(i+51,name.name), value=scores[i+50][1]['onevsone'], inline=True)
					msg3 = await ctx.send(embed=ladder3)
				elif x <= 100:
					for i in range(25):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value=language[150].format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentClan']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(50):
						name = await bot.fetch_user(scores[i+25][0])
						ladder2.add_field(name=language[140].format(i+26,name.name), value=scores[i+25][1]['onevsone'], inline=True)
					msg2 = await ctx.send(embed=ladder2)
					for i in range(75):
						name = await bot.fetch_user(scores[i+50][0])
						ladder3.add_field(name=language[140].format(i+51,name.name), value=scores[i+50][1]['onevsone'], inline=True)
					msg3 = await ctx.send(embed=ladder3)
					for i in range(x-75):
						name = await bot.fetch_user(scores[i+75][0])
						ladder4.add_field(name=language[140].format(i+76,name.name), value=scores[i+75][1]['onevsone'], inline=True)
					msg4 = await ctx.send(embed=ladder4)
			except Exception as e:
				await ctx.send(language[146].format('<@138752093308583936>'))
				print("Oneboard command call failed.")
				print(e)
		else:
			await ctx.send(language[151])
	except:
		await ctx.send(language[147])
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
			text3 = textList[2].split()
			for i in range(len(text3) - 1):
				clan += text3[i]
			points = text3[len(text3) - 1]
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
			ref2 = db.reference('/gameData')
			ref3 = db.reference('/gameData2')
			ref2.push({
			'Map': map,
			'Players': players,
			'Clan': clan,
			'Score': float(points),
			'Time': time
			})
			ref3.push({
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
#------------------------------ START Image Tracking ---------------------------
#-------------------------------------------------------------------------------
async def imagelooper(channel):
	message2 = None
	message = None
	try:
		mRef = db.reference('/imageChannels/{0}/lastMessage'.format(channel.guild.id))
		if mRef.get() == "None":
			lastM = db.reference('/imageChannels/{0}'.format(channel.guild.id))
			lastM.update({
						'lastMessage': "952233422540144721"
						})
		else:
			message2 = int(mRef.get())
	except:
		# Fetch message line goes here
		try:
			message3 = await channel.history(limit=1).flatten()
			mRef.update({
						'lastMessage': str(message3.id)
						})
			print(channel.id)
			print(channel)
		except:
			print(channel)
	
	i = 0
	if message2 == "None":
		lastM = db.reference('/imageChannels/{0}'.format(channel.guild.id))
		lastM.update({
					'lastMessage': "952233422540144721"
					})
	else:
		try:
			message = await channel.fetch_message(
				channel.last_message_id)
			mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
			mRef.update({
			'lastMessage': str(message.id)
			})
			if message2 == message.id:
				return
			else:
				# Exclude t!win command
				if ("t!win" in message.content):
					print("t!win found")
					mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
					mRef.update({
					'lastMessage': str(message.id)
					})
					return
				# Get user ID and Guild
				user = message.author.id
				guild = message.guild.id
				guild = bot.get_guild(guild)
				# Check if user exists, and create profile if not
				ref = db.reference('/users/{0}'.format(user))
				if ref.get() == None:
					# Add to scope list
					newRef = db.reference('/userIDs/{0}'.format(user))
					newRef.set({
					'scope': True
					})
					# Get username/nickname
					username = ((await guild.fetch_member(user)).nick)
					if username == None:
						username = ((await guild.fetch_member(user)).name)
					username = username.replace('/',' ')
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
					os.remove(attachment.filename)
					return await channel.send(language[108])
				else:
					# Get/Set Language
					language = LangCog.languagePicker(user)
				opt = db.reference('/users/{0}/opt'.format(user))
				if (opt.get() == True):
					return await channel.send(language[106])
				if len(message.attachments) > 0:
					if len(message.attachments) > 1:
						await channel.send(language[107])
					attachment = message.attachments[0]
					if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".PNG") or attachment.filename.endswith(".JPG") or attachment.filename.endswith(".JPEG"):
						await attachment.save(attachment.filename)
						image_path = r"{0}".format(attachment.filename)
						img = cv2.imread(image_path)
						kernel = np.ones((1, 1), np.uint8)
						img = cv2.dilate(img, kernel, iterations=1)
						img = cv2.erode(img, kernel, iterations=1)
						#plt.imshow(img, cmap="gray")
						#plt.show()
						pytesseract.tesseract_cmd = path_to_tesseract
						text = pytesseract.image_to_string(img)
						#print(text[:30])
						# Get clan 
						fRef = db.reference('/users/{0}/clans'.format(user))
						info = fRef.get()
						infoList = list(info.items())
						index = len(infoList) - 1
						clan = infoList[index][1]
						# Check if clan is not set
						if clan == "none":
							os.remove(attachment.filename)
							return await channel.send(language[108])
						# Debug line print(attachment.url)
						pRef = db.reference('/users/{0}/clans/{1}/previous'.format(user,clan))
						# Cheating check
						if pRef.get() != None:
							if text[:15] == pRef.get():
								print("{0} tried to cheat".format(user))
								os.remove(attachment.filename)
								return await channel.send(language[109].format(user))
						# Convert database version to game version
						clan = clan.replace('PERIOD5', '.')
						clan = clan.replace('DOLLAR5', '$')
						clan = clan.replace('HTAG5', '#')
						clan = clan.replace('LBRACKET5', '[')
						clan = clan.replace('SLASH5', '/')
						clan = clan.replace('RBRACKET5', ']')
						clan = clan.replace('QMARK5', '?')
						# Set win strings
						win = "[{0}] has won".format(clan)
						win2 = "[{0}] has won".format(clan)
						win3 = "[{0}]has won".format(clan)
						win4 = "[ {0}] has won".format(clan)
						win5 = "[ {0} ] has won".format(clan)
						win6 = "[{0} ] has won".format(clan)
						win7 = "{0}] has won".format(clan)
						win8 = "[{0} has won".format(clan)
						win9 = "[ {0}] has won".format(clan)
						win10 = "[ {0} ] has won".format(clan)
						try:
							# Find points string
							result = re.search('has won(.*)p', text)
							if result == None:
								points2 = "0"
								#print(text)
							else:
								points2 = result.group(1)
							# Check if double point game
							if "x" in points2:
								points2 = points2.split("x")
								points2 = points2[0]
								points2 = points2.strip(" ")
								points2 = points2.strip('.')
								points2 = points2.strip('/')
								points2 = int(points2)
								points2 = points2 * 2
								# Cheating check
								if(points2 > 1100):
									os.remove(attachment.filename)
									return await channel.send(language[176].format(user))
							else:
								points2 = points2.strip('/')
								points2 = points2.strip(" ")
								points2 = points2.strip('.')
								points2 = int(points2)
								# Cheating check
								if(points2 > 600):
									os.remove(attachment.filename)
									return await channel.send(language[176].format(user))
						except Exception as e:
							print("Points error")
							print(e)
						# Check for clan win statement
						if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text or win8 in text or win9 in text or win10 in text:
							ref2 = db.reference('/users/{0}/clans/{1}/wins'.format(user,clan))
							wins = ref2.get()
							ref2 = db.reference('/users/{0}/clans/{1}/points'.format(user,clan))
							try:
								points = int(ref2.get()) + int(points2)
								ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
							except Exception as e:
								ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
								points = points2
							wins = wins + 1
							ref2.update({
								'wins': wins,
								'previous': text[:30],
								'points': points
							})
							os.remove(attachment.filename)
							# Send win confirmation
							await channel.send(language[110].format(user,wins))
							# Interact with ELITE bot
							if(message.guild.id == 900982253679702036) and (clan.lower() == "elite"):
								try:
									update = await channel.send("e.tracker <@{0}> {1}".format(user,points2))
									await asyncio.sleep(3)
									await update.delete()
								except Exception as e:
									print(e)
							return
						else:
							with Image.open(image_path) as img:
								width, height = img.size
								left = width / 5
								top = height / 4
								right = width
								bottom = height
								img = img.crop((left, top, right, bottom))
								img = img.convert('L')  # convert image to monochrome
								img = img.point(lambda p: p > 100 and 255)
								text = pytesseract.image_to_string(img)
								# Debug commands plt.imshow(img) plt.show() print(text[:-1])
								try:
									result = re.search('has won(.*)p', text)
									if result == None:
										points2 = "0"
									else:
										points2 = result.group(1)
									if "x" in points2:
										points2 = points2.split("x")
										points2 = points2[0]
										points2 = re.sub('[^0-9]+', '', points2)
										points2 = int(points2)
										points2 = points2 * 2
										if(points2 > 1100):
											os.remove(attachment.filename)
											return await channel.send(language[176].format(user))
									else:
										points2 = re.sub('[^0-9]+', '', points2)
										points2 = int(points2)
										if(points2 > 600):
											os.remove(attachment.filename)
											return await channel.send(language[176].format(user))
								except Exception as e:
									print("Points error")
									print(e)
								if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text or win8 in text or win9 in text or win10 in text:
								# Check if clan is not set
									ref2 = db.reference('/users/{0}/clans/{1}/wins'.format(user,clan))
									wins = ref2.get()
									ref2 = db.reference('/users/{0}/clans/{1}/points'.format(user,clan))
									try:
										points = int(ref2.get()) + int(points2)
										ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
									except Exception as e:
										ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
										points = points2
									wins = wins + 1
									ref2.update({
										'wins': wins,
										'previous': text[:30],
										'points': points
									})
									os.remove(attachment.filename)
									await channel.send(language[110].format(user,wins))
									if(message.guild.id == 900982253679702036) and (clan.lower() == "elite"):
										try:
											update = await channel.send("e.tracker <@{0}> {1}".format(user,points2))
											await asyncio.sleep(3)
											await update.delete()
										except Exception as e:
											print(e)
										return
					else:
						await channel.send("Invalid image type")
		except Exception as e:
			if isinstance(e, discord.ext.commands.MessageNotFound):
				await channel.send(language[111])
				try:
					mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
					mRef.update({
					'lastMessage': str(message.id)
					})
				except:
					mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
					mRef.update({
					'lastMessage': str(message2)
					})
			elif isinstance(e, discord.ext.commands.BotMissingPermissions):
				ref = db.reference('/imageChannels/{0}'.format(channel.id))
				ref.delete()
				try:
					await channel.send(language[112].format('<@138752093308583936>'))
				except:
					print("The channel {0} in guild {1}".format(channel.id,channel.guild.name))
			else:
				#print("Channel then guild id")
				#print(channel.id)
				#print(channel.guild.id)
				try:
					mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
					mRef.update({
					'lastMessage': str(message.id)
					})
				except:
					mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
					mRef.update({
					'lastMessage': str(message2)
					})
				#await channel.send("Uh oh, something went wrong! Please harrass your local Ryo5678 to fix it.")
				#print("imageTrack loops = {0}".format(i))
				#print(e)
			#await ctx.send("!imageTrack")
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def imageTrack(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	language = LangCog.languagePicker(user)
	# Get guild id
	guild = ctx.message.guild.id
	ref = db.reference('/imageChannels/{0}'.format(guild))
	if ref.get() != None:
		await ctx.send(language[113])
	else:
		ref = db.reference('/imageChannels/{0}'.format(guild))
		ref.update({
		'channelID': "{0}".format(ctx.channel.id),
		'lastMessage': str(ctx.message.id)
		})
		channel = bot.get_channel(ctx.channel.id)
		new_task = tasks.loop(seconds=5.0,count=None,reconnect=True)(imagelooper)
		new_task.start(channel)
		await ctx.send(language[114])
	await ctx.message.delete()
#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
bot.run('Bot token goes here', reconnect=True)