import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot

#English
textfile = open('Strings/en-strings.txt', 'r')
english = textfile.read().splitlines()
textfile.close()

class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#------------------------------ GET Admin Commands -----------------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.has_permissions(administrator=True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def ahelp(self,ctx):
		# Set language
		language = english
		# Embed
		sheet = discord.Embed(title=language[5], description=language[6], color=0x0000FF)
		sheet.add_field(name=language[7], value=language[8] + '\n' + language[9], inline=False)
		sheet.add_field(name=language[10], value=language[11] + '\n' + language[12], inline=False)
		sheet.add_field(name=language[13], value=language[14] + '\n' + language[15], inline=False)
		sheet.add_field(name=language[16], value=language[17] + '\n' + language[18], inline=False)
		sheet.add_field(name=language[19], value=language[20] + '\n' + language[21], inline=False)
		sheet.add_field(name=language[22], value=language[23] + '\n' + language[24], inline=False)
		sheet.add_field(name=language[25], value=language[26] + '\n' + language[27], inline=False)
		sheet.add_field(name=language[28], value=language[29] + '\n' + language[30] + '\n' + language[31], inline=False)
		sheet.add_field(name=language[32], value=language[33] + '\n' + language[34], inline=False)
		sheet.add_field(name=language[35], value=language[36] + '\n' + language[37], inline=False)
		sheet.add_field(name=language[38], value=language[39] + '\n' + language[40] + '\n' + language[41], inline=False)
		sheet.add_field(name=language[42], value=language[43] + '\n' + language[44] + '\n' + language[45], inline=False)
		await ctx.send(embed=sheet)
	#-------------------------------------------------------------------------------
	#------------------------------ HELP Override -----------------------------
	#-------------------------------------------------------------------------------	
	@commands.command(pass_context = True)
	@commands.cooldown(1, 600, commands.BucketType.user)
	async def help(self,ctx):
		# Set language
		language = english
		# Embed
		sheet2 = discord.Embed(title=language[47], description=language[48], color=0x0000FF)
		# Policy
		sheet2.add_field(name=language[22], value=language[49] + '\n' + language[50] + 
		'\n' + language[51] + '\n' + language[52] + '\n' + '\u200b', inline=False)
		# Language Commands
		sheet2.add_field(name=language[23], value=language[77] + '\n' + language[78] + '\n' + '\u200b', inline=False)
		# Clan Search Commands
		sheet2.add_field(name=language[24], value=language[56] + '\n' + language[57] + '\n' + language[58] + '\n' + language[72] + '\n' + language[73] + '\n' + language[74] + '\n' + language[66] + '\n' + language[67] + '\n' + language[32] + '\n' + language[33] + '\n' + language[35] + '\n' + language[36] + '\n' + '\u200b', inline=False)
		# Player Search Commands
		sheet2.add_field(name=language[27], value=language[16] + '\n' + language[17] + '\n' + language[18] + '\n' + language[42] + '\n' + language[43] + '\n' + '\u200b', inline=False)
		# Discord Profile Commands
		sheet2.add_field(name=language[25], value=language[10] + '\n' + language[11] + '\n' + language[12] + '\n' + language[19] + '\n' + language[20] + '\n' + language[21] + '\n' + language[13] + '\n' + language[14] + '\n' + language[15] + '\n' + language[59] + '\n' + language[60] + '\n' + language[61] + '\n' + language[62] + '\n' + '\u200b', inline=False)
		# Data Commands
		sheet2.add_field(name=language[26], value=language[53] + '\n' + language[54] + '\n' + language[55] + '\n' + language[68] + '\n' + language[69] + '\n' + language[70] + '\n' + language[71] + '\n' + '\u200b', inline=False)
		sheet2.add_field(name=language[75], value=language[76], inline=False)
		await ctx.send(embed=sheet2)
	#-------------------------------------------------------------------------------
	#------------------------------ SETUP Command ----------------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.has_permissions(administrator=True)
	@commands.cooldown(1, 1800, commands.BucketType.user)
	async def setup(self,ctx):
		# Set language
		language = english
		# Send text wall 
		await ctx.send(language[79] + '\n' + language[80] + '\n' + language[81])
		await asyncio.sleep(5)
		await ctx.send(language[82] + '\n' + language[83] + '\n' + language[84] + '\n' + language[85] + '\n' + language[86])
		await asyncio.sleep(10)
		await ctx.send(language[82] + '\n' + language[87] + '\n' + language[88] + '\n' + language[89])
		await asyncio.sleep(15)
		await ctx.send(language[82] + '\n' + language[90] + '\n' + language[91] + '\n' + language[92] + '\n' + language[93] + '\n' + language[94])
		await asyncio.sleep(20)
		await ctx.send(language[82] + '\n' + language[95] + '\n' + language[96])
		await asyncio.sleep(10)
		await ctx.send(language[82] + '\n' + language[97] + '\n' + language[98] + '\n' + language[99] + '\n' + language[100])
		await asyncio.sleep(20)
		await ctx.send(language[82] + '\n' + language[101] + '\n' + language[102] + '\n' + language[103] + '\n' + language[104] + '\n' + language[105])
		
	#-------------------------------------------------------------------------------
	#------------------------------ Check Cog Status -------------------------------
	#-------------------------------------------------------------------------------	
	# Not functioning correctly, offline cogs do not show up at all.
	@commands.command(pass_context = True)
	@commands.cooldown(1, 300, commands.BucketType.user)
	async def status(self,ctx):
		stat = discord.Embed(title="Bot Status",description="What should be working.", color=0x0000FF)
		# Error
		try:
			await self.bot.load_extension("Error")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Error Handling", value="Online", inline=False)
			else:
				stat.add_field(name="Error Handling", value="Offline", inline=False)
		# Clans
		try:
			await self.bot.load_extension("Clans")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Clans commands", value="Online", inline=False)
			else:
				stat.add_field(name="Clans commands", value="Offline", inline=False)
		# Wins
		try:
			await self.bot.load_extension("Wins")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Win Tracking", value="Online", inline=False)
			else:
				stat.add_field(name="Win Tracking", value="Offline", inline=False)
		# Admin
		try:
			await self.bot.load_extension("Admin")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Admin commands", value="Online", inline=False)
			else:
				stat.add_field(name="Admin commands", value="Offline", inline=False)
		# Custom
		try:
			await self.bot.load_extension("Custom")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Custom commands", value="Online", inline=False)
			else:
				stat.add_field(name="Custom commands", value="Offline", inline=False)
		# Profile
		try:
			await self.bot.load_extension("Profile")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Profile commands", value="Online", inline=False)
			else:
				stat.add_field(name="Profile commands", value="Offline", inline=False)
		await ctx.send(embed = stat)
async def setup(bot):
	await bot.add_cog(Help(bot))