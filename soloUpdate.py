import re, asyncio, math, firebase_admin, datetime
from urllib.request import Request, urlopen
from firebase_admin import db

database_url = "database url"

cred = firebase_admin.credentials.Certificate('JSON credentials file')
databaseApp = firebase_admin.initialize_app(cred, { 'databaseURL' : database_url})

# Outdated, needs to be reworked

###################
###################
# SUPER IMPORTANT # This program is called by Windows Task Scheduler on a Daily Basis!
################### If it stops functioning, make sure the python.exe path has not changed
################### Make sure this scripts path is unchanged as well


#-------------------------------------------------------------------------------
#------------------------- Update Most Recent 1v1 Scores -----------------------
#-------------------------------------------------------------------------------
try:
	# Update clan scores that are outdated
	try:
		# Download the webpage as text
		req = Request(
			url = "https://territorial.io/clans",
			headers={'User-Agent': 'Mozilla/5.0'}
		)
		with urlopen(req) as webpage:
			content = webpage.read().decode()
		# print(content)
		# Convert webpage text to string list by lines
		content = content.splitlines()
		content.pop(3)
		content.pop(2)
		content.pop(1)
		content.pop(0)
		# Grab only top 100 clans
		for i in range(100):
			# Split string to extract clan name
			text = content[i].split(', ')
			clan = text[1]
			clan = clan.replace('.', 'period5')
			clan = clan.replace('$', 'dollar5')
			clan = clan.replace('#', 'htag5')
			clan = clan.replace('[', 'lbracket5')
			clan = clan.replace('/', 'slash5')
			clan = clan.replace(']', 'rbracket5')
			clan = clan.replace('?', 'qmark5')
			ref = db.reference('/780723109128962070/clans/{0}'.format(clan))
			ref.set({
			'score': float(text[2])
			})
		#print(clans)
	except Exception as e:
		print("Clan update error")
		print(e)


	now = datetime.datetime.now().isoformat()
	# Download the webpage as text
	req = Request(
		url = "https://territorial.io/players", 
		headers={'User-Agent': 'Mozilla/5.0'}
	)
	with urlopen(req) as webpage:
		content = webpage.read().decode()
	#print(content)
	# Create db reference and convert string to list
	storage = db.reference('/onevsone')
	content = content.splitlines()
	content.pop(3)
	content.pop(2)
	content.pop(1)
	content.pop(0)
	#print(content[0])
	# Forbidden characters adjustment
	rep = {".": ",1pd,", "$": ",1ds,", "#": ",1ht,", "[": ",1lb,", "]": ",1rb,", "/": ",1fs,"}
	rep = dict((re.escape(k), v) for k, v in rep.items())
	pattern = re.compile("|".join(rep.keys()))
	
	dups = {}
	for i in range(len(content)):
		text = content[i].split(', ')
		temp = text[1]
		if temp not in dups:
			# Store index of first occurrence and occurrence value
			dups[temp] = [i, 1]
			#print(dups[temp])
			dups[temp][1] += 1
		else:
			#print(dups[temp][1])
			# Special case for first occurrence
			if dups[temp][1] != 1:
				# Use stored occurrence value
				text[1] = str(temp) + str(dups[temp][1])
				#print(dups[temp])
				#print(text[1])
			# Increment occurrence value, index value doesn't matter anymore
			dups[temp][1] += 1
		rank = text[0]
		name = text[1]
		score = text[2]
		wins = text[3]
		name = pattern.sub(lambda m: rep[re.escape(m.group(0))], name)
	
		if i == 0:
			#print(name)
			storage.push({
				name: {
					'rank': rank,
					'score': score,
					'wins': wins,
					'time': now
				}
			})
			ref = db.reference('/onevsone').get()
			snapshot = list(ref.items())
			storage = db.reference('/onevsone/{0}'.format(snapshot[len(snapshot) - 1][0]))
		else:
			#print(name)
			storage.update({
				name: {
					'rank': rank,
					'score': score,
					'wins': wins,
					'time': now
				}
			})
	print("1v1 update completed")
except Exception as e:
	print("An erorr occured in updateSolo")
	print(e)