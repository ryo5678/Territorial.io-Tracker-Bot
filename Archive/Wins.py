import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics, typing, functools
from discord.ext import commands, tasks
from discord.ext.commands import bot
from firebase_admin import db
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageOps
from pytesseract import pytesseract
import numpy as np
from matplotlib import pyplot as plt, ticker as ticker, dates as mdates
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# List of removeWins admins
winAdmins = ((138752093308583936,"ELITE"),(524835935276498946,"ELITE"),(746381696139788348,"ISLAM"),(735145539494215760,"ISLAM"),(514953130178248707,"RL"))

class Wins(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	# NEW COMMANDS FOR TESTING #
	def to_thread(func: typing.Callable) -> typing.Coroutine:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			return await asyncio.to_thread(func, *args, **kwargs)
		return wrapper


	@to_thread
	def testStats(self,message):
		# Take message time
		old = message.created_at
		# Get now time
		new = datetime.now(timezone.utc)
		# Compare if 24 hours have passed
		diff = new - old
		#print((diff.days*24) + (diff.seconds/3600))
		#print(f"TestStats: old time {old} new time {new}")
		#print(diff.seconds/3600)
		# If so, check main channel for new post
		if (diff.days) >= 1:
			# If new post, send it to community channel
			return True
		else:
			# If Not New, end and wait for next loop
			return False
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def ryoTest(self,ctx):
		channel = self.bot.get_channel(1048351975751819305)
		try:
			message = await channel.fetch_message(
					channel.last_message_id)
			result = await self.testStats(message)
			
		except Exception as e:
			# if message != none crashes bot if try/catch failed on message = await
			print("An erorr occured in RyoTest")
			print(e)
	#-------------------------------------------------------------------------------
	#------------------------------ Best Players Log Tracking ----------------------
	#-------------------------------------------------------------------------------	
	@tasks.loop(seconds=30.0,count=None,reconnect=True)
	async def bestPlayer(self):
		channel = self.bot.get_channel(918557973209571358)
		try:
			message = await channel.fetch_message(
					channel.last_message_id)
					
			mRef = db.reference('/780723109128962070/lastMessageBestPlayer')
			message2 = int(mRef.get())
			
			if message2 != message.id:
				message2 = message
				text = message.content
				channel2 = self.bot.get_channel(1048352090717696020)
				channel3 = self.bot.get_channel(1079823196943028256)
				await channel2.send(text)
				await channel3.send(text)
				
				mRef = db.reference('/780723109128962070')
				mRef.update({
				'lastMessageBestPlayer': str(message.id)
				})
		except Exception as e:
			# if message != none crashes bot if try/catch failed on message = await
			print("An erorr occured in best player log, previous message null")
			print(e)
	#-------------------------------------------------------------------------------
	#----------------------- Top Players  AND Clans Tracking -----------------------
	#-------------------------------------------------------------------------------	
	@tasks.loop(seconds=3600.0,count=None,reconnect=True)
	async def topPlayer(self):
		try:
			# Set channels
			channel = self.bot.get_channel(918557607298470009)
			channel2 = self.bot.get_channel(1048351975751819305)
			channel3 = self.bot.get_channel(917733087859834890)
			# 1v1 Server
			channel4 = self.bot.get_channel(1079823196943028256)
			# Get messages from new community
			message3 = await channel2.fetch_message(
						channel2.last_message_id)
						
			result = await self.testStats(message3)
			if result == True:
				# Best Players
				try:
					message = await channel.fetch_message(
							channel.last_message_id)
							
					mRef = db.reference('/780723109128962070/lastMessageTopPlayer')
					message2 = int(mRef.get())
					
					if message2 != message.id:
						message2 = message
						text = message.content
						await channel2.send("**Top 20 Players**")
						await channel2.send(text + "\n")
						await channel4.send(text)
						
						mRef = db.reference('/780723109128962070')
						mRef.update({
						'lastMessageTopPlayer': str(message.id)
						})
				except Exception as e:
					# if message != none crashes bot if try/catch failed on message = await
					print("An erorr occured in top player, previous message null")
					print(e)
				# Best clans
				await asyncio.sleep(60)
				try:
					message = await channel3.fetch_message(
							channel3.last_message_id)
							
					mRef = db.reference('/780723109128962070/lastMessageBestClan')
					message2 = int(mRef.get())
					
					if message2 != message.id:
						message2 = message
						text = message.content
						await channel2.send("**Top 10 Clans**")
						await channel2.send(text)
						
						mRef = db.reference('/780723109128962070')
						mRef.update({
						'lastMessageBestClan': str(message.id)
						})
				except Exception as e:
					# if message != none crashes bot if try/catch failed on message = await
					print("An erorr occured in best clans, previous message null")
					print(e)
		except Exception as e:
			print("topPlayers loop error")
			print(e)
	#-------------------------------------------------------------------------------
	#------------------------------ User Count Tracking ----------------------------
	#-------------------------------------------------------------------------------
	@to_thread
	def testStats2(self,message):
		# Take message time
		old = message.created_at
		# Get now time
		new = datetime.now(timezone.utc)
		# Compare if 24 hours have passed
		diff = new - old
		#print((diff.days*24) + (diff.seconds/3600))
		# If so, check main channel for new post
		if ((diff.days*24) + (diff.seconds/3600)) > 23:
			# If new post, send it to community channel
			return True
		else:
			# If Not New, end and wait for next loop
			return False
	@to_thread
	def userStats(self,channel,message):
		try:
			#print("userStats Test")
			# Set reference
			ref = db.reference('/userCount')
			# Check time of last message in user stat channel
			#message = await channel.fetch_message(
			#		channel.last_message_id)
			# original code
			#newTime = message.created_at
			oldTime = message.created_at
			
			# Set time settings
			timeDif = timedelta(1)
			#oldTime = newTime - timeDif
			#newTime = newTime + timedelta(1)
			newTime = oldTime + timeDif
			
			# Update database, include timestamp
			now = datetime.now().isoformat()
			
			# Get data
			snapshot = ref.order_by_child('time').start_at(str(oldTime)).end_at(str(newTime)).get()
			snapshot = list(snapshot.items())
			#print(snapshot)
			times = list()
			usercount = list()
			# Fill plot lists
			for i in range(len(snapshot)):
				usercount.append(int(snapshot[i][1]['count']))
				try:
					times.append(datetime.fromisoformat(snapshot[i][1]['time']))
				except:
					times.append(datetime.strptime(snapshot[i][1]['time']),"%H:%M")
			#print(times)
			return times, usercount
		except Exception as e:
			# if message != none crashes bot if try/catch failed on message = await
			print("An erorr occured in user stats")
			print(e)
	@tasks.loop(seconds=3600.0,count=None,reconnect=True)
	async def userStatCheck(self):
		channel2 = self.bot.get_channel(1048355200601178243)
		message3 = await channel2.fetch_message(
			channel2.last_message_id)
			
		result = await self.testStats2(message3)
		if result == True:
			data = await self.userStats(channel2,message3)
			try:
				plt.clf()
				plt.rcParams["figure.figsize"] = (20,5)
				plt.xlabel("Time")
				plt.ylabel("User Count")
				plt.title("Daily change in users")
				
				ax = plt.gca()
				myFmt = mdates.DateFormatter('%H:%M')
				ax.xaxis.set_major_formatter(myFmt)
				#ax.xaxis.set_major_locator(ticker.LinearLocator(12))
				plt.plot(data[0],data[1])
				
				# Save plot for discord embed
				data_stream = io.BytesIO()
				plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
				data_stream.seek(0)
				chart = discord.File(data_stream,filename="plot.png")
				
				# Send report to channel
				try:
					avg = round(statistics.mean(data[1]))
				except:
					return
				plot = discord.Embed(title="User Changes In The Past Day", description='{0} average players'.format(avg), color=0x03fcc6)
				plot.set_image(
				   url="attachment://plot.png"
				)
				plt.clf()
				plt.rcParams["figure.figsize"] = plt.rcParamsDefault["figure.figsize"]
				
				await channel2.send(embed=plot, file=chart)
			except Exception as e:
				print(e)
	@tasks.loop(seconds=1800.0,count=None,reconnect=True)
	async def userCount(self):
		channel = self.bot.get_channel(798537217106116608)
		try:
			message = await channel.fetch_message(
					channel.last_message_id)
			#------------------------------------- 2340 Players
			mRef = db.reference('/780723109128962070/lastMessageUserCount')
			#print(message.id)
			message2 = int(mRef.get())
			
			if message2 != message.id:
				message2 = message
				#  Outdated, being replaced
				text = message.content
				#if text == None:
				mRef = db.reference('/780723109128962070')
				mRef.update({
				'lastMessageUserCount': str(message.id)
				})
				now = datetime.now().isoformat()
				try:
					# Set reference and strip all but numbers from text
					ref = db.reference('/userCount')
					text = re.sub("[^0-9]", "", text)
					
					# Update database, include timestamp
					ref.push({
						'count': text,
						'time': now
					})
				except Exception as e:
					print(e)
					print(now)
					print("issue in user count")
					print(message.content)
		except Exception as e:
			# if message != none crashes bot if try/catch failed on message = await
			print("An erorr occured in user count, previous message null")
			print(e)
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
			print(ctx.guild.name)
			print(ctx.channel.id)
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
		#ref = db.reference('/imageChannels')
		#info = ref.get()
		#channels = list(info.items())
		#channelList = []
		# Check if command called in tracking channel
		#for i in range(len(channels)):
		#	channelList.append(int(channels[i][1]['channelID']))
		#if int(ctx.channel.id) not in channelList:
		#	return await ctx.send("Command used outside of a win tracking channel. Please get an administrator to specify a channel with t!imagetrack")
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
async def setup(bot):
	await bot.add_cog(Wins(bot))

