import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime
from discord import Embed, Emoji

label1 = "one"
label2 = "two"
label3 = "three"
label4 = "three"

class Poll(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#@commands.Cog.listener()
	#async def on_ready():
	#	print("Cog poll ready")

	async def pollStart(self):
		try:
			global label1
			global label2
			ref = db.reference('/openPolls')
			polls = ref.get()
			polls = list(polls.items())
			for i in range(len(polls)):
				channel = await self.bot.fetch_channel(int(polls[i][1]['channel']))
				msg = await channel.fetch_message(int(polls[i][0]))
				embed = msg.embeds[0]
				# Get existing vote total from embed
				fieldList = embed.fields
				text = fieldList[0].value
				text = text.split('\n')
				label1 = text[0]
				label2 = text[1]
				# Set new total
				votes = polls[i][1]['votes']
				embed.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
				print("TesT")
				i = len(text)
				match i:
					case 2:
						view = VoteTwo(answers[0],answers[1])
					case 3:
						view = VoteThree(answers[0],answers[1],answers[2])
					case 4:
						view = VoteFour()
				await msg.edit(embed=embed,view=view)
		except Exception as e:
			print(e)
	@commands.command(pass_context = True)
	@commands.cooldown(1, 43200, commands.BucketType.user)
	async def poll(self,ctx):
		def check(c):
			return c.channel == ctx.author.dm_channel and c.author == ctx.author
		await ctx.author.send("Please enter the question.")
		try:
			question = await self.bot.wait_for('message', check=check)
			question = question.content
			await asyncio.sleep(1)
			await ctx.author.send("Please enter the response options seperated by a comma. Example: Blue, Red, Yellow")
			answers = await self.bot.wait_for('message', check=check)
			answers = answers.content
			#await ctx.author.send("Please enter the time limit.")
			#timer = await self.bot.wait_for('message', check=check)
			#timer = timer.content
			
			answers = answers.split(',')
			if len(answers) < 2:
				await ctx.author.send("Please enter at least two options seperated by comma.")
				answers = await self.bot.wait_for('message', check=check)
				answers = answers.content
			if len(answers) > 4:
				await ctx.author.send("Please enter four or less options seperated by comma.")
				answers = await self.bot.wait_for('message', check=check)
				answers = answers.content
			if len(answers) > 4 or len(answers) < 2:
				return
			
			sheet = discord.Embed(title=ctx.author.name, description="**{0}**".format(question), color=0x0000FF)
			a = ""
			progress = "```"
			votes = 0
			global label1
			global label2
			global label3
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
			# Set guild
			guild = ctx.message.guild.id
			guild = self.bot.get_guild(guild)
			match len(answers):
				case 2:
					view = VoteTwo(answers[0],answers[1])
				case 3:
					view = VoteThree(answers[0],answers[1],answers[2])	
				
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
							# Inform poll starter who voted
							username = ((await guild.fetch_member(user)).nick)
							if username == None:
								username = (await guild.fetch_member(user)).name
							await ctx.author.send("{} has voted.".format(username))
							await interaction.response.defer()
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
						async def optionThree(self, interaction: discord.Interaction, button: discord.ui.Button):
							await interaction.msg.edit(view=self)
						@discord.ui.button(label=answers[3], style=discord.ButtonStyle.grey,emoji="4️⃣")
						async def optionThree(self, interaction: discord.Interaction, button: discord.ui.Button):
							await interaction.msg.edit(view=self)
			#view = Vote()
			msg = await ctx.send(embed=sheet,view=view)
			lref = db.reference('/openPolls/{0}'.format(msg.id))
			lref.update({
				'labels': {
					'one': answers[0],
					'two': answers[1]
					}
			})
			ref = db.reference('/openPolls/{0}'.format(msg.id))
			ref.update({
				'votes': votes,
				'channel': str(msg.channel.id),
				'author': str(ctx.message.author.id),
				'message': str(ctx.message.id)
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
# Two voting options
class VoteTwo(discord.ui.View):
	def __init__(self,label1,label2):
		self.label1 = label1
		self.label2 = label2
		super().__init__(timeout = None)
		self.add_buttons()
	def add_buttons(self):
		button1 = discord.ui.Button(label=self.label1,style=discord.ButtonStyle.grey,emoji="1️⃣")
		button2 = discord.ui.Button(label=self.label2,style=discord.ButtonStyle.grey,emoji="2️⃣")
		async def optionOne(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
			# Get Channel
			channel = interaction.channel
			# Get author message id
			ref = db.reference('/openPolls/{0}/message'.format(interaction.message.id))
			mid = ref.get()
			msg = await channel.fetch_message(int(mid))
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
			sheet = interaction.message.embeds[0]
			fieldList = sheet.fields
			# Set new total
			votes = int(fieldList[2].value) + 1
			sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
			vref = db.reference('/openPolls/{0}'.format(interaction.message.id))
			vref.update({
				'votes': votes
			})
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
			# Inform poll starter who voted
			username = ((await guild.fetch_member(user)).nick)
			if username == None:
				username = (await guild.fetch_member(user)).name
			await msg.author.send("{} has voted.".format(username))
			await interaction.response.defer()
		async def optionTwo(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
			# Get Channel
			channel = interaction.channel
			# Get author message id
			ref = db.reference('/openPolls/{0}/message'.format(interaction.message.id))
			mid = ref.get()
			msg = await channel.fetch_message(int(mid))
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
			sheet = interaction.message.embeds[0]
			fieldList = sheet.fields
			# Set new total
			votes = int(fieldList[2].value) + 1
			sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
			vref = db.reference('/openPolls/{0}'.format(interaction.message.id))
			vref.update({
				'votes': votes
			})
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
			# Inform poll starter who voted
			username = ((await guild.fetch_member(user)).nick)
			if username == None:
				username = (await guild.fetch_member(user)).name
			await msg.author.send("{} has voted.".format(username))
			await interaction.response.defer()
		button1.callback = optionOne
		self.add_item(button1)
		button2.callback = optionTwo
		self.add_item(button2)
	# End Poll Button
	@discord.ui.button(label="End Poll",style=discord.ButtonStyle.red)
	async def endPoll(self, interaction: discord.Interaction, child: discord.ui.Button):
		ref = db.reference('/openPolls/{0}/author'.format(interaction.message.id))
		author = ref.get()
		if(interaction.user.id == int(author)):
			for child in self.children:
				child.disabled=True
			await interaction.response.edit_message(view=self)
			ref = db.reference('/openPolls/{0}'.format(interaction.message.id))
			ref.delete()
# Three Voting Options
class VoteThree(discord.ui.View):
	def __init__(self,label1,label2,label3):
		self.label1 = label1
		self.label2 = label2
		self.label3 = label3
		super().__init__(timeout = None)
		self.add_buttons()
	def add_buttons(self):
		button1 = discord.ui.Button(label=self.label1,style=discord.ButtonStyle.grey,emoji="1️⃣")
		button2 = discord.ui.Button(label=self.label2,style=discord.ButtonStyle.grey,emoji="2️⃣")
		button3 = discord.ui.Button(label=self.label3,style=discord.ButtonStyle.grey,emoji="3️⃣")
		async def optionOne(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
			# Get Channel
			channel = interaction.channel
			# Get author message id
			ref = db.reference('/openPolls/{0}/message'.format(interaction.message.id))
			mid = ref.get()
			msg = await channel.fetch_message(int(mid))
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
			sheet = interaction.message.embeds[0]
			fieldList = sheet.fields
			# Set new total
			votes = int(fieldList[2].value) + 1
			sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
			vref = db.reference('/openPolls/{0}'.format(interaction.message.id))
			vref.update({
				'votes': votes
			})
			# Set progress bar
			ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
			numbers = ref2.get()
			numbers = list(numbers.items())
			progress = "```"
			# Get two vote count values
			decimal = round(((int(numbers[0][1]) + 1) / int(votes)),4)
			decimal2 = round(((int(numbers[2][1])) / int(votes)),4)
			decimal3 = (1 - (decimal2 + decimal))
			# Get all three percent values
			percent = (str(decimal * 100) + "%")
			percent2 = (str(decimal2 * 100) + "%")
			percent3 = (str(decimal3 * 100) + "%")
			# Get all 3 progress bars
			filledLength = int(20 * decimal)
			filledLength2 = int(20 * decimal2)
			filledLength3 = filledLength + filledLength2
			bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
			bar2 = "\u25A0" * filledLength2 + '-' * (20 - filledLength2)
			bar3 = "\u25A0" * (20 - (filledLength3)) + '-' * (filledLength3)
			progress += "1 |{0}| {1} \n".format(bar,percent)
			progress += "2 |{0}| {1} \n".format(bar2,percent2)
			progress += "3 |{0}| {1} \n".format(bar3,percent3)
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
			# Inform poll starter who voted
			username = ((await guild.fetch_member(user)).nick)
			if username == None:
				username = (await guild.fetch_member(user)).name
			await msg.author.send("{} has voted.".format(username))
			await interaction.response.defer()
		async def optionTwo(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
			# Get Channel
			channel = interaction.channel
			# Get author message id
			ref = db.reference('/openPolls/{0}/message'.format(interaction.message.id))
			mid = ref.get()
			msg = await channel.fetch_message(int(mid))
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
			sheet = interaction.message.embeds[0]
			fieldList = sheet.fields
			# Set new total
			votes = int(fieldList[2].value) + 1
			sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
			vref = db.reference('/openPolls/{0}'.format(interaction.message.id))
			vref.update({
				'votes': votes
			})
			# Set progress bar
			ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
			numbers = ref2.get()
			numbers = list(numbers.items())
			progress = "```"
			# Get two vote count values
			decimal = round(((int(numbers[2][1]) + 1) / int(votes)),4)
			decimal2 = round(((int(numbers[0][1])) / int(votes)),4)
			decimal3 = (1 - (decimal2 + decimal))
			# Get all three percent values
			percent = (str(decimal * 100) + "%")
			percent2 = (str(decimal2 * 100) + "%")
			percent3 = (str(decimal3 * 100) + "%")
			# Get all 3 progress bars
			filledLength = int(20 * decimal)
			filledLength2 = int(20 * decimal2)
			filledLength3 = filledLength + filledLength2
			bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
			bar2 = "\u25A0" * filledLength2 + '-' * (20 - filledLength2)
			bar3 = "\u25A0" * (20 - (filledLength3)) + '-' * (filledLength3)
			progress += "1 |{0}| {1} \n".format(bar2,percent2)
			progress += "2 |{0}| {1} \n".format(bar,percent)
			progress += "3 |{0}| {1} \n".format(bar3,percent3)
			progress += "```"
			sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
			# Edit the embed
			await interaction.message.edit(embed=sheet,view=self)
			# Update user list and vote count
			ref2.update({
				'two': numbers[2][1] + 1
			})
			ref.update({
				len(users): str(user)
			})
			# Inform poll starter who voted
			username = ((await guild.fetch_member(user)).nick)
			if username == None:
				username = (await guild.fetch_member(user)).name
			await msg.author.send("{} has voted.".format(username))
			await interaction.response.defer()
		async def optionThree(interaction: discord.Interaction):
			# Get user ID
			user = interaction.user.id
			# Get Guild
			guild = interaction.guild
			# Get Channel
			channel = interaction.channel
			# Get author message id
			ref = db.reference('/openPolls/{0}/message'.format(interaction.message.id))
			mid = ref.get()
			msg = await channel.fetch_message(int(mid))
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
			sheet = interaction.message.embeds[0]
			fieldList = sheet.fields
			# Set new total
			votes = int(fieldList[2].value) + 1
			sheet.set_field_at(2,name="**Total Votes**", value=votes, inline=False)
			vref = db.reference('/openPolls/{0}'.format(interaction.message.id))
			vref.update({
				'votes': votes
			})
			# Set progress bar
			ref2 = db.reference('/openPolls/{0}/options'.format(interaction.message.id))
			numbers = ref2.get()
			numbers = list(numbers.items())
			progress = "```"
			# Get two vote count values
			decimal = round(((int(numbers[1][1]) + 1) / int(votes)),4)
			decimal2 = round(((int(numbers[2][1])) / int(votes)),4)
			decimal3 = (1 - (decimal2 + decimal))
			# Get all three percent values
			percent = (str(decimal * 100) + "%")
			percent2 = (str(decimal2 * 100) + "%")
			percent3 = (str(decimal3 * 100) + "%")
			# Get all 3 progress bars
			filledLength = int(20 * decimal)
			filledLength2 = int(20 * decimal2)
			filledLength3 = filledLength + filledLength2
			bar = "\u25A0" * filledLength + '-' * (20 - filledLength)
			bar2 = "\u25A0" * filledLength2 + '-' * (20 - filledLength2)
			bar3 = "\u25A0" * (20 - (filledLength3)) + '-' * (filledLength3)
			progress += "1 |{0}| {1} \n".format(bar3,percent3)
			progress += "2 |{0}| {1} \n".format(bar2,percent2)
			progress += "3 |{0}| {1} \n".format(bar,percent)
			progress += "```"
			sheet.set_field_at(1,name="\u200b", value=progress, inline=False)
			# Edit the embed
			await interaction.message.edit(embed=sheet,view=self)
			# Update user list and vote count
			ref2.update({
				'three': numbers[1][1] + 1
			})
			ref.update({
				len(users): str(user)
			})
			# Inform poll starter who voted
			username = ((await guild.fetch_member(user)).nick)
			if username == None:
				username = (await guild.fetch_member(user)).name
			await msg.author.send("{} has voted.".format(username))
			await interaction.response.defer()
		button1.callback = optionOne
		self.add_item(button1)
		button2.callback = optionTwo
		self.add_item(button2)
		button3.callback = optionThree
		self.add_item(button3)
	# End Poll Button
	@discord.ui.button(label="End Poll",style=discord.ButtonStyle.red)
	async def endPoll(self, interaction: discord.Interaction, child: discord.ui.Button):
		ref = db.reference('/openPolls/{0}/author'.format(interaction.message.id))
		author = ref.get()
		if(interaction.user.id == int(author)):
			for child in self.children:
				child.disabled=True
			await interaction.response.edit_message(view=self)
			ref = db.reference('/openPolls/{0}'.format(interaction.message.id))
			ref.delete()
async def setup(bot):
	await bot.add_cog(Poll(bot))

