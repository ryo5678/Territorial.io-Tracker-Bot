import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, ticker as ticker, dates as mdates
from collections import defaultdict
from urllib.request import Request, urlopen
import functools
import typing
from discord.utils import get

#English
textfile = open('Strings/en-strings.txt', 'r')
english = textfile.read().splitlines()
textfile.close()

class Clans(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#------------------------------ Compare Clans Command --------------------------
	#-------------------------------------------------------------------------------
	#async def compare(self,ctx,*,clans):
	#	asyncio.create_task(self.compare2(ctx,clans))
	def to_thread(func: typing.Callable) -> typing.Coroutine:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			return await asyncio.to_thread(func, *args, **kwargs)
		return wrapper
		
	@commands.command(pass_context = True)
	@commands.cooldown(1, 300, commands.BucketType.user)
	async def compare(self,ctx,*,clans):
		try:
			# Set language
			language = english
			# Set user
			user = ctx.message.author.id
			# Set time
			time = ctx.message.created_at
			day = time.day
			month = time.month
			year = time.year
			hour = time.hour
			time = time.isoformat()
			# Initialize empty message
			scoreMessage = ""
			
			# Reset cooldown if user fails to use command correctly
			clanList = clans.split()
			if len(clanList) < 2 or clanList == None:
				await ctx.send("Minimum clans is 2, please try again.")
				# May need to change to self.reset, unsure for cogs
				ctx.command.reset_cooldown(ctx)
				return
			if len(clanList) > 5:
				await ctx.send("Maximum clans is 5, please try again.")
				ctx.command.reset_cooldown(ctx)
				return
			
			#plt.clf()
			#TEMPORARY 
			await ctx.send("This command is being remade, in the near future it will get buttons to switch between day/month/2months of data.")
			#TEMPORARY
			await ctx.send(language[3])
			
			# Make plot for score vs time
			fig1, ax1 = plt.subplots()
			#print(ax1.lines)
			# DAY
			#if ax1.get_xlabel == language[157]:
			# MONTH
			if ax1.get_xlabel == language[178]:
				print("Testing")
				fig2, ax2 = plt.subplots()
				figure = fig2
				axe = ax2
			else:
				figure = fig1
				axe = ax1
			# DAY
			#axe.set_title(language[159])
			#axe.set_xlabel(language[157])
			#axe.set_ylabel(language[158])
			# MONTH
			axe.set_title(language[180])
			axe.set_xlabel(language[178])
			axe.set_ylabel(language[179])
			
			#figure.title(language[169])
			# MONTH
			myFmt = mdates.DateFormatter('%m/%d')
			# DAY
			#myFmt = mdates.DateFormatter('%H:%M')
			axe.xaxis.set_major_formatter(myFmt)
			axe.xaxis.set_major_locator(ticker.LinearLocator(9))
			axe.xaxis.set_minor_locator(ticker.LinearLocator(10))
		except Exception as e:
			print("Error in t!compare first part")
			print(e)
		
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
					ctx.command.reset_cooldown(ctx)
					return
				else:
					# Get the data for a clan DAY
					#stuff = await self.clanMathDay(ctx,clan,year,month,day,hour)
					# Get the data for a clan MONTH
					stuff = await self.clanMathMonth(ctx,clan,year,month,day,hour)
					if stuff is None:
						await ctx.send("Something went wrong, or not enough recent data exists")
						ctx.command.reset_cooldown(ctx)
						return
					# Organize returned data
					x = stuff[2]
					times = sorted(stuff[0])
					scores = list()
					for a in times:
						scores.append(stuff[1][stuff[0].index(a)])
					
					# Convert database readable clan name back to normal
					clan = clan.replace('PERIOD5', '.')
					clan = clan.replace('DOLLAR5', '$')
					clan = clan.replace('HTAG5', '#')
					clan = clan.replace('LBRACKET5', '[')
					clan = clan.replace('SLASH5', '/')
					clan = clan.replace('RBRACKET5', ']')
					clan = clan.replace('QMARK5', '?')
					# Set current clan score
					score = clanData['score']
					# Plot clan data
					axe.plot(times,scores,label=clan)
					# Update reply message DAY
					#scoreMessage += f"The clan, {clan}, has a last known score of {score} and {x} wins today. \n"
					# Update reply message MONTH
					scoreMessage += f"The clan, {clan}, has a last known score of {score} and {x} wins this past month. \n"
		
			except Exception as e:
				print(e)
				await ctx.send(language[153])
				ctx.command.reset_cooldown(ctx)
				return
		try:
			axe.legend(loc="upper left")
			# Save plot for discord embed
			data_stream = io.BytesIO()
			figure.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
			data_stream.seek(0)
			chart = discord.File(data_stream,filename="plot.png")
			# Make and send embed DAY
			#plot = discord.Embed(title="{0}".format(clans), description=language[160], color=0x03fcc6)
			# Make and send embed MONTH
			plot = discord.Embed(title="{0}".format(clans), description=language[181], color=0x03fcc6)
			plot.set_image(
			   url="attachment://plot.png"
			)
			await ctx.send(embed=plot, file=chart)
			plt.close(figure)
			await ctx.send(scoreMessage)
		except Exception as e:
			print("Error in t!compare final part")
			print(e)
			await ctx.send(language[153])
	#-------------------------------------------------------------------------------
	#----------------------------- Search For Clan  --------------------------------
	#-------------------------------------------------------------------------------
	@to_thread
	def clanMathDay(self,ctx,clan,year,month,day,hour):
		try:
			# Get all games from previous day
			months0 = (4,6,9,11)
			months1 = (1,3,5,7,8,10,12)
			# Add leap year logic when not being lazy
			# February case
			if month == 2:
				if day < 29 and day > 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month}/day{day-1}/{clan}')
				if day == 1:
					ref2 = db.reference(f'gameDataFinal/{year}/1/day31/{clan}')
			# April June September November
			elif month in months0:
				if day < 31 and day > 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month}/day{day-1}/{clan}')
				if day == 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month-1}/day31/{clan}')
			# January March May July August October December
			elif month in months1:
				if day < 32 and day > 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month}/day{day-1}/{clan}')
				if day == 1:
					if month == 1:
						ref2 = db.reference(f'gameDataFinal/{year}/12/day31/{clan}')
					elif month == 3:
						ref2 = db.reference(f'gameDataFinal/{year}/2/day28/{clan}')
					else:
						ref2 = db.reference(f'gameDataFinal/{year}/{month-1}/day31/{clan}')

			# Get all games from today
			ref = db.reference(f'gameDataFinal/{year}/{month}/day{day}/{clan}')
			snapshot = ref.get()
			snapshot2 = ref2.get()
			if snapshot == None and snapshot2 == None:
				return
			else:
				# Total number of games
				y = 0
				# Empty lists
				times = list()
				scores = list()
				# Previous day  games
				if snapshot2 != None:
					games = list(snapshot2.items())
					# Number of maps from today
					x = len(games)
					# Loop games
					for i in range(x):
						z = 0
						# List from each map
						tempGames = list(games[i][1].items())
						z = len(tempGames)
						for j in range(z):
							# Get time from each game
							temp = tempGames[j][1]['Time'].replace('T',' ')
							dt = datetime.fromisoformat(temp)
							if hour <= dt.hour:
								try:
									times.append(dt)
								except:
									times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
									#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
								# Get score from each game
								scores.append(tempGames[j][1]['Score'])
								y += 1
				if snapshot != None:
					# Current day games
					games = list(snapshot.items())
					# Number of maps from today
					x = len(games)
					# Loop games
					for i in range(x):
						z = 0
						# List from each map
						tempGames = list(games[i][1].items())
						z = len(tempGames)
						for j in range(z):
							# Get time from each game
							temp = tempGames[j][1]['Time'].replace('T',' ')
							try:
								times.append(datetime.fromisoformat(temp))
							except:
								times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
								#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
							# Get score from each game
							scores.append(tempGames[j][1]['Score'])
							y += 1
			return times,scores,y
		except Exception as e:
			print("clanMathDay error")
			print(e)
			return None
	@to_thread
	def clanMathMonth(self,ctx,clan,year,month,day,hour):
		try:
			# Get all games from previous day
			months0 = (4,6,9,11)
			months1 = (1,3,5,7,8,10,12)
			# Add leap year logic when not being lazy
			# February case
			if month == 2:
				day2 = 28
			# April June September November
			elif month in months0:
				day2 = 30
			# January March May July August October December
			elif month in months1:
				day2 = 31

			# Get all games from today
			ref = db.reference(f'gameDataFinal/{year}/{month}')
			ref2 = db.reference(f'gameDataFinal/{year}/{month-1}')
			snapshot = ref.get()
			snapshot2 = ref2.get()
			
			if snapshot == None and snapshot2 == None:
				return
			else:
				# Total number of games
				y = 0
				# Empty lists
				times = list()
				scores = list()
				# Previous day  games
				if snapshot2 != None:
					# Only get current day of last month to end of month, EX: 14 to 31 if today is 14th
					a = day
					data = snapshot2
					while a != (day2 + 1):
						try:
							# Get a day of games
							games = list(data[f'day{a}'][clan].items())
							# Number of maps from today
							x = len(games)
							# Loop games
							for i in range(x):
								z = 0
								# List from each map
								tempGames = list(games[i][1].items())
								z = len(tempGames)
								for j in range(z):
									# Get time from each game
									temp = tempGames[j][1]['Time'].replace('T',' ')
									dt = datetime.fromisoformat(temp)
									if hour <= dt.hour:
										try:
											times.append(dt)
										except:
											times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
											#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
										# Get score from each game
										scores.append(tempGames[j][1]['Score'])
										y += 1
						except:
							status = "failed"
						a += 1
				if snapshot != None:
					b = 1
					data2 = snapshot
					while b != (day + 1):
						try:
							# Get a day of games
							games = list(data2[f'day{b}'][clan].items())
							# Number of maps
							x = len(games)
							# Loop games
							for i in range(x):
								z = 0
								# List from each map
								tempGames = list(games[i][1].items())
								z = len(tempGames)
								for j in range(z):
									# Get time from each game
									temp = tempGames[j][1]['Time'].replace('T',' ')
									try:
										times.append(datetime.fromisoformat(temp))
									except:
										times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
										#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
									# Get score from each game
									scores.append(tempGames[j][1]['Score'])
									y += 1
						except Exception as e:
							status = "failed"
						b += 1
			return times,scores,y
		except Exception as e:
			print("clanMathMonth error")
			print(e)
			return None
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def clan(self,ctx,clan):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		# Set time
		time = ctx.message.created_at
		day = time.day
		month = time.month
		year = time.year
		hour = time.hour
		time = time.isoformat()
		#TEMPORARY 
		await ctx.send("This command will receive a month and 2month button in the near future.")
		#TEMPORARY
		plt.clf()
		try:
			# Download the webpage as text
			req = Request(
				url = "https://territorial.io/clans",
				headers={'User-Agent': 'Mozilla/5.0'}
			)
			with urlopen(req) as webpage:
				content = webpage.read().decode()
			# print(content)
			# Create db reference and convert string to list
			clan = clan.upper()
			clanCheck = f' {clan}, '
			if (clanCheck not in content):
				await ctx.send(language[156].format(clan))
			else:
				# Convert clan name to database readable name
				clan.strip("[]")
				clan = clan.replace('.', 'period5')
				clan = clan.replace('$', 'dollar5')
				clan = clan.replace('#', 'htag5')
				clan = clan.replace('[', 'lbracket5')
				clan = clan.replace('/', 'slash5')
				clan = clan.replace(']', 'rbracket5')
				clan = clan.replace('?', 'qmark5')

				try:
					stuff = await self.clanMathMonth(ctx,clan,year,month,day,hour)
					if stuff is None:
						await ctx.send("Something went wrong, or not enough recent data exists")
						ctx.command.reset_cooldown(ctx)
						return
					x = stuff[2]
					times = sorted(stuff[0])
					scores = list()
					for a in times:
						scores.append(stuff[1][stuff[0].index(a)])
					# Make plot for score vs time MONTH
					plt.xlabel(language[178])
					plt.ylabel(language[179])
					plt.title(language[180])
					plt.plot(times,scores)
					ax = plt.gca()
					# Format for month
					myFmt = mdates.DateFormatter('%m/%d')
					ax.xaxis.set_major_formatter(myFmt)
					if len(times) < 9:
						ax.xaxis.set_major_locator(ticker.LinearLocator(len(times)))
						ax.xaxis.set_minor_locator(ticker.LinearLocator(0))
						ax.yaxis.set_major_locator(ticker.LinearLocator(len(scores)))
					else:
						ax.xaxis.set_major_locator(ticker.LinearLocator(9))
						ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
					# Save plot for discord embed
					data_stream = io.BytesIO()
					plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
					data_stream.seek(0)
					chart = discord.File(data_stream,filename="plot.png")
					# Make and send embed
					try:
						# Convert database readable clan name back to normal
						clan2 = clan
						clan2 = clan2.replace('period5', '.')
						clan2 = clan2.replace('dollar5', '$')
						clan2 = clan2.replace('htag5', '#')
						clan2 = clan2.replace('lbracket5', '[')
						clan2 = clan2.replace('slash5', '/')
						clan2 = clan2.replace('rbracket5', ']')
						clan2 = clan2.replace('qmark5', '?')
						# Get score
						content = content.splitlines()
						for c in range(len(content)):
							if clanCheck in content[c]:
								score = content[c][-6:]
								score.strip(" ")
						# Make embed
						plot = discord.Embed(title="{0}".format(clan2), description=language[182].format(clan2,score,x), color=0x03fcc6)
						plot.set_image(
						   url="attachment://plot.png"
						)
						view = discord.ui.View(timeout = 180)
						button1 = discord.ui.Button(label="Day")
						async def button1_callback(button_inter: discord.Interaction):
							try:
								language = english
								stuff = await self.clanMathDay(ctx,clan,year,month,day,hour)
								if stuff is None:
									await ctx.send("Something went wrong, or not enough recent data exists")
									ctx.command.reset_cooldown(ctx)
									return
								x = stuff[2]
								times = sorted(stuff[0])
								scores = list()
								for a in times:
									scores.append(stuff[1][stuff[0].index(a)])
								# Make plot for score vs time DAY
								plt.xlabel(language[157])
								plt.ylabel(language[158])
								plt.title(language[159])
								
								plt.plot(times,scores)
								ax = plt.gca()
								# Format for one day
								myFmt = mdates.DateFormatter('%H:%M')
								ax.xaxis.set_major_formatter(myFmt)
								if len(times) < 9:
									ax.xaxis.set_major_locator(ticker.LinearLocator(len(times)))
									ax.xaxis.set_minor_locator(ticker.LinearLocator(0))
									ax.yaxis.set_major_locator(ticker.LinearLocator(len(scores)))
								else:
									ax.xaxis.set_major_locator(ticker.LinearLocator(9))
									ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
								# Save plot for discord embed
								data_stream = io.BytesIO()
								plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
								data_stream.seek(0)
								chart = discord.File(data_stream,filename="plot.png")
								# Make and send embed
								try:
									# Day
									plot = discord.Embed(title="{0}".format(clan2), description=language[162].format(clan2,score,x), color=0x03fcc6)
									plot.set_image(
									   url="attachment://plot.png"
									)
								except Exception as e:
									print("t!clan error")
									print(e)
								plt.clf()
							except Exception as e:
								print(e)
								print("daily button fail")
								await ctx.send(language[161])

							await button_inter.response.edit_message(embed=plot, attachments=[chart])
						
						button1.callback = button1_callback
						view.add_item(button1)
						
						await ctx.send(embed=plot, file=chart, view=view)
						
					except Exception as e:
						print("t!clan error")
						print(e)
						print(clan)
					plt.clf()
				except Exception as e:
					print(e)
					await ctx.send(language[161])
					return

		except Exception as e:
			print(e)
			print("test")
			# Catch missing message permission
			try:
				await ctx.send(language[153])
			except:
				try:
					await ctx.author.send(language[153])
				except Exception as e:
					print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
					print(e)
	#-------------------------------------------------------------------------------
	#-------------------------------  History Grab  --------------------------------
	#-------------------------------------------------------------------------------
	@to_thread
	def clanExtra(self,text3,clan,players,map,message):	
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
		
		# push to database
		ref2 = db.reference('/May23GameData')
		ref2.push({
		'Map': map,
		'Players': players,
		'Clan': clan,
		'Score': float(points),
		'Time': time
		})
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def grabGameHistory(self,ctx):
		channel = self.bot.get_channel(917537295261913159)
		try:
			print("Starting message download")
			x = datetime(2023,5,26,1,1,20)
			z = datetime(2023,6,1,1,1,20)
			messages = [msg async for msg in channel.history(limit=None,before=z,after=x)]
			print("Finished discord list gathering")
			for msg in messages:
				text = msg.content
				textList = text.split(4*' ')
				clan = ""
				# Set map
				text2 = textList[0].split()
				if len(text2) == 2:
					map = text2[0] + text2[1]
					try:
						map.strip("**")
					except:
						print("Error1 in grabGameHistory")
				else:
					map = text2[0]
					try:
						map.strip("**")
					except:
						print("Error2 in grabGameHistory")
				# Set Players
				players = textList[1]
				# Set Clan
				text3 = textList[2].rsplit(' ',1)
				clan = text3[0]
				# Run extra stuff
				await self.clanExtra(text3,clan,players,map,msg)
			print("Finished discord list posting")
		except Exception as e:
			# if message != none crashes bot if try/catch failed on message = await
			print("An erorr occured in grabGameHistory, previous message null")
			print(e)

	@to_thread
	def compareMathRyo(self,snapshot,clan,b):
		pF = 0
		pS = 0
		mF = ''
		mS = ''
		gF = 0
		gS = 0
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
				times.append(datetime.fromisoformat(temp))
			except:
				times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
				#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
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
			#print(players)
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
			return times, scores, pF, mF, gF,
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
			return times, scores, pS, mS, gS
		elif(b == 3):
			if(players == []):
				pT = 0
			else:
				pT = int(statistics.mean(players))
			if(maps == []):
				mT = "N/A"
			else:
				for map in maps:
					for name in map.split():
						temp2[name] += 1
				mT = max(temp2, key=temp2.get)
			gT = count
			return times, scores, pT, mT, gT
		elif(b == 4):
			if(players == []):
				pR = 0
			else:
				pR = int(statistics.mean(players))
			if(maps == []):
				mR = "N/A"
			else:
				for map in maps:
					for name in map.split():
						temp2[name] += 1
				mR = max(temp2, key=temp2.get)
			gR = count
			return times, scores, pR, mR, gR
		elif(b == 5):
			if(players == []):
				pR = 0
			else:
				pR = int(statistics.mean(players))
			if(maps == []):
				mR = "N/A"
			else:
				for map in maps:
					for name in map.split():
						temp2[name] += 1
				mR = max(temp2, key=temp2.get)
			gR = count
			return times, scores, pR, mR, gR
	
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def compareRyo(self,ctx,*,clans):
		try:
			# Set language
			language = english
			# Set user
			user = ctx.message.author.id
			# Set time
			time = ctx.message.created_at
			day = time.day
			month = time.month
			year = time.year
			hour = time.hour
			time = time.isoformat()
			# Initialize empty message
			scoreMessage = ""
			
			# Reset cooldown if user fails to use command correctly
			clanList = clans.split()
			if len(clanList) < 2 or clanList == None:
				await ctx.send("Minimum clans is 2, please try again.")
				# May need to change to self.reset, unsure for cogs
				ctx.command.reset_cooldown(ctx)
				return
			if len(clanList) > 5:
				await ctx.send("Maximum clans is 5, please try again.")
				ctx.command.reset_cooldown(ctx)
				return
			
			#plt.clf()
			#TEMPORARY 
			await ctx.send("This command is temporarily limited while it is being rebuilt.")
			#TEMPORARY
			await ctx.send(language[3])
			
			# Make plot for score vs time
			fig1, ax1 = plt.subplots()
			#print(ax1.lines)
			# DAY
			#if ax1.get_xlabel == language[157]:
			# MONTH
			if ax1.get_xlabel == language[178]:
				print("Testing")
				fig2, ax2 = plt.subplots()
				figure = fig2
				axe = ax2
			else:
				figure = fig1
				axe = ax1
			# DAY
			#axe.set_title(language[159])
			#axe.set_xlabel(language[157])
			#axe.set_ylabel(language[158])
			# MONTH
			axe.set_title(language[180])
			axe.set_xlabel(language[178])
			axe.set_ylabel(language[179])
			
			#figure.title(language[169])
			# MONTH
			myFmt = mdates.DateFormatter('%m/%d')
			# DAY
			#myFmt = mdates.DateFormatter('%H:%M')
			axe.xaxis.set_major_formatter(myFmt)
			axe.xaxis.set_major_locator(ticker.LinearLocator(9))
			axe.xaxis.set_minor_locator(ticker.LinearLocator(10))
		except Exception as e:
			print("Error in t!compare first part")
			print(e)
		
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
					ctx.command.reset_cooldown(ctx)
					return
				else:
					# Get the data for a clan DAY
					#stuff = await self.clanMathDay(ctx,clan,year,month,day,hour)
					# Get the data for a clan MONTH
					stuff = await self.clanMathMonth(ctx,clan,year,month,day,hour)
					if stuff is None:
						await ctx.send("Something went wrong, or not enough recent data exists")
						ctx.command.reset_cooldown(ctx)
						return
					# Organize returned data
					x = stuff[2]
					times = sorted(stuff[0])
					scores = list()
					for a in times:
						scores.append(stuff[1][stuff[0].index(a)])
					
					# Convert database readable clan name back to normal
					clan = clan.replace('PERIOD5', '.')
					clan = clan.replace('DOLLAR5', '$')
					clan = clan.replace('HTAG5', '#')
					clan = clan.replace('LBRACKET5', '[')
					clan = clan.replace('SLASH5', '/')
					clan = clan.replace('RBRACKET5', ']')
					clan = clan.replace('QMARK5', '?')
					# Set current clan score
					score = clanData['score']
					# Plot clan data
					axe.plot(times,scores,label=clan)
					# Update reply message DAY
					#scoreMessage += f"The clan, {clan}, has a last known score of {score} and {x} wins today. \n"
					# Update reply message MONTH
					scoreMessage += f"The clan, {clan}, has a last known score of {score} and {x} wins this past month. \n"
		
			except Exception as e:
				print(e)
				await ctx.send(language[153])
				ctx.command.reset_cooldown(ctx)
				return
		try:
			axe.legend(loc="upper left")
			# Save plot for discord embed
			data_stream = io.BytesIO()
			figure.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
			data_stream.seek(0)
			chart = discord.File(data_stream,filename="plot.png")
			# Make and send embed DAY
			#plot = discord.Embed(title="{0}".format(clans), description=language[160], color=0x03fcc6)
			# Make and send embed MONTH
			plot = discord.Embed(title="{0}".format(clans), description=scoreMessage, color=0x03fcc6)
			plot.set_image(
			   url="attachment://plot.png"
			)
			view = discord.ui.View(timeout = 180)
			button1 = discord.ui.Button(label="Day")
			async def button1_callback(button_inter: discord.Interaction):
				do = "nothing"
			button1.callback = button1_callback
			view.add_item(button1)
			await ctx.send(embed=plot, file=chart, view=view)
			plt.close(figure)
		except Exception as e:
			print("Error in t!compare final part")
			print(e)
			await ctx.send(language[153])
	@to_thread
	def clanMathDayTest(self,ctx,clan,year,month,day,hour):
		try:
			# Get all games from previous day
			months0 = (4,6,9,11)
			months1 = (1,3,5,7,8,10,12)
			# Add leap year logic when not being lazy
			# February case
			if month == 2:
				if day < 29 and day > 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month}/day{day-1}/{clan}')
				if day == 1:
					ref2 = db.reference(f'gameDataFinal/{year}/1/day31/{clan}')
			# April June September November
			elif month in months0:
				if day < 31 and day > 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month}/day{day-1}/{clan}')
				if day == 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month-1}/day31/{clan}')
			# January March May July August October December
			elif month in months1:
				if day < 32 and day > 1:
					ref2 = db.reference(f'gameDataFinal/{year}/{month}/day{day-1}/{clan}')
				if day == 1:
					if month == 1:
						ref2 = db.reference(f'gameDataFinal/{year}/12/day31/{clan}')
					elif month == 3:
						ref2 = db.reference(f'gameDataFinal/{year}/2/day28/{clan}')
					else:
						ref2 = db.reference(f'gameDataFinal/{year}/{month-1}/day31/{clan}')

			# Get all games from today
			ref = db.reference(f'gameDataFinal/{year}/{month}/day{day}/{clan}')
			snapshot = ref.get()
			snapshot2 = ref2.get()
			if snapshot == None and snapshot2 == None:
				return
			else:
				# Total number of games
				y = 0
				# Empty lists
				times = list()
				scores = list()
				# Previous day  games
				if snapshot2 != None:
					games = list(snapshot2.items())
					# Number of maps from today
					x = len(games)
					# Loop games
					for i in range(x):
						z = 0
						# List from each map
						tempGames = list(games[i][1].items())
						z = len(tempGames)
						for j in range(z):
							# Get time from each game
							temp = tempGames[j][1]['Time'].replace('T',' ')
							dt = datetime.fromisoformat(temp)
							if hour <= dt.hour:
								try:
									times.append(dt)
								except:
									times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
									#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
								# Get score from each game
								scores.append(tempGames[j][1]['Score'])
								y += 1
				if snapshot != None:
					# Current day games
					games = list(snapshot.items())
					# Number of maps from today
					x = len(games)
					# Loop games
					for i in range(x):
						z = 0
						# List from each map
						tempGames = list(games[i][1].items())
						z = len(tempGames)
						for j in range(z):
							# Get time from each game
							temp = tempGames[j][1]['Time'].replace('T',' ')
							try:
								times.append(datetime.fromisoformat(temp))
							except:
								times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
								#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
							# Get score from each game
							scores.append(tempGames[j][1]['Score'])
							y += 1
			return times,scores,y
		except Exception as e:
			print("clanMathDayTest error")
			print(e)
			return None
	@to_thread
	def clanMathMonthTest(self,ctx,clan,year,month,day,hour):
		try:
			# Get all games from previous day
			months0 = (4,6,9,11)
			months1 = (1,3,5,7,8,10,12)
			# Add leap year logic when not being lazy
			# February case
			if month == 2:
				day2 = 28
			# April June September November
			elif month in months0:
				day2 = 30
			# January March May July August October December
			elif month in months1:
				day2 = 31

			# Get all games from today
			ref = db.reference(f'gameDataFinal/{year}/{month}')
			ref2 = db.reference(f'gameDataFinal/{year}/{month-1}')
			snapshot = ref.get()
			snapshot2 = ref2.get()
			
			if snapshot == None and snapshot2 == None:
				return
			else:
				# Total number of games
				y = 0
				# Empty lists
				times = list()
				scores = list()
				# Previous day  games
				if snapshot2 != None:
					# Only get current day of last month to end of month, EX: 14 to 31 if today is 14th
					a = day
					data = snapshot2
					while a != (day2 + 1):
						try:
							# Get a day of games
							games = list(data[f'day{a}'][clan].items())
							# Number of maps from today
							x = len(games)
							# Loop games
							for i in range(x):
								z = 0
								# List from each map
								tempGames = list(games[i][1].items())
								z = len(tempGames)
								for j in range(z):
									# Get time from each game
									temp = tempGames[j][1]['Time'].replace('T',' ')
									dt = datetime.fromisoformat(temp)
									if hour <= dt.hour:
										try:
											times.append(dt)
										except:
											times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
											#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
										# Get score from each game
										scores.append(tempGames[j][1]['Score'])
										y += 1
						except:
							status = "failed"
						a += 1
				if snapshot != None:
					b = 1
					data2 = snapshot
					while b != (day + 1):
						try:
							# Get a day of games
							games = list(data2[f'day{b}'][clan].items())
							# Number of maps
							x = len(games)
							# Loop games
							for i in range(x):
								z = 0
								# List from each map
								tempGames = list(games[i][1].items())
								z = len(tempGames)
								for j in range(z):
									# Get time from each game
									temp = tempGames[j][1]['Time'].replace('T',' ')
									try:
										times.append(datetime.fromisoformat(temp))
									except:
										times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
										#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
									# Get score from each game
									scores.append(tempGames[j][1]['Score'])
									y += 1
						except Exception as e:
							status = "failed"
						b += 1
			return times,scores,y
		except Exception as e:
			print("clanMathMonthTEST error")
			print(e)
			return None
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def clanRyo(self,ctx,clan):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		# Set time
		time = ctx.message.created_at
		day = time.day
		month = time.month
		year = time.year
		hour = time.hour
		time = time.isoformat()
		#TEMPORARY 
		await ctx.send("This command is temporarily limited while it is being rebuilt.")
		#TEMPORARY
		plt.clf()
		try:
			# Convert clan name to database readable name
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
				try:
					stuff = await self.clanMathMonthTest(ctx,clan,year,month,day,hour)
					if stuff is None:
						await ctx.send("Something went wrong, or not enough recent data exists")
						ctx.command.reset_cooldown(ctx)
						return
					x = stuff[2]
					times = sorted(stuff[0])
					scores = list()
					for a in times:
						scores.append(stuff[1][stuff[0].index(a)])
					# Make plot for score vs time MONTH
					plt.xlabel(language[178])
					plt.ylabel(language[179])
					plt.title(language[180])
					plt.plot(times,scores)
					ax = plt.gca()
					# Format for month
					myFmt = mdates.DateFormatter('%m/%d')
					ax.xaxis.set_major_formatter(myFmt)
					if len(times) < 9:
						ax.xaxis.set_major_locator(ticker.LinearLocator(len(times)))
						ax.xaxis.set_minor_locator(ticker.LinearLocator(0))
						ax.yaxis.set_major_locator(ticker.LinearLocator(len(scores)))
					else:
						ax.xaxis.set_major_locator(ticker.LinearLocator(9))
						ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
					# Save plot for discord embed
					data_stream = io.BytesIO()
					plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
					data_stream.seek(0)
					chart = discord.File(data_stream,filename="plot.png")
					# Make and send embed
					try:
						# Convert database readable clan name back to normal
						clan = clan.replace('PERIOD5', '.')
						clan = clan.replace('DOLLAR5', '$')
						clan = clan.replace('HTAG5', '#')
						clan = clan.replace('LBRACKET5', '[')
						clan = clan.replace('SLASH5', '/')
						clan = clan.replace('RBRACKET5', ']')
						clan = clan.replace('QMARK5', '?')
						# Get score
						score = clanData['score']
						# Make embed
						plot = discord.Embed(title="{0}".format(clan), description=language[182].format(clan,score,x), color=0x03fcc6)
						plot.set_image(
						   url="attachment://plot.png"
						)
						view = discord.ui.View()
						button1 = discord.ui.Button(label="Day")
						async def button1_callback(button_inter: discord.Interaction):
							try:
								language = english
								stuff = await self.clanMathDayTest(ctx,clan,year,month,day,hour)
								if stuff is None:
									await ctx.send("Something went wrong, or not enough recent data exists")
									ctx.command.reset_cooldown(ctx)
									return
								x = stuff[2]
								times = sorted(stuff[0])
								scores = list()
								for a in times:
									scores.append(stuff[1][stuff[0].index(a)])
								# Make plot for score vs time DAY
								plt.xlabel(language[157])
								plt.ylabel(language[158])
								plt.title(language[159])
								
								plt.plot(times,scores)
								ax = plt.gca()
								# Format for one day
								myFmt = mdates.DateFormatter('%H:%M')
								ax.xaxis.set_major_formatter(myFmt)
								if len(times) < 9:
									ax.xaxis.set_major_locator(ticker.LinearLocator(len(times)))
									ax.xaxis.set_minor_locator(ticker.LinearLocator(0))
									ax.yaxis.set_major_locator(ticker.LinearLocator(len(scores)))
								else:
									ax.xaxis.set_major_locator(ticker.LinearLocator(9))
									ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
								# Save plot for discord embed
								data_stream = io.BytesIO()
								plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
								data_stream.seek(0)
								chart = discord.File(data_stream,filename="plot.png")
								# Make and send embed
								try:
									# Day
									plot = discord.Embed(title="{0}".format(clan), description=language[162].format(clan,score,x), color=0x03fcc6)
									plot.set_image(
									   url="attachment://plot.png"
									)
								except Exception as e:
									print("t!clan error")
									print(e)
								plt.clf()
							except Exception as e:
								print(e)
								print("daily button fail")
								await ctx.send(language[161])

							await button_inter.response.edit_message(embed=plot, attachments=[chart])
						
						button1.callback = button1_callback
						view.add_item(button1)
						
						await ctx.send(embed=plot, file=chart, view=view)
					except Exception as e:
						print("t!clan error")
						print(e)
						print(clan)
					plt.clf()
				except Exception as e:
					print(e)
					await ctx.send(language[161])
					return

		except Exception as e:
			print(e)
			print("test")
			# Catch missing message permission
			try:
				await ctx.send(language[153])
			except:
				try:
					await ctx.author.send(language[153])
				except Exception as e:
					print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
					print(e)
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top50(self,ctx):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		#TEMPORARY 
		await ctx.send("This command is temporarily disabled while it is being rebuilt.")
		return
		#TEMPORARY
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top25(self,ctx):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		#TEMPORARY 
		await ctx.send("This command is temporarily disabled while it is being rebuilt.")
		return
		#TEMPORARY
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top(self,ctx):
		# Set language
		language = english
		#TEMPORARY 
		await ctx.send("This command is temporarily disabled while it is being rebuilt.")
		return
		#TEMPORARY
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top100(self,ctx):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		#TEMPORARY 
		await ctx.send("This command is temporarily disabled while it is being rebuilt.")
		return
		#TEMPORARY
	@commands.command(pass_context = True)
	@commands.cooldown(1, 3600, commands.BucketType.user)
	async def clanboard(self,ctx,clan):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		#TEMPORARY 
		await ctx.send("This command is temporarily disabled while it is being rebuilt.")
		return
		#TEMPORARY
# View for t!clan
class clanSelector(discord.ui.View):
	def __init__(self, ctx, clan, year, month, day, hour, timeout = 180):
		super().__init__(timeout = 180)
		self.ctx = ctx
		self.clan = clan
		self.year = year
		self.month = month
		self.day = day
		self.hour = hour
		self.add_buttons()
	def add_buttons(self):
		# Declare the buttons
		button1 = discord.ui.Button(label="Month",style=discord.ButtonStyle.grey,disabled = True)
		button2 = discord.ui.Button(label="Day",style=discord.ButtonStyle.grey)
		async def daily(interaction: discord.Interaction):
			try:
				language = english
				stuff = await Clans.clanMathDayTest(self,self.ctx,self.clan,self.year,self.month,self.day,self.hour)
				if stuff is None:
					await self.ctx.send("Something went wrong, or not enough recent data exists")
					self.ctx.command.reset_cooldown(self.ctx)
					return
				x = stuff[2]
				times = sorted(stuff[0])
				scores = list()
				for a in times:
					scores.append(stuff[1][stuff[0].index(a)])
				# Make plot for score vs time DAY
				plt.xlabel(language[157])
				plt.ylabel(language[158])
				plt.title(language[159])
				
				plt.plot(times,scores)
				ax = plt.gca()
				# Format for one day
				myFmt = mdates.DateFormatter('%H:%M')
				ax.xaxis.set_major_formatter(myFmt)
				if len(times) < 9:
					ax.xaxis.set_major_locator(ticker.LinearLocator(len(times)))
					ax.xaxis.set_minor_locator(ticker.LinearLocator(0))
					ax.yaxis.set_major_locator(ticker.LinearLocator(len(scores)))
				else:
					ax.xaxis.set_major_locator(ticker.LinearLocator(9))
					ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
				# Save plot for discord embed
				data_stream = io.BytesIO()
				plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
				data_stream.seek(0)
				chart = discord.File(data_stream,filename="plot.png")
				# Make and send embed
				try:
					# Day
					plot = discord.Embed(title="{0}".format(self.clan), description=language[163], color=0x03fcc6)
					plot.set_image(
					   url="attachment://plot.png"
					)
				except Exception as e:
					print("t!clan error")
					print(e)
				plt.clf()
			except Exception as e:
				print(e)
				print("daily button fail")
				await self.ctx.send(language[161])
	
			await interaction.response.edit_message(embed=plot, file=chart, view=self)
		async def monthly(interaction: discord.Interaction):
			try:
				language = english
				stuff = await Clans.clanMathMonthTest(self,self.ctx,self.clan,self.year,self.month,self.day,self.hour)
				if stuff is None:
					await ctx.send("Something went wrong, or not enough recent data exists")
					ctx.command.reset_cooldown(ctx)
					return
				x = stuff[2]
				times = sorted(stuff[0])
				scores = list()
				for a in times:
					scores.append(stuff[1][stuff[0].index(a)])
				# Make plot for score vs time DAY
				#plt.xlabel(language[157])
				#plt.ylabel(language[158])
				#plt.title(language[159])
				# Make plot for score vs time MONTH
				plt.xlabel(language[178])
				plt.ylabel(language[179])
				plt.title(language[180])
				
				
				plt.plot(times,scores)
				ax = plt.gca()
				# Format for one day
				#myFmt = mdates.DateFormatter('%H:%M')
				# Format for month
				myFmt = mdates.DateFormatter('%m/%d')
				ax.xaxis.set_major_formatter(myFmt)
				if len(times) < 9:
					ax.xaxis.set_major_locator(ticker.LinearLocator(len(times)))
					ax.xaxis.set_minor_locator(ticker.LinearLocator(0))
					ax.yaxis.set_major_locator(ticker.LinearLocator(len(scores)))
				else:
					ax.xaxis.set_major_locator(ticker.LinearLocator(9))
					ax.xaxis.set_minor_locator(ticker.LinearLocator(10))
				# Save plot for discord embed
				data_stream = io.BytesIO()
				plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
				data_stream.seek(0)
				chart = discord.File(data_stream,filename="plot.png")
				# Make and send embed
				try:
					# Month
					plot = discord.Embed(title="{0}".format(self.clan), description=language[181], color=0x03fcc6)
					plot.set_image(
					   url="attachment://plot.png"
					)
				except Exception as e:
					print("t!clan error")
					print(e)
					print(clan)
				plt.clf()
				# Convert database readable clan name back to normal
				clan = clan.replace('PERIOD5', '.')
				clan = clan.replace('DOLLAR5', '$')
				clan = clan.replace('HTAG5', '#')
				clan = clan.replace('LBRACKET5', '[')
				clan = clan.replace('SLASH5', '/')
				clan = clan.replace('RBRACKET5', ']')
				clan = clan.replace('QMARK5', '?')
				
				score = clanData['score']
			except Exception as e:
				print(e)
				print("monthly button fail")
			await interaction.send(language[182].format(clan,score,x))
			# Await button press
			await interaction.response.edit_message(embed=plot, file=chart, view=self)

		# Assign the buttons
		button1.callback = monthly
		self.add_item(button1)
		button2.callback = daily
		self.add_item(button2)

		
async def setup(bot):
	await bot.add_cog(Clans(bot))