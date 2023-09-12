NOT CURRENTLY IN USE




import discord, firebase_admin, discord.utils
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime

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

class Broadcast(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	# Get update channels
	ref = db.reference('/channels')
	info = ref.get()
	channels = list(info.items())
	
	# Get Image Channels
	ref = db.reference('/imageChannels')
	info = ref.get()
	channels2 = list(info.items())
	channels3 = []
	# Image channels warning
	for i in range(len(channels)):
		try:
			channels3.append(int(channels[i][1]))
			channel = bot.get_channel(int(channels[i][1]))
			# Check if channel still exists, if not, delete from database
			if channel == None:
				ref = db.reference('/channels/{0}/'.format(int(channels[i][0])))
				ref.delete()
			else:
				try:
					await channel.send(text)
				except Exception as e:
					if isinstance(e, discord.ext.commands.BotMissingPermissions):
						print("A channel {0} has blocked updates in {1}").format(channel.id,channel.guild)
		#await channel.send("Image Tracking Rebooted! You may now post again.")
		except Exception as e:
			if isinstance(e, discord.ext.commands.BotMissingPermissions):
				try:
					await channel.send("The bot does not have access to use this command here.")
					print("A channel {0} has blocked permissions in {1}").format(channel.id,channel.guild)
				except:
					print("A channel {0} has blocked sending permissions in {1}").format(channel.id,channel.guild)
			

	# Announcement channels warning
	for i in range(len(channels3)):
		# Not fixed, still messages same channel twice!
		if int(channels2[i][1]['channelID']) in channels3:
			x = "Do Nothing"
		else:
			channel = bot.get_channel(int(channels2[i][1]['channelID']))
			if channel == None:
				ref = db.reference('/imageChannels/{0}/'.format(int(channels2[i][0]['channelID'])))
				ref.delete()
			else:
				# Try to send message
				try:
					await channel.send(text)
				except Exception as e:
					if isinstance(e, discord.ext.commands.BotMissingPermissions):
						print("A channel {0} has blocked updates in {1}").format(channel.id,channel.guild)
	
def setup(bot):
	bot.add_cog(Broadcast(bot))
