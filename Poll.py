import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime
from discord import Embed, Emoji


class Poll(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.Cog.listener()
	async def on_ready():
		print("Cog poll ready")

	async def pollUpdate(self,ctx,msg,channel,votes):
	#'\u1F44D'
		while True:
			def check(reaction,user):
				try:
					return user == ctx.author and str(reaction.emoji) == '\u27A1'
				except Exception as e:
					print(e)
			print("test1")
			poll = discord.Embed(title=msg.embeds[0].title,description=msg.embeds[0].description, color=0x0000FF)
			fieldList = msg.embeds[0].fields
			#print(fieldList)
			poll.add_field(name=fieldList[0].name, value=fieldList[0].value, inline=False)
			poll.add_field(name=fieldList[1].name, value=fieldList[1].value, inline=False)
			poll.add_field(name=fieldList[2].name, value=int(fieldList[2].value) + votes, inline=False)
			try:
				print("test3")
				reaction, user = await self.bot.wait_for('reaction_add',timeout = 60, check=check)
				print("Test2")
				await msg.edit(embed = poll)
			except Exception as e:
				print(e)
		#print(msg.embeds[0].fields)
		#ladder.set_field_at(i,name="#{0} ".format(i+1) + clanList2[i][0], value=clanList2[i][1]['score'], inline=True)
	@commands.command(pass_context = True)
	#@commands.has_permissions(administrator=True)
	@commands.is_owner()
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
				progress += "{} |                    | 0% \n".format(i+1)
			progress += "```"
			sheet.add_field(name="\u200b", value=a, inline=False)
			sheet.add_field(name="\u200b", value=progress, inline=False)
			sheet.add_field(name="**Total Votes**", value=votes, inline=False)
			votes = 0
			match len(answers):
				case 2:
					# Button Interaction
					################################ 
					# This button is the test button, it will be used to copy code to other buttons
					class Vote(discord.ui.View):
						def __init__(self):
							super().__init__(timeout = None)
						@discord.ui.button(label=answers[0],style=discord.ButtonStyle.grey,emoji="1️⃣")
						async def optionOne(self, interaction: discord.Interaction, button: discord.ui.Button):
							# Get user ID
							user = interaction.user.id
							# Get existing user list
							ref = db.reference('/openPolls/{0}/users'.format(interaction.message.id))
							users = ref.get()
							# Check if first user
							if users == None:
								users = []
								users.append(user)
							# If user in list , return, otherwise proceed
							else:
								try:
									users = list(users)
									if str(user) in users:
										return
								except:
									if str(user) in users[0][1]:
										return
							# Get existing vote total from embed
							fieldList = interaction.message.embeds[0].fields
							# Set new total
							votes = int(fieldList[2].value) + 1
							sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
							# Set progress bar
							ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
							numbers = ref2.get()
							numbers = list(numbers.items())
							progress = "```"
							decimal = round(((int(numbers[0][1]) + 1) / int(votes)),2)
							percent = (str(decimal * 100) + "%")
							percent2 = (str(100 - (decimal * 100)) + "%")
							filledLength = int(20 * decimal)
							bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
							bar2 = "\u25A0" * (20 - filledLength) + '-' * (filledLength)
							progress += "1 |{0}| {1} \n".format(bar,percent)
							progress += "2 |{0}| {1} \n".format(bar2,percent2)
							progress += "```"
							sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
							# Edit the embed
							await interaction.message.edit(embed=sheet,view=self)
							# Update user list and vote count
							ref2.update({
								'one': numbers[0][1] + 1
							})
							ref.update({
								len(users): str(user)
							})
						@discord.ui.button(label=answers[1], style=discord.ButtonStyle.grey,emoji="2️⃣")
						async def optionTwo(self, interaction: discord.Interaction, button: discord.ui.Button):
							# Get user ID
							user = interaction.user.id
							# Get existing user list
							ref = db.reference('/openPolls/{0}/users'.format(interaction.message.id))
							users = ref.get()
							# Check if first user
							if users == None:
								users = []
								users.append(user)
							# If user in list , return, otherwise proceed
							else:
								try:
									users = list(users)
									if str(user) in users:
										return
								except:
									if str(user) in users[0][1]:
										return
							# Get existing vote total from embed
							fieldList = interaction.message.embeds[0].fields
							# Set new total
							votes = int(fieldList[2].value) + 1
							sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
							# Set progress bar
							ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
							numbers = ref2.get()
							numbers = list(numbers.items())
							progress = "```"
							decimal = round(((int(numbers[1][1]) + 1) / int(votes)),2)
							percent = (str(decimal * 100) + "%")
							percent2 = (str(100 - (decimal * 100)) + "%")
							filledLength = int(20 * decimal)
							bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
							bar2 = "\u25A0" * (20 - filledLength) + '-' * (filledLength)
							progress += "1 |{0}| {1} \n".format(bar2,percent2)
							progress += "2 |{0}| {1} \n".format(bar,percent)
							progress += "```"
							sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
							# Edit the embed
							await interaction.message.edit(embed=sheet,view=self)
							# Update user list and vote count
							ref2.update({
								'two': numbers[1][1] + 1
							})
							ref.update({
								len(users): str(user)
							})
				case 3:
					# Button Interaction
					class Vote(discord.ui.View):
						def __init__(self):
							super().__init__(timeout = None)
						@discord.ui.button(label=answers[0],style=discord.ButtonStyle.grey,emoji="1️⃣")
						async def optionOne(self, interaction: discord.Interaction, button: discord.ui.Button):
							# Get user ID
							user = interaction.user.id
							# Get existing user list
							ref = db.reference('/openPolls/{0}/users'.format(interaction.message.id))
							users = ref.get()
							# Check if first user
							if users == None:
								users = []
								users.append(user)
							# If user in list , return, otherwise proceed
							else:
								try:
									users = list(users)
									if str(user) in users:
										return
								except:
									if str(user) in users[0][1]:
										return
							# Get existing vote total from embed
							fieldList = interaction.message.embeds[0].fields
							# Set new total
							votes = int(fieldList[2].value) + 1
							sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
							# Set progress bar
							ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
							numbers = ref2.get()
							numbers = list(numbers.items())
							progress = "```"
							decimal = round(((int(numbers[0][1]) + 1) / int(votes)),2)
							percent = (str(decimal * 100) + "%")
							percent2 = (str(100 - (decimal * 100)) + "%")
							filledLength = int(20 * decimal)
							bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
							bar2 = "\u25A0" * (20 - filledLength) + '-' * (filledLength)
							progress += "1 |{0}| {1} \n".format(bar,percent)
							progress += "2 |{0}| {1} \n".format(bar2,percent2)
							progress += "```"
							sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
							# Edit the embed
							await interaction.message.edit(embed=sheet,view=self)
							# Update user list and vote count
							ref2.update({
								'one': numbers[0][1] + 1
							})
							ref.update({
								len(users): str(user)
							})
						@discord.ui.button(label=answers[1], style=discord.ButtonStyle.grey,emoji="2️⃣")
						async def optionTwo(self, interaction: discord.Interaction, button: discord.ui.Button):
							# Get user ID
							user = interaction.user.id
							# Get existing user list
							ref = db.reference('/openPolls/{0}/users'.format(interaction.message.id))
							users = ref.get()
							# Check if first user
							if users == None:
								users = []
								users.append(user)
							# If user in list , return, otherwise proceed
							else:
								try:
									users = list(users)
									if str(user) in users:
										return
								except:
									if str(user) in users[0][1]:
										return
							# Get existing vote total from embed
							fieldList = interaction.message.embeds[0].fields
							# Set new total
							votes = int(fieldList[2].value) + 1
							sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
							# Set progress bar
							ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
							numbers = ref2.get()
							numbers = list(numbers.items())
							progress = "```"
							decimal = round(((int(numbers[1][1]) + 1) / int(votes)),2)
							percent = (str(decimal * 100) + "%")
							percent2 = (str(100 - (decimal * 100)) + "%")
							filledLength = int(20 * decimal)
							bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
							bar2 = "\u25A0" * (20 - filledLength) + '-' * (filledLength)
							progress += "1 |{0}| {1} \n".format(bar2,percent2)
							progress += "2 |{0}| {1} \n".format(bar,percent)
							progress += "```"
							sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
							# Edit the embed
							await interaction.message.edit(embed=sheet,view=self)
							# Update user list and vote count
							ref2.update({
								'two': numbers[1][1] + 1
							})
							ref.update({
								len(users): str(user)
							})
						@discord.ui.button(label=answers[2], style=discord.ButtonStyle.grey,emoji="3️⃣")
						async def optionThree(self, button: discord.ui.Button, interaction: discord.Interaction):
							await interaction.msg.edit(view=self)
				case 4:
					# Button Interaction
					class Vote(discord.ui.View):
						def __init__(self):
							super().__init__(timeout = None)
						@discord.ui.button(label=answers[0],style=discord.ButtonStyle.grey,emoji="1️⃣")
						async def optionOne(self, interaction: discord.Interaction, button: discord.ui.Button):
							# Get user ID
							user = interaction.user.id
							# Get existing user list
							ref = db.reference('/openPolls/{0}/users'.format(interaction.message.id))
							users = ref.get()
							# Check if first user
							if users == None:
								users = []
								users.append(user)
							# If user in list , return, otherwise proceed
							else:
								try:
									users = list(users)
									if str(user) in users:
										return
								except:
									if str(user) in users[0][1]:
										return
							# Get existing vote total from embed
							fieldList = interaction.message.embeds[0].fields
							# Set new total
							votes = int(fieldList[2].value) + 1
							sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
							# Set progress bar
							ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
							numbers = ref2.get()
							numbers = list(numbers.items())
							progress = "```"
							decimal = round(((int(numbers[0][1]) + 1) / int(votes)),2)
							percent = (str(decimal * 100) + "%")
							percent2 = (str(100 - (decimal * 100)) + "%")
							filledLength = int(20 * decimal)
							bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
							bar2 = "\u25A0" * (20 - filledLength) + '-' * (filledLength)
							progress += "1 |{0}| {1} \n".format(bar,percent)
							progress += "2 |{0}| {1} \n".format(bar2,percent2)
							progress += "```"
							sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
							# Edit the embed
							await interaction.message.edit(embed=sheet,view=self)
							# Update user list and vote count
							ref2.update({
								'one': numbers[0][1] + 1
							})
							ref.update({
								len(users): str(user)
							})
						@discord.ui.button(label=answers[1], style=discord.ButtonStyle.grey,emoji="2️⃣")
						async def optionTwo(self, interaction: discord.Interaction, button: discord.ui.Button):
							# Get user ID
							user = interaction.user.id
							# Get existing user list
							ref = db.reference('/openPolls/{0}/users'.format(interaction.message.id))
							users = ref.get()
							# Check if first user
							if users == None:
								users = []
								users.append(user)
							# If user in list , return, otherwise proceed
							else:
								try:
									users = list(users)
									if str(user) in users:
										return
								except:
									if str(user) in users[0][1]:
										return
							# Get existing vote total from embed
							fieldList = interaction.message.embeds[0].fields
							# Set new total
							votes = int(fieldList[2].value) + 1
							sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
							# Set progress bar
							ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
							numbers = ref2.get()
							numbers = list(numbers.items())
							progress = "```"
							decimal = round(((int(numbers[1][1]) + 1) / int(votes)),2)
							percent = (str(decimal * 100) + "%")
							percent2 = (str(100 - (decimal * 100)) + "%")
							filledLength = int(20 * decimal)
							bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
							bar2 = "\u25A0" * (20 - filledLength) + '-' * (filledLength)
							progress += "1 |{0}| {1} \n".format(bar2,percent2)
							progress += "2 |{0}| {1} \n".format(bar,percent)
							progress += "```"
							sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
							# Edit the embed
							await interaction.message.edit(embed=sheet,view=self)
							# Update user list and vote count
							ref2.update({
								'two': numbers[1][1] + 1
							})
							ref.update({
								len(users): str(user)
							})
						@discord.ui.button(label=answers[2], style=discord.ButtonStyle.grey,emoji="3️⃣")
						async def optionThree(self, button: discord.ui.Button, interaction: discord.Interaction):
							await interaction.msg.edit(view=self)
						@discord.ui.button(label=answers[3], style=discord.ButtonStyle.grey,emoji="4️⃣")
						async def optionThree(self, button: discord.ui.Button, interaction: discord.Interaction):
							await interaction.msg.edit(view=self)
			view = Vote()
			msg = await ctx.send(embed=sheet,view=view)
			ref = db.reference('/openPolls/{0}'.format(msg.id))
			ref.update({
				'votes': votes
			})
			match len(answers):
				case 2:
					ref.update({
						'options': {
							'one': 0,
							'two': 0
							}
					})
				case 3:
					ref.update({
						'options': {
							'one': 0,
							'two': 0,
							'three': 0
							}
					})
				case 4:
					ref.update({
						'options': {
							'one': 0,
							'two': 0,
							'three': 0,
							'four': 0
							}
					})
			#poll.pollUpdate(ctx,msg,ctx.channel,votes)
		except Exception as e:
			print(e)
		
async def setup(bot):
	await bot.add_cog(Poll(bot))

