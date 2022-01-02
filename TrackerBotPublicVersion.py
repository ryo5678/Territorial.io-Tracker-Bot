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
path_to_tesseract = r"Path to tesseract.exe goes here"

intents = discord.Intents.default()
intents.members = True

#def read_creds():
#	with open("territorial-tracker-bot-6e0ec07d6eca.json", "r") as f:
#		lines = f.readlines()
#		return lines[0].strip()
#creds = read_creds()
creds = service_account.Credentials.from_service_account_file(
    'json file here')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'google sheet ID here'
RANGE_NAME = 'column name goes here'

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="Work In Progress"), status=discord.Status.online,help_command=None)

firebase_key = {
  'Fire base key goes here'
  'Will be replaced with json file in future'
}	
database_url = "firebase database url here"

cred = credentials.Certificate(firebase_key)
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})



    
#-------------------------------------------------------------------------------
#------------------------------ ON READY EVENT ---------------------------------
#-------------------------------------------------------------------------------		

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))


	
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
	sheet.add_field(name="!setup", value="Create the database for your server.\nUsage: !setup", inline=False)
	sheet.add_field(name="!profile", value="Display a user profile.\nUsage: self/other\nSelf: !profile\nOther: !profile @user", inline=False)
	sheet.add_field(name="!leaderboard", value="Display the current clan wins leaderboard.\nUsage: !leaderboard", inline=False)
	sheet.add_field(name="!soloboard", value="Display the current clan 1v1 score leaderboard.\nUsage: !soloboard", inline=False)
	sheet.add_field(name="!setclan", value="Set a users clan name.\nUsage: !setclan CUM", inline=False)
	sheet.add_field(name="!setSolo", value="Set a users 1v1 elo.\nUsage: !setSolo elo", inline=False)
	sheet.add_field(name="!setWins", value="Set a users rated clan wins.\nUsage: !setWins @user wins", inline=False)
	sheet.add_field(name="!top50", value="Display the current top 50 clans.\nUsage: !top50", inline=False)
	sheet.add_field(name="!top50clan", value="Display the current top 50 clans and update every 30 seconds.\nUsage: !top50clan", inline=False)
	sheet.add_field(name="!setPart", value="Depreciated! Does not display anywhere, message Ryo5678 for questions.\nSet a users participation rated clan wins.\nThese are wins in clan rated where the user was not the top clan player.\nUsage: !setPart @user wins", inline=False)
	sheet.add_field(name="!setFirst", value="Depreciated! Does not display anywhere, message Ryo5678 for questions.\nSet a users firstplace rated clan wins.\nThese are wins in clan rated where the user was the top clan player.\nUsage: !setFirst @user wins", inline=False)
	
	await ctx.send(embed=sheet)
#-------------------------------------------------------------------------------
#------------------------------ HELP Override -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def help(ctx):
	sheet2 = discord.Embed(title="Help", description="**Commands for users**".format(ctx), color=0x0000FF)
	sheet2.add_field(name="!profile", value="Display a user profile.\nUsage: self/other\nSelf: !profile\nOther: !profile @user", inline=False)
	sheet2.add_field(name="!setclan", value="Set a users clan name.\nUsage: !setclan CUM", inline=False)
	sheet2.add_field(name="!setSolo", value="Set a users 1v1 elo.\nUsage: !setSolo elo", inline=False)
	sheet2.add_field(name="Win Tracking", value="Find your server's picture channel. Post a screenshot of your latest clan win.\n The win must include [clan name] wins in the bottom corner. \n Image quality may affect results. Crop out everything but territorial if possible.", inline=False)
	sheet2.add_field(name="!top50", value="Display the current top 50 clans.\nUsage: !top50", inline=False)
	await ctx.send(embed=sheet2)
#-------------------------------------------------------------------------------
#------------------------------ SETUP Command -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def setup(ctx):
	user  = ctx.message.author.id
	guild = ctx.message.guild.id
	
	#api_url = 'https://territorial-io-tracker-default-rtdb.firebaseio.com'
	
	ref = db.reference('/{0}/users/{1}'.format(guild,user))
	ref.set({
	'firstplace': 0,
	'leaderboard': 0,
	'participation': 0,
	'soloboard': 0,
	'clan': "none"
	})

	#todo = {
	#guild: {
    #	"users": {
     #   ".indexOn": ["leaderboard","soloboard"],
      #  "$uid": {
       #   "leaderboard": {
        #    ".indexOn": ".value"
         # },
          #"soloboard": {
           # ".indexOn": ".value"
          #}
        #}
      #}
    #}
	#}

	#response = requests.put(api_url, json=todo)
	#print(todo)
	#print(response.status_code)
#-------------------------------------------------------------------------------
#------------------------------ START Image Tracking ---------------------------
#-------------------------------------------------------------------------------	
@commands.has_permissions(administrator=True)
@bot.command(pass_context = True)
async def imageTrack(ctx):
	check = True
	if ctx.message.guild.id == 900982253679702036:
		channel = bot.get_channel(900982254287855688)
		win = "[ELITE] won"
		win2 = "[ELITE]  won"
		win3 = "[ELITE]won"
		win4 = "[ ELITE] won"
		win5 = "[ ELITE ] won"
		win6 = "[ELITE ] won"
		win7 = "ELITE] won"
	else:
		channel = bot.get_channel(909607895665102898)
		win = "[CUM] won"
		win2 = "[CUM]  won"
		win3 = "[CUM]won"
		win4 = "[ CUM] won"
		win5 = "[ CUM ] won"
		win6 = "[CUM ] won"
		win7 = "CUM] won"
	message2 = None
	#print("Before loop")
	i = 0
	await ctx.message.delete()
	await ctx.send("Image Tracking Rebooted! You may now post again.")
	while check:
		await asyncio.sleep(5)
		try:
			message = await channel.fetch_message(
				channel.last_message_id)
			#print("Before first if")
			user = None
			guild = None
			if message2 == message:
				i += 1
			else:
				message2 = message
				if len(message.attachments) > 0:
					if len(message.attachments) > 1:
						await ctx.send("Only your first image was grabbed! Please submit any additional images after 30 seconds")
					attachment = message.attachments[0]
					print(attachment.url)
					if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".gif") or attachment.filename.endswith(".PNG"):
						image = attachment.url
						await attachment.save(attachment.filename)
						#print(attachment.filename)
						image_path = r"{0}".format(attachment.filename)
						#print(image_path)
						img = Image.open(image_path)
						pytesseract.tesseract_cmd = path_to_tesseract
						text = pytesseract.image_to_string(img)
						#print(text[:-1])
						if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text:
							user = message.author.id
							guild = message.guild.id
							#print(guild)
							#print(user)
							
							fRef = db.reference('/{0}/users/{1}'.format(guild,user))
							if fRef.get() == None:
								ref = db.reference('/{0}/users/{1}'.format(guild,user))
								ref.set({
								'firstplace': 0,
								'leaderboard': 1,
								'participation': 0,
								'soloboard': 0
								})
								await ctx.send("Profile created. Please type !profile again to display it.")
							else:
								ref2 = db.reference('/{0}/users/{1}/leaderboard'.format(guild,user))
								wins = ref2.get()
								wins = wins + 1
								ref3 = db.reference('/{0}/users/{1}'.format(guild,user))
								ref3.update({
								'leaderboard': wins
								})
						os.remove(attachment.filename)
					else:
						print("Invalid image type")
						print(attachment.filename)
				#i+=240
				#print("Loop restarting")
		except:
			await ctx.send("Uh oh, something went wrong! Your image was not received, not read, the quality is low or clan won statement is covered. This bot does not track 1v1 score either. Please use !setsolo #")
			print("imageTrack loops = {0}".format(i))
		#await ctx.send("!imageTrack")	
	check = True

#-------------------------------------------------------------------------------
#------------------------------ SET Solo Elo Score -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def setSolo(ctx,elo):
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	num = float(elo)
	#print(guild)
	#print(user)
	
	await ctx.send("This command will be replaced by image tracking in the future!")
	fRef = db.reference('/{0}/users/{1}'.format(guild,user))
	if fRef.get() == None:
		fRef.set({
		'firstplace': 0,
		'leaderboard': 0,
		'participation': 0,
		'soloboard': num,
		'clan': "none"
		})
		await ctx.send("Profile created. Please type !profile again to display it.")
	else:
		fRef.update({
		'soloboard': num
		})
		# Get profile information
		clanRef = db.reference('/{0}/users/{1}/leaderboard'.format(guild,user))
		cscore = clanRef.get()

		soloRef = db.reference('/{0}/users/{1}/soloboard'.format(guild,user))
		sscore = soloRef.get()
		
		cRef = db.reference('/{0}/users/{1}/clan'.format(guild,user))
		clan = cRef.get()

		#print("Above sheet declaration")
		guild = bot.get_guild(guild)
		sheet = discord.Embed(title="Profile", description="**{0}'s stats**".format(((await guild.fetch_member(user)).nick)), color=0x0000FF)
		sheet.add_field(name="Clan", value=clan, inline=False)
		sheet.add_field(name="1v1 elo", value=sscore, inline=True)
		sheet.add_field(name="Total Clan Wins", value=cscore, inline=False)
		await ctx.send(embed=sheet)
@setSolo.error
async def setSolo_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please include the 1v1 score to set.\nExample: !setSolo 42.0")	

#-------------------------------------------------------------------------------
#--------------------------------- SET Clan ------------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def setclan(ctx,name):
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	clan = name.upper()
	
	# check if user exists and update clan or create user
	fRef = db.reference('/{0}/users/{1}'.format(guild,user))
	if fRef.get() == None:
		fRef.set({
		'firstplace': 0,
		'leaderboard': 0,
		'participation': 0,
		'soloboard': 0,
		'clan': clan
		})
		await ctx.send("Profile created. Please type !profile again to display it.")
	else:
		fRef.update({
		'clan': clan
		})
	    # Get profile information
		clanRef = db.reference('/{0}/users/{1}/leaderboard'.format(guild,user))
		cscore = clanRef.get()

		soloRef = db.reference('/{0}/users/{1}/soloboard'.format(guild,user))
		sscore = soloRef.get()
		
		# Profil Embed
		guild = bot.get_guild(guild)
		sheet = discord.Embed(title="Profile", description="**{0}'s stats**".format(((await guild.fetch_member(user)).nick)), color=0x0000FF)
		sheet.add_field(name="Clan", value=clan, inline=False)
		sheet.add_field(name="1v1 elo", value=sscore, inline=False)
		sheet.add_field(name="Total Clan Wins", value=cscore, inline=False)
		await ctx.send(embed=sheet)
@setclan.error
async def setclan_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please the name of the clan. Example: !setclan CUM")	
#-------------------------------------------------------------------------------
#------------------------------ SET First Place Wins ---------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def setFirst(ctx, name: discord.User ,wins):
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
		pref = db.reference('/{0}/users/{1}/firstplace'.format(guild,user))
		pnum = pref.get()
		#print("Inside else")
		ref = db.reference('/{0}/users/{1}'.format(guild,user))
		ref.update({
		'firstplace': num
		})
		ref2 = db.reference('/{0}/users/{1}/leaderboard'.format(guild,user))
		wins = ref2.get()
		ref3 = db.reference('/{0}/users/{1}'.format(guild,user))
		ref3.update({
		'leaderboard': wins+num-pnum
		})
@setFirst.error
async def setFirst_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please enter the name of the user you wish to update.\nAfter the name please include the number of wins to set.\nExample: !setFirst @Ryo5678 100")	
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
#------------------------------ SET Participation Wins -------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def setPart(ctx, name: discord.User ,wins):
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
		pref = db.reference('/{0}/users/{1}/participation'.format(guild,user))
		pnum = pref.get()
		#print("Inside else")
		ref = db.reference('/{0}/users/{1}'.format(guild,user))
		ref.update({
		'participation': num
		})
		ref2 = db.reference('/{0}/users/{1}/leaderboard'.format(guild,user))
		wins = ref2.get()
		ref3 = db.reference('/{0}/users/{1}'.format(guild,user))
		ref3.update({
		'leaderboard': wins+num-pnum
		})
@setPart.error
async def setPart_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please enter the name of the user you wish to update.\nAfter the name please include the number of wins to set.\nExample: !setPart @Ryo5678 16")	

#-------------------------------------------------------------------------------
#------------------------------ PROFILE COMMAND ---------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
async def profile(ctx, name: discord.Member):
	user = name.id
	#print(name.id)
	#print(user.name)
	guild = ctx.message.guild.id
	# check if user exists
	ref3 = db.reference('/{0}/users/{1}'.format(guild,user))
	if ref3.get() == None:
		user  = name.id
		guild = ctx.message.guild.id
		ref = db.reference('/{0}/users/{1}'.format(guild,user))
		ref.set({
		'firstplace': 0,
		'leaderboard': 0,
		'participation': 0,
		'soloboard': 0,
		'clan': "none"
		})
		await ctx.send("Profile created. Please type !profile again to display it.")
	else:
		# Get profile information
		clanRef = db.reference('/{0}/users/{1}/leaderboard'.format(guild,user))
		cscore = clanRef.get()

		soloRef = db.reference('/{0}/users/{1}/soloboard'.format(guild,user))
		sscore = soloRef.get()
		
		cRef = db.reference('/{0}/users/{1}/clan'.format(guild,user))
		clan = cRef.get()

		# Profile Embed
		guild = bot.get_guild(guild)
		sheet = discord.Embed(title="Profile", description="**{0}'s stats**".format(((await guild.fetch_member(user)).nick)), color=0x0000FF)
		sheet.add_field(name="Clan", value=clan, inline=False)
		sheet.add_field(name="1v1 elo", value=sscore, inline=False)
		sheet.add_field(name="Total Clan Wins", value=cscore, inline=False)
		await ctx.send(embed=sheet)
		#print("After sheet send")
@profile.error
async def profile_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		user = ctx.message.author.id
		guild = ctx.message.guild.id
		# check if user exists
		ref3 = db.reference('/{0}/users/{1}'.format(guild,user))
		if ref3.get() == None:
			user  = ctx.message.author.id
			guild = ctx.message.guild.id
			ref = db.reference('/{0}/users/{1}'.format(guild,user))
			ref.set({
			'firstplace': 0,
			'leaderboard': 0,
			'participation': 0,
			'soloboard': 0,
			'clan': "none"
			})
			await ctx.send("Profile created. Please type !profile again to display it.")
		else:
			# Get profile information
			clanRef = db.reference('/{0}/users/{1}/leaderboard'.format(guild,user))
			cscore = clanRef.get()
			
			soloRef = db.reference('/{0}/users/{1}/soloboard'.format(guild,user))
			sscore = soloRef.get()
			
			cRef = db.reference('/{0}/users/{1}/clan'.format(guild,user))
			clan = cRef.get()

			# Profile Embed
			guild = bot.get_guild(guild)
			sheet = discord.Embed(title="Profile", description="**{0}'s stats**".format((await guild.fetch_member(user)).nick), color=0x0000FF)
			sheet.add_field(name="Clan", value=clan, inline=False)
			sheet.add_field(name="1v1 elo", value=sscore, inline=False)
			sheet.add_field(name="Total Clan Wins", value=cscore, inline=False)
			await ctx.send(embed=sheet)
			
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
	board.add_field(name="🥇**1st Place**🥇", value="test", inline=False)
	board.add_field(name="🥈**2nd Place**🥈", value="test", inline=False)
	board.add_field(name="🥉**3rd Place**🥉", value="test", inline=False)
	board.add_field(name="🏅**4th and 5th**🏅", value="test", inline=False)
	board.add_field(name="🎖️**6th to 10th🎖️**", value="test", inline=False)
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
		board.set_field_at(0,name="🥇**1st Place**🥇", value="{0} - {1} wins".format(bL[9][0],bL[9][1]['leaderboard']), inline=False)
		board.set_field_at(1,name="🥈**2nd Place**🥈", value="{0} - {1} wins".format(bL[8][0],bL[8][1]['leaderboard']), inline=False)
		board.set_field_at(2,name="🥉**3rd Place**🥉", value="{0} - {1} wins".format(bL[7][0],bL[7][1]['leaderboard']), inline=False)
		board.set_field_at(3,name="🏅**4th and 5th**🏅", value="{0} - {1} wins \n{2} - {3} wins \n".format(bL[6][0],bL[6][1]['leaderboard'],bL[5][0],bL[5][1]['leaderboard']), inline=False)
		board.set_field_at(4,name="🎖️**6th to 10th🎖️**", value="{0} - {1} wins \n{2} - {3} wins \n{4} - {5} wins \n{6} - {7} wins \n{8} - {9} wins \n".format(bL[4][0],bL[4][1]['leaderboard'],bL[3][0],bL[3][1]['leaderboard'],bL[2][0],bL[2][1]['leaderboard'],bL[1][0],bL[1][1]['leaderboard'],bL[0][0],bL[0][1]['leaderboard']), inline=False)
		timestamp = datetime.now()
		board.set_field_at(5,name="\u200b",value="Last refreshed at " + timestamp.strftime(r"%I:%M %p"),inline=False)
		await msg.edit(embed = board)
		await asyncio.sleep(900)
	check = True
#-------------------------------------------------------------------------------
#------------------------- 1v1 LEADERBOARD COMMAND -----------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def soloboard(ctx):
	check = True
	await ctx.message.delete()
	guild = ctx.message.guild.id
	guild = bot.get_guild(guild)
	sboard = discord.Embed(title="{0} Leaderboard".format(guild.name), description="**Current Top 10**", color=0x33FF61)
	sboard.add_field(name="🥇**1st Place**🥇", value="test", inline=False)
	sboard.add_field(name="🥈**2nd Place**🥈", value="test", inline=False)
	sboard.add_field(name="🥉**3rd Place**🥉", value="test", inline=False)
	sboard.add_field(name="🏅**4th and 5th**🏅", value="test", inline=False)
	sboard.add_field(name="🎖️**6th to 10th🎖️**", value="test", inline=False)
	timestamp = datetime.now()
	sboard.add_field(name="\u200b",value="Last refreshed at " + timestamp.strftime(r"%I:%M %p") + " EST",inline=False)
	msg = await ctx.send(embed=sboard)
	while check:
		sboardRef = db.reference('/{0}/users'.format(guild.id))
		sboardList = sboardRef.order_by_child('soloboard').limit_to_last(10).get()
		scbL = list(sboardList.items())
		scbL.reverse()
		max = 10
		y = len(scbL)
		if y <= 10:
			max = max - y 
		for x in range(max):
			scbL.append(["None",{'soloboard':0}])
		scbL.reverse()
		sbL = [[0 for x in range(2)] for y in range(10)]
		for x in range(10):
			sbL[x][1] = scbL[x][1]
			if scbL[x][0] is not "None":
				temp = scbL[x][0]
				try:
					sbL[x][0] = ((await guild.fetch_member(temp)).nick)
				except:
					ref = db.reference('/{0}/users/{1}/soloboard'.format(guild.id,temp))
					ref.delete()
					check = False
				if sbL[x][0] is None:
					sbL[x][0] = (await guild.fetch_member(temp)).name
		sboard.set_field_at(0,name="🥇**1st Place**🥇", value="{0} - {1} elo".format(sbL[9][0],sbL[9][1]['soloboard']), inline=False)
		sboard.set_field_at(1,name="🥈**2nd Place**🥈", value="{0} - {1} elo".format(sbL[8][0],sbL[8][1]['soloboard']), inline=False)
		sboard.set_field_at(2,name="🥉**3rd Place**🥉", value="{0} - {1} elo".format(sbL[7][0],sbL[7][1]['soloboard']), inline=False)
		sboard.set_field_at(3,name="🏅**4th and 5th**🏅", value="{0} - {1} elo \n{2} - {3} elo \n".format(sbL[6][0],sbL[6][1]['soloboard'],sbL[5][0],sbL[5][1]['soloboard']), inline=False)
		sboard.set_field_at(4,name="🎖️**6th to 10th🎖️**", value="{0} - {1} elo \n{2} - {3} elo \n{4} - {5} elo \n{6} - {7} elo \n{8} - {9} elo \n".format(sbL[4][0],sbL[4][1]['soloboard'],sbL[3][0],sbL[3][1]['soloboard'],sbL[2][0],sbL[2][1]['soloboard'],sbL[1][0],sbL[1][1]['soloboard'],sbL[0][0],sbL[0][1]['soloboard']), inline=False)
		timestamp = datetime.now()
		sboard.set_field_at(5,name="\u200b",value="Last refreshed at " + timestamp.strftime(r"%I:%M %p"),inline=False)
		await msg.edit(embed = sboard)
		await asyncio.sleep(900)
	check = True
#-------------------------------------------------------------------------------
#------------------------------ Clan Ranking Tracking ---------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.is_owner()
async def clanRanker(ctx):

#### Add check for if length of text array is 5, use 3 and 4, due to white/black arena maps
	channel = bot.get_channel(917537295261913159)
	message2 = None
	await ctx.message.delete()
	await ctx.send("Clan ranks are now being tracked!")
	i = 0
	while True:
		i = i + 1
		if (i % 100) == 0:
			print("Loop at {0}".format(i))
		message = await channel.fetch_message(
				channel.last_message_id)
		if message2 == message:
			await asyncio.sleep(3)
		else:
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
			ref = db.reference('/780723109128962070/clans/{0}'.format(clan))
			ref.set({
		    'score': float(points)
			})
			await asyncio.sleep(3)
	print("While loop ended in clanRanker")
	
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
		await asyncio.sleep(30)
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
#-------------------------------------------------------------------------------
@bot.event
async def on_command_error(ctx,error):
	if isinstance(error, CommandNotFound):
		return
	if isinstance(error, MissingPermissions):
		await ctx.send("You do not have permission to use this command.\n Try !help for commands you can use")
		return

#-------------------------------------------------------------------------------
#------------------------------ SHUTDOWN COMMAND -------------------------------
#-------------------------------------------------------------------------------
				
# Shutdown the bot!
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
	await ctx.message.delete()
	await ctx.send('Territorial IO Tracker is offline. Sorry for the inconvenience.')
	await bot.change_presence(status=discord.Status.invisible)
	await bot.close() 

#-------------------------------------------------------------------------------
#------------------------------ LOOP CODE --------------------------------------
#-------------------------------------------------------------------------------

bot.run('bot key goes here', bot=True, reconnect=True)