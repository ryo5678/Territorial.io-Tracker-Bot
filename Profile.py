import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics, typing, functools
from discord.ext import commands, tasks
from discord.ext.commands import bot
from discord import Embed
from firebase_admin import db
from urllib.request import Request, urlopen
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, ticker as ticker, dates as mdates
from datetime import datetime, timedelta, timezone
from discord.utils import get

class Profile(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# NEW COMMANDS FOR TESTING #
	def to_thread(func: typing.Callable) -> typing.Coroutine:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			return await asyncio.to_thread(func, *args, **kwargs)
		return wrapper
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
	@to_thread
	def playerMath(self,content,iteration):
		# Convert user for database searching
		rep = {".": ",1pd,", "$": ",1ds,", "#": ",1ht,", "[": ",1lb,", "]": ",1rb,", "/": ",1fs,"}
		rep = dict((re.escape(k), v) for k, v in rep.items())
		pattern = re.compile("|".join(rep.keys()))
		score = content[iteration].split(', ')
		name = score[1]
		nameData = pattern.sub(lambda m: rep[re.escape(m.group(0))], name)
		
		# Gather the last 7 days of 1v1 scores
		ref = db.reference('/onevsone')
		scores = ref.order_by_key().limit_to_last(7).get()
		scores = list(scores.items())
		#print(scores[0][0])
		playerData = list()
		# Grab the last 7 days of a specific player
		missing = 0
		for i in range(7):
			try:
				ref = db.reference('/onevsone/{0}/{1}'.format(scores[i][0],nameData))
				player = ref.get()
				playerData.append(player)
				#print(player)
				#print(playerData)
			# Catch when player data is missing for a day
			except:
				if missing == 0:
					missing += 1
		# Loop through and create ranks/times list
		times = []
		ranks = []
		for i in range(len(playerData)):
			temp = playerData[i]['time'].replace('T',' ')
			try:
				ranks.append(playerData[i]['rank'])
			except:
				print("Error in ranks.append")
			try:
				times.append(datetime.fromisoformat(temp))
			except:
				times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S.%f"))
				#times.append(datetime.strptime(temp,"%Y-%m-%d %H:%M:%S"))
		return times, ranks, missing, score, name
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
			iteration = None
			# Create and send embed for player score
			dups = {}
			sheet = discord.Embed(title="Find Player", description=user, color=0x0000FF)
			counter = 0
			for i in range(len(content)):
				if counter < 15:
					text = content[i].split(', ')
					if(user in text[1]):
						iteration = i
						sheet.add_field(name="{0}. {1}".format(text[0],text[1]), value="Score: {0}, Wins: {1}".format(text[2],text[3]), inline=False)
						counter +=1
			await ctx.send(embed=sheet)
			if iteration is None:
				await ctx.send("Player not found.")
				return

			result = await self.playerMath(content,iteration)
			# check if error occured
			if result[2] > 0:
				await ctx.send("Some data was missing or corrupted. Results may not be accurate.")
			
			# Setup graphic for displaying score over time
			plt.clf()
			plt.xlabel("Time")
			plt.ylabel("Rank")
			plt.title("Rank changes over one week.")
			ax = plt.gca()
			myFmt = mdates.DateFormatter('%d')
			ax.xaxis.set_major_formatter(myFmt)
			ax.xaxis.set_major_locator(ticker.LinearLocator(8))
			ax.xaxis.set_minor_locator(ticker.LinearLocator(8))
			plt.plot(result[0],result[1],label=result[4])
			# Post the graphic to discord
			plt.legend(loc="upper right")
			data_stream = io.BytesIO()
			plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
			data_stream.seek(0)
			chart = discord.File(data_stream,filename="plot.png")
			# Make and send embed
			plot = discord.Embed(title="{0}".format(result[4]), description="Rank changes over one week.", color=0x03fcc6)
			plot.set_image(
			   url="attachment://plot.png"
			)
			await ctx.send(embed=plot, file=chart)
			
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
	#-------------------------------------------------------------------------------
	#------------------------------ Add User(s) Points -----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.is_owner()
	async def w(self,ctx,points,*users: discord.Member):
		# Get/Set Language
		LangCog = self.bot.get_cog("LangCog")
		user2 = ctx.message.author.id
		language = LangCog.languagePicker(user2)
		
		# Verify points is an integer
		try:
			int(points)
		except:
			await ctx.send("Please input a valid number for points. Example: t!w 100 @name")
			self.w.reset_cooldown(ctx)
			return
		
		# Verify points is positive
		if int(points) <= 0:
			await ctx.send("You entered an invalid amounts of points.")
			return
		# Verify points is positive
		if int(points) > 9999999999999:
			await ctx.send("You entered an invalid amounts of points.")
			return
		
		# Verify guild/server is setup
		guild_ref = db.reference(f"/ClanData/{ctx.guild.id}")
		if guild_ref.get() is None:
			await ctx.send(f"This server has not setup the points system.")
			return

		# Verify user role
		role_ref = db.reference(f"/ClanData/{ctx.guild.id}/addRole")
		role = get(ctx.guild.roles, id=int(role_ref.get()))
		if role not in ctx.message.author.roles:
			await ctx.send(f"You do not have access to this command. You need the {role.name} role.")
			return
		
		# Initialize variables
		names = list()
		# Get guild reference
		ref = db.reference(f"/ClanData/{ctx.guild.id}")
		# Set provided users new values
		for user in users:
			try:
				# Set references
				user_ref = db.reference(f"/ClanData/{ctx.guild.id}/users/{user.id}")
				points_ref = db.reference(f"/ClanData/{ctx.guild.id}/users/{user.id}/points")
				season_ref = db.reference(f"/ClanData/{ctx.guild.id}/users/{user.id}/seasonPoints")
				interval_ref = db.reference(f"/ClanData/{ctx.guild.id}/season")
				
				# Verify user exits
				if user_ref.get() is None:
					user_ref.set({
						'name': "Placeholder",
						'points': 0,
						'seasonPoints': 0
					})
				# Get season interval
				intervalNumber = [30,7,1]
				intervals = ["Monthly","Weekly","Daily"]
				interval = interval_ref.get()
				interval = intervals[intervalNumber.index(interval)]
				# Get existing points
				points_old = points_ref.get()
				season_old = season_ref.get()
				# Set new points
				points_new = points_old + int(points)
				season_new = season_old + int(points)
				# Verify points is positive
				if points_new < 0:
					points_new = 0
				if season_new < 0:
					season_new = 0
				# Update db
				user_ref.update({
					'points': points_new,
					'seasonPoints': season_new
				})
				# Append user to new list
				names.append("\n" + f"<@{user.id}>" + "\n" + f"Total: {points_old} -> {points_new}" + "\n" + f"{interval}: {season_old} -> {season_new}")
			except Exception as e:
				print(e)
		names = " ".join(names)
		await ctx.send(f"Added {points} to: {names}")
	#-------------------------------------------------------------------------------
	#---------------------------- Remove User(s) Points ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.is_owner()
	async def r(self,ctx,points,*users: discord.Member):
		# Get/Set Language
		LangCog = self.bot.get_cog("LangCog")
		user2 = ctx.message.author.id
		language = LangCog.languagePicker(user2)
		
		# Verify points is an integer
		try:
			int(points)
		except:
			await ctx.send("Please input a valid number for points. Example: t!r 100 @name")
			self.r.reset_cooldown(ctx)
			return
		
		# Verify points is positive
		if int(points) <= 0:
			await ctx.send("You entered an invalid amounts of points.")
			return
		
		# Verify points is positive
		if int(points) > 9999999999999:
			await ctx.send("You entered an invalid amounts of points.")
			return

		# Verify guild/server is setup
		guild_ref = db.reference(f"/ClanData/{ctx.guild.id}")
		if guild_ref.get() is None:
			await ctx.send(f"This server has not setup the points system.")
			return

		# Verify user role
		role_ref = db.reference(f"/ClanData/{ctx.guild.id}/delRole")
		role = get(ctx.guild.roles, id=int(role_ref.get()))
		if role not in ctx.message.author.roles:
			await ctx.send(f"You do not have access to this command. You need the {role.name} role.")
			return
		
		# Initialize variables
		names = list()
		# Get guild reference
		ref = db.reference(f"/ClanData/{ctx.guild.id}")
		# Set provided users new values
		for user in users:
			try:
				# Set references
				user_ref = db.reference(f"/ClanData/{ctx.guild.id}/users/{user.id}")
				points_ref = db.reference(f"/ClanData/{ctx.guild.id}/users/{user.id}/points")
				season_ref = db.reference(f"/ClanData/{ctx.guild.id}/users/{user.id}/seasonPoints")
				interval_ref = db.reference(f"/ClanData/{ctx.guild.id}/season")
				
				# Verify user exits
				if user_ref.get() is None:
					user_ref.set({
						'name': "Placeholder",
						'points': 0,
						'seasonPoints': 0
					})
				# Get season interval
				intervalNumber = [30,7,1]
				intervals = ["Monthly","Weekly","Daily"]
				interval = interval_ref.get()
				interval = intervals[intervalNumber.index(interval)]
				# Get existing points
				points_old = points_ref.get()
				season_old = season_ref.get()
				# Set new points
				points_new = points_old - int(points)
				season_new = season_old - int(points)
				# Verify points is positive
				if points_new < 0:
					points_new = 0
				if season_new < 0:
					season_new = 0
				# Update db
				user_ref.update({
					'points': points_new,
					'seasonPoints': season_new
				})
				# Append user to new list
				names.append("\n" + f"<@{user.id}>" + "\n" + f"Total: {points_old} -> {points_new}" + "\n" + f"{interval}: {season_old} -> {season_new}")
			except Exception as e:
				print(e)
		names = " ".join(names)
		await ctx.send(f"Removed {points} to: {names}")
	#-------------------------------------------------------------------------------
	#---------------------------- Leaderboard for Points ---------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 180, commands.BucketType.user)
	@commands.is_owner()
	async def lb(self,ctx):
		clan_ref = db.reference(f"/ClanData/{ctx.guild.id}/name")
		clan = clan_ref.get()
		users_ref = db.reference(f"/ClanData/{ctx.guild.id}/users")
		users = list(users_ref.get().items()) #users[0][1]["seasonPoints"] #[:-1]
		board = discord.Embed(title=f"{clan} Leaderboard", description="Total Points", color=0x33DDFF)
		count = 0
		#for user in users:
		#	count += 1
		#	id = int(user[0])
		#	board.add_field(name=f"{count}.", value=f"<@{id}> Total: {user[1]['points']} Season: {user[1]['seasonPoints']}", inline=False)
		#await ctx.send(embed=board)
		#for user in users:
		#	count += 1
		#	id = int(user[0])
		#	board.add_field(name=f"{count}.", value=f"<@{id}> {user[1]['points']} Season: {user[1]['seasonPoints']}", inline=False)
		#await ctx.send(embed=board)
		for user in users:
			count += 1
			id = int(user[0])
			board.add_field(name=f" ", value=f"**{count}**. <@{id}> {user[1]['points']}", inline=False)
		view = Total()
		msg = await ctx.send(embed=board,view=view)
	@to_thread
	def testStats(self,old):
		# Get now time
		new = datetime.now()
		# Compare if 24 hours have passed
		diff = new - old
		#print((diff.days*24) + (diff.seconds/3600))
		#print(f"TestStats: old time {old} new time {new}")
		#print(diff.seconds/3600)
		# (diff.days) > 1
		if (diff.seconds) > 100:	
			return True
		else:
			return False
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def stats(self,ctx):
		# Declare references
		interval_ref = db.reference(f"/ClanData/{ctx.guild.id}/season")
		time_ref = db.reference(f"/ClanData/{ctx.guild.id}/timer")
		ref = db.reference(f"/ClanData/{ctx.guild.id}/seasons")
		users_ref = db.reference(f"/ClanData/{ctx.guild.id}/users")
		clan_ref = db.reference(f"/ClanData/{ctx.guild.id}/clan")
		clan = clan_ref.get()
		# Get time
		old = datetime.fromisoformat(time_ref.get())
		# Get users
		users = list(users_ref.get().items()) #users[0][1]["seasonPoints"] #[:-1]
		# Set up string
		times = list()
		totalPoints = 0
		# Make plot for score vs time
		fig3, ax3 = plt.subplots()
		#print(ax3.lines)
		if ax3.get_xlabel == "Seasons":
			print("Testing")
			fig4, ax4 = plt.subplots()
			figure = fig4
			axe = ax4
		else:
			figure = fig3
			axe = ax3
		axe.set_title("{clan} seasons over time")
		axe.set_xlabel("Seasons")
		axe.set_ylabel("Total Points")
		#figure.title(language[169])
		myFmt = mdates.DateFormatter('%m/%d')
		axe.xaxis.set_major_formatter(myFmt)
		#axe.xaxis.set_major_locator(ticker.LinearLocator(9))
		#axe.xaxis.set_minor_locator(ticker.LinearLocator(10))
		try:
			count = 0
			for user in users:
				if count == 0:
					totalPoints += user[1]['seasonPoints']
					times.append(old)
					count += 1
				else:
					totalPoints += user[1]['seasonPoints']
					count += 1
			points = list()
			points.append(totalPoints)
			seasons = ref.get()
			if seasons is not None:
				seasons = list(seasons.items())
				seasonCount = len(seasons)
				count = 0
				for season in seasons:
					totalPoints = 0
					count += 1
					times.append(old - (timedelta(count*30)))
					players = list(season[1].items())
					for player in players:
						totalPoints += player[1]
					points.append(totalPoints)
				
			print(points,times)
			axe.plot(times,points,label=clan)
			axe.legend(loc="upper left")
			# Save plot for discord embed
			data_stream = io.BytesIO()
			figure.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
			data_stream.seek(0)
			chart = discord.File(data_stream,filename="plot.png")
			# Make and send embed
			plot = discord.Embed(title=f"{clan}", description="Season points over time", color=0x03fcc6)
			plot.set_image(
			   url="attachment://plot.png"
			)
			await ctx.send(embed=plot, file=chart)
			plt.close(figure)
		except Exception as e:
			ctx.command.reset_cooldown(ctx)
			print(e)
# View for main leaderboard
class Total(discord.ui.View):
	def __init__(self):
		super().__init__(timeout = None)
		self.add_buttons()
	def add_buttons(self):
		# Declare the buttons
		button1 = discord.ui.Button(label="Previous Page",style=discord.ButtonStyle.grey)
		button2 = discord.ui.Button(label="Season Points",style=discord.ButtonStyle.grey)
		button3 = discord.ui.Button(label="Next Page",style=discord.ButtonStyle.grey)
		async def changeSeason(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
			#print(interaction.message.embeds[0])
			# Get reference
			clan_ref = db.reference(f"/ClanData/{guild.id}/clan")
			clan = clan_ref.get()
			users_ref = db.reference(f"/ClanData/{guild.id}/users")
			users = list(users_ref.get().items())
			count = 1
			# Edit embed
			sheet = discord.Embed(title=f"{clan} Leaderboard", description="Season Points", color=0x33DDFF)
			for user in users:
				id = int(user[0])
				sheet.add_field(name=f" ", value=f"**{count}**. <@{id}> {user[1]['seasonPoints']}", inline=False)
				count += 1
			# Edit the embed
			view = Total()
			await interaction.message.edit(embed=sheet,view=view)
			await interaction.response.defer()
		async def nextPage(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
		async def previousPage(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
		# Assign the buttons
		button1.callback = previousPage
		self.add_item(button1)
		button2.callback = changeSeason
		self.add_item(button2)
		button3.callback = nextPage
		self.add_item(button3)
# View for season version of leaderboard
class Season(discord.ui.View):
	def __init__(self):
		super().__init__(timeout = None)
		self.add_buttons()
	def add_buttons(self):
		# Declare the buttons
		button1 = discord.ui.Button(label="Previous Page",style=discord.ButtonStyle.grey)
		button2 = discord.ui.Button(label="Total Points",style=discord.ButtonStyle.grey)
		button3 = discord.ui.Button(label="Next Page",style=discord.ButtonStyle.grey)
		async def changeTotal(interaction: discord.Interaction):
			try:
				# Get user ID
				user = interaction.user.id
				# Get Guild
				guild = interaction.guild
				#print(interaction.message.embeds[0])
				# Get reference
				clan_ref = db.reference(f"/ClanData/{guild.id}/clan")
				clan = clan_ref.get()
				users_ref = db.reference(f"/ClanData/{guild.id}/users")
				users = list(users_ref.get().items())
				count = 1
				# Edit embed
				sheet = discord.Embed(title=f"{clan} Leaderboard", description="Total Points", color=0x33DDFF)
				for user in users:
					id = int(user[0])
					sheet.add_field(name=f" ", value=f"**{count}**. <@{id}> {user[1]['points']}", inline=False)
					count += 1
				# Edit the embed
				view = Total()
				await interaction.message.edit(embed=sheet,view=view)
				await interaction.response.defer()
			except Exception as e:
				print(e)
				print("changeTotal error")
		async def nextPage(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
		async def previousPage(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
		# Assign the buttons
		button1.callback = previousPage
		self.add_item(button1)
		button2.callback = changeTotal
		self.add_item(button2)
		button3.callback = nextPage
		self.add_item(button3)
async def setup(bot):
	await bot.add_cog(Profile(bot))