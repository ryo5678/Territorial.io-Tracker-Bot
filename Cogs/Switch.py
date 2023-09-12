import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot, ExtensionAlreadyLoaded

class Switch(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Lang Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def langSwitch(self,ctx):
		try:
			global LangCog
			await self.bot.load_extension("LangCog")
			LangCog = self.bot.get_cog("LangCog")
			await ctx.send("Language is online")
			return LangCog
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("LangCog")
			await ctx.send("Language is offline")	
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
			await ctx.send("Wins is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Wins")
			await ctx.send("Wins is offline")
	#-------------------------------------------------------------------------------
	#----------------------------- Load/Unload Poll Cog ----------------------------
	#-------------------------------------------------------------------------------
	@commands.command(pass_context = True)
	@commands.is_owner()
	async def pollSwitch(self,ctx):
		try:
			await self.bot.load_extension("Poll")
			PollCog = self.bot.get_cog("Poll")
			await PollCog.pollStart()
			await ctx.send("Poll is online")
		except commands.ExtensionAlreadyLoaded:
			await self.bot.unload_extension("Poll")
			await ctx.send("Poll is offline")
async def setup(bot):
	await bot.add_cog(Switch(bot))
	
