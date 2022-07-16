import discord, firebase_admin, discord.utils
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime
from datetime import datetime, timedelta
from discord.ext.commands import CommandNotFound, MissingPermissions, MessageNotFound, NotOwner, BotMissingPermissions, CommandOnCooldown, MissingRequiredArgument

#Russian
textfile = open('ru-errors.txt', 'r', encoding="utf-8")
russian = textfile.read().splitlines()
textfile.close()
#English
textfile = open('en-errors.txt', 'r')
english = textfile.read().splitlines()
textfile.close()
#French
textfile = open('fr-errors.txt', 'r', encoding="utf-8")
french = textfile.read().splitlines()
textfile.close()
#Turkish
textfile = open('tr-errors.txt', 'r', encoding="utf8")
turkish = textfile.read().splitlines()
textfile.close()


class Error(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		error = getattr(error, 'original', error)
		#language = english
		# Get user ID
		user = ctx.author.id
		# Set reference
		ref = db.reference('/users/{0}/lang'.format(user))
		if ref.get() == "french":
			language = french
			s = "D\u00e8"
			a = "\u00e8"
		if ref.get() == "english":
			language = english
		if ref.get() == "russian":
			language = russian
		if ref2.get() == "turkish":
			language = turkish
		if ref.get() == None:
			language = english
		# Catch CommandNotFound Error
		if isinstance(error, discord.ext.commands.CommandNotFound):
			try:
				return await ctx.send(language[4])
			except:
				return
		# Catch MessageNotFound Error
		if isinstance(error, discord.ext.commands.MessageNotFound):
			try:
				return await ctx.send(language[6])
			except:
				try:
					return await ctx.author.send(language[6])
				except:
					return
		# Catch NotOwner Error
		if isinstance(error, discord.ext.commands.NotOwner):
			try:
				return await ctx.send(language[2])
			except:
				try:
					return await ctx.author.send(language[2])
				except:
					return
		# Catch Cooldown Error
		if isinstance(error, discord.ext.commands.CommandOnCooldown):
			error = str(error)
			error = error.split()
			time = error[len(error) - 1]
			try:
				await ctx.send(language[3].format(time))
			except Exception as e:
				print(e)
				try:
					return await ctx.author.send(language[3].format(time))
				except:
					return
		# Catch MissingPermissions Error
		if isinstance(error, discord.ext.commands.MissingPermissions):
			try:
				return await ctx.send(language[5])
			except:
				try:
					return await ctx.author.send(language[5])
				except:
					return
		# Catch MissingPermissions Error
		if isinstance(error, discord.ext.commands.MissingRequiredArgument):
			try:
				command = str(ctx.invoked_with)
				command = command.lower()
				#print(command)
			except Exception as e:
				print(e)
			if(command == 'setsolo'):
				try:
					return await ctx.send(language[7] + '\n' + language[8])
				except:
					try:
						return await ctx.author.send(language[7] + '\n' + language[8])
					except:
						return
			if(command == 'setclan'):
				try:
					return await ctx.send(language[9])
				except:
					try:
						return await ctx.author.send(language[9])
					except:
						return
			if(command == 'removewins'):
				try:
					return await ctx.send(language[10] + '\n' + language[11] + '\n' + language[12])
				except:
					try:
						return await ctx.send(language[10] + '\n' + language[11] + '\n' + language[12])
					except:
						return
			if(command == 'setlanguage'):
				try:
					return await ctx.send(language[13])
				except:
					try:
						return await ctx.send(language[13])
					except:
						return
			if(command == 'clanboard'):
				try:
					return await ctx.send(language[9])
				except:
					try:
						return await ctx.send(language[9])
					except:
						return
			if(command == 'clan'):
				try:
					return await ctx.send(language[9])
				except:
					try:
						return await ctx.send(language[9])
					except:
						return
		# Catch BotMissingPermissions Error
		if isinstance(error, discord.ext.commands.BotMissingPermissions):
			try:
				return await ctx.send(language[0])
			except:
				try:
					return await ctx.author.send(language[0])
				except:
						print("{0} id {1} name ".format(ctx.message.guild.id,ctx.message.guild.name))
						return
def setup(bot):
	bot.add_cog(Error(bot))
