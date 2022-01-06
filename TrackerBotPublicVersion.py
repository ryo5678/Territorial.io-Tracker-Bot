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
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MissingPermissions
from discord.ext.commands import MessageNotFound
path_to_tesseract = r"PATH TO TESSERACT.EXE GOES HERE"

intents = discord.Intents.default()
intents.members = True

creds = service_account.Credentials.from_service_account_file(
    'Google credential json file here')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'google sheet id here'
RANGE_NAME = 'A2'

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="Work In Progress"), status=discord.Status.online,help_command=None)

	
database_url = "Firebase url here"

cred = firebase_admin.credentials.Certificate('firebase admin credential json file here')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})



    
#-------------------------------------------------------------------------------
#------------------------------ ON READY EVENT ---------------------------------
#-------------------------------------------------------------------------------		

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	clanRanker.start()
	
	ref = db.reference('/channels')
	info = ref.get()
	channels = list(info.items())
	for i in range(len(channels)):
		print(channels[i][1])
		channel = bot.get_channel(int(channels[i][1]))
		imageLooper.start(channel)


	
# Plans for future updates
# Make a search method to display other clans leaderboards.
# Example !leaderboard cum   searches all discord databases for name attribute cum


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
#-------------------------------------------------------------------------------
#------------------------------ GET Admin Commands -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def ahelp(ctx):
	sheet = discord.Embed(title="Admin Help", description="**Commands for admins**".format(ctx), color=0x0000FF)
	sheet.add_field(name="t!setup", value="Create the database for your server.\nUsage: !setup", inline=False)
	sheet.add_field(name="t!profile", value="Display a user profile.\nUsage: self/other\nSelf: !profile\nOther: !profile @user", inline=False)
	sheet.add_field(name="t!leaderboard", value="Display the current clan wins leaderboard.\nUsage: !leaderboard", inline=False)
	sheet.add_field(name="t!soloboard", value="Display the current clan 1v1 score leaderboard.\nUsage: !soloboard", inline=False)
	sheet.add_field(name="t!setclan", value="Set a users clan name.\nUsage: !setclan CUM", inline=False)
	sheet.add_field(name="t!setSolo", value="Set a users 1v1 elo.\nUsage: !setSolo elo", inline=False)
	sheet.add_field(name="t!setWins", value="Set a users rated clan wins. \nWarning, this is a manual override of image tracking.\nUsage: !setWins @user wins", inline=False)
	sheet.add_field(name="t!top50", value="Display the current top 50 clans.\nUsage: !top50", inline=False)
	sheet.add_field(name="t!top50clan", value="Display the current top 50 clans and update every 30 seconds.\nUsage: !top50clan", inline=False)
	
	await ctx.send(embed=sheet)
#-------------------------------------------------------------------------------
#------------------------------ HELP Override -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def help(ctx):
	sheet2 = discord.Embed(title="Help", description="**Commands for users**".format(ctx), color=0x0000FF)
	sheet2.add_field(name="t!profile", value="Display a user profile.\nUsage: self/other\nSelf: !profile\nOther: !profile @user", inline=False)
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
	await ctx.send("---------------------------------------------\nTo get started, create a discord channel for posting images. \nYou can create a new one or use an existing one. \nMake sure the bot has view, send message, edit message, attach files, add reactions, and view message history permissions in the channel. \nOnce you have a channel, type t!imageTrack and the bot will confirm tracking started. \nNext a user can post an image and the bot will begin updating their profile.")
	await asyncio.sleep(15)
	await ctx.send("---------------------------------------------\nLeaderboards are a great feature with this bot. \nt!top50clan will display a updating leaderboard. \nThis means it will update every 30 seconds infinitely. \nAbuse/spam of this command will result in blacklisting your discord server. \nNormal users can use t!top50 which displays a static unchanging view of the current top 50 clans. \nMore versions of this are planned (top 25, top100 etc.)")
	await asyncio.sleep(15)
	await ctx.send("---------------------------------------------\nThere is a also a leaderboard for battle royal wins, 1v1 score, and clan wins. \nThese three leaderboards update every 15 minutes. \nt!soloboard will display the top 1v1 players using this bot. \nt!royalboard will do the same for battle royal wins. \n!leaderboard CLAN will show the top winners for the selected clan.")
#-------------------------------------------------------------------------------
#------------------------------ START Image Tracking ---------------------------
#-------------------------------------------------------------------------------	
@loop(seconds=30.0,count=None,reconnect=True)
async def imageLooper(channel):
	
	
@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def imageTrack(ctx):
	check = True
	message2 = None
	channel = bot.get_channel(ctx.channel.id)
	#print("Before loop")
	i = 0
	await ctx.message.delete()
	await ctx.send("Image Tracking Rebooted! You may now post again.")
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
						await ctx.send("Only your first image was grabbed! Please submit any additional images after 10 second intervals.")
					attachment = message.attachments[0]
					# Debug line print(attachment.url)
					if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".PNG") or attachment.filename.endswith(".JPG") or attachment.filename.endswith(".JPEG"):
						image = attachment.url
						await attachment.save(attachment.filename)
						#print(attachment.filename)
						image_path = r"{0}".format(attachment.filename)
						#print(image_path)
						img = Image.open(image_path)
						pytesseract.tesseract_cmd = path_to_tesseract
						text = pytesseract.image_to_string(img)
						#print(text[:-1])
						
						user = message.author.id
						
						# Check if user exists, and create profile if not
						ref = db.reference('/users/{0}'.format(user))
						if ref.get() == None:
							# check for guild/clan
							guild = ctx.message.guild.id
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
								await ctx.send("Profile transferred from old to new system. Please send your picture again.")
							else:
								ref.set({
								'brwins': 0,
								'clans': {
									'currentclan': "none"
								},
								'name': username,
								'onevsone': 0
								})
								await ctx.send("Please set a clan before trying to track clan wins. t!setclan NAME")
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

							# Check for clan win statement
							if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text:
								# Check if clan is not set
								if clan == "none":
									await ctx.send("Please set a clan before trying to track clan wins.")
								else:
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
			else:
				await ctx.send("Uh oh, something went wrong! Please harrass your local Ryo5678 to fix it.")
				print("imageTrack loops = {0}".format(i))
		#await ctx.send("!imageTrack")	
	check = True
@imageTrack.error
async def imageTrack_error(ctx, error):
	if isinstance(error, discord.ext.commands.MessageNotFound):
		note = "Do nothing!"
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
			ref3.set({
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
			await ctx.send("Profile transferred from old to new system. Please type t!profile again.")
		else:
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
@loop(seconds=3.0,count=None,reconnect=True)
async def sololoop(ctx):
	try:
		ref = db.reference('/users')
		refList = ref.order_by_child('onevsone').limit_to_last(25).get()
		scores = list(refList.items())
		scores.reverse()
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
		await ctx.send("Command failed. Please contact {0}".format('<@138752093308583936>'))
		check = False
		print("Soloboard command call failed before loop started.")

@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def soloboard(ctx):
	guild = ctx.message.guild.id
	sololoop.start(ctx)

#-------------------------------------------------------------------------------
#------------------------------ Clan Ranking Tracking --------------------------
#-------------------------------------------------------------------------------	
# NEW VERSION OF COMMAND LOOP
@loop(seconds=3.0,count=None,reconnect=True)
async def clanRanker():
	channel = bot.get_channel(917537295261913159)
	message2 = None
	try:
		message = await channel.fetch_message(
				channel.last_message_id)
		if message2 != message:
			message2 = message
			text = message.content
			textList = text.split()
			if len(textList) > 4:
				clan = textList[3]
				points = textList[4]
				points = re.sub(r'[^\d.]+', '', points)
				points.strip("[]")
			else:
				clan = textList[2]
				points = textList[3]
				points = re.sub(r'[^\d.]+', '', points)
				points.strip("[]")
			# Temp fix, might not work
			clan = clan.replace('.', '*')
				
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
	except:
		if message != None:
			print("An error in clanRanker occured. Previous message: " + message2.content)
		else:
			print("An erorr occured in clanRanker, previous message null")
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
	check = True
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
		check = False
	while check:
		await asyncio.sleep(20)
		try:
			ref = db.reference('/{0}/clans'.format(780723109128962070))
			clanList = ref.order_by_child('score').limit_to_last(50).get()
			clanList2 = list(clanList.items())
			clanList2.reverse()
			# First Ladder Edit
			for i in range(25):
				ladder.set_field_at(i,name="#{0} ".format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
			await msg.edit(embed = ladder)
			# Second Ladder Edit
			for i in range(25):
				ladder2.set_field_at(i,name="#{0} ".format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
			await msg2.edit(embed = ladder2)
		except:
			await ctx.send("Hey Ryo5678, you suck and an error occured.")
	await ctx.send("Error! Loop ended! Ryo5678 fix please")
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
		ladder.set_field_at(0,name="LC Team 1", value=LC1, inline=True)
		ladder.set_field_at(1,name="LC Team 2", value=LC2, inline=True)
		ladder.set_field_at(3,name="LC Team 3", value=LC3, inline=True)
		ladder.set_field_at(4,name="LC Team 4", value=LC4, inline=True)
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
	ladder.add_field(name="LC Team 1", value=LC1, inline=True)
	ladder.add_field(name="LC Team 2", value=LC2, inline=True)
	ladder.add_field(name="\u200b", value="\u200b", inline=True)
	ladder.add_field(name="LC Team 3", value=LC3, inline=True)
	ladder.add_field(name="LC Team 4", value=LC4, inline=True)
	ladder.add_field(name="\u200b", value="\u200b", inline=True)
	msg = await ctx.send(embed=ladder)
	# Begin EMBED edit loop
	await asyncio.sleep(30)
	lcstatloop.start(ctx,ladder,msg)
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
	for i in range(len(channels)):
		channel = bot.get_channel(int(channels[i][1]))
		await channel.send(warning)
	await asyncio.sleep(int(time))
	for i in range(len(channels)):
		channel = bot.get_channel(int(channels[i][1]))
		await channel.send('Territorial IO Tracker is offline. Sorry for the inconvenience.')
	await bot.change_presence(status=discord.Status.invisible)
	await bot.close() 

#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
bot.run('BOT KEY GOES HERE', bot=True, reconnect=True)
