import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime
from datetime import datetime, timedelta
import numpy as np
from matplotlib import pyplot as plt, ticker as ticker, dates as mdates
from collections import defaultdict

class Clans(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#------------------------------ Compare Clans Command --------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def compare(self,ctx,*,clans):
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
		plt.clf()
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
			timeDif = timedelta(180)
		else:
		# Set times to search back 3 weeks
			timeDif = timedelta(21)
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
		ref = db.reference('gameData4')
		ref5 = db.reference('gameData5')
		ref6 = db.reference('gameData6')
		snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot5 = ref5.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot6 = ref6.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
		snapshot = list(snapshot.items())
		snapshot6 = list(snapshot6.items())
		snapshot5 = list(snapshot5.items())
		snapshot = snapshot + snapshot5 + snapshot6
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
				ctx.command.reset_cooldown(ctx)
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
				await ctx.send(language[153])
	#-------------------------------------------------------------------------------
	#----------------------------- Search For Clan  --------------------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def clan(self,ctx,clan):
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
		plt.clf()
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
				# $5 Patron, 6 months instead of 1 week
				if(user == 746994669715587182 or user == 138752093308583936 or user == 681457461441593371):
					timeDif = timedelta(180)
				else:
				# Set times to search back 3 weeks
					timeDif = timedelta(21)
				newTime = ctx.message.created_at
				oldTime = newTime - timeDif
				newTime = newTime + timedelta(1)
				# Get all games from one week ago to present
				ref = db.reference('gameData4')
				ref5 = db.reference('gameData5')
				ref6 = db.reference('gameData6')
				snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot5 = ref5.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot6 = ref6.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot = list(snapshot.items())
				snapshot5 = list(snapshot5.items())
				snapshot6 = list(snapshot6.items())
				snapshot = snapshot + snapshot5 + snapshot6
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
							times.append(datetime.fromisoformat(temp))
						except:
							times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
							#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
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
					snapshot3 = ref5.order_by_child('Clan').equal_to(clan).get()
					snapshot4 = ref6.order_by_child('Clan').equal_to(clan).get()
					snapshot2 = list(snapshot2.items())
					snapshot3 = list(snapshot3.items())
					snapshot4 = list(snapshot4.items())
					snapshot2 = snapshot2 + snapshot3 + snapshot4
					y = len(snapshot2)
					ref2.update({
					'wins': y
					})
				# Check for wins2023
				try:
					z = clanData['wins2023']
				except:
					try:
						# Set wins2023 if it does not yet exist
						snapshot3 = ref5.order_by_child('Time').start_at("2022-01-01T00:00:00.000Z").get()
						snapshot4 = ref6.order_by_child('Clan').equal_to(clan).get()
						snapshot3 = list(snapshot3.items())
						snapshot4 = list(snapshot4.items())
						games = list()
						for i in range(len(snapshot3)):
							if(snapshot3[i][1]['Clan'] == clan):
								games.append(snapshot3[i])
						z = len(snapshot4) + len(games)
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
				await ctx.send(language[162].format(clan,score,x,z,y))
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
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
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
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
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
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
		await ctx.send(language[154])

	#-------------------------------------------------------------------------------
	#---------------------- Public Top 100 Clans (Non updating) --------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def top100(self,ctx):
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
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
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
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
	@commands.command(pass_context = True)
	@commands.is_owner()
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def ryo(self,ctx,clan):
		LangCog = self.bot.get_cog("LangCog")
		# Get/Set Language
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
		plt.clf()
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
				# $5 Patron, 6 months instead of 1 week
				if(user == 746994669715587182 or user == 138752093308583936 or user == 681457461441593371):
					timeDif = timedelta(720)
				else:
				# Set times to search back 3 weeks
					timeDif = timedelta(21)
				newTime = ctx.message.created_at
				oldTime = newTime - timeDif
				newTime = newTime + timedelta(1)
				# Get all games from one week ago to present
				gd1 = db.reference('gameData')
				gd2 = db.reference('gameData2')
				gd3 = db.reference('gameData3')
				ref = db.reference('gameData4')
				ref5 = db.reference('gameData5')
				snapshot = ref.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot5 = ref5.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot = list(snapshot.items())
				snapshot5 = list(snapshot5.items())
				snapshot2 = gd1.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot2 = list(snapshot2.items())
				snapshot3 = gd2.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot3 = list(snapshot3.items())
				snapshot4 = gd3.order_by_child('Time').start_at(str(oldTime)).end_at(str(newTime)).get()
				snapshot4 = list(snapshot4.items())
				snapshot = snapshot + snapshot5 + snapshot2 + snapshot3 + snapshot4
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
							times.append(datetime.fromisoformat(temp))
						except:
							times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
							#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
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
					snapshot3 = ref5.order_by_child('Clan').equal_to(clan).get()
					snapshot2 = list(snapshot2.items())
					snapshot3 = list(snapshot3.items())
					snapshot2 = snapshot2 + snapshot3
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
				await ctx.send(language[153])
			except:
				try:
					await ctx.author.send(language[153])
				except Exception as e:
					print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
					print(e)
async def setup(bot):
	await bot.add_cog(Clans(bot))