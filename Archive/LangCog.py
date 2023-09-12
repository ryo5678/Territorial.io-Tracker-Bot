import discord, random, math, asyncio, firebase_admin, requests, io, re, datetime, os, cv2, discord.utils, subprocess, statistics
from discord.ext import commands
from discord.ext.commands import bot
from firebase_admin import db
import datetime


#Russian
textfile = open('ru-strings.txt', 'r', encoding="utf8")
russian = textfile.read().splitlines()
textfile.close()
#English
textfile = open('en-strings.txt', 'r')
english = textfile.read().splitlines()
textfile.close()
#French
textfile = open('fr-strings.txt', 'r', encoding="utf8")
french = textfile.read().splitlines()
textfile.close()
#Turkish
textfile = open('tr-strings.txt', 'r', encoding="utf8")
turkish = textfile.read().splitlines()
textfile.close()
#German
textfile = open('de-strings.txt', 'r', encoding="utf8")
german = textfile.read().splitlines()
textfile.close()

class LangCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	#-------------------------------------------------------------------------------
	#------------------------------- Language Picker -------------------------------
	#-------------------------------------------------------------------------------
	def languagePicker(ctx,user):
		ref2 = db.reference('/users/{0}/lang'.format(user))
		lang = ref2.get()
		if lang == "french":
			language = french
		if lang == "english":
			language = english
		if lang == "russian":
			language = russian
		if lang == "turkish":
			language = turkish
		if lang == "german":
			language = german
		if lang == None:
			language = english
		return language
	
async def setup(bot):
	await bot.add_cog(LangCog(bot))
