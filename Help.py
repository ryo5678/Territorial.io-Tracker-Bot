import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot

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
		# Get/Set Language
		LangCog = self.bot.get_cog("LangCog")
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
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
		# Get/Set Language
		LangCog = self.bot.get_cog("LangCog")
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
		# Embed
		sheet2 = discord.Embed(title=language[47], description=language[48], color=0x0000FF)
		sheet2.add_field(name=language[49], value=language[50], inline=False)
		sheet2.add_field(name=language[51], value=language[52], inline=False)
		sheet2.add_field(name=language[53], value=language[54] + '\n' + language[55], inline=False)
		sheet2.add_field(name=language[10], value=language[11] + '\n' + language[12], inline=False)
		sheet2.add_field(name=language[56], value=language[57] + '\n' + language[58], inline=False)
		sheet2.add_field(name=language[19], value=language[20] + '\n' + language[21], inline=False)
		sheet2.add_field(name=language[22], value=language[23] + '\n' + language[24], inline=False)
		sheet2.add_field(name=language[13], value=language[14] + '\n' + language[15], inline=False)
		sheet2.add_field(name=language[59], value=language[60] + '\n' + language[61] + '\n' + language[62], inline=False)
		sheet2.add_field(name=language[63], value=language[64] + '\n' + language[65], inline=False)
		sheet2.add_field(name=language[66], value=language[67], inline=False)
		sheet2.add_field(name=language[32], value=language[33], inline=False)
		sheet2.add_field(name=language[35], value=language[36], inline=False)
		sheet2.add_field(name=language[25], value=language[26] + '\n' + language[27], inline=False)
		sheet2.add_field(name=language[68], value=language[69] + '\n' + language[70] + '\n' + language[71], inline=False)
		sheet2.add_field(name=language[72], value=language[73] + '\n' + language[74], inline=False)
		sheet2.add_field(name=language[75], value=language[76], inline=False)
		sheet2.add_field(name=language[77], value=language[78], inline=False)
		await ctx.send(embed=sheet2)
	#-------------------------------------------------------------------------------
	#------------------------------ SETUP Command ----------------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.has_permissions(administrator=True)
	@commands.cooldown(1, 1800, commands.BucketType.user)
	async def setup(self,ctx):
		# Get/Set Language
		LangCog = self.bot.get_cog("LangCog")
		user = ctx.message.author.id
		language = LangCog.languagePicker(user)
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
	@commands.command(pass_context = True)
	@commands.cooldown(1, 300, commands.BucketType.user)
	async def status(self,ctx):
		stat = discord.Embed(title="Bot Status",description="What should be working.", color=0x0000FF)
		try:
			await self.bot.load_extension("Error")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Error Handling", value="Online", inline=False)
			else:
				stat.add_field(name="Error Handling", value="Offline", inline=False)
		try:
			await self.bot.load_extension("LangCog")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Language Translation (Effects most commands)", value="Online", inline=False)
			else:
				stat.add_field(name="Language Translation (Effects most commands)", value="Offline", inline=False)
		try:
			await self.bot.load_extension("Clans")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Clans commands", value="Online", inline=False)
			else:
				stat.add_field(name="Clans commands", value="Offline", inline=False)
		try:
			await self.bot.load_extension("Wins")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Win Tracking", value="Online", inline=False)
			else:
				stat.add_field(name="Win Tracking", value="Offline", inline=False)
		try:
			await self.bot.load_extension("Poll")
		except Exception as e:
			if isinstance(e,discord.ext.commands.ExtensionAlreadyLoaded):
				stat.add_field(name="Poll System", value="Online", inline=False)
			else:
				stat.add_field(name="Poll System", value="Offline", inline=False)
		await ctx.send(embed = stat)
async def setup(bot):
	await bot.add_cog(Help(bot))