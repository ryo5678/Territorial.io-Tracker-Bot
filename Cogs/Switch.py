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
			await self.bot.load_extension("Cogs.Help")
			await ctx.send("Help is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Cogs.Help")
			await ctx.send("Help is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Error Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def errorSwitch(self,ctx):
		try:
			await self.bot.load_extension("Cogs.Error")
			await ctx.send("Error is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Cogs.Error")
			await ctx.send("Error is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Clans Cog ---------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def clanSwitch(self,ctx):
		try:
			await self.bot.load_extension("Cogs.Clans")
			await ctx.send("Clans is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Cogs.Clans")
			await ctx.send("Clans is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Profile Cog -------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def profileSwitch(self,ctx):
		try:
			await self.bot.load_extension("Cogs.Profile")
			await ctx.send("Profile is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Cogs.Profile")
			await ctx.send("Profile is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Wins Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def winSwitch(self,ctx):
		try:
			await self.bot.load_extension("Cogs.Wins")
			WinsCog = self.bot.get_cog("Cogs.Wins")
			#WinsCog.bestPlayer.start()
			#WinsCog.topPlayer.start()
			#WinsCog.userCount.start()
			#WinsCog.userStatCheck.start()
			await ctx.send("Wins is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Cogs.Wins")
			await ctx.send("Wins is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Admin Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def adminSwitch(self,ctx):
		try:
			await self.bot.load_extension("Cogs.Admin")
			await ctx.send("Admin is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Cogs.Admin")
			await ctx.send("Admin is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Custom Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def customSwitch(self,ctx):
		try:
			await self.bot.load_extension("Cogs.Custom")
			await ctx.send("Custom is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Cogs.Custom")
			await ctx.send("Custom is offline")

async def setup(bot):
	await bot.add_cog(Switch(bot))
	
