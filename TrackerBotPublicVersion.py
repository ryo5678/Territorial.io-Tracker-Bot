import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import credentials
from firebase_admin import db
from discord import Embed, Emoji
from discord.ext import tasks
from discord.ext.tasks import loop
from discord.utils import get
from datetime import datetime, timedelta
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
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

intents = discord.Intents.default()
intents.messages = True
intents.members = True

creds = service_account.Credentials.from_service_account_file(
    'google docs credentials .json file')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'Google spreadsheet ID'
RANGE_NAME = 'A2'

bot = commands.Bot(command_prefix="t!", case_insensitive=True, activity=discord.Game(name="t!help for commands"), status=discord.Status.online,help_command=None,intents=intents)


# List of removeWins admins
winAdmins = ((138752093308583936,"ELITE"),(524835935276498946,"ELITE"))
	
database_url = "URL to database"

cred = firebase_admin.credentials.Certificate('Firebase credentials .json file')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

#textfile = open('en-strings.txt', 'r')
#english = textfile.read().splitlines()
#textfile.close()

# Strings are private to prevent copy cats
textfile = open('en-strings.txt', 'r')
language = textfile.read().splitlines()
textfile.close()

textfile = open('fr-strings.txt', 'r')
french = textfile.read().splitlines()
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
			clanRanker.start()
		except Exception as e:
			print(".start() error")
			if str(e) == "object Nonetype can't be used in 'await' expression":
				print("found")
			print(e)
		ref = db.reference('/imageChannels')
		info = ref.get()
		channels = list(info.items())
		
		# Deleting this part at some point, it half works
		for i in range(len(channels)):
				#print(int(channels[i][1]['channelID']))
			try:
				channel = bot.get_channel(int(channels[i][1]['channelID']))
				# Check if channel still exists, if not, delete from database
				if channel == None:
					ref = db.reference('/imageChannels/{0}/'.format(int(channels[i][0])))
					ref.delete()
				else:
					new_task = tasks.loop(seconds=7.0,count=None,reconnect=True)(imagelooper)
					new_task.start(channel)
					testLine = "test"
			#await channel.send("Image Tracking Rebooted! You may now post again.")
			except Exception as e:
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
@joinEvent.error
async def joinEvent_error(ctx, error):
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send(language[3])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#------------------------------ GET Admin Commands -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def ahelp(ctx):
	sheet = discord.Embed(title=language[5], description=language[6], color=0x0000FF)
	sheet.add_field(name=language[7], value=language[8] + '\n' + language[9], inline=False)
	sheet.add_field(name=language[10], value=language[11] + '\n' + language[12], inline=False)
	sheet.add_field(name=language[13], value=language[14] + '\n' + language[15], inline=False)
	sheet.add_field(name=language[16], value=language[17] + '\n' + language[18], inline=False)
	sheet.add_field(name=language[19], value=language[20] + '\n' + language[21], inline=False)
	sheet.add_field(name=language[22], value=language[23] + '\n' + language[24], inline=False)
	sheet.add_field(name=language[25], value=language[26] + '\n' + language[27], inline=False)
	sheet.add_field(name=language[28], value=language[29] + '\n' + language[30] + '\n' + language[31], inline=False)
	sheet.add_field(name=language[32], value=language[33] + '\n' + language[34], inline=False)
	sheet.add_field(name=language[35], value=language[36] + '\n' + language[37], inline=False)
	sheet.add_field(name=language[38], value=language[39] + '\n' + language[40] + '\n' + language[41], inline=False)
	sheet.add_field(name=language[42], value=language[43] + '\n' + language[44] + '\n' + language[45], inline=False)
	await ctx.send(embed=sheet)
@ahelp.error
async def ahelp_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send(language[46])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#------------------------------ HELP Override -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def help(ctx):
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
@help.error
async def help_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send(language[46])
#-------------------------------------------------------------------------------
#------------------------------ SETUP Command ----------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 1800, commands.BucketType.user)
async def setup(ctx):
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
@setup.error
async def setup_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send(language[46])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
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
			#try:
				# Get user ID
			user = message.author.id
				# Set reference
				#ref5 = db.reference('/users/{0}/lang'.format(user))
				#if ref5.get() == "french":
				#	language = french
				#	s = "D\u00e8"
				#	a = "\u00e8"
				#if ref5.get() == "english":
				#	language = english
				#	s = ""
				#	a = ""
				#if ref5.get() == None:
				#	language = english
				#	s = ""
				#	a = ""
			#except Exception as e:
				#print(e)
			opt = db.reference('/users/{0}/opt'.format(user))
			if (opt.get() == True):
				await channel.send(language[106])
				return
			user = None
			guild = None
			if message2 == message.id:
				i += 1
			else:
				if len(message.attachments) > 0:
					if len(message.attachments) > 1:
						await channel.send(language[107])
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
						#print(text[:-1])
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
							'name': username,
							'onevsone': 0
							})
							await channel.send(language[108])
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
								if text[:30] == pRef.get():
									await channel.send(language[109].format(user))
									print("{0} tried to cheat".format(user))
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
							#print("BEfore win check")
							# Check for clan win statement
							if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text or win8 in text or win9 in text or win10 in text:
								# Check if clan is not set
								if clan == "none":
									await channel.send(language[108])
								else:
									#print("BEfore win update")
									ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
									wins = ref2.get()
									wins = wins['wins']
									wins = wins + 1
									ref2.update({
										'wins': wins,
										'previous': text[:30]
									})
									await channel.send(language[110].format(user,wins))
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
								if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text or win8 in text or win9 in text or win10 in text:
								# Check if clan is not set
									if clan == "none":
										mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
										mRef.update({
										'lastMessage': str(message.id)
										})
										await channel.send(language[108])
									else:
										#print("BEfore win update")
										ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
										wins = ref2.get()
										wins = wins['wins']
										wins = wins + 1
										ref2.update({
											'wins': wins,
											'previous': text[:30]
										})
										mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
										mRef.update({
										'lastMessage': str(message.id)
										})
										await channel.send(language[110].format(user,wins))
						os.remove(attachment.filename)
						mRef = db.reference('/imageChannels/{0}'.format(channel.guild.id))
						mRef.update({
						'lastMessage': str(message.id)
						})
					else:
						z = "do nothing"
						#print("Invalid image type")
						#print(attachment.filename)
		except Exception as e:
			#language = english
			if isinstance(e, discord.ext.commands.MessageNotFound):
				await channel.send(language[111])
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
@imageTrack.error
async def imageTrack_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send(language[46])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#------------------------------ Set Announcement Channel -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def updates(ctx):
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
@updates.error
async def updates_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send(language[46])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#------------------------------ SET Solo Elo Score -----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 60, commands.BucketType.user)
async def setSolo(ctx,elo):
	user = ctx.message.author.id
	guild = ctx.message.guild.id
	num = float(elo)
	if num >= 500 or num < 0:
		await ctx.send(language[117])
	else:
		guild = bot.get_guild(guild)
		username = ((await guild.fetch_member(user)).nick)
		if username == None:
			username = ((await guild.fetch_member(user)).name)
			
		await ctx.send(language[118])
		
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
		await ctx.send(language[119])	
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#--------------------------------- SET Clan ------------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 60, commands.BucketType.user)
async def setclan(ctx,name):
	user = ctx.message.author.id
	guild = ctx.message.guild.id
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
		await ctx.send(language[120])	
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))

#-------------------------------------------------------------------------------
#------------------------------ Remove Clan Wins ----------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
async def removeWins(ctx,user,wins):
	# Assign/Retrieve command caller ID
	caller = ctx.author.id
	# Check if caller is approved user
	for x in range(len(winAdmins)):
		if caller == winAdmins[x][0]:
			clan = winAdmins[x][1]
	if clan == None:
		await ctx.send(language[121])
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
	await ctx.send(language[125].format(total))
@removeWins.error
async def removeWins_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send(language[126] + '\n' + language[127] + '\n' + language[128])
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])

#-------------------------------------------------------------------------------
#------------------------------ PROFILE COMMAND --------------------------------
#-------------------------------------------------------------------------------

def profileDisplay(ctx,user,username):
	# Get user ID
	user = ctx.message.author.id
	# Set reference
	#ref = db.reference('/users/{0}/lang'.format(user))
	#if ref.get() == "french":
	#	language = french
	#	s = "D\u00e8"
	#	a = "\u00e8"
	#if ref.get() == "english":
	#	language = english
	#	s = ""
	#	a = ""
	#if ref.get() == None:
	#	language = english
	#	s = ""
	#	a = ""
	ref = db.reference('/users/{0}'.format(user))
	info = ref.get()
	
	cw = 0
	
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
		wins = []
		try:
			# Loop through all user's clans
			while x >= 0:
				clanList.append(clans[x][0])
				temp = clans[x][1]
				try:
					temp = list(temp.items())
					if len(temp) < 2:
						ref = db.reference('/users/{0}/clans/{1}'.format(user,clans[x][0]))
						ref.update({
							'previous': "test"
							})
						wins.append(temp[0][1])
					else:
						wins.append(temp[1][1])
				
				except:
						ref = db.reference('/users/{0}/clans/{1}'.format(user,temp))
						ref.update({
							'previous': "test",
							'wins': 0
							})
						wins.append(0)
				x = x - 1	
		except Exception as e:
			print(e)
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
	
	guild = ctx.message.guild.id
	# Profile Embed
	sheet = discord.Embed(title=language[129], description=language[130].format(username), color=0x0000FF)
	sheet.add_field(name=language[131], value=clan, inline=False)
	sheet.add_field(name=language[132], value=ovo, inline=False)
	sheet.add_field(name=language[133], value=br, inline=False)
	# Loop through all user clans
	for x in range(len(wins)):
		sheet.add_field(name=language[134].format(clanList[x]), value=wins[x], inline=False)
	return sheet

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
		await ctx.send(language[0])	
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))

@bot.command(pass_context = True)
@commands.cooldown(1, 7200, commands.BucketType.user)
async def clanboard(ctx,clan):
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
			ladder2 = discord.Embed(title=language[135].format(clan), description=language[137], color=0x33DDFF)
			ladder3 = discord.Embed(title=language[135].format(clan), description=language[138], color=0x33DDFF)
			ladder4 = discord.Embed(title=language[135].format(clan), description=language[139], color=0x33DDFF)
			# One Ladder
			if x <= 25:
				for i in range(x):
					name = await bot.fetch_user(users2[i][0])
					ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
				msg = await ctx.send(embed=ladder)
			# Two Ladders
			elif x <= 50:
				await ctx.send(language[142])
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
				await ctx.send(language[143])
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
				await ctx.send(language[144])
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
				await ctx.send(language[145])
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
			await ctx.send(language[146].format('<@138752093308583936>'))
			print("Clanboard command call failed.")
			print(e)
	except:
		await ctx.send(language[147])
@clanboard.error
async def clanboard_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send(language[46])
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send(language[120])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
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
	guild = ctx.message.guild.id
	sololoop.start(ctx,clan)
@soloboard.error
async def soloboard_error(ctx, error):
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send(language[3])
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send(language[120])
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])

@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
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
@oneboard.error
async def oneboard_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		await ctx.send(language[46])
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
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
					points = points.split("->")
					points = points[1]
					points = re.sub(r'[^\d.]+', '', points)
					points.strip("[]")
				else:
					map = textList[0]
					players = textList[1]
					clan = textList[2]
					points = textList[3]
					points = points.split("->")
					points = points[1]
					points = re.sub(r'[^\d.]+', '', points)
					points.strip("[]")
				# Temp fix, might not work
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
	ladder2 = discord.Embed(title=language[152], description=language[137], color=0x33DDFF)
	# First Ladder
	for i in range(25):
		ladder.add_field(name=language[149].format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
	msg = await ctx.send(embed=ladder)
	# Second Ladder
	for i in range(25):
		ladder2.add_field(name=language[149].format(i+26) + clanList2[i+25][0], value=clanList2[i+25][1]['score'], inline=True)
	msg2 = await ctx.send(embed=ladder2)
@top50.error
async def top50_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		try:
			await ctx.send(language[46])
		except:
			print("Missing send permissions")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#---------------------- Public Top 25 Clans (Non updating) ---------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def top25(ctx):	
	ref = db.reference('/{0}/clans'.format(780723109128962070))
	clanList = ref.order_by_child('score').limit_to_last(25).get()
	clanList2 = list(clanList.items())
	clanList2.reverse()
	ladder = discord.Embed(title=language[152], description=language[136], color=0x33DDFF)
	# First Ladder
	for i in range(25):
		ladder.add_field(name=language[149].format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
	msg = await ctx.send(embed=ladder)
@top25.error
async def top25_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		try:
			await ctx.send(language[46])
		except:
			print("Missing send permissions")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#-------------------------------  Top Override  --------------------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def top(ctx):
	await ctx.send(language[154])
@top.error
async def top_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		try:
			await ctx.send(language[46])
		except:
			print("Missing send permissions")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#---------------------- Public Top 100 Clans (Non updating) ---------------------
#-------------------------------------------------------------------------------	
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def top100(ctx):
	ref = db.reference('/{0}/clans'.format(780723109128962070))
	clanList = ref.order_by_child('score').limit_to_last(100).get()
	clanList2 = list(clanList.items())
	clanList2.reverse()
	ladder = discord.Embed(title=language[152], description=language[136], color=0x33DDFF)
	ladder2 = discord.Embed(title=language[152], description=language[137], color=0x33DDFF)
	ladder3 = discord.Embed(title=language[152], description=language[138], color=0x33DDFF)
	ladder4 = discord.Embed(title=language[152], description=language[139], color=0x33DDFF)
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
@top100.error
async def top100_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		await ctx.send(language[0])
	if isinstance(error, discord.ext.commands.MissingPermissions):
		try:
			await ctx.send(language[46])
		except:
			print("Missing send permissions")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#--------------------- LC Events Leaderboard ---- NOT IN USE -------------------
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
@commands.cooldown(1, 60, commands.BucketType.user)
async def clan(ctx,clan):
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
			await ctx.send(language[156].format(clan))
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
				plt.title(language[159])
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
				await ctx.send(language[161])
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
			await ctx.send(language[162].format(clan,score,x,y))
	except Exception as e:
		print(e)
		# Catch missing message permission
		try:
			await ctx.send(language[163])
		except:
			try:
				print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
			except Exception as e:
				print(e)
@clan.error
async def clan_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		try:
			await ctx.send(language[0])
		except:
			print("bot is missing message permissions")
			try:
				print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
			except:
				print("Guild indentify failed")
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		# Catch missing message permission
		try:
			await ctx.send(language[155])
		except:
			print("bot is missing message permissions")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		try:
			await ctx.send(language[4].format(time))
		except:
			print("bot is missing message permissions")
			try:
				print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
			except:
				print("Guild indentify failed")
#-------------------------------------------------------------------------------
#------------------------------ Change bot status ------------------------------
#-------------------------------------------------------------------------------	
@commands.is_owner()
@bot.command(pass_context = True)
async def status(ctx,*,text):
	await bot.change_presence(activity=discord.Game(name=text))
	await ctx.message.delete()
@status.error
async def status_error(ctx,error):
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send(language[3])
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
		await ctx.send(language[3])
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
		# Try to send shutdown notice, catch missing send message permission
		try:
			await channel.send(warning)
		except Exception as e:
			if isinstance(error, discord.ext.commands.BotMissingPermissions):
				print("A channel {0} has blocked updates in {1}").format(channel.id,channel.guild)
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
		await ctx.send(language[3])	
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		print("A channel has blocked updates")
	print(error)

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
@historyGrab.error
async def historyGrab_error(ctx, error):
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send(language[3])	
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		print("A channel has blocked history grab")
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

@say.error
async def say_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Please enter the time (seconds) and reason. t!shutdown 10 Reboot")
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send(language[3])
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		print("A channel has blocked updates")
	print(error)
#-------------------------------------------------------------------------------
#------------------------------ add COMMAND -------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def add(ctx):
	await ctx.send("Link to add: https://discord.com/api/oauth2/authorize?client_id=844800624028549120&permissions=388160&scope=bot")
	await ctx.send("Video on bot: https://youtu.be/-wD1-BPU7Gk")
@add.error
async def add_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		try:
			await ctx.send(language[0])
		except:
			print("bot is missing message permissions")
			try:
				print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
			except:
				print("Guild indentify failed")
	if isinstance(error, discord.ext.commands.MissingPermissions):
		try:
			await ctx.send(language[46])
		except:
			print("Missing send permissions")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
		
#-------------------------------------------------------------------------------
#------------------------------ LCEVENTSTATS COMMAND -------------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def lc(ctx):
	# Get pdf from database
	
	# Attatch pdf to discord message
	
	# Post to channel
	await ctx.send("LC Event Stats",file=discord.File("StatisticsLCEvent.pdf"))
@lc.error
async def lc_error(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		try:
			await ctx.send(language[0])
		except:
			print("bot is missing message permissions")
			try:
				print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
			except:
				print("Guild indentify failed")
	if isinstance(error, discord.ext.commands.MissingPermissions):
		try:
			await ctx.send(language[46])
		except:
			print("Missing send permissions")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send(language[4].format(time))
#-------------------------------------------------------------------------------
#------------------------------ Compare Clans Command --------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def compare(ctx,*,clans):
	#if (ctx.message.guild.id == 780723109128962070):
	#	await ctx.send("This server does not support this command. Please ask the administrator(s) to assign embed permissions")
	#	return
	#else:
	plt.clf()
	await ctx.send("This command processes large amounts of data, please be patient.")
	clanList = clans.split()
	if len(clanList) > 5:
		await ctx.send("Maximum clans is 5, please try again.")
		await compare.reset_cooldown(ctx)
		return
	# Set times to search back 1 week
	timeDif = timedelta(10)
	newTime = ctx.message.created_at
	oldTime = newTime - timeDif
	newTime = newTime + timedelta(1)
	# Make plot for score vs time
	plt.xlabel("Time")
	plt.ylabel("Score")
	plt.title("Score over last 10 days.")
	ax = plt.gca()
	myFmt = mdates.DateFormatter('%m/%d')
	ax.xaxis.set_major_formatter(myFmt)
	ax.xaxis.set_major_locator(ticker.LinearLocator(9))
	ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
	# Loop through each clan name given
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
				await ctx.send("The clan {0} does not exist or is spelled/typed incorrectly.".format(clan))
				await compare.reset_cooldown(ctx)
				return
			else:
				# Get all games from one week ago to present
				ref = db.reference('gameData')
				snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot = list(snapshot.items())
				games = list()
				for i in range(len(snapshot)):
					if(snapshot[i][1]['Clan'] == clan):
						games.append(snapshot[i])
				
				times = list()
				scores = list()
				# Plot lines
				for i in range(len(games)):
					temp = games[i][1]['Time'].replace('T',' ')
					try:
						times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
					except:
						times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
					scores.append(games[i][1]['Score'])
				plt.plot(times,scores,label=clan)
		except Exception as e:
			print(e)
			await ctx.send("An error occured. Please try the command again or contact Ryo5678 to fix it")
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
		plot = discord.Embed(title="{0}".format(clans), description="**Score over 10 days**", color=0x03fcc6)
		plot.set_image(
		   url="attachment://plot.png"
		)
		await ctx.send(embed=plot, file=chart)
		plt.clf()
	except Exception as e:
			print(e)
			print("Test")
			await ctx.send("An error occured. Please try the command again or contact Ryo5678 to fix it")
@compare.error
async def compare_error(ctx, error):
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("This command requires a clan, please try t!compare NAME NAME.")
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		error = str(error)
		error = error.split()
		time = error[len(error) - 1]
		await ctx.send("You must wait {0} from last command use.".format(time))
		
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
		ref = db.reference('/userIDs')
		snapshot = ref.get()
		for key in snapshot:
			users.append(key)
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
			ref = db.reference('/userIDs/{0}'.format(users[i]))
			ref.update({
			'scope': False,
			'time': str(datetime.now())
			})
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
	ref = db.reference('/users/{0}/'.format(ctx.author.id))
	ref.delete()
@data.error
async def data(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		x = "do nothing"
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		await ctx.send("You must wait 10 minutes from last command use.")
#-------------------------------------------------------------------------------
#------------------------- OPT IN AND OUT OF DATA STORAGE ----------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 1800, commands.BucketType.user)
async def disable(ctx):
	user = ctx.message.author.id
	opt = db.reference('/users/{0}/opt'.format(user))
	if (opt.get() == True):
		await ctx.send("You already have message content storage disabled. This is used to track your clan wins. To opt in, use the t!enable command")
		return
	ref = db.reference('/users/{0}'.format(ctx.author.id))
	ref.update({
	'opt': True
	})
	await ctx.send("You have opted out of message content storage. This will prevent you from tracking your win count. Use t!enable to re-enable this.")
	
@disable.error
async def disable(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		x = "do nothing"
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		await ctx.send("You must wait 10 minutes from last command use.")
		
@bot.command(pass_context = True)
@commands.cooldown(1, 1800, commands.BucketType.user)
async def enable(ctx):
	user = ctx.message.author.id
	opt = db.reference('/users/{0}/opt'.format(user))
	if (opt.get() == False):
		await ctx.send("You already have message content storage enabled. This is used to track your clan wins. To opt out, use the t!disable command")
		return
	ref = db.reference('/users/{0}/opt'.format(ctx.author.id))
	ref.update({
	'opt': False
	})
	await ctx.send("You have opted into the the storage of message content. This will let you track your win count. Use t!disable to change this.")
@enable.error
async def enable(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		x = "do nothing"
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		await ctx.send("You must wait 10 minutes from last command use.")
#-------------------------------------------------------------------------------
#------------------------------- Donate link command ---------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.cooldown(1, 180, commands.BucketType.user)
async def donate(ctx):
	try:
		await ctx.send("Donate to support the bots existence and growth. https://www.patreon.com/Ryo5678")
	except:
		print(ctx.message.guild.id + ctx.message.guild.name + " guild id and name, no send permissions")
@donate.error
async def donate(ctx, error):
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		x = "do nothing"
	if isinstance(error, discord.ext.commands.CommandOnCooldown):
		await ctx.send("You must wait 10 minutes from last command use.")
		
################################################################################
#---------------------------- DISCONTINUED COMMANDS-----------------------------
#-------------------------------------------------------------------------------
#----------------------- CLAN RATED LEADERBOARD COMMAND ------------------------
#-------------------------------------------------------------------------------
@bot.command(pass_context = True)
@commands.is_owner()
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
@leaderboard.error
async def leaderboard_error(ctx, error):
	if isinstance(error, discord.ext.commands.NotOwner):
		await ctx.send(language[3])	
	if isinstance(error, discord.ext.commands.BotMissingPermissions):
		print(language[0])
#-------------------------------------------------------------------------------
#------------------------------- RUN LINE --------------------------------------
#-------------------------------------------------------------------------------
bot.run('Bot Token Goes Here', bot=True, reconnect=True)
