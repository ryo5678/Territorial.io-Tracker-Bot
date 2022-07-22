import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime
from PIL import Image, ImageOps
from pytesseract import pytesseract
import numpy as np
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# List of removeWins admins
winAdmins = ((138752093308583936,"ELITE"),(524835935276498946,"ELITE"),(746381696139788348,"ISLAM"),(735145539494215760,"ISLAM"),(514953130178248707,"RL"))

class Wins(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#------------------------------ Remove Wins Self Version -----------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def remove(self,ctx,wins,points = None):
		try:
			LangCog = self.bot.get_cog("LangCog")
			# Get/Set Language
			user = ctx.message.author.id
			language = LangCog.languagePicker(user)
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
			print(ctx.message.id)
			print("t!remove fail")
	#-------------------------------------------------------------------------------
	#--------------------------- Remove Any User's Clan Wins -----------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def removeWins(self,ctx,name: discord.Member,wins):
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = name.id
		user2 = ctx.message.author.id
		language = LangCog.languagePicker(user2)
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
	#-------------------------------------------------------------------------------
	#------------------------------ START Image Tracking ---------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def win(self,ctx):
		# Get language cog
		LangCog = self.bot.get_cog("LangCog")
		# Get image channel list
		ref = db.reference('/imageChannels')
		info = ref.get()
		channels = list(info.items())
		channelList = []
		# Check if command called in tracking channel
		for i in range(len(channels)):
			channelList.append(int(channels[i][1]['channelID']))
		if int(ctx.channel.id) not in channelList:
			return await ctx.send("Command used outside of a win tracking channel. Please get an administrator to specify a channel with t!imagetrack")
		# Remove Try/Except eventually, using temporarily to catch bugs
		try:
			# Set message object
			message = ctx.message
			# Get user ID and Guild
			user = message.author.id
			guild = message.guild.id
			guild = self.bot.get_guild(guild)
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
				# Send missing clan warning and end command (Default is English, this does not need to be in string file)
				return await ctx.send("Tracker profile generated. Please set a clan before trying to track clan wins. t!setclan NAME")
			else:
				# Get/Set Language
				language = LangCog.languagePicker(user)
			# Check privacy opt in/out
			opt = db.reference('/users/{0}/opt'.format(user))
			if (opt.get() == True):
				return await ctx.send(language[106])
			# Check if attachment picture is given
			if len(message.attachments) > 0:
				# Set attachments list to handle multiple if needed
				attachments = message.attachments
				# Loop through attachments list
				for i in range(len(attachments)):
					# Grab a single attachment
					attachment = message.attachments[i]
					if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".PNG") or attachment.filename.endswith(".JPG") or attachment.filename.endswith(".JPEG"):
						#image = attachment.url
						# Downlaod image and create object by path
						await attachment.save(attachment.filename)
						image_path = r"{0}".format(attachment.filename)
						# Read image and begin conversion
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
							return await ctx.send(language[108])
						pRef = db.reference('/users/{0}/clans/{1}/previous'.format(user,clan))
						if pRef.get() != None:
							if text[:15] == pRef.get():
								print("{0} tried to cheat".format(user))
								os.remove(attachment.filename)
								return await ctx.send(language[109].format(user))
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
							else:
								points2 = result.group(1)
							# Check if double point game
							if "x" in points2:
								points2 = points2.split("x")
								points2 = points2[0]
								points2 = re.sub('[^0-9]+', '', points2)
								points2 = int(points2)
								points2 = points2 * 2
								# Cheating check
								if(points2 > 1100):
									os.remove(attachment.filename)
									return await ctx.send(language[176].format(user))
							else:
								points2 = re.sub('[^0-9]+', '', points2)
								points2 = int(points2)
								# Cheating check
								if(points2 > 600):
									os.remove(attachment.filename)
									return await ctx.send(language[176].format(user))
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
							except:
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
							await ctx.send(language[110].format(user,wins))
							# Interact with ELITE bot
							if(message.guild.id == 900982253679702036) and (clan.lower() == "elite"):
								try:
									update = await ctx.send("e.tracker <@{0}> {1}".format(user,points2))
									await asyncio.sleep(3)
									await update.delete()
								except Exception as e:
									print(e)
						else:
							# Run 2nd image pass differently if first failed
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
											return await ctx.send(language[176].format(user))
									else:
										points2 = re.sub('[^0-9]+', '', points2)
										points2 = int(points2)
										if(points2 > 600):
											os.remove(attachment.filename)
											return await ctx.send(language[176].format(user))
								except Exception as e:
									print("Points error")
									print(e)
								if win in text or win2 in text or win3 in text or win4 in text or win5 in text or win6 in text or win7 in text or win8 in text or win9 in text or win10 in text:
									ref2 = db.reference('/users/{0}/clans/{1}/wins'.format(user,clan))
									wins = ref2.get()
									ref2 = db.reference('/users/{0}/clans/{1}/points'.format(user,clan))
									try:
										points = int(ref2.get()) + int(points2)
										ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
									except:
										ref2 = db.reference('/users/{0}/clans/{1}'.format(user,clan))
										points = points2
									wins = wins + 1
									ref2.update({
										'wins': wins,
										'previous': text[:30],
										'points': points
									})
									os.remove(attachment.filename)
									await ctx.send(language[110].format(user,wins))
									if(message.guild.id == 900982253679702036) and (clan.lower() == "elite"):
										try:
											update = await ctx.send("e.tracker <@{0}> {1}".format(user,points2))
											await asyncio.sleep(3)
											await update.delete()
										except Exception as e:
											print(e)
		except Exception as e:
			print(e)
			print("Win command fail")
# Setup command
def setup(bot):
	bot.add_cog(Wins(bot))

