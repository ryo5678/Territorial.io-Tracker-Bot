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
from discord.ext.commands import CommandNotFound, MissingPermissions, MessageNotFound, NotOwner, BotMissingPermissions, CommandOnCooldown
path_to_tesseract = r"Tesseract.exe here"
#from threading import Thread
intents = discord.Intents.default()
intents.messages = True
intents.members = True

creds = service_account.Credentials.from_service_account_file(
    'Google credentials here')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'Google sheet id here'
RANGE_NAME = 'A2'

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="t!help for commands"), status=discord.Status.online,help_command=None,intents=intents)


# List of removeWins admins
winAdmins = ((138752093308583936,"ELITE"),(524835935276498946,"ELITE"),(746381696139788348,"ISLAM"),(735145539494215760,"ISLAM"),(514953130178248707,"RL"))
	
database_url = "Firebase database url here"

cred = firebase_admin.credentials.Certificate('Firebase credentials here')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

textfile = open('ru-strings.txt', 'r', encoding="utf8")
russian = textfile.read().splitlines()
textfile.close()

textfile = open('en-strings.txt', 'r')
english = textfile.read().splitlines()
textfile.close()

textfile = open('fr-strings.txt', 'r', encoding="utf8")
french = textfile.read().splitlines()
textfile.close()

textfile = open('tr-strings.txt', 'r', encoding="utf8")
turkish = textfile.read().splitlines()
textfile.close()

#global message3
counter = 1
    
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
			bot.load_extension("Error")
			bot.load_extension("Poll")
			clanRanker.start()
		except Exception as e:
			print(".start() error")
			if str(e) == "object Nonetype can't be used in 'await' expression":
				print("found")
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
#----------------------------- Spreadsheet Filler ------------------------------
#-------------------------------------------------------------------------------

@bot.command(pass_context = True)
@commands.cooldown(1, 604800, commands.BucketType.user)
async def joinEvent(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
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
#------------------------------ GET Admin Commands -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def ahelp(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	a = ''
	c = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "D\u00e8"
		a = "\u00e8"
		c = "\u00e7"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	sheet = discord.Embed(title=language[5], description=language[6], color=0x0000FF)
	sheet.add_field(name=language[7], value=language[8] + '\n' + language[9], inline=False)
	sheet.add_field(name=language[10], value=language[11] + '\n' + language[12], inline=False)
	sheet.add_field(name=language[13], value=language[14] + '\n' + language[15], inline=False)
	sheet.add_field(name=language[16], value=language[17] + '\n' + language[18], inline=False)
	sheet.add_field(name=language[19], value=s + language[20] + '\n' + language[21], inline=False)
	sheet.add_field(name=language[22], value=s + language[23] + '\n' + language[24], inline=False)
	sheet.add_field(name=language[25], value=language[26] + '\n' + language[27], inline=False)
	sheet.add_field(name=language[28], value=language[29] + '\n' + language[30] + '\n' + language[31], inline=False)
	sheet.add_field(name=language[32], value=language[33] + '\n' + language[34], inline=False)
	sheet.add_field(name=language[35], value=language[36] + '\n' + language[37], inline=False)
	sheet.add_field(name=language[38], value=s + language[39] + '\n' + language[40] + '\n' + language[41], inline=False)
	sheet.add_field(name=language[42], value=s + language[43] + '\n' + language[44] + '\n' + language[45], inline=False)
	await ctx.send(embed=sheet)
#-------------------------------------------------------------------------------
#------------------------------ HELP Override -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def help(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	a = ''
	c = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "D\u00e8"
		a = "\u00e8"
		c = "\u00e7"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	sheet2 = discord.Embed(title=language[47], description=language[48], color=0x0000FF)
	sheet2.add_field(name=language[49], value=language[50], inline=False)
	sheet2.add_field(name=language[51], value=language[52], inline=False)
	sheet2.add_field(name=language[53], value=language[54] + '\n' + language[55], inline=False)
	sheet2.add_field(name=language[10], value=language[11] + '\n' + language[12], inline=False)
	sheet2.add_field(name=language[56], value=language[57] + '\n' + language[58], inline=False)
	sheet2.add_field(name=language[19], value=language[20] + '\n' + language[21], inline=False)
	sheet2.add_field(name=language[22], value=language[23] + '\n' + language[24], inline=False)
	sheet2.add_field(name=language[13], value=language[14] + '\n' + language[15], inline=False)
	sheet2.add_field(name=language[59], value=language[60] + '\n' + language[61] + '\n' + language[62], inline=False)
	sheet2.add_field(name=language[63], value=language[64] + '\n' + language[65], inline=False)
	sheet2.add_field(name=language[66], value=language[67], inline=False)
	sheet2.add_field(name=language[32], value=language[33], inline=False)
	sheet2.add_field(name=language[35], value=language[36], inline=False)
	sheet2.add_field(name=language[25], value=language[26] + '\n' + language[27], inline=False)
	sheet2.add_field(name=language[68], value=language[69] + '\n' + language[70] + '\n' + language[71], inline=False)
	sheet2.add_field(name=language[72], value=language[73] + '\n' + language[74], inline=False)
	sheet2.add_field(name=language[75], value=language[76], inline=False)
	sheet2.add_field(name=language[77], value=language[78], inline=False)
	await ctx.send(embed=sheet2)

#-------------------------------------------------------------------------------
#------------------------------ SETUP Command ----------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 1800, commands.BucketType.user)
async def setup(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	a = ''
	c = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "D\u00e8"
		a = "\u00e8"
		c = "\u00e7"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	await ctx.send(language[79] + '\n' + language[80] + '\n' + language[81])
	await asyncio.sleep(5)
	await ctx.send(language[82] + '\n' + language[83] + '\n' + language[84] + '\n' + language[85] + '\n' + language[86])
	await asyncio.sleep(10)
	await ctx.send(language[82] + '\n' + language[87] + '\n' + language[88] + '\n' + language[89])
	await asyncio.sleep(15)
	await ctx.send(language[82] + '\n' + language[90] + '\n' + language[91] + '\n' + language[92] + '\n' + language[93] + '\n' + language[94])
	await asyncio.sleep(20)
	await ctx.send(language[82] + '\n' + language[95] + '\n' + language[96])
	await asyncio.sleep(10)
	await ctx.send(language[82] + '\n' + language[97] + '\n' + language[98] + '\n' + language[99] + '\n' + language[100])
	await asyncio.sleep(20)
	await ctx.send(language[82] + '\n' + language[101] + '\n' + language[102] + '\n' + language[103] + '\n' + language[104] + '\n' + language[105])



#-------------------------------------------------------------------------------
#------------------------------ Set Announcement Channel -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def updates(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	a = ''
	c = ''
	s = ''
	j = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		c = "\u00e7"
		s = "\u00e0"
		j = "\u00ee"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	guild = ctx.message.guild.id
	ref = db.reference('/channels/{0}'.format(guild))
	if ref.get() != None:
		await ctx.send(language[115].format(a,s,j))
	else:
		ref = db.reference('/channels'.format(guild))
		ref.update({
		guild: "{0}".format(ctx.channel.id)
		})
		await ctx.send(language[116].format(a,s,j))
	await ctx.message.delete()
#-------------------------------------------------------------------------------
#------------------------------ SET Solo Elo Score -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 60, commands.BucketType.user)
async def setSolo(ctx,elo):
	user = ctx.message.author.id
	# Get/Set Language
	a = ''
	s = ''
	j = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		s = "\u00e0"
		j = "\u00ee"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	guild = ctx.message.guild.id
	num = float(elo)
	if num >= 500 or num < 0:
		await ctx.send(language[117].format(a,s))
	else:
		guild = bot.get_guild(guild)
		username = ((await guild.fetch_member(user)).nick)
		if username == None:
			username = ((await guild.fetch_member(user)).name)
			
		await ctx.send(language[118].format(a,s,j))
		
		fRef = db.reference('/users/{0}'.format(user))
		if fRef.get() == None:
			# Add to scope list
			newRef = db.reference('/userIDs/{0}'.format(user))
			newRef.set({
			'scope': True
			})
			# Add to user list
			fRef.set({
			'brwins': 0,
			'clans': {
				'currentclan': "none"
			},
			'lang': 'english',
			'name': username,
			'onevsone': num
			})
			await ctx.send(embed=profileDisplay(ctx,user,username))
		else:
			fRef.update({
			'onevsone': num
			})
			await ctx.send(embed=profileDisplay(ctx,user,username))
#-------------------------------------------------------------------------------
#--------------------------------- SET Clan ------------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 60, commands.BucketType.user)
async def setclan(ctx,name):
	# Get user ID and guild ID
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	# Convert clan name for database
	clan = name.upper()
	clan = clan.replace('.', 'period5')
	clan = clan.replace('$', 'dollar5')
	clan = clan.replace('#', 'htag5')
	clan = clan.replace('[', 'lbracket5')
	clan = clan.replace('/', 'slash5')
	clan = clan.replace(']', 'rbracket5')
	clan = clan.replace('?', 'qmark5')
	
	guild = bot.get_guild(guild)
	username = ((await guild.fetch_member(user)).nick)
	if username == None:
		username = ((await guild.fetch_member(user)).name)
	
	# check if user exists and update clan or create user
	fRef = db.reference('/users/{0}'.format(user))
	if fRef.get() == None:
		# Add to scope list
		newRef = db.reference('/userIDs/{0}'.format(user))
		newRef.set({
		'scope': True
		})
		# Add to user list
		fRef.set({
		'brwins': 0,
		'clans': {
			clan: {
				'wins': 0
				},
			'currentclan': clan
		},
		'lang': 'english',
		'name': username,
		'onevsone': num
		})
		await ctx.send(embed=profileDisplay(ctx,user,username))
	else:
		fRef = db.reference('/users/{0}/clans'.format(user))
		info = fRef.get()
		infoList = list(info.items())
		clans = []
		
		for i in range(len(infoList)):
			clans.append(infoList[i][0])
			
		if clan not in clans:
			fRef.update({
			clan: {
				'wins': 0
			},
			'currentclan': clan,
			})
		else:
			fRef.update({
			'currentclan': clan,
			})
		await ctx.send(embed=profileDisplay(ctx,user,username))

#-------------------------------------------------------------------------------
#------------------------------ Remove Clan Wins ----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def removeWins(ctx,name: discord.Member,wins):
	# Get/Set Language
	user = name.id
	user2 = ctx.message.author.id
	a = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user2))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		s = "\u00e0"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	# Assign/Retrieve command caller ID
	caller = ctx.author.id
	# Check if caller is approved user
	for x in range(len(winAdmins)):
		if caller == winAdmins[x][0]:
			clan = winAdmins[x][1]
	if clan == None:
		await ctx.send(language[121].format(a,s))
		return
	# Check if integer discord ID was provided
	try:
		int(user)
	except:
		await ctx.send(language[122])
		return
	# Check if integer was provided for wins
	try:
		int(wins)
	except:
		await ctx.send(language[122])
		return
	# Check if user exists in databse
	ref = db.reference('users/{0}'.format(user))
	if ref.get() == None:
		await ctx.send(language[123])
		return
	# Check if user is in callers clan
	ref = db.reference('users/{0}/clans/{1}/wins'.format(user,clan))
	count = ref.get()
	if count == None:
		await ctx.send(language[124].format(clan))
		return
	# Update wins
	total = count - int(wins)
	if total < 0:
		total = 0
	ref = db.reference('users/{0}/clans/{1}'.format(user,clan))
	ref.update({
		'wins': total
	})
	await ctx.send(language[125].format(total,a))

#-------------------------------------------------------------------------------
#------------------------------ PROFILE COMMAND --------------------------------
#-------------------------------------------------------------------------------

def profileDisplay(ctx,user,username):
	# Get/Set Language
	user3 = ctx.message.author.id
	ref2 = db.reference('/users/{0}/lang'.format(user3))
	lang = ref2.get()
	if lang == "french":
		language = french
	if lang == "english":
		language = english
	if lang == "russian":
		language = russian
	if lang == "turkish":
		language = turkish
	if lang == None:
		language = english
	# Get user ID
	user2 = ctx.message.author.id
	ref = db.reference('/users/{0}'.format(user))
	info = ref.get()
	
	cw = 0
	wins = []
	points = []
	
	infoList = list(info.items())
	if(infoList[1][1]['currentclan'] == "none"):
		br = infoList[0][1]
		ovo = infoList[4][1]
		clan = infoList[1][1]['currentclan']
	else:
		clans = infoList[1][1]
		clans = list(clans.items())
		x = len(clans) - 2
		clanList = []
		try:
			# Loop through all user's clans
			while x >= 0:
				clanList.append(clans[x][0])
				temp = clans[x][1]
				try:
					temp = list(temp.items())
					ref = db.reference('/users/{0}/clans/{1}'.format(user,clans[x][0]))
					# Set points if missing
					ref2 = db.reference('/users/{0}/clans/{1}/points'.format(user,clans[x][0]))
					p = ref2.get()
					if p == None:
						ref.update({
							'points': 0
							})
						points.append(0)
					else:
						points.append(p)
					# Set wins if missing
					ref3 = db.reference('/users/{0}/clans/{1}/wins'.format(user,clans[x][0]))
					w = ref3.get()
					if w == None:
						ref.update({
							'wins': 0
							})
						wins.append(0)
					else:
						wins.append(int(w))
					# Set previous if missing
					ref4 = db.reference('/users/{0}/clans/{1}/previous'.format(user,clans[x][0]))
					if ref4.get() == None:
						ref.update({
							'previous': "test"
							})
				except Exception as e:
					print(temp)
					print(e)
				x = x - 1
		except Exception as e:
			print(e)
		try:
			br = infoList[0][1]
			ovo = infoList[4][1]
			clan = infoList[1][1]['currentclan']
			if '.' or '$' or'#' or '[' or '/' or ']' or '?' in clan:
				clan = clan.replace('.', 'period5')
				clan = clan.replace('$', 'dollar5')
				clan = clan.replace('#', 'htag5')
				clan = clan.replace('[', 'lbracket5')
				clan = clan.replace('/', 'slash5')
				clan = clan.replace(']', 'rbracket5')
				clan = clan.replace('?', 'qmark5')
			# CW = total clan wins, unused at the moment
			#cw = infoList[1][1]['{0}'.format(clan)]['wins']
			br = int(br)
			ovo = float(ovo)
			#cw = int(cw)
		except Exception as e:
			print(e)
			print("first")
	try:
		guild = ctx.message.guild.id
		# Profile Embed
		sheet = discord.Embed(title=language[129], description=language[130].format(username), color=0x0000FF)
		sheet.add_field(name="Language", value=lang, inline=False)
		sheet.add_field(name=language[131], value=clan, inline=False)
		sheet.add_field(name=language[132], value=ovo, inline=False)
		sheet.add_field(name=language[133], value=br, inline=False)
		# Loop through all user clans
		for x in range(len(wins)):
			# + language[164].format(points[x])
			sheet.add_field(name=language[134].format(clanList[x]), value=language[164].format(wins[x],points[x]), inline=False)
		return sheet
	except Exception as e:
		print(e)

@bot.command(pass_context = True)
@commands.cooldown(1, 60, commands.BucketType.user)
async def profile(ctx, name: discord.Member = None):
	# check if user wants to display self or other
	if name == None:
		user = ctx.message.author.id
	else:
		user = name.id
	# Get users discord nickname or default name
	guild = ctx.message.guild.id
	guild = bot.get_guild(guild)
	# check if user exists
	ref3 = db.reference('/users/{0}'.format(user))
	if ref3.get() == None:
		# Add to scope list
		newRef = db.reference('/userIDs/{0}'.format(user))
		newRef.set({
		'scope': True
		})
		# Add to user list
		# Wrap in try/except in future, for this scenario t!profile @user (user does not exist)
		username = ((await guild.fetch_member(user)).nick)
		if username == None:
			username = (await guild.fetch_member(user)).name
		# Add name to database (Incase a user does not exist in a discord server)
		ref5 = db.reference('/users/{0}/name'.format(user))
		ref5.set({
		'name': username
		})
		# Get guild id for old database
		guild = ctx.message.guild.id
		# Create new user
		ref = db.reference('/users/{0}'.format(user))
		ref.set({
		'brwins': 0,
		'clans': {
			'currentclan': "none"
		},
		'lang': 'english',
		'name': username,
		'onevsone': 0
		})
		# Display profile
		await ctx.send(embed=profileDisplay(ctx,user,username))
	else:
		# Get name from database rather than discord. OR set it if not already in database
		ref4 = db.reference('/users/{0}/name'.format(user))
		username2 = ref4.get()
		username = ((await guild.fetch_member(user)).nick)
		if username == None:
			username = (await guild.fetch_member(user)).name
		if username2 == None:
			ref3.update({
			'name': username
			})
			# Display profile
			await ctx.send(embed=profileDisplay(ctx,user,username))
		else:
			# Display profile
			await ctx.send(embed=profileDisplay(ctx,user,username))


@bot.command(pass_context = True)
@commands.cooldown(1, 3600, commands.BucketType.user)
async def clanboard(ctx,clan):
	# Get/Set Language
	user = ctx.message.author.id
	a = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		s = "\u00e0"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	try:
		clan.strip("[]")
		clan = clan.replace('.', 'period5')
		clan = clan.replace('$', 'dollar5')
		clan = clan.replace('#', 'htag5')
		clan = clan.replace('[', 'lbracket5')
		clan = clan.replace('/', 'slash5')
		clan = clan.replace(']', 'rbracket5')
		clan = clan.replace('?', 'qmark5')
		clan = clan.upper()
		guild = ctx.message.guild.id
		try:
			ref = db.reference('/users')
			refList = ref.get()
			users = list(refList.items())
			#print(users)
			users2 = list()
			for i in range(len(users)):
				try:
					exists = users[i][1]['clans']['{0}'.format(clan)]['wins']
					users2.append(users[i])
				except:
					pass
			x = len(users2)
			users2.sort(key=lambda x: int(x[1]['clans']['{0}'.format(clan)]['wins']))
			users2.reverse()
			ladder = discord.Embed(title=language[135].format(clan), description=language[136], color=0x33DDFF)
			ladder2 = discord.Embed(title=language[135].format(clan), description=language[137].format(s), color=0x33DDFF)
			ladder3 = discord.Embed(title=language[135].format(clan), description=language[138].format(s), color=0x33DDFF)
			ladder4 = discord.Embed(title=language[135].format(clan), description=language[139].format(s), color=0x33DDFF)
			# One Ladder
			if x <= 25:
				for i in range(x):
					name = await bot.fetch_user(users2[i][0])
					ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg = await ctx.send(embed=ladder)
			# Two Ladders
			elif x <= 50:
				await ctx.send(language[142].format(a))
				for i in range(25):
					name = await bot.fetch_user(users2[i][0])
					ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg = await ctx.send(embed=ladder)
				for i in range(x-25):
					name = await bot.fetch_user(users2[i+25][0])
					ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg2 = await ctx.send(embed=ladder2)
			# Three Ladders
			elif x <= 75:
				await ctx.send(language[143].format(a))
				for i in range(25):
					name = await bot.fetch_user(users2[i][0])
					ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg = await ctx.send(embed=ladder)
				for i in range(25):
					name = await bot.fetch_user(users2[i+25][0])
					ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg2 = await ctx.send(embed=ladder2)
				for i in range(x-50):
					name = await bot.fetch_user(users2[i+50][0])
					ladder3.add_field(name=language[140].format(i+51,name.name), value=language[141].format(users2[i+50][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg3 = await ctx.send(embed=ladder3)
			# Four Ladders
			elif x <= 100:
				await ctx.send(language[144].format(a))
				for i in range(25):
					name = await bot.fetch_user(users2[i][0])
					ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg = await ctx.send(embed=ladder)
				for i in range(25):
					name = await bot.fetch_user(users2[i+25][0])
					ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg2 = await ctx.send(embed=ladder2)
				for i in range(25):
					name = await bot.fetch_user(users2[i+50][0])
					ladder3.add_field(name=language[140].format(i+51,name.name), value=language[141].format(users2[i+50][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg3 = await ctx.send(embed=ladder3)
				for i in range(x-75):
					name = await bot.fetch_user(users2[i+75][0])
					ladder4.add_field(name=language[140].format(i+76,name.name), value=language[141].format(users2[i+75][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg4 = await ctx.send(embed=ladder4)
			# Catch if members is > 100. Four ladder maximum
			else:
				await ctx.send(language[145].format(a,s))
				for i in range(25):
					name = await bot.fetch_user(users2[i][0])
					ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg = await ctx.send(embed=ladder)
				for i in range(25):
					name = await bot.fetch_user(users2[i+25][0])
					ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg2 = await ctx.send(embed=ladder2)
				for i in range(25):
					name = await bot.fetch_user(users2[i+50][0])
					ladder3.add_field(name=language[140].format(i+51,name.name), value=language[141].format(users2[i+50][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg3 = await ctx.send(embed=ladder3)
				for i in range(25):
					name = await bot.fetch_user(users2[i+75][0])
					ladder4.add_field(name=language[140].format(i+76,name.name), value=language[141].format(users2[i+75][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg4 = await ctx.send(embed=ladder4)
		except Exception as e:
			await ctx.send(language[146].format('<@138752093308583936>',a))
			print("Clanboard command call failed.")
			print(e)
	except:
		await ctx.send(language[147].format(a))
#-------------------------------------------------------------------------------
#------------------------- 1v1 LEADERBOARD COMMAND -----------------------------
#-------------------------------------------------------------------------------
@loop(seconds=30,count=None,reconnect=True)
async def sololoop(ctx,clan,l):
	try:
		a = ''
		if (l == "french"):
			a = "\u00e8"
			language = french
		elif (l == "russian"):
			language = russian
		elif (l == "turkish"):
			language = turkish
		else:
			language = english
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
		await ctx.send(language[146].format('<@138752093308583936>',a))
		check = False
		print("Soloboard command call failed before loop started.")

@bot.command(pass_context = True)
@commands.is_owner()
async def soloboard(ctx,clan):
	# Get/Set Language
	user = ctx.message.author.id
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		l = "french"
	if ref2.get() == "english":
		l = "english"
		language = english
	if ref2.get() == "russian":
		l = "russian"
		language = russian
	if ref2.get() == "turkish":
		l = "turkish"
		language = turkish
	if ref2.get() == None:
		l = "english"
		language = english
	guild = ctx.message.guild.id
	sololoop.start(ctx,clan,language)

@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def oneboard(ctx,x):
	# Get/Set Language
	user = ctx.message.author.id
	a = ''
	c = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "D\u00e8"
		a = "\u00e8"
		c = "\u00e7"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
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
			ref2.push({
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
#---------------------- Public Top 50 Clans (Non updating) ---------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def top50(ctx):	
	# Get/Set Language
	user = ctx.message.author.id
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "\u00e0"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	ref = db.reference('/{0}/clans'.format(780723109128962070))
	clanList = ref.order_by_child('score').limit_to_last(50).get()
	clanList2 = list(clanList.items())
	clanList2.reverse()
	# Embed disabled work around
	#if int(ctx.guild.id) == 780723109128962070:
	#	nonembed = ""
	#	for i in range(50):
	#		if i % 2 == 0:
	#			nonembed2 = "#{0} {1} {2}   |   ".format(i+1,clanList2[i][0],clanList2[i][1]['score'])
	#		else:
	#			nonembed2 = "#{0} {1} {2} \n".format(i+1,clanList2[i][0],clanList2[i][1]['score'])
	#		nonembed = nonembed + nonembed2
	#	await ctx.send(nonembed)
	#else:
	ladder = discord.Embed(title=language[152], description=language[136], color=0x33DDFF)
	ladder2 = discord.Embed(title=language[152], description=language[137].format(s), color=0x33DDFF)
	# First Ladder
	for i in range(25):
		ladder.add_field(name=language[149].format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
	msg = await ctx.send(embed=ladder)
	# Second Ladder
	for i in range(25):
		ladder2.add_field(name=language[149].format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
	msg2 = await ctx.send(embed=ladder2)
#-------------------------------------------------------------------------------
#---------------------- Public Top 25 Clans (Non updating) ---------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def top25(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	ref = db.reference('/{0}/clans'.format(780723109128962070))
	clanList = ref.order_by_child('score').limit_to_last(25).get()
	clanList2 = list(clanList.items())
	clanList2.reverse()
	ladder = discord.Embed(title=language[152], description=language[136], color=0x33DDFF)
	# First Ladder
	for i in range(25):
		ladder.add_field(name=language[149].format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
	msg = await ctx.send(embed=ladder)
#-------------------------------------------------------------------------------
#-------------------------------  Top Override  --------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def top(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	await ctx.send(language[154])

#-------------------------------------------------------------------------------
#---------------------- Public Top 100 Clans (Non updating) ---------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def top100(ctx):
	# Get/Set Language
	user = ctx.message.author.id
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "\u00e0"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	ref = db.reference('/{0}/clans'.format(780723109128962070))
	clanList = ref.order_by_child('score').limit_to_last(100).get()
	clanList2 = list(clanList.items())
	clanList2.reverse()
	ladder = discord.Embed(title=language[152], description=language[136], color=0x33DDFF)
	ladder2 = discord.Embed(title=language[152], description=language[137].format(s), color=0x33DDFF)
	ladder3 = discord.Embed(title=language[152], description=language[138].format(s), color=0x33DDFF)
	ladder4 = discord.Embed(title=language[152], description=language[139].format(s), color=0x33DDFF)
	# For top 200 clans
	#ladder5 = discord.Embed(title="Global Clan Rankings", description="**Current Top 101 to 125**", color=0x33DDFF)
	#ladder6 = discord.Embed(title="Global Clan Rankings", description="**Current Top 126 to 150**", color=0x33DDFF)
	#ladder7 = discord.Embed(title="Global Clan Rankings", description="**Current Top 151 to 175**", color=0x33DDFF)
	#ladder8 = discord.Embed(title="Global Clan Rankings", description="**Current Top 176 to 200**", color=0x33DDFF)
	# First Ladder
	for i in range(25):
		ladder.add_field(name=language[149].format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
	msg = await ctx.send(embed=ladder)
	# Second Ladder
	for i in range(25):
		ladder2.add_field(name=language[149].format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
	msg2 = await ctx.send(embed=ladder2)
	for i in range(25):
		ladder3.add_field(name=language[149].format(i+51) + clanList2[i+50][0], value=clanList2[i+50][1]['score'], inline=True)
	msg3 = await ctx.send(embed=ladder3)
	# Second Ladder
	for i in range(25):
		ladder4.add_field(name=language[149].format(i+76) + clanList2[i+75][0], value=clanList2[i+75][1]['score'], inline=True)
	msg4 = await ctx.send(embed=ladder4)
	# For top 200 clans
	#for i in range(25):
	#	ladder5.add_field(name="#{0} ".format(i+101) + clanList2[i+100][0], value=clanList2[i+100][1]['score'], inline=True)
	#msg5 = await ctx.send(embed=ladder5)
	#for i in range(25):
	#	ladder6.add_field(name="#{0} ".format(i+126) + clanList2[i+125][0], value=clanList2[i+125][1]['score'], inline=True)
	#msg6 = await ctx.send(embed=ladder6)
	#for i in range(25):
	#	ladder7.add_field(name="#{0} ".format(i+151) + clanList2[i+150][0], value=clanList2[i+150][1]['score'], inline=True)
	#msg7 = await ctx.send(embed=ladder7)
	#for i in range(25):
	#	ladder8.add_field(name="#{0} ".format(i+176) + clanList2[i+175][0], value=clanList2[i+175][1]['score'], inline=True)
	#msg8 = await ctx.send(embed=ladder8)

#-------------------------------------------------------------------------------
#----------------------------- Search For Clan  --------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 60, commands.BucketType.user)
async def clan(ctx,clan):
	# Get/Set Language
	user = ctx.message.author.id
	a = ''
	s = ''
	j = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		s = "\u00e0"
		j = "\u00ee"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	try:
		clan.strip("[]")
		clan = clan.replace('.', 'period5')
		clan = clan.replace('$', 'dollar5')
		clan = clan.replace('#', 'htag5')
		clan = clan.replace('[', 'lbracket5')
		clan = clan.replace('/', 'slash5')
		clan = clan.replace(']', 'rbracket5')
		clan = clan.replace('?', 'qmark5')
		clan = clan.upper()
		ref2 = db.reference('/{0}/clans/{1}'.format(780723109128962070,clan))
		clanData = ref2.get()
		if (clanData == None):
			await ctx.send(language[156].format(clan,a))
		else:
			# Set times to search back 1 week
			timeDif = timedelta(7)
			newTime = ctx.message.created_at
			oldTime = newTime - timeDif
			newTime = newTime + timedelta(1)
			# Get all games from one week ago to present
			ref = db.reference('gameData')
			snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
			snapshot = list(snapshot.items())
			games = list()
			for i in range(len(snapshot)):
				if(snapshot[i][1]['Clan'] == clan):
					games.append(snapshot[i])
			x = len(games)
			try:
				# Make plot for score vs time
				plt.xlabel(language[157])
				plt.ylabel(language[158])
				plt.title(language[159].format(a,s))
				times = list()
				scores = list()
				for i in range(len(games)):
					temp = games[i][1]['Time'].replace('T',' ')
					try:
						times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
					except:
						times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
					scores.append(games[i][1]['Score'])
				plt.plot(times,scores)
				ax = plt.gca()
				myFmt = mdates.DateFormatter('%m/%d')
				ax.xaxis.set_major_formatter(myFmt)
				ax.xaxis.set_major_locator(ticker.LinearLocator(9))
				ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
				# Save plot for discord embed
				data_stream = io.BytesIO()
				plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
				data_stream.seek(0)
				chart = discord.File(data_stream,filename="plot.png")
				# Make and send embed
				try:
					plot = discord.Embed(title="{0}".format(clan), description=language[160], color=0x03fcc6)
					plot.set_image(
					   url="attachment://plot.png"
					)
					await ctx.send(embed=plot, file=chart)
				except Exception as e:
					print("t!clan error")
					print(e)
					print(clan)
				plt.clf()
			except:
				await ctx.send(language[161].format(a,j))
			#print(games[x - 1])
			try:
				y = clanData['wins']
			except:
				snapshot2 = ref.order_by_child('Clan').equal_to(clan).get()
				snapshot2 = list(snapshot2.items())
				y = len(snapshot2)
				ref2.update({
				'wins': y
				})
			
			
			clan = clan.replace('PERIOD5', '.')
			clan = clan.replace('DOLLAR5', '$')
			clan = clan.replace('HTAG5', '#')
			clan = clan.replace('LBRACKET5', '[')
			clan = clan.replace('SLASH5', '/')
			clan = clan.replace('RBRACKET5', ']')
			clan = clan.replace('QMARK5', '?')
			
			score = clanData['score']
			await ctx.send(language[162].format(clan,score,x,y,a))
	except Exception as e:
		print(e)
		# Catch missing message permission
		try:
			await ctx.send(language[153].format(a))
		except:
			try:
				print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
			except Exception as e:
				print(e)
#-------------------------------------------------------------------------------
#------------------------------ Change bot status ------------------------------
#-------------------------------------------------------------------------------	
@commands.is_owner()
@bot.command(pass_context = True)
async def status(ctx,*,text):
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
	a = ''
	c = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "D\u00e8"
		a = "\u00e8"
		c = "\u00e7"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
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
	a = ''
	c = ''
	s = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		s = "D\u00e8"
		a = "\u00e8"
		c = "\u00e7"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	# Post to channel
	await ctx.send(language[168],file=discord.File("StatisticsLCEvent.pdf"))
#-------------------------------------------------------------------------------
#------------------------------ Compare Clans Command --------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def compare(ctx,*,clans):
	# Get/Set Language
	user = ctx.message.author.id
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french

	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	plt.clf()
	await ctx.send(language[3])
	clanList = clans.split()
	if len(clanList) < 2:
		await ctx.send("Minimum clans is 2, please try again.")
		await compare.reset_cooldown(ctx)
		return
	if len(clanList) > 5:
		await ctx.send("Maximum clans is 5, please try again.")
		await compare.reset_cooldown(ctx)
		return
	# Set times to search back 1 week
	timeDif = timedelta(9)
	newTime = ctx.message.created_at
	oldTime = newTime - timeDif
	newTime = newTime + timedelta(1)
	# Make plot for score vs time
	plt.xlabel(language[157])
	plt.ylabel(language[158])
	plt.title(language[169])
	ax = plt.gca()
	myFmt = mdates.DateFormatter('%m/%d')
	ax.xaxis.set_major_formatter(myFmt)
	ax.xaxis.set_major_locator(ticker.LinearLocator(9))
	ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
	# Loop through each clan name given
	b = 1
	pF = 0
	pS = 0
	mF = ''
	mS = ''
	gF = 0
	gS = 0
	ref = db.reference('gameData')
	snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
	snapshot = list(snapshot.items())
	for clan in clanList:
		try:
			clan.strip("[]")
			clan = clan.replace('.', 'period5')
			clan = clan.replace('$', 'dollar5')
			clan = clan.replace('#', 'htag5')
			clan = clan.replace('[', 'lbracket5')
			clan = clan.replace('/', 'slash5')
			clan = clan.replace(']', 'rbracket5')
			clan = clan.replace('?', 'qmark5')
			clan = clan.upper()
			ref = db.reference('/{0}/clans/{1}'.format(780723109128962070,clan))
			clanData = ref.get()
			if (clanData == None):
				await ctx.send(language[156].format(clan))
				await compare.reset_cooldown(ctx)
				return
			else:
				games = list()
				# Get all games from one week ago to present
				for i in range(len(snapshot)):
					if(snapshot[i][1]['Clan'] == clan):
						games.append(snapshot[i])
				count = len(games)
				times = list()
				scores = list()
				maps = list()
				players = list()
				# Plot lines
				for i in range(count):
					temp2 = defaultdict(int)
					temp = games[i][1]['Time'].replace('T',' ')
					try:
						times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
					except:
						times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
					scores.append(games[i][1]['Score'])
					try:
						maps.append(games[i][1]['Map'])
					except:
						print(games[i][1]['Map'])
					try:
						players.append(int(games[i][1]['Players']))
					except:
						print(games[i][1]['Players'])
				if(b == 1):
					if(players == []):
						pF = 0
					else:
						pF = int(statistics.mean(players))
					if(maps == []):
						mF = "N/A"
					else:
						for map in maps:
							for name in map.split():
								temp2[name] += 1
						mF = max(temp2, key=temp2.get)
					gF = count
				elif(b == 2):
					if(players == []):
						pS = 0
					else:
						pS = int(statistics.mean(players))
					if(maps == []):
						mS = "N/A"
					else:
						for map in maps:
							for name in map.split():
								temp2[name] += 1
						mS = max(temp2, key=temp2.get)
					gS = count
				b += 1
				plt.plot(times,scores,label=clan)
		except Exception as e:
			print(e)
			await ctx.send(language[153])
			await compare.reset_cooldown(ctx)
			return
	try:
		plt.legend(loc="upper right")
		# Save plot for discord embed
		data_stream = io.BytesIO()
		plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
		data_stream.seek(0)
		chart = discord.File(data_stream,filename="plot.png")
		# Make and send embed
		plot = discord.Embed(title="{0}".format(clans), description=language[163], color=0x03fcc6)
		plot.set_image(
		   url="attachment://plot.png"
		)
		await ctx.send(embed=plot, file=chart)
		try:
			await ctx.send(language[4].format(clanList[0],pF,mF,gF))
			await ctx.send(language[4].format(clanList[1],pS,mS,gS))
		except Exception as e:
			print("t!compare")
			print(e)
			print(ctx.message.guild.name)
			print(ctx.message.guild.id)
		plt.clf()
	except Exception as e:
			print(e)
			print("Test")
			await ctx.send(language[153])
		
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
	a = ''
	c = ''
	s = ''
	j = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		c = "\u00e7"
		s = "\u00e0"
		j = "\u00ee"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english

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
	a = ''
	c = ''
	s = ''
	j = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		c = "\u00e7"
		s = "\u00e0"
		j = "\u00ee"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
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
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
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
	languages = ['english','french','russian','turkish']
	a = ''
	c = ''
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
			'onevsone': 0,
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
			ref2 = db.reference('/users/{0}/lang'.format(user))
			if ref2.get() == "french":
				language = french
				a = "\u00e8"
				c = "\u00e7"
			if ref2.get() == "english":
				language = english
			if ref2.get() == "russian":
				language = russian
			if ref2.get() == "turkish":
				language = turkish
			if ref2.get() == None:
				language = english
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
			if lang == "french":
				language = french
			if lang == "english":
				language = english
			if lang == "russian":
				language = russian
			if lang == "turkish":
				language = turkish
			if lang == None:
				language = english
			print("Issue check, string index of out range")
			return await ctx.send(language[175].format(lang))
	except Exception as e:
		print(e)
#-------------------------------------------------------------------------------
#------------------------------ Remove Wins Self Version -----------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def remove(ctx,wins,points = None):
	try:
		# Get/Set Language
		user = ctx.message.author.id
		ref2 = db.reference('/users/{0}/lang'.format(user))
		if ref2.get() == "french":
			language = french
		if ref2.get() == "english":
			language = english
		if ref2.get() == "russian":
			language = russian
		if ref2.get() == "turkish":
			language = turkish
		if ref2.get() == None:
			language = english
		# Check if integer was provided for wins
		try:
			wins = int(wins)
			if (int(wins) < 0):
				return
		except:
			await ctx.send(language[122])
			return
		# Check if user exists in databse
		ref = db.reference('users/{0}'.format(user))
		if ref.get() == None:
			await ctx.send(language[123])
			return
		try:
			points = int(points)
			if (int(points) < 0):
				return
		except:
			points = 0
		ref = db.reference('users/{0}/clans/currentclan'.format(user))
		clan = ref.get()
		ref = db.reference('users/{0}/clans/{1}/wins'.format(user,clan))
		count = ref.get()
		if count == None:
			await ctx.send(language[124].format(clan))
			return
		# Check if points exist
		ref = db.reference('users/{0}/clans/{1}/points'.format(user,clan))
		count2 = ref.get()
		if count2 == None:
			await ctx.send(language[124].format(clan))
			count2 = 0
		# Update wins and points
		total = count - int(wins)
		if (count2 != 0):
			total2 = count2 - points
		if total < 0:
			total = 0
		if total2 < 0:
			total2 = 0
		ref = db.reference('users/{0}/clans/{1}'.format(user,clan))
		ref.update({
			'wins': total,
			'points': total2
		})
		await ctx.send(language[177].format(user,total,total2))
	except Exception as e:
		print(e)
#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.is_owner()
async def pollSwitch(ctx):
	try:
		bot.load_extension("Poll")
		await ctx.send("Poll is online")
	except commands.ExtensionAlreadyLoaded:
		bot.unload_extension("Poll")
		await ctx.send("Poll is offline")
#-------------------------------------------------------------------------------
#------------------------------ START Image Tracking ---------------------------
#-------------------------------------------------------------------------------
async def imagelooper(channel):
	message2 = None
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
			# Get user ID
			#print("Test")
			user = message.author.id
			# Get/Set Language
			a = ''
			c = ''
			s = ''
			ref2 = db.reference('/users/{0}/lang'.format(user))
			if ref2.get() == "french":
				language = french
				a = "\u00e8"
				c = "\u00e7"
				s = "\u00e0"
			if ref2.get() == "english":
				language = english
			if ref2.get() == "russian":
				language = russian
			if ref2.get() == "turkish":
				language = turkish
			if ref2.get() == None:
				language = english
			#except Exception as e:
				#print(e)
			opt = db.reference('/users/{0}/opt'.format(user))
			if (opt.get() == True):
				await channel.send(language[106].format(a))
				return
			user = None
			guild = None
			if message2 == message.id:
				i += 1
			else:
				if len(message.attachments) > 0:
					if len(message.attachments) > 1:
						await channel.send(language[107].format(a))
					attachment = message.attachments[0]
					if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".PNG") or attachment.filename.endswith(".JPG") or attachment.filename.endswith(".JPEG"):
						image = attachment.url
						await attachment.save(attachment.filename)
						#print(attachment.filename)
						image_path = r"{0}".format(attachment.filename)
						#print(image_path)
						img = cv2.imread(image_path)
						kernel = np.ones((1, 1), np.uint8)
						img = cv2.dilate(img, kernel, iterations=1)
						img = cv2.erode(img, kernel, iterations=1)
						#plt.imshow(img, cmap="gray")
						#plt.show()
						pytesseract.tesseract_cmd = path_to_tesseract
						text = pytesseract.image_to_string(img)
						print(text[:30])
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
							# check for guild/clan
							ref.set({
							'brwins': 0,
							'clans': {
								'currentclan': "none"
							},
							'lang': 'english',
							'name': username,
							'onevsone': 0
							})
							await channel.send(language[108].format(a))
							mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
							mRef.update({
							'lastMessage': str(message.id)
							})
							os.remove(attachment.filename)
							return
						else:
							# Get clan 
							fRef = db.reference('/users/{0}/clans'.format(user))
							info = fRef.get()
							infoList = list(info.items())
							index = len(infoList) - 1
							clan = infoList[index][1]
							# Debug line print(attachment.url)
							pRef = db.reference('/users/{0}/clans/{1}/previous'.format(user,clan))
							#print(pRef.get() + "test")
							if pRef.get() != None:
								if text[:15] == pRef.get():
									await channel.send(language[109].format(user,a,s))
									print("{0} tried to cheat".format(user))
									os.remove(attachment.filename)
									mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
									mRef.update({
									'lastMessage': str(message.id)
									})
									#language = english
									return
							# Convert database version to game version
							clan = clan.replace('PERIOD5', '.')
							clan = clan.replace('DOLLAR5', '$')
							clan = clan.replace('HTAG5', '#')
							clan = clan.replace('LBRACKET5', '[')
							clan = clan.replace('SLASH5', '/')
							clan = clan.replace('RBRACKET5', ']')
							clan = clan.replace('QMARK5', '?')
							
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
								result = re.search('has won(.*)p', text)
								if result == None:
									points2 = "0"
									#print(text)
								else:
									points2 = result.group(1)
								if "x" in points2:
									points2 = points2.split("x")
									points2 = points2[0]
									points2 = points2.strip(" ")
									points2 = points2.strip('.')
									points2 = points2.strip('/')
									points2 = int(points2)
									points2 = points2 * 2
									if(points2 > 1100):
										await channel.send(language[176].format(user))
										os.remove(attachment.filename)
										return
								else:
									points2 = points2.strip('/')
									points2 = points2.strip(" ")
									points2 = points2.strip('.')
									points2 = int(points2)
									if(points2 > 600):
										await channel.send(language[176].format(user))
										os.remove(attachment.filename)
										return
							except Exception as e:
								print("Points error")
								print(e)
							#print("BEfore win check")
							# Check for clan win statement
							if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text or win8 in text or win9 in text or win10 in text:
								# Check if clan is not set
								if clan == "none":
									await channel.send(language[108].format(a))
									mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
									mRef.update({
									'lastMessage': str(message.id)
									})
									try:
										os.remove(attachment.filename)
									except Exception as e:
										print("Os.remove error")
										print(e)
									return
								else:
									#wins = 0
									#print("BEfore win update")
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
									mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
									mRef.update({
									'lastMessage': str(message.id)
									})
									os.remove(attachment.filename)
									await channel.send(language[110].format(user,wins,a))
									if(message.guild.id == 900982253679702036) and (clan.lower() == "elite"):
										try:
											update = await channel.send("e.tracker <@{0}> {1}".format(user,points2))
											await asyncio.sleep(3)
											await update.delete()
										except Exception as e:
											print(e)
									return
									#language = english
							else:
								img = Image.open(image_path)
								width, height = img.size
								left = width / 5
								top = height / 4
								right = width
								bottom = height
								img = img.crop((left, top, right, bottom))
								img = img.convert('L')  # convert image to monochrome
								img = img.point(lambda p: p > 100 and 255)
								text = pytesseract.image_to_string(img)
								#plt.imshow(img)
								#plt.show()
								#print(text[:-1])
								try:
									result = re.search('has won(.*)p', text)
									if result == None:
										points2 = "0"
										#print(text)
									else:
										points2 = result.group(1)
									if "x" in points2:
										points2 = points2.split("x")
										points2 = points2[0]
										points2 = points2.strip(" ")
										points2 = points2.strip('.')
										points2 = points2.strip('/')
										points2 = int(points2)
										points2 = points2 * 2
										if(points2 > 1100):
											await channel.send(language[176].format(user))
											os.remove(attachment.filename)
											return
									else:
										points2 = points2.strip(" ")
										points2 = points2.strip('.')
										points2 = points2.strip('/')
										points2 = int(points2)
										if(points2 > 600):
											await channel.send(language[176].format(user))
											os.remove(attachment.filename)
											return
								except Exception as e:
									print("Points error")
									print(e)
								if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text or win8 in text or win9 in text or win10 in text:
								# Check if clan is not set
									if clan == "none":
										mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
										mRef.update({
										'lastMessage': str(message.id)
										})
										os.remove(attachment.filename)
										await channel.send(language[108].format(a))
										return
									else:
										#print("BEfore win update")
										#wins = 0
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
										mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
										mRef.update({
										'lastMessage': str(message.id)
										})
										os.remove(attachment.filename)
										await channel.send(language[110].format(user,wins,a))
										if(message.guild.id == 900982253679702036) and (clan.lower() == "elite"):
											try:
												update = await channel.send("e.tracker <@{0}> {1}".format(user,points2))
												await asyncio.sleep(3)
												await update.delete()
											except Exception as e:
												print(e)
											return
					else:
						os.remove(attachment.filename)
						z = "do nothing"
						#print("Invalid image type")
						#print(attachment.filename)
		except Exception as e:
			try:
				os.remove(attachment.filename)
			except:
				do = "nothing"
			#language = english
			if isinstance(e, discord.ext.commands.MessageNotFound):
				await channel.send(language[111].format(a))
				mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
				mRef.update({
				'lastMessage': str(message2)
				})
			elif isinstance(e, discord.ext.commands.BotMissingPermissions):
				ref = db.reference('/imageChannels/{0}'.format(channel.id))
				ref.delete()
				try:
					await channel.send(language[112].format('<@138752093308583936>',a))
				except:
					print("The channel {0} in guild {1}".format(channel.id,channel.guild.name))
			else:
				#print("Channel then guild id")
				#print(channel.id)
				#print(channel.guild.id)
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
	a = ''
	c = ''
	s = ''
	j = ''
	ref2 = db.reference('/users/{0}/lang'.format(user))
	if ref2.get() == "french":
		language = french
		a = "\u00e8"
		c = "\u00e7"
		s = "\u00e0"
		j = "\u00ee"
	if ref2.get() == "english":
		language = english
	if ref2.get() == "russian":
		language = russian
	if ref2.get() == "turkish":
		language = turkish
	if ref2.get() == None:
		language = english
	guild = ctx.message.guild.id
	ref = db.reference('/imageChannels/{0}'.format(guild))
	if ref.get() != None:
		await ctx.send(language[113].format(a,s,j))
	else:
		ref = db.reference('/imageChannels/{0}'.format(guild))
		ref.update({
		'channelID': "{0}".format(ctx.channel.id),
		'lastMessage': str(ctx.message.id)
		})
		channel = bot.get_channel(ctx.channel.id)
		new_task = tasks.loop(seconds=5.0,count=None,reconnect=True)(imagelooper)
		new_task.start(channel)
		await ctx.send(language[114].format(a,j))
	await ctx.message.delete()
#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
bot.run('Token goes here', bot=True, reconnect=True)
