import discord, firebase_admin, discord.utils
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime
from datetime import datetime, timedelta
from discord.ext.commands import CommandNotFound, MissingPermissions, MessageNotFound, NotOwner, BotMissingPermissions, CommandOnCooldown, MissingRequiredArgument

#English
textfile = open('Strings/en-errors.txt', 'r')
english = textfile.read().splitlines()
textfile.close()

class Error(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		error = getattr(error, 'original', error)
		# Get user ID
		user = ctx.author.id
		# Set language
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
				return await ctx.send(language[3].format(time))
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
		else:
			print(error)
async def setup(bot):
	await bot.add_cog(Error(bot))