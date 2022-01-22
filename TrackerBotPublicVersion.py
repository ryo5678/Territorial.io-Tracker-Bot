import discord
from discord.ext import commands
from discord.ext.commands import bot
import random
import math
import asyncio
import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import db
import re
from discord import Embed, Emoji
from discord.ext import tasks
from discord.ext.tasks import loop
import datetime
from datetime import datetime
owner_id = 138752093308583936
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from PIL import Image
from pytesseract import pytesseract
import os
import re
import cv2
import numpy as np
import matplotlib.pyplot as plt
from discord.ext.commands import CommandNotFound, MissingPermissions, MessageNotFound, NotOwner, BotMissingPermissions
path_to_tesseract = r"FILE PATH TO TESSERACT EXE"

intents = discord.Intents.default()
intents.members = True

creds = service_account.Credentials.from_service_account_file(
    'Goolge service credentials JSON file, for google sheets')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'ID OF Google sheet to use'
RANGE_NAME = 'Column range to output to'

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="Work In Progress"), status=discord.Status.online,help_command=None)

	
database_url = "Firebase Realtime URL"

cred = firebase_admin.credentials.Certificate('Firebase Admin Credentials JSON file')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

global message3

    
#-------------------------------------------------------------------------------
#------------------------------ ON READY EVENT ---------------------------------
#-------------------------------------------------------------------------------		

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	clanRanker.start()
	ref = db.reference('/imageChannels')
	info = ref.get()
	channels = list(info.items())
	
	ref2 = db.reference('/top50clans')
	info2 = ref2.get()
	clans = list(info2.items())
	
	for i in range(len(channels)):
		try:
			channel = bot.get_channel(int(channels[i][1]))
			new_task = tasks.loop(count=1,reconnect=True)(imagelooper)
			new_task.start(channel)
		except:
			print(channels[i][1] + " channel does not exist anymore")
	for i in range(len(clans)):
		try:
			channel2 = bot.get_channel(int(clans[i][0]))
			message = await channel2.fetch_message(int(clans[i][1]['message']))
			message2 = await channel2.fetch_message(int(clans[i][1]['message2']))
			top50_task = tasks.loop(count=1,reconnect=True)(top50loop)
			top50_task.start(message,message2,channel2)
		except:
			print(clans[i][0] + "Channel id, message does not exist anymore in channel")
# Plans for future updates
# Make a search method to display other clans leaderboards.
# Example !leaderboard cum   searches all discord databases for name attribute cum

@commands.is_owner()
@bot.command(pass_context = True)
async def joinEvent(ctx):
	# Gather discord user and server information
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	guild = bot.get_guild(guild)
	name = (await guild.fetch_member(user)).nick
	
	# Check if user has a discord nickname
	if name == None:
	
		# Get discord default name instead of nickname
		name2 = (await guild.fetch_member(user)).name
		
		# Log into the google sheet
		service = build('sheets', 'v4', credentials=creds)
		
		# Set the entry value for sheet
		values = [
			[
			name2
			],
		]
		body = {
			'values': values
		}
		
		# Send the update to the live google sheet
		result = service.spreadsheets().values().append(
			spreadsheetId=SPREADSHEET_ID,range=RANGE_NAME,
			valueInputOption="RAW",body=body).execute()
		
		# Provide feedback to user on success
		await ctx.send("Thanks for joining {0}! If this name is not your territorial name, please change your discord nickname and let us know.".format(name2))
		
	# Continue using discord nickname if name != none
	else:
	
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
		# Send the update to the live google sheet
		result = service.spreadsheets().values().append(
			spreadsheetId=SPREADSHEET_ID,range=RANGE_NAME,
			valueInputOption="RAW",body=body).execute()
			
		# Provide feedback to user on success
		await ctx.send("Thanks for joining {0}! If this name is not your territorial name, please change your discord nickname and let us know.".format(name))
@joinEvent.error
async def joinEvent_error(ctx, error):
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send("This command is restricted to Ryo5678 only.")
#-------------------------------------------------------------------------------
#------------------------------ GET Admin Commands -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def ahelp(ctx):
	sheet = discord.Embed(title="Admin Help", description="**Commands for admins**".format(ctx), color=0x0000FF)
	sheet.add_field(name="t!setup", value="How to setup your server.\nUsage: t!setup", inline=False)
	sheet.add_field(name="t!profile", value="Display a user profile.\nUsage: self/other\nSelf: t!profile\nOther: t!profile @user", inline=False)
	sheet.add_field(name="t!leaderboard", value="Display the current clan wins leaderboard.\nUsage: t!leaderboard", inline=False)
	sheet.add_field(name="t!soloboard", value="Display the current clan 1v1 score leaderboard.\nUsage: t!soloboard", inline=False)
	sheet.add_field(name="t!setclan", value="Set a users clan name.\nUsage: t!setclan CUM", inline=False)
	sheet.add_field(name="t!setSolo", value="Set a users 1v1 elo.\nUsage: t!setSolo elo", inline=False)
	sheet.add_field(name="t!setWins", value="Set a users rated clan wins. \nWarning, this is a manual override of image tracking.\nUsage: t!setWins @user wins", inline=False)
	sheet.add_field(name="t!top50", value="Display the current top 50 clans.\nUsage: t!top50", inline=False)
	sheet.add_field(name="t!top50clan", value="Display the current top 50 clans and update every 20 seconds. This command can only be used once! Choose the channel for it wisely.\nUsage: t!top50clan", inline=False)
	sheet.add_field(name="t!updates", value="Set the channel for Bot announcements/updates to show in.\nThis command can only be used once!\nUsage:USE IN DESIRED CHANNEL t!updates", inline=False)
	sheet.add_field(name="t!imagetrack", value="Set the channel for Bot image tracking to be in.\nThis command can only be used once!\nUsage:USE IN DESIRED CHANNEL t!imagetrack", inline=False)
	await ctx.send(embed=sheet)
#-------------------------------------------------------------------------------
#------------------------------ HELP Override -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def help(ctx):
	sheet2 = discord.Embed(title="Help", description="**Commands for users**".format(ctx), color=0x0000FF)
	sheet2.add_field(name="t!profile", value="Display a user profile.\nUsage: self/other\nSelf: !profile\nOther: !profile @user", inline=False)
	sheet2.add_field(name="t!clan", value="Display a clans current score.\nUsage: !clan CUM", inline=False)
	sheet2.add_field(name="t!setclan", value="Set a users clan name.\nUsage: !setclan CUM", inline=False)
	sheet2.add_field(name="t!setSolo", value="Set a users 1v1 elo.\nUsage: !setSolo elo", inline=False)
	sheet2.add_field(name="Win Tracking", value="Find your server's picture channel. Post a screenshot of your latest clan win.\n The win must include [clan name] wins in the bottom corner. \n Image quality may affect results. Crop out everything but territorial if possible.", inline=False)
	sheet2.add_field(name="t!top50", value="Display the current top 50 clans.\nUsage: !top50", inline=False)
	sheet2.add_field(name="t!top100", value="Display the current top 100 clans.\nUsage: !top100", inline=False)
	await ctx.send(embed=sheet2)
#-------------------------------------------------------------------------------
#------------------------------ SETUP Command -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def setup(ctx):
	await ctx.send("Welcome to Territorial Tracker setup! \nWarning! Setup is for discord users with the administrator role. \nThese commands will not work for normal users.")
	await asyncio.sleep(5)
	await ctx.send("---------------------------------------------\nThis bot uses image tracking to get information. \nFor example, if a user posts a picture of their win screen the bot will check it for a win statement. \nThe bot will then update the user profile with +1 win. \nThe bot currently checks for 1v1 scores, battle royal wins, and clan game wins.")
	await asyncio.sleep(10)
	await ctx.send("---------------------------------------------\nFor clan game wins, a user must have set their current clan. Users can do this with t!setclan NAME. \nClan wins will be tracked seperately depending on current set clan. \nYou may gain wins for any clan, but they will not be added together.")
	await asyncio.sleep(15)
	await ctx.send("---------------------------------------------\nTo get started, create a discord channel for posting images. \nYou can create a new one or use an existing one. \nMake sure the bot has view, send message, embed links, edit message, attach files, add reactions, and view message history permissions in the channel. \nOnce you have a channel, type t!imageTrack and the bot will confirm tracking started. \nNext a user can post an image and the bot will begin updating their profile.")
	await asyncio.sleep(20)
	await ctx.send("---------------------------------------------\nRepeat this process for bot updates or use an existing bot commands channel. The command to enable update/maintenance/shutdown notices is t!updates.")
	await asyncio.sleep(10)
	await ctx.send("---------------------------------------------\nRepeat this process for again for showing top 50 clans. t!top50clan can be used once to set the channel and display initial leaderboard. The bot will update it every 20 seconds. ")
	await asyncio.sleep(10)
	await ctx.send("---------------------------------------------\nLeaderboards are a great feature with this bot. \nt!top50clan will display a updating leaderboard. \nThis means it will update every 30 seconds infinitely. \nAbuse/spam of this command will result in blacklisting your discord server. \nNormal users can use t!top50 which displays a static unchanging view of the current top 50 clans. \nMore versions of this are planned (top 25, top100 etc.)")
	await asyncio.sleep(20)
	await ctx.send("---------------------------------------------\nThere is a also a leaderboard for battle royal wins, 1v1 score, and clan wins. \nThese three leaderboards update every 15 minutes. \nt!soloboard will display the top 1v1 players using this bot. \nt!royalboard will do the same for battle royal wins. \n!leaderboard CLAN will show the top winners for the selected clan.")
@help.error
async def help_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
#-------------------------------------------------------------------------------
#------------------------------ START Image Tracking ---------------------------
#-------------------------------------------------------------------------------	
async def imagelooper(channel):
	check = True
	message2 = None
	
	#mRef = db.reference('/780723109128962070/lastMessage'.format(channel.id)
	#message2 = int(mRef.get())
	
	#mRef = db.reference('/780723109128962070')
	#mRef.update({
	#'lastMessage': str(message.id)
	#})
	#print("Before loop")
	i = 0
	await channel.send("Image Tracking Rebooted! You may now post again.")
	while check:
		await asyncio.sleep(5)
		try:
			message = await channel.fetch_message(
				channel.last_message_id)
			user = None
			guild = None
			if message2 == message:
				i += 1
			else:
				message2 = message
				if len(message.attachments) > 0:
					if len(message.attachments) > 1:
						await channel.send("Only your first image was grabbed! Please submit any additional images after 10 second intervals.")
					attachment = message.attachments[0]
					# Debug line print(attachment.url)
					if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".PNG") or attachment.filename.endswith(".JPG") or attachment.filename.endswith(".JPEG"):
						image = attachment.url
						await attachment.save(attachment.filename)
						#print(attachment.filename)
						image_path = r"{0}".format(attachment.filename)
						#print(image_path)
						img = cv2.imread(image_path)
						#ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY) 
						#kernel = np.ones((3,3),np.uint8)
						#img = cv2.erode(thresh,kernel,iterations = 1)
						#plt.imshow(img, cmap="gray")
						#plt.show()
						img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
						kernel = np.ones((1, 1), np.uint8)
						img = cv2.dilate(img, kernel, iterations=1)
						img = cv2.erode(img, kernel, iterations=1)
						
						pytesseract.tesseract_cmd = path_to_tesseract
						text = pytesseract.image_to_string(img)
						#print(text[:-1])
						
						user = message.author.id
						
						# Check if user exists, and create profile if not
						ref = db.reference('/users/{0}'.format(user))
						if ref.get() == None:
							# check for guild/clan
							guild = message.guild.id
							if guild == 900982253679702036:
								clan = "ELITE"
							if guild == 907381503716114513:
								clan = "CUM"
							ref2 = db.reference('/{0}/users/{1}'.format(guild,user))
							oldUser = ref2.get()
							guild = bot.get_guild(guild)
							username = ((await guild.fetch_member(user)).nick)
							if username == None:
								username = ((await guild.fetch_member(user)).name)
							# check if old system user
							if(oldUser is not None):
								old = list(oldUser.items())
								if len(old) == 3:
									index = 2
									index2 = 1
								if len(old) == 5:
									index = 4
									index2 = 2
								if len(old) == 4:
									index = 3
									index2 = 1
								ref.set({
								'brwins': 0,
								'clans': {
								clan: {
									'wins': old[index2][1]
								},
								'currentclan': clan
								},
								'name': username,
								'onevsone': (old[index][1])
								})
								await channel.send("Profile transferred from old to new system. Please send your picture again.")
							else:
								ref.set({
								'brwins': 0,
								'clans': {
									'currentclan': "none"
								},
								'name': username,
								'onevsone': 0
								})
								await channel.send("Please set a clan before trying to track clan wins. t!setclan NAME")
						else:
							# Get clan 
							fRef = db.reference('/users/{0}/clans'.format(user))
							info = fRef.get()
							infoList = list(info.items())
							index = len(infoList) - 1
							clan = infoList[index][1]
							
							win = "[{0}] won".format(clan)
							win2 = "[{0}]  won".format(clan)
							win3 = "[{0}]won".format(clan)
							win4 = "[ {0}] won".format(clan)
							win5 = "[ {0} ] won".format(clan)
							win6 = "[{0} ] won".format(clan)
							win7 = "{0}] won".format(clan)
							
							#print("BEfore win check")
							# Check for clan win statement
							if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text:
								# Check if clan is not set
								if clan == "none":
									await channel.send("Please set a clan before trying to track clan wins.")
								else:
									#print("BEfore win update")
									ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
									wins = ref2.get()
									wins = wins['wins']
									wins = wins + 1
									ref2.update({
											'wins': wins
									})
						os.remove(attachment.filename)
					else:
						print("Invalid image type")
						print(attachment.filename)
				#i+=240
				#print("Loop restarting")
		except Exception as e:
			if isinstance(e, discord.ext.commands.MessageNotFound):
				note = "Do nothing!"
			if isinstance(e, discord.ext.commands.BotMissingPermissions):
				ref = db.reference('/imageChannels/{0}'.format(channel.id))
				ref.delete()
				try:
					await channel.send("This bot no longer has proper permissions to run image tracking in this channel. It has now been removed. Please contact {0}".format('<@138752093308583936>'))
				except:
					print("The channel {0} in guild {1}".format(channel.id,channel.guild.name))
			else:
				print("Channel then guild id")
				print(channel.id)
				print(message.guild.id)
				await channel.send("Uh oh, something went wrong! Please harrass your local Ryo5678 to fix it.")
				print("imageTrack loops = {0}".format(i))
				print(e)
		#await ctx.send("!imageTrack")	
	check = True	
@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def imageTrack(ctx):
	guild = ctx.message.guild.id
	ref = db.reference('/imageChannels/{0}'.format(guild))
	if ref.get() != None:
		await ctx.send("Sorry this server already has a channel with image tracking enabled. Please dm Ryo5678 to change channels.")
	else:
		ref = db.reference('/imageChannels')
		ref.update({
		guild: "{0}".format(ctx.channel.id)
		})
		await ctx.send("Image Tracking Enabled For This Channel")
	await ctx.message.delete()
#-------------------------------------------------------------------------------
#------------------------------ Set Announcement Channel -----------------------------
#-------------------------------------------------------------------------------	
@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def updates(ctx):
	guild = ctx.message.guild.id
	ref = db.reference('/channels/{0}'.format(guild))
	if ref.get() != None:
		await ctx.send("Sorry this server already has a channel with updates enabled. Please dm Ryo5678 to change channels.")
	else:
		ref = db.reference('/channels'.format(guild))
		ref.update({
		guild: "{0}".format(ctx.channel.id)
		})
		await ctx.send("Updates Enabled For This Channel")
	await ctx.message.delete()
#-------------------------------------------------------------------------------
#------------------------------ SET Solo Elo Score -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def setSolo(ctx,elo):
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	num = float(elo)

	guild = bot.get_guild(guild)
	username = ((await guild.fetch_member(user)).nick)
	if username == None:
		username = ((await guild.fetch_member(user)).name)
		
	await ctx.send("This command will be replaced by image tracking in the future!")
	
	fRef = db.reference('/users/{0}'.format(user))
	if fRef.get() == None:
		# check for guild/clan
		guild = ctx.message.guild.id
		if guild == 900982253679702036:
			clan = "ELITE"
		if guild == 907381503716114513:
			clan = "CUM"
		ref2 = db.reference('/{0}/users/{1}'.format(guild,user))
		oldUser = ref2.get()
		# check if old system user
		if(oldUser is not None):
			old = list(oldUser.items())
			if len(old) == 3:
				index = 2
				index2 = 1
			if len(old) == 5:
				index = 4
				index2 = 2
			if len(old) == 4:
				index = 3
				index2 = 1
			fRef.set({
			'brwins': 0,
			'clans': {
			clan: {
				'wins': old[index2][1]
			},
			'currentclan': clan
			},
			'name': username,
			'onevsone': (old[index][1])
			})
			await ctx.send("Profile transferred from old to new system. Please type t!setsolo again.")
		else:
			fRef.set({
			'brwins': 0,
			'clans': {
				'currentclan': "none"
			},
			'name': username,
			'onevsone': num
			})
			await ctx.send(embed=profileDisplay(ctx,user,username))
	else:
		fRef.update({
		'onevsone': num
		})
		await ctx.send(embed=profileDisplay(ctx,user,username))
@setSolo.error
async def setSolo_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please include the 1v1 score to set.\nExample: t!setSolo 42.0")	
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
#-------------------------------------------------------------------------------
#--------------------------------- SET Clan ------------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def setclan(ctx,name):
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	clan = name.upper()
	
	guild = bot.get_guild(guild)
	username = ((await guild.fetch_member(user)).nick)
	if username == None:
		username = ((await guild.fetch_member(user)).name)
	
	# check if user exists and update clan or create user
	fRef = db.reference('/users/{0}'.format(user))
	if fRef.get() == None:
		guild = ctx.message.guild.id
		if guild == 900982253679702036:
			clan = "ELITE"
		if guild == 907381503716114513:
			clan = "CUM"
		ref2 = db.reference('/{0}/users/{1}'.format(guild,user))
		oldUser = ref2.get()
		# check if old system user
		if(oldUser is not None):
			old = list(oldUser.items())
			if len(old) == 3:
				index = 2
				index2 = 1
			if len(old) == 5:
				index = 4
				index2 = 2
			if len(old) == 4:
				index = 3
				index2 = 1
			fRef.set({
			'brwins': 0,
			'clans': {
			clan: {
				'wins': old[index2][1]
			},
			'currentclan': clan
			},
			'name': username,
			'onevsone': (old[index][1])
			})
			await ctx.send("Profile transferred from old to new system.")
		else:
			fRef.set({
			'brwins': 0,
			'clans': {
				clan: {
					'wins': 0
					},
				'currentclan': clan
			},
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
@setclan.error
async def setclan_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please enter the name of the clan. Example: t!setclan CUM")	
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")

#-------------------------------------------------------------------------------
#------------------------------ SET Total Clan Wins ----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def setWins(ctx, name: discord.User ,wins):
	user = name.id
	guild = ctx.message.guild.id
	num = int(wins)
	#print(guild)
	#print(user)
	
	fRef = db.reference('/{0}/users/{1}'.format(guild,user))
	if fRef.get() == None:
		#print("Inside if")
		await ctx.send("User does not exist yet. Make sure to initialize them with !add @{0}".format(ctx.message.author))
	else:
		#print("Inside else")
		ref = db.reference('/{0}/users/{1}'.format(guild,user))
		ref.update({
		'leaderboard': num
		})
@setWins.error
async def setWins_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please enter the name of the user you wish to update.\nAfter the name please include the number of wins to set.\nExample: !setWins @Ryo5678 29")	

#-------------------------------------------------------------------------------
#------------------------------ PROFILE COMMAND --------------------------------
#-------------------------------------------------------------------------------

def profileDisplay(ctx,user,username):
	ref = db.reference('/users/{0}'.format(user))
	info = ref.get()
	
	cw = 0
	
	infoList = list(info.items())
	if(infoList[1][1]['currentclan'] == "none"):
		br = infoList[0][1]
		ovo = infoList[3][1]
		clan = infoList[1][1]['currentclan']
	else:
		br = infoList[0][1]
		ovo = infoList[3][1]
		clan = infoList[1][1]['currentclan']
		cw = infoList[1][1]['{0}'.format(clan)]['wins']
		br = int(br)
		ovo = float(ovo)
		cw = int(cw)
	
	guild = ctx.message.guild.id
	# Profile Embed
	sheet = discord.Embed(title="Profile", description="**{0}'s stats**".format(username), color=0x0000FF)
	sheet.add_field(name="Clan", value=clan, inline=False)
	sheet.add_field(name="1v1 elo", value=ovo, inline=False)
	sheet.add_field(name="Battle Royal Wins", value=br, inline=False)
	sheet.add_field(name="Total Clan Wins", value=cw, inline=False)
	
	return sheet

@bot.command(pass_context = True)
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
@profile.error
async def profile_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
#-------------------------------------------------------------------------------
#----------------------- CLAN RATED LEADERBOARD COMMAND ------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def leaderboard(ctx):
	check = True
	await ctx.message.delete()
	guild = ctx.message.guild.id
	guild = bot.get_guild(guild)
	board = discord.Embed(title="{0} Leaderboard".format(guild.name), description="**Current Top 10**", color=0xa81207)
	board.add_field(name="ðŸ¥‡**1st Place**ðŸ¥‡", value="test", inline=False)
	board.add_field(name="ðŸ¥ˆ**2nd Place**ðŸ¥ˆ", value="test", inline=False)
	board.add_field(name="ðŸ¥‰**3rd Place**ðŸ¥‰", value="test", inline=False)
	board.add_field(name="ðŸ…**4th and 5th**ðŸ…", value="test", inline=False)
	board.add_field(name="ðŸŽ–ï¸**6th to 10thðŸŽ–ï¸**", value="test", inline=False)
	timestamp = datetime.now()
	board.add_field(name="\u200b",value="Last refreshed at " + timestamp.strftime(r"%I:%M %p") + " EST",inline=False)
	msg = await ctx.send(embed=board)
	while check:
		boardRef = db.reference('/{0}/users'.format(guild.id))
		boardList = boardRef.order_by_child('leaderboard').limit_to_last(10).get()
		cL = list(boardList.items())
		cL.reverse()
		max = 10
		y = len(cL)
		if y <= 10:
			max = max - y
		for x in range(max):
			cL.append(["None",{'leaderboard':0}])
		cL.reverse()
		
		bL = [[0 for x in range(2)] for y in range(10)]
		for x in range(10):
			bL[x][1] = cL[x][1]
			if cL[x][0] is not "None":
				temp = cL[x][0]
			try:
				bL[x][0] = ((await guild.fetch_member(temp)).nick)
			except:
				ref = db.reference('/{0}/users/{1}/leaderboard'.format(guild.id,temp))
				ref.delete()
				check = False
			if bL[x][0] is None:
				bL[x][0] = (await guild.fetch_member(temp)).name
		board.set_field_at(0,name="ðŸ¥‡**1st Place**ðŸ¥‡", value="{0} - {1} wins".format(bL[9][0],bL[9][1]['leaderboard']), inline=False)
		board.set_field_at(1,name="ðŸ¥ˆ**2nd Place**ðŸ¥ˆ", value="{0} - {1} wins".format(bL[8][0],bL[8][1]['leaderboard']), inline=False)
		board.set_field_at(2,name="ðŸ¥‰**3rd Place**ðŸ¥‰", value="{0} - {1} wins".format(bL[7][0],bL[7][1]['leaderboard']), inline=False)
		board.set_field_at(3,name="ðŸ…**4th and 5th**ðŸ…", value="{0} - {1} wins \n{2} - {3} wins \n".format(bL[6][0],bL[6][1]['leaderboard'],bL[5][0],bL[5][1]['leaderboard']), inline=False)
		board.set_field_at(4,name="ðŸŽ–ï¸**6th to 10thðŸŽ–ï¸**", value="{0} - {1} wins \n{2} - {3} wins \n{4} - {5} wins \n{6} - {7} wins \n{8} - {9} wins \n".format(bL[4][0],bL[4][1]['leaderboard'],bL[3][0],bL[3][1]['leaderboard'],bL[2][0],bL[2][1]['leaderboard'],bL[1][0],bL[1][1]['leaderboard'],bL[0][0],bL[0][1]['leaderboard']), inline=False)
		timestamp = datetime.now()
		board.set_field_at(5,name="\u200b",value="Last refreshed at " + timestamp.strftime(r"%I:%M %p"),inline=False)
		await msg.edit(embed = board)
		await asyncio.sleep(900)
	check = True
#-------------------------------------------------------------------------------
#------------------------- 1v1 LEADERBOARD COMMAND -----------------------------
#-------------------------------------------------------------------------------
@loop(seconds=30,count=None,reconnect=True)
async def sololoop(ctx,clan):
	try:
		ref = db.reference('/users')
		refList = ref.order_by_child('onevsone').limit_to_last(25).get()
		scores = list(refList.items())
		scores.reverse()
		ladder = discord.Embed(title="Global 1v1 Rankings", description="**Current Top 25**", color=0x33DDFF)
		# First Ladder
		for i in range(25):
			ladder.add_field(name="#{0} ".format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
		msg = await ctx.send(embed=ladder)
	except:
		await ctx.send("Command failed. Please contact {0}".format('<@138752093308583936>'))
		check = False
		print("Soloboard command call failed before loop started.")

@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def soloboard(ctx,clan):
	guild = ctx.message.guild.id
	sololoop.start(ctx,clan)

@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def oneboard(ctx,x):
	try:
		x = int(x)
		guild = ctx.message.guild.id
		if x <= 50:
			try:
				ref = db.reference('/users')
				refList = ref.order_by_child('onevsone').limit_to_last(x).get()
				scores = list(refList.items())
				scores.reverse()
				ladder = discord.Embed(title="Global 1v1 Rankings", description="**Current Top 25**", color=0x33DDFF)
				ladder2 = discord.Embed(title="Global 1v1 Rankings", description="**Current Top 26 to 50**", color=0x33DDFF)
				ladder3 = discord.Embed(title="Global 1v1 Rankings", description="**Current Top 51 to 75**", color=0x33DDFF)
				ladder4 = discord.Embed(title="Global 1v1 Rankings", description="**Current Top 76 to 100**", color=0x33DDFF)
				# First Ladder
				if x <= 25:
					for i in range(x):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name="#{0} {1} ".format(i+1,name.name), value="Elo: {0} Clan: {1}".format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentclan']), inline=True)
					msg = await ctx.send(embed=ladder)
				elif x <= 50:
					for i in range(25):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name="#{0} {1} ".format(i+1,name.name), value="Elo: {0} Clan: {1}".format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentclan']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(x-25):
						name = await bot.fetch_user(scores[i+25][0])
						ladder2.add_field(name="#{0} {1} ".format(i+26,name.name), value="Elo: {0} Clan: {1}".format(scores[i+25][1]['onevsone'],scores[i+25][1]['clans']['currentclan']), inline=True)
					msg2 = await ctx.send(embed=ladder2)
				elif x <= 75:
					for i in range(25):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name="#{0} {1} ".format(i+1,name.name), value="Elo: {0} Clan: {1}".format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentClan']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(50):
						name = await bot.fetch_user(scores[i+25][0])
						ladder2.add_field(name="#{0} {1} ".format(i+26,name.name), value=scores[i+25][1]['onevsone'], inline=True)
					msg2 = await ctx.send(embed=ladder2)
					for i in range(x-50):
						name = await bot.fetch_user(scores[i+50][0])
						ladder3.add_field(name="#{0} {1} ".format(i+51,name.name), value=scores[i+50][1]['onevsone'], inline=True)
					msg3 = await ctx.send(embed=ladder3)
				elif x <= 100:
					for i in range(25):
						name = await bot.fetch_user(scores[i][0])
						ladder.add_field(name="#{0} {1} ".format(i+1,name.name), value="Elo: {0} Clan: {1}".format(scores[i][1]['onevsone'],scores[i][1]['clans']['currentClan']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(50):
						name = await bot.fetch_user(scores[i+25][0])
						ladder2.add_field(name="#{0} {1} ".format(i+26,name.name), value=scores[i+25][1]['onevsone'], inline=True)
					msg2 = await ctx.send(embed=ladder2)
					for i in range(75):
						name = await bot.fetch_user(scores[i+50][0])
						ladder3.add_field(name="#{0} {1} ".format(i+51,name.name), value=scores[i+50][1]['onevsone'], inline=True)
					msg3 = await ctx.send(embed=ladder3)
					for i in range(x-75):
						name = await bot.fetch_user(scores[i+75][0])
						ladder4.add_field(name="#{0} {1} ".format(i+76,name.name), value=scores[i+75][1]['onevsone'], inline=True)
					msg4 = await ctx.send(embed=ladder4)
			except Exception as e:
				await ctx.send("Command failed. Please contact {0}".format('<@138752093308583936>'))
				check = False
				print("Soloboard command call failed before loop started.")
				print(e)
		else:
			await ctx.send("50 is the maximum value for this command")
	except:
		await ctx.send("The value entered is not an integer. It must be a positive number, no decimals.")
@oneboard.error
async def oneboard_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send("You need to be an administrator to use this command.")
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
			textList = text.split()
			if len(textList) == 3:
				check3 = False
			else:
				if len(textList) > 4:
					map = textList[0] + textList[1]
					players = textList[2]
					clan = textList[3]
					points = textList[4]
					points = re.sub(r'[^\d.]+', '', points)
					points.strip("[]")
				else:
					map = textList[0]
					players = textList[1]
					clan = textList[2]
					points = textList[3]
					points = re.sub(r'[^\d.]+', '', points)
					points.strip("[]")
				# Temp fix, might not work
				clan = clan.replace('.', '*')
				clan = clan.replace('$', 'S')
				time = message.created_at.isoformat()
					
				# Set clan data, either create or update.
				ref = db.reference('/780723109128962070/clans/{0}'.format(clan))
				if(ref.get() == None):
					ref.set({
					'score': float(points)
					})
				else:
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
# OLD COMMAND VERSION, SAVED IN CASE OF ERRORS WITH NEW VERSION
#@bot.command(pass_context = True)
#@commands.is_owner()
#async def clanRanker(ctx):	
	#channel = bot.get_channel(917537295261913159)
	#message2 = None
	#await ctx.message.delete()
	#await ctx.send("Clan ranks are now being tracked!")
	#i = 0
	#while True:
		#i = i + 1
		#if (i % 100) == 0:
			#print("Loop at {0}".format(i))
		#message = await channel.fetch_message(
		#		channel.last_message_id)
		#if message2 == message:
		#	await asyncio.sleep(3)
		#else:
			#message2 = message
			#text = message.content
			#textList = text.split()
			#if len(textList) > 4:
			#	clan = textList[3]
			#	points = textList[4]
			#	points = re.sub(r'[^\d.]+', '', points)
			#	points.strip("[]")
			#else:
			#	clan = textList[2]
			#	points = textList[3]
			#	points = re.sub(r'[^\d.]+', '', points)
			#	points.strip("[]")
			# Temp fix, might not work
			#clan.replace('.', '*')
			#
			# Set clan data, either create or update.
			#ref = db.reference('/780723109128962070/clans/{0}'.format(clan))
			#if(ref.get() == None):
			#	ref.set({
			#	'score': float(points)
			#	})
			#else:
			#	ref.update({
			#	'score': float(points)
			#	})
			#await asyncio.sleep(3)
	#print("While loop ended in clanRanker")
#-------------------------------------------------------------------------------
#--------------------------- Private Top 50 Clans (Updating) -------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def top50clan(ctx):
	await ctx.message.delete()
	channel = ctx.message.channel
	try:
		ref = db.reference('/top50clans/{0}'.format(channel.id))
		if ref.get() != None:
			await ctx.send("Sorry this server already has a channel with top50 enabled. Please dm Ryo5678 to change channels.")
		else:
			ref = db.reference('/{0}/clans'.format(780723109128962070))
			clanList = ref.order_by_child('score').limit_to_last(50).get()
			clanList2 = list(clanList.items())
			clanList2.reverse()
			
			ladder = discord.Embed(title="Global Clan Rankings", description="**Current Top 25**", color=0x33DDFF)
			ladder2 = discord.Embed(title="Global Clan Rankings", description="**Current Top 25 to 50**", color=0x33DDFF)
			# First Ladder
			for i in range(25):
				ladder.add_field(name="#{0} ".format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
			msg = await ctx.send(embed=ladder)
			await asyncio.sleep(2)
			id1 = await channel.fetch_message(
					channel.last_message_id)
			id1 = id1.id
			# Second Ladder
			for i in range(25):
				ladder2.add_field(name="#{0} ".format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
			msg2 = await ctx.send(embed=ladder2)
			await asyncio.sleep(2)
			id2 = await channel.fetch_message(
					channel.last_message_id)
			id2 = id2.id
			# Setup database entry
			ref = db.reference('/top50clans')
			name = '{0}'.format(channel.id)
			ref.update({
			name: {
				'message': "{0}".format(id1),
				'message2': "{0}".format(id2)
				}
			})
			await ctx.send("Updates Enabled For This Channel")
	except:
		await ctx.send("An error occured. Please try the command again or contact Ryo5678 to fix it")
@top50clan.error
async def top50clan_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send("You need to be an administrator to use this command.")
async def top50loop(message,message2,channel2):
	check = True
	while check:
		await asyncio.sleep(30)
		try:
			ladder = discord.Embed(title="Global Clan Rankings", description="**Current Top 25**", color=0x33DDFF)
			ladder2 = discord.Embed(title="Global Clan Rankings", description="**Current Top 25 to 50**", color=0x33DDFF)
			
			ref = db.reference('/{0}/clans'.format(780723109128962070))
			clanList = ref.order_by_child('score').limit_to_last(50).get()
			clanList2 = list(clanList.items())
			clanList2.reverse()
			# First Ladder Edit
			for i in range(25):
				ladder.add_field(name="#{0} ".format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
			await message.edit(embed = ladder)
			await asyncio.sleep(2)
			# Second Ladder Edit
			for i in range(25):
				ladder2.add_field(name="#{0} ".format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
			await message2.edit(embed = ladder2)
		except:
			await channel2.send("Hey Ryo5678, you suck and an error occured.")
	await channel2.send("Error! Loop ended! Ryo5678 fix please")
#-------------------------------------------------------------------------------
#---------------------- Public Top 50 Clans (Non updating) ---------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def top50(ctx):
	try:
		ref = db.reference('/{0}/clans'.format(780723109128962070))
		clanList = ref.order_by_child('score').limit_to_last(50).get()
		clanList2 = list(clanList.items())
		clanList2.reverse()
		ladder = discord.Embed(title="Global Clan Rankings", description="**Current Top 25**", color=0x33DDFF)
		ladder2 = discord.Embed(title="Global Clan Rankings", description="**Current Top 25 to 50**", color=0x33DDFF)
		# First Ladder
		for i in range(25):
			ladder.add_field(name="#{0} ".format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
		msg = await ctx.send(embed=ladder)
		# Second Ladder
		for i in range(25):
			ladder2.add_field(name="#{0} ".format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
		msg2 = await ctx.send(embed=ladder2)
	except:
		await ctx.send("An error occured. Please try the command again or contact Ryo5678 to fix it")
@top50.error
async def top50_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
#-------------------------------------------------------------------------------
#---------------------- Public Top 200 Clans (Non updating) ---------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def top100(ctx):
	try:
		ref = db.reference('/{0}/clans'.format(780723109128962070))
		clanList = ref.order_by_child('score').limit_to_last(100).get()
		clanList2 = list(clanList.items())
		clanList2.reverse()
		ladder = discord.Embed(title="Global Clan Rankings", description="**Current Top 25**", color=0x33DDFF)
		ladder2 = discord.Embed(title="Global Clan Rankings", description="**Current Top 26 to 50**", color=0x33DDFF)
		ladder3 = discord.Embed(title="Global Clan Rankings", description="**Current Top 51 to 75**", color=0x33DDFF)
		ladder4 = discord.Embed(title="Global Clan Rankings", description="**Current Top 76 to 100**", color=0x33DDFF)
		# For top 200 clans
		#ladder5 = discord.Embed(title="Global Clan Rankings", description="**Current Top 101 to 125**", color=0x33DDFF)
		#ladder6 = discord.Embed(title="Global Clan Rankings", description="**Current Top 126 to 150**", color=0x33DDFF)
		#ladder7 = discord.Embed(title="Global Clan Rankings", description="**Current Top 151 to 175**", color=0x33DDFF)
		#ladder8 = discord.Embed(title="Global Clan Rankings", description="**Current Top 176 to 200**", color=0x33DDFF)
		# First Ladder
		for i in range(25):
			ladder.add_field(name="#{0} ".format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
		msg = await ctx.send(embed=ladder)
		# Second Ladder
		for i in range(25):
			ladder2.add_field(name="#{0} ".format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
		msg2 = await ctx.send(embed=ladder2)
		for i in range(25):
			ladder3.add_field(name="#{0} ".format(i+51) + clanList2[i+50][0], value=clanList2[i+50][1]['score'], inline=True)
		msg3 = await ctx.send(embed=ladder3)
		# Second Ladder
		for i in range(25):
			ladder4.add_field(name="#{0} ".format(i+76) + clanList2[i+75][0], value=clanList2[i+75][1]['score'], inline=True)
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
	except:
		await ctx.send("An error occured. Please try the command again or contact Ryo5678 to fix it")
@top100.error
async def top100_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
#-------------------------------------------------------------------------------
#--------------------------- LC Events Leaderboard -----------------------------
#-------------------------------------------------------------------------------
@loop(seconds=30.0,count=None,reconnect=True)
async def lcstatloop(ctx,ladder,msg):
	try:
		ref = db.reference('/{0}/clans/LC1/score'.format(780723109128962070))
		ref2 = db.reference('/{0}/clans/LC2/score'.format(780723109128962070))
		ref3 = db.reference('/{0}/clans/LC3/score'.format(780723109128962070))
		ref4 = db.reference('/{0}/clans/LC4/score'.format(780723109128962070))
		
		LC1 = ref.get()
		LC2 = ref2.get()
		LC3 = ref3.get()
		LC4 = ref4.get()
		# For top 200 clans
		#ladder5 = discord.Embed(title="Global Clan Rankings", description="**Current Top 101 to 125**", color=0x33DDFF)
		#ladder6 = discord.Embed(title="Global Clan Rankings", description="**Current Top 126 to 150**", color=0x33DDFF)
		#ladder7 = discord.Embed(title="Global Clan Rankings", description="**Current Top 151 to 175**", color=0x33DDFF)
		#ladder8 = discord.Embed(title="Global Clan Rankings", description="**Current Top 176 to 200**", color=0x33DDFF)
		# First Ladder
		ladder.set_field_at(0,name="LC Team 1", value=LC1+0.5, inline=True)
		ladder.set_field_at(1,name="LC Team 2", value=LC2, inline=True)
		ladder.set_field_at(3,name="LC Team 3", value=LC3+0.5, inline=True)
		ladder.set_field_at(4,name="LC Team 4", value=LC4+2.0, inline=True)
		await msg.edit(embed=ladder)
	except:
		await ctx.send("An error occured. Please try the command again or contact Ryo5678 to fix it")
# Command to start LCStatLoop
@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def lcstats(ctx):
	# Get LC team scores
	ref = db.reference('/{0}/clans/LC1/score'.format(780723109128962070))
	ref2 = db.reference('/{0}/clans/LC2/score'.format(780723109128962070))
	ref3 = db.reference('/{0}/clans/LC3/score'.format(780723109128962070))
	ref4 = db.reference('/{0}/clans/LC4/score'.format(780723109128962070))
	LC1 = ref.get()
	LC2 = ref2.get()
	LC3 = ref3.get()
	LC4 = ref4.get()
	# Initialize EMBED
	ladder = discord.Embed(title="League Of Clans", description="**Tournament Ranking**", color=0x03fcc6)
	ladder.add_field(name="LC Team 1", value=LC1 + 0.5, inline=True)
	ladder.add_field(name="LC Team 2", value=LC2, inline=True)
	ladder.add_field(name="\u200b", value="\u200b", inline=True)
	ladder.add_field(name="LC Team 3", value=LC3 + 0.5, inline=True)
	ladder.add_field(name="LC Team 4", value=LC4 + 2.0, inline=True)
	ladder.add_field(name="\u200b", value="\u200b", inline=True)
	msg = await ctx.send(embed=ladder)
	# Begin EMBED edit loop
	await asyncio.sleep(30)
	lcstatloop.start(ctx,ladder,msg)
@lcstats.error
async def lcstats_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send("This server does not support this command.")
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send("You need to be an administrator to use this command.")
#-------------------------------------------------------------------------------
#----------------------------- Search For Clan  --------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def clan(ctx,clan):
	try:
		clan = clan.replace('.', '*')
		clan = clan.replace('$', 'S')
		clan = clan.upper()
		ref = db.reference('/{0}/clans/{1}'.format(780723109128962070,clan))
		clanData = ref.get()
		if (clanData == None):
			await ctx.send("The clan {0} does not exist or is spelled/typed incorrectly.".format(clan))
		else:
			score = clanData['score']
			await ctx.send("The clan, {0}, has a last known score of {1}.".format(clan,score))
	except:
		await ctx.send("An error occured. Please try the command again or contact Ryo5678 to fix it")
@clan.error
async def clan_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("This command requires a clan, please try t!clan NAME.")
#-------------------------------------------------------------------------------
#------------------------------ Change bot status ------------------------------
#-------------------------------------------------------------------------------	
@commands.is_owner()
@bot.command(pass_context = True)
async def status(ctx,*,text):
	await bot.change_presence(activity=discord.Game(name=text))
	await ctx.message.delete()
#-------------------------------------------------------------------------------
#------------------------------ EMOJI DEBUG COMMAND ----------------------------
#-------------------------------------------------------------------------------
#@bot.command(pass_context=True)
#async def debug(ctx, emoji: Emoji):
    #embed = Embed(description=f"emoji: {emoji}", title=f"emoji: {emoji}")
    #embed.add_field(name="id", value=repr(emoji.id))
    #embed.add_field(name="name", value=repr(emoji.name))
    #await bot.say(embed=embed)
#-------------------------------------------------------------------------------
#----------------------------- Catch Missing Permission Error ------------------
#---------------------------------- Not needed anymore -------------------------
#@bot.event
#async def on_command_error(ctx,error):
	#if isinstance(error, CommandNotFound):
	#	return
	#if isinstance(error, MissingPermissions):
	#	await ctx.send("You do not have permission to use this command.\n Try !help for commands you can use")
	#	return
#-------------------------------------------------------------------------------
#------------------------------ PING CRASH TEST --------------------------------
#-------------------------------------------------------------------------------
@bot.command()
@commands.is_owner()
async def ping(ctx):
			await ctx.send("Pong")
@ping.error
async def ping_error(ctx, error):
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send("This command is restricted to Ryo5678 only.")
#-------------------------------------------------------------------------------
#------------------------------ SHUTDOWN COMMAND -------------------------------
#-------------------------------------------------------------------------------
# Shutdown the bot!
@bot.command()
@commands.is_owner()
async def shutdown(ctx,time,*,warning):
	await ctx.message.delete()
	ref = db.reference('/channels')
	info = ref.get()
	channels = list(info.items())
	ref2 = db.reference('/imageChannels')
	info2 = ref2.get()
	channels2 = list(info2.items())
	# Image channels
	#for i in range(len(channels2)):
	#	channel = bot.get_channel(int(channels2[i][1]))
	#	await channel.send(warning)
	#await asyncio.sleep(int(time))
	#for i in range(len(channels2)):
		#channel = bot.get_channel(int(channels2[i][1]))
		#await channel.send('Territorial IO Tracker is offline. Sorry for the inconvenience.')
	# Announcement channels
	for i in range(len(channels)):
		channel = bot.get_channel(int(channels[i][1]))
		await channel.send(warning)
	await asyncio.sleep(int(time))
	for i in range(len(channels)):
		channel = bot.get_channel(int(channels[i][1]))
		await channel.send('Territorial IO Tracker is offline. Sorry for the inconvenience.')
	await bot.change_presence(status=discord.Status.invisible)
	await bot.close() 
@shutdown.error
async def shutdown_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please enter the time (seconds) and reason. t!shutdown 10 Reboot")
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send("This command is restricted to Ryo5678 only.")	
	print(error)
#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
bot.run('TOKEN GOES HERE', bot=True, reconnect=True)
