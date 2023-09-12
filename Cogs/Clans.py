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
import functools
import typing

#English
textfile = open('/Strings/en-errors.txt', 'r')
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


	@to_thread
	def compareMath(self,snapshot,clan,b):
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
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def compare(self,ctx,*,clans):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		#plt.clf()
		await ctx.send(language[3])
		
		clanList = clans.split()
		if len(clanList) < 2:
			await ctx.send("Minimum clans is 2, please try again.")
			# May need to change to self.reset, unsure for cogs
			ctx.command.reset_cooldown(ctx)
			return
		if len(clanList) > 5:
			await ctx.send("Maximum clans is 5, please try again.")
			ctx.command.reset_cooldown(ctx)
			return
		# $5 Patrons, 6 months instead of 1 week
		if(user == 746994669715587182 or user == 138752093308583936 or user == 681457461441593371):
			timeDif = timedelta(180)
		# $10 Patrons, 1 year
		elif(user == 314969222516047872):
			timeDif = timedelta(360)
		# $1 Patrons, 1 month
		elif(user == 205367377506992128):
			timeDif = timedelta(31)
		else:
			# Set times to search back 3 weeks
			timeDif = timedelta(21)
		newTime = ctx.message.created_at
		oldTime = newTime - timeDif
		newTime = newTime + timedelta(1)
		# Make plot for score vs time
		fig1, ax1 = plt.subplots()
		#print(ax1.lines)
		if ax1.get_xlabel == language[157]:
			print("Testing")
			fig2, ax2 = plt.subplots()
			figure = fig2
			axe = ax2
		else:
			figure = fig1
			axe = ax1
		axe.set_title(language[169])
		axe.set_xlabel(language[157])
		axe.set_ylabel(language[158])
		#figure.title(language[169])
		myFmt = mdates.DateFormatter('%m/%d')
		axe.xaxis.set_major_formatter(myFmt)
		axe.xaxis.set_major_locator(ticker.LinearLocator(9))
		axe.xaxis.set_minor_locator(ticker.LinearLocator(10))
		# Loop through each clan name given
		b = 1
		ref = db.reference('gameData4')
		ref5 = db.reference('gameData5')
		ref6 = db.reference('gameData6')
		ref7 = db.reference('gameData7')
		snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot5 = ref5.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot6 = ref6.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot7 = ref7.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot = list(snapshot.items())
		snapshot6 = list(snapshot6.items())
		snapshot5 = list(snapshot5.items())
		snapshot7 = list(snapshot7.items())
		snapshot = snapshot + snapshot5 + snapshot6 + snapshot7
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
					stuff = await self.compareMath(snapshot,clan,b)
					if b == 1:
						pF = stuff[2]
						mF = stuff[3]
						gF = stuff[4]
					if b == 2:
						pS = stuff[2]
						mS = stuff[3]
						gS = stuff[4]
					if b == 3:
						pT = stuff[2]
						mT = stuff[3]
						gT = stuff[4]
					if b == 4:
						pR = stuff[2]
						mR = stuff[3]
						gR = stuff[4]
					b += 1
					axe.plot(stuff[0],stuff[1],label=clan)
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
			# Make and send embed
			plot = discord.Embed(title="{0}".format(clans), description=language[163], color=0x03fcc6)
			plot.set_image(
			   url="attachment://plot.png"
			)
			await ctx.send(embed=plot, file=chart)
			try:
				await ctx.send(language[4].format(clanList[0],pF,mF,gF))
				await ctx.send(language[4].format(clanList[1],pS,mS,gS))
				if b == 4:
					await ctx.send(language[4].format(clanList[2],pT,mT,gT))
				if b >= 5:
					await ctx.send(language[4].format(clanList[3],pR,mR,gR))
			except Exception as e:
				print("t!compare")
				print(e)
				print(ctx.message.guild.name)
				print(ctx.message.guild.id)
			plt.close(figure)
		except Exception as e:
				print(e)
				await ctx.send(language[153])
	#-------------------------------------------------------------------------------
	#----------------------------- Search For Clan  --------------------------------
	#-------------------------------------------------------------------------------
	@to_thread
	def clanMath(self,user,ctx,clan,duration):
		try:
			timeDif = timedelta(duration)
			newTime = ctx.message.created_at
			oldTime = newTime - timeDif
			newTime = newTime + timedelta(1)
			# Get all games from one week ago to present
			ref = db.reference('gameData4')
			ref5 = db.reference('gameData5')
			ref6 = db.reference('gameData6')
			ref7 = db.reference('gameData7')
			snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
			snapshot5 = ref5.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
			snapshot6 = ref6.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
			snapshot7 = ref7.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
			snapshot = list(snapshot.items())
			snapshot5 = list(snapshot5.items())
			snapshot6 = list(snapshot6.items())
			snapshot7 = list(snapshot7.items())
			snapshot = snapshot + snapshot5 + snapshot6 + snapshot7
			games = list()
			for i in range(len(snapshot)):
				if(snapshot[i][1]['Clan'] == clan):
					games.append(snapshot[i])
			x = len(games)
			times = list()
			scores = list()
			for i in range(len(games)):
				temp = games[i][1]['Time'].replace('T',' ')
				try:
					times.append(datetime.fromisoformat(temp))
				except:
					times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
					#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
				scores.append(games[i][1]['Score'])
			return x,times,scores
		except Exception as e:
			print("clanMath error")
			print(e)
			return None
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def clan(self,ctx,clan,duration = None):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		plt.clf()
		# Check for valid duration
		if(duration is not None):
			try:
				# Valid integer check
				duration = int(duration)
				# $5 Patrons, 1 year instead of 3 weeks
				if(user == 746994669715587182 or user == 138752093308583936 or user == 681457461441593371) and (duration >= 360):
					ctx.command.reset_cooldown(ctx)
					await ctx.send("Please select a duration less than or equal to 360")
					return
				# $10 Patrons, 2 years
				elif(user == 314969222516047872) and (duration > 720) :
					ctx.command.reset_cooldown(ctx)
					await ctx.send("Please select a duration less than or equal to 720")
					return
				# $1 Patrons, 6 months
				elif(user == 205367377506992128) and (duration > 180):
					ctx.command.reset_cooldown(ctx)
					await ctx.send("Please select a duration less than or equal to 180")
					return
				elif(duration > 60) and (user != 746994669715587182 and user != 138752093308583936 and user != 681457461441593371 and user != 205367377506992128 and user != 314969222516047872):
					ctx.command.reset_cooldown(ctx)
					await ctx.send("Please select a duration less than or equal to 60")
					return
			except:
				ctx.command.reset_cooldown(ctx)
				await ctx.send("Duration must be a valid positive integer between 1 and 720")
				return
		else:
			duration = 21
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
				try:
					stuff = await self.clanMath(user,ctx,clan,duration)
					if stuff is None:
						await ctx.send("Something went wrong")
						ctx.command.reset_cooldown(ctx)
						return
					x = stuff[0]
					times = stuff[1]
					scores = stuff[2]
					# Make plot for score vs time
					plt.xlabel(language[157])
					plt.ylabel(language[158])
					plt.title(language[159])
					
					
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
					ref = db.reference('gameData4')
					ref5 = db.reference('gameData5')
					ref6 = db.reference('gameData6')
					ref7 = db.reference('gameData7')
					snapshot2 = ref.order_by_child('Clan').equal_to(clan).get()
					snapshot3 = ref5.order_by_child('Clan').equal_to(clan).get()
					snapshot4 = ref6.order_by_child('Clan').equal_to(clan).get()
					snapshot7 = ref7.order_by_child('Clan').equal_to(clan).get()
					snapshot2 = list(snapshot2.items())
					snapshot3 = list(snapshot3.items())
					snapshot4 = list(snapshot4.items())
					snapshot7 = list(snapshot7.items())
					snapshot2 = snapshot2 + snapshot3 + snapshot4 + snapshot7
					y = len(snapshot2)
					ref2.update({
					'wins': y
					})
				# Check for wins2023
				try:
					z = clanData['wins2023']
				except:
					try:
						ref = db.reference('gameData4')
						ref5 = db.reference('gameData5')
						ref6 = db.reference('gameData6')
						ref7 = db.reference('gameData7')
						# Set wins2023 if it does not yet exist
						snapshot3 = ref5.order_by_child('Time').start_at("2022-01-01T00:00:00.000Z").get()
						snapshot4 = ref6.order_by_child('Clan').equal_to(clan).get()
						snapshot7 = ref7.order_by_child('Clan').equal_to(clan).get()
						snapshot3 = list(snapshot3.items())
						snapshot4 = list(snapshot4.items())
						snapshot7 = list(snapshot7.items())
						games = list()
						for i in range(len(snapshot3)):
							if(snapshot3[i][1]['Clan'] == clan):
								games.append(snapshot3[i])
						z = len(snapshot4) + len(snapshot7) + len(games)
						ref2.update({
						'wins2023': z
						})
					except Exception as e:
						print(e)
				
				clan = clan.replace('PERIOD5', '.')
				clan = clan.replace('DOLLAR5', '$')
				clan = clan.replace('HTAG5', '#')
				clan = clan.replace('LBRACKET5', '[')
				clan = clan.replace('SLASH5', '/')
				clan = clan.replace('RBRACKET5', ']')
				clan = clan.replace('QMARK5', '?')
				
				score = clanData['score']
				await ctx.send(language[162].format(clan,score,x,z,y,duration))
		except Exception as e:
			print(e)
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
	#---------------------- Public Top 50 Clans (Non updating) ---------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top50(self,ctx):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		# Get scores
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
	#-------------------------------------------------------------------------------
	#---------------------- Public Top 25 Clans (Non updating) ---------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top25(self,ctx):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		# Get scores
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
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top(self,ctx):
		# Set language
		language = english
		await ctx.send(language[154])
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
	#-------------------------------------------------------------------------------
	#---------------------- Public Top 100 Clans (Non updating) --------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top100(self,ctx):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		# Get scores
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
	#-------------------------------------------------------------------------------
	#----------------------------- Clan Wins Leaderboard ---------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 3600, commands.BucketType.user)
	async def clanboard(self,ctx,clan):
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
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
						name = await self.bot.fetch_user(users2[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg = await ctx.send(embed=ladder)
				# Two Ladders
				elif x <= 50:
					await ctx.send(language[142])
					for i in range(25):
						name = await self.bot.fetch_user(users2[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(x-25):
						name = await self.bot.fetch_user(users2[i+25][0])
						ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg2 = await ctx.send(embed=ladder2)
				# Three Ladders
				elif x <= 75:
					await ctx.send(language[143])
					for i in range(25):
						name = await self.bot.fetch_user(users2[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(25):
						name = await self.bot.fetch_user(users2[i+25][0])
						ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg2 = await ctx.send(embed=ladder2)
					for i in range(x-50):
						name = await self.bot.fetch_user(users2[i+50][0])
						ladder3.add_field(name=language[140].format(i+51,name.name), value=language[141].format(users2[i+50][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg3 = await ctx.send(embed=ladder3)
				# Four Ladders
				elif x <= 100:
					await ctx.send(language[144])
					for i in range(25):
						name = await self.bot.fetch_user(users2[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(25):
						name = await self.bot.fetch_user(users2[i+25][0])
						ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg2 = await ctx.send(embed=ladder2)
					for i in range(25):
						name = await self.bot.fetch_user(users2[i+50][0])
						ladder3.add_field(name=language[140].format(i+51,name.name), value=language[141].format(users2[i+50][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg3 = await ctx.send(embed=ladder3)
					for i in range(x-75):
						name = await self.bot.fetch_user(users2[i+75][0])
						ladder4.add_field(name=language[140].format(i+76,name.name), value=language[141].format(users2[i+75][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg4 = await ctx.send(embed=ladder4)
				# Catch if members is > 100. Four ladder maximum
				else:
					await ctx.send(language[145])
					for i in range(25):
						name = await self.bot.fetch_user(users2[i][0])
						ladder.add_field(name=language[140].format(i+1,name.name), value=language[141].format(users2[i][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg = await ctx.send(embed=ladder)
					for i in range(25):
						name = await self.bot.fetch_user(users2[i+25][0])
						ladder2.add_field(name=language[140].format(i+26,name.name), value=language[141].format(users2[i+25][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg2 = await ctx.send(embed=ladder2)
					for i in range(25):
						name = await self.bot.fetch_user(users2[i+50][0])
						ladder3.add_field(name=language[140].format(i+51,name.name), value=language[141].format(users2[i+50][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg3 = await ctx.send(embed=ladder3)
					for i in range(25):
						name = await self.bot.fetch_user(users2[i+75][0])
						ladder4.add_field(name=language[140].format(i+76,name.name), value=language[141].format(users2[i+75][1]['clans']['{0}'.format(clan)]['wins']), inline=True)
					msg4 = await ctx.send(embed=ladder4)
			except Exception as e:
				await ctx.send(language[146].format('<@138752093308583936>'))
				print("Clanboard command call failed.")
				print(e)
		except:
			await ctx.send(language[147])
	#@commands.command(pass_context = True)
	#@commands.is_owner()
	#async def ryo2(self,ctx,clan):
	#	asyncio.create_task(self.ryo(ctx,clan))
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
		# Set language
		language = english
		# Set user
		user = ctx.message.author.id
		#plt.clf()
		await ctx.send(language[3])
		
		clanList = clans.split()
		if len(clanList) < 2:
			await ctx.send("Minimum clans is 2, please try again.")
			# May need to change to self.reset, unsure for cogs
			ctx.command.reset_cooldown(ctx)
			return
		if len(clanList) > 5:
			await ctx.send("Maximum clans is 5, please try again.")
			ctx.command.reset_cooldown(ctx)
			return
		# Set times to search back 6 months for $5 patrons
		if(user == 746994669715587182 or user == 138752093308583936 or user == 681457461441593371):
			timeDif = timedelta(720)
		else:
		# Set times to search back 3 weeks
			timeDif = timedelta(21)
		newTime = ctx.message.created_at
		oldTime = newTime - timeDif
		newTime = newTime + timedelta(1)
		# Make plot for score vs time
		fig1, ax1 = plt.subplots()
		#print(ax1.lines)
		if ax1.get_xlabel == language[157]:
			print("Testing")
			fig2, ax2 = plt.subplots()
			figure = fig2
			axe = ax2
		else:
			figure = fig1
			axe = ax1
		axe.set_title(language[169])
		axe.set_xlabel(language[157])
		axe.set_ylabel(language[158])
		#figure.title(language[169])
		myFmt = mdates.DateFormatter('%m/%d')
		axe.xaxis.set_major_formatter(myFmt)
		axe.xaxis.set_major_locator(ticker.LinearLocator(9))
		axe.xaxis.set_minor_locator(ticker.LinearLocator(10))
		# Loop through each clan name given
		b = 1
		ref9 = db.reference('gameData')
		ref8 = db.reference('gameData2')
		ref7 = db.reference('gameData3')
		ref = db.reference('gameData4')
		ref5 = db.reference('gameData5')
		ref6 = db.reference('gameData6')
		refGD7 = db.reference('gameData7')
		snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot5 = ref5.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot6 = ref6.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot7 = ref7.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot8 = ref8.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot9 = ref9.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshotGD7 = refGD7.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot = list(snapshot.items())
		snapshot6 = list(snapshot6.items())
		snapshot5 = list(snapshot5.items())
		snapshot7 = list(snapshot7.items())
		snapshot8 = list(snapshot8.items())
		snapshot9 = list(snapshot9.items())
		snapshotGD7 = list(snapshotGD7.items())
		snapshot = snapshot + snapshot5 + snapshot6 + snapshot7 + snapshot8 + snapshot9 + snapshotGD7
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
					stuff = await self.compareMathRyo(snapshot,clan,b)
					if b == 1:
						pF = stuff[2]
						mF = stuff[3]
						gF = stuff[4]
					if b == 2:
						pS = stuff[2]
						mS = stuff[3]
						gS = stuff[4]
					if b == 3:
						pT = stuff[2]
						mT = stuff[3]
						gT = stuff[4]
					if b == 4:
						pR = stuff[2]
						mR = stuff[3]
						gR = stuff[4]
					b += 1
					axe.plot(stuff[0],stuff[1],label=clan)
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
			# Make and send embed
			plot = discord.Embed(title="{0}".format(clans), description=language[163], color=0x03fcc6)
			plot.set_image(
			   url="attachment://plot.png"
			)
			await ctx.send(embed=plot, file=chart)
			try:
				await ctx.send(language[4].format(clanList[0],pF,mF,gF))
				await ctx.send(language[4].format(clanList[1],pS,mS,gS))
				if b == 4:
					await ctx.send(language[4].format(clanList[2],pT,mT,gT))
				if b >= 5:
					await ctx.send(language[4].format(clanList[3],pR,mR,gR))
			except Exception as e:
				print("t!compare")
				print(e)
				print(ctx.message.guild.name)
				print(ctx.message.guild.id)
			plt.close(figure)
		except Exception as e:
				print(e)
				await ctx.send(language[153])
		
async def setup(bot):
	await bot.add_cog(Clans(bot))