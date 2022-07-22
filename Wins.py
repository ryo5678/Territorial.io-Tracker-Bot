import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime

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
		
def setup(bot):
	bot.add_cog(Wins(bot))

