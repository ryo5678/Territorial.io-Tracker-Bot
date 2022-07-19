import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime

class Poll(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.command(pass_context = True)
	@commands.has_permissions(administrator=True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def poll(self,ctx):
		def check(c):
			return c.channel == ctx.author.dm_channel
		await ctx.author.send("Please enter the question.")
		try:
			question = await self.bot.wait_for('message', check=check)
			question = question.content
			await ctx.author.send("Please enter the response options seperated by a comma. Example: Blue, Red, Yellow")
			answers = await self.bot.wait_for('message', check=check)
			answers = answers.content
			#await ctx.author.send("Please enter the time limit.")
			#timer = await self.bot.wait_for('message', check=check)
			#timer = timer.content
			
			answers = answers.split(',')
			
			sheet = discord.Embed(title=ctx.author.name, description="**{0}**".format(question), color=0x0000FF)
			a = ""
			progress = "```"
			votes = 0
			for i in range(len(answers)):
				match i:
					case 0:
						emote = ":one:"
					case 1:
						emote = ":two:"
					case 2:
						emote = ":three:"
					case 3:
						emote = ":four:"
				a += emote + answers[i] + "\n"
				progress += "{} | bar goes here | % here \n".format(i+1)
			progress += "```"
			sheet.add_field(name="\u200b", value=a, inline=False)
			sheet.add_field(name="\u200b", value=progress, inline=False)
			sheet.add_field(name="**Total Votes**", value=votes, inline=False)
			await ctx.send(embed=sheet)
			
		except Exception as e:
			print(e)
		
def setup(bot):
	bot.add_cog(Poll(bot))

