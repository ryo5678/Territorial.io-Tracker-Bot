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

#English
textfile = open('/Strings/en-errors.txt', 'r')
english = textfile.read().splitlines()
textfile.close()

class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# NEW COMMANDS FOR TESTING #
	def to_thread(func: typing.Callable) -> typing.Coroutine:
		@functools.wraps(func)
		async def wrapper(*args, **kwargs):
			return await asyncio.to_thread(func, *args, **kwargs)
		return wrapper
	
	
	#-------------------------------------------------------------------------------
	#------------------------------ Add User(s) Points -----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.is_owner()
	async def w(self,ctx,points,*users: discord.Member):
		# Set language
		language = english
		
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
		# Set language
		language = english
		
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
		# Set language
		language = english
		
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
		# Set language
		language = english
	
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
		button1 = discord.ui.Button(label="Previous Page",style=discord.ButtonStyle.grey,disabled = True)
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
			#view = Total()
			#await interaction.message.edit(embed=sheet,view=view)
			await interaction.message.edit(embed=sheet)
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
	# End Poll Button
	#@discord.ui.button(label="End Poll",style=discord.ButtonStyle.red)
	#async def endPoll(self, interaction: discord.Interaction, child: discord.ui.Button):
	#	for child in self.children:
	#		child.disabled=True
	#	await interaction.response.edit_message(view=self)
async def setup(bot):
	await bot.add_cog(Profile(bot))