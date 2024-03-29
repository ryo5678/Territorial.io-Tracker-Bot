import discord, asyncio, firebase_admin, requests, io, re, discord.utils
from discord.ext import commands
from discord.ext.commands import bot, ExtensionAlreadyLoaded

class Switch(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Help Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def helpSwitch(self,ctx):
		try:
			await self.bot.load_extension("Help")
			await ctx.send("Help is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Help")
			await ctx.send("Help is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Clans Cog ---------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def clanSwitch(self,ctx):
		try:
			await self.bot.load_extension("Clans")
			await ctx.send("Clans is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Clans")
			await ctx.send("Clans is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Profile Cog -------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def profileSwitch(self,ctx):
		try:
			await self.bot.load_extension("Profile")
			await ctx.send("Profile is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Profile")
			await ctx.send("Profile is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Wins Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def winSwitch(self,ctx):
		try:
			await self.bot.load_extension("Wins")
			WinsCog = self.bot.get_cog("Wins")
			WinsCog.bestPlayer.start()
			WinsCog.topPlayer.start()
			WinsCog.userCount.start()
			WinsCog.userStatCheck.start()
			await ctx.send("Wins is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Wins")
			await ctx.send("Wins is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Admin Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def adminSwitch(self,ctx):
		try:
			await self.bot.load_extension("Admin")
			await ctx.send("Admin is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Admin")
			await ctx.send("Admin is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Custom Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def customSwitch(self,ctx):
		try:
			await self.bot.load_extension("Custom")
			await ctx.send("Custom is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Custom")
			await ctx.send("Custom is offline")

async def setup(bot):
	await bot.add_cog(Switch(bot))
	
