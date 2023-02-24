import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands, tasks
from discord.ext.commands import bot
from firebase_admin import db
from urllib.request import Request, urlopen

class Profile(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#------------------------------ PROFILE COMMAND --------------------------------
	#-------------------------------------------------------------------------------
	def profileDisplay(self,ctx,user,user2,username):
		# Get/Set Language
		LangCog = self.bot.get_cog("LangCog")
		language = LangCog.languagePicker(user2)
		# Get user ID
		ref = db.reference('/users/{0}'.format(user))
		info = ref.get()
		
		cw = 0
		wins = []
		points = []
		
		infoList = list(info.items())
		if(infoList[1][1]['currentclan'] == "none"):
			br = infoList[0][1]
			#ovo = infoList[4][1]
			clan = infoList[1][1]['currentclan']
			lang = infoList[2][1]
		else:
			# Need to fix this error at some point, clan field of embed becomes currentClan, 'str' has no attribute 'items' error
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
				#ovo = infoList[4][1]
				lang = infoList[2][1]
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
				#ovo = float(ovo)
				#cw = int(cw)
			except Exception as e:
				print(e)
				print("first")
		try:
			if(lang == None):
				lang = "english"
			guild = ctx.message.guild.id
			# Profile Embed
			sheet = discord.Embed(title=language[129], description=language[130].format(username), color=0x0000FF)
			sheet.add_field(name="Language", value=lang, inline=False)
			sheet.add_field(name=language[131], value=clan, inline=False)
			#sheet.add_field(name=language[132], value=ovo, inline=False)
			sheet.add_field(name=language[133], value=br, inline=False)
			# Loop through all user clans
			for x in range(len(wins)):
				# + language[164].format(points[x])
				sheet.add_field(name=language[134].format(clanList[x]), value=language[164].format(wins[x],points[x]), inline=False)
			return sheet
		except Exception as e:
			print(e)
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def profile(self,ctx, name: discord.Member = None):
		# check if user wants to display self or other
		profile = self.bot.get_cog("Profile")
		user2 = ctx.message.author.id
		if name == None:
			user = ctx.message.author.id
		else:
			user = name.id
		# Get users discord nickname or default name
		guild = ctx.message.guild.id
		guild = self.bot.get_guild(guild)
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
			await ctx.send(embed=profile.profileDisplay(ctx,user,user2,username))
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
				await ctx.send(embed=profile.profileDisplay(ctx,user,user2,username))
			else:
				# Display profile
				await ctx.send(embed=profile.profileDisplay(ctx,user,user2,username))
	#-------------------------------------------------------------------------------
	#--------------------------------- SET Clan ------------------------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def setclan(self,ctx,name):
		# Get user ID and guild ID
		profile = self.bot.get_cog("Profile")
		user2 = ctx.message.author.id
		user = ctx.message.author.id
		guild = ctx.message.guild.id
		# Convert clan name for database
		clan = name.upper()
		clan = clan.replace('.', 'period5')
		clan = clan.replace('$', 'dollar5')
		clan = clan.replace('#', 'htag5')
		clan = clan.replace('[', '')
		clan = clan.replace('/', 'slash5')
		clan = clan.replace(']', '')
		clan = clan.replace('?', 'qmark5')
		
		guild = self.bot.get_guild(guild)
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
			'onevsone': 0
			})
			await ctx.send(embed=profile.profileDisplay(ctx,user,user2,username))
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
				'currentclan': clan
				})
			else:
				fRef.update({
				'currentclan': clan
				})
			await ctx.send(embed=profile.profileDisplay(ctx,user,user2,username))
	
	#-------------------------------------------------------------------------------
	#--------------------------- Find a user's 1v1 stats ---------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def findPlayer(self,ctx,*,user):
		try:
			await ctx.send("If you don't get the expected results, make sure you include things like clan tags. The name should match exactly with what is shown in territorial.")
			
			# Download the webpage as text
			req = Request(
				url = "https://territorial.io/players",
				headers={'User-Agent': 'Mozilla/5.0'}
			)
			with urlopen(req) as webpage:
				content = webpage.read().decode()
			# print(content)
			# Create db reference and convert string to list
			content = content.splitlines()
			content.pop(3)
			content.pop(2)
			content.pop(1)
			content.pop(0)
			
			dups = {}
			sheet = discord.Embed(title="Find Player", description=user, color=0x0000FF)
			for i in range(len(content)):
				text = content[i].split(', ')
				if(user in text[1]):
					sheet.add_field(name="{0}. {1}".format(text[0],text[1]), value="Score: {0}, Wins: {1}".format(text[2],text[3]), inline=False)
			await ctx.send(embed=sheet)
			
		except Exception as e:
			print("Error in findPlayer command")
			print(e)
	#-------------------------------------------------------------------------------
	#--------------------------- Display Live Top 100 ------------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def topPlayers(self,ctx):
		try:
			# Download the webpage as text
			req = Request(
				url = "https://territorial.io/players", 
				headers={'User-Agent': 'Mozilla/5.0'}
			)
			with urlopen(req) as webpage:
				content = webpage.read().decode()
			# print(content)
			# Create db reference and convert string to list
			content = content.splitlines()
			content.pop(3)
			content.pop(2)
			content.pop(1)
			content.pop(0)
			
			dups = {}
			sheet = discord.Embed(title="Top 100 Players", description=" ", color=0x0000FF)
			for i in range(100):
				text = content[i].split(', ')
				temp = text[1]
				if temp not in dups:
					# Store index of first occurrence and occurrence value
					dups[temp] = [i, 1]
				else:
					#print(dups[temp][1])
					# Special case for first occurrence
					if dups[temp][1] != 1:
						# Use stored occurrence value
						text[1] = str(temp) + str(dups[temp][1])
					# Increment occurrence value, index value doesn't matter anymore
					dups[temp][1] += 1
				sheet.add_field(name="{0}. {1}".format(text[0],text[1]), value="Score: {0}, Wins: {1}".format(text[2],text[3]), inline=False)
			await ctx.send(embed=sheet)
		except Exception as e:
			print("An erorr occured in topPlayers")
			print(e)
	
async def setup(bot):
	await bot.add_cog(Profile(bot))