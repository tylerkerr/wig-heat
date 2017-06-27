#!/usr/bin/env python3

import sys
import os
from sqlalchemy import *
from datetime import datetime, timezone
from time import strftime, gmtime
from math import floor, ceil
from csv import DictWriter
import random

try:
	gateway = sys.argv[1]
	assert gateway in ['Azeroth', 'Lordaeron', 'Northrend', 'Kalimdor']
	assert os.path.exists(gateway + '.db')
except:
	print('usage:', sys.argv[0], '[gateway]')
	sys.exit(1)

dbname = 'sqlite:///' + gateway + '.db'

db = create_engine(dbname)
metadata = MetaData(db)
games = Table('wiggames', metadata, autoload=True)
minlength = 3

gametypes = {'tft': ['Solo', 'Random 2v2', 'Random 3v3', 'Random 4v4', 'Arranged 2v2',
					 'Arranged 3v3', 'Arranged 4v4', 'Tournament', 'FFA'], 
			'roc': ['Solo', 'Random 2v2', 'Random 3v3', 'Arranged 2v2', 'Arranged 3v3', 'FFA']}

# maps as of June 26 2017

rocmaps = {'Solo': ['Plunder Isle', 'Frostsabre', 'Legends', 'Lost Temple', 'Tranquil Paths', 
					'Gnoll Wood', 'Moonglade', 'Scorched Basin'],
		'Random 2v2': ['Duskwood', 'Harvest Moon', 'Lost Temple', 'Gnoll Wood', 'Scorched Basin', 
					'Stromguarde', 'Swamp of Sorrows', 'Golems In The Mist', 'The Crucible'],
		'Random 3v3': ['Dark Forest', 'Dragon Fire', 'Stromguarde', 'Swamp of Sorrows', 
					'Timbermaw Hold', 'Battleground', 'Plains of Snow', 'The Crucible'],
		'Arranged 2v2': ['Duskwood', 'Harvest Moon', 'Lost Temple', 'Gnoll Wood', 'Scorched Basin', 
					'Stromguarde', 'Swamp of Sorrows', 'Golems In The Mist', 'The Crucible'],
		'Arranged 3v3': ['Dark Forest', 'Dragon Fire', 'Stromguarde', 'Swamp of Sorrows', 
					'Timbermaw Hold', 'Battleground', 'Plains of Snow', 'The Crucible'],
		'FFA': ['Harvest Moon', 'Lost Temple', 'Mystic Isles', 'Gnoll Wood', 'Scorched Basin', 
				'Stromguarde', 'Swamp of Sorrows', 'Battleground', 'The Crucible']}

tftmaps = {'Solo': ['Secret Valley', 'Melting Valley', 'Echo Isles', 'Terenas Stand', 
					'Centaur Grove', 'Lost Temple', 'Tidewater Glades', 'Turtle Rock', 
					'Twisted Meadows', 'Gnoll Wood', 'The Two Rivers', 'Wetlands', 'Plunder Isle'],
		'Random 2v2': ['Centaur Grove', 'Goldshire', 'Lost Temple', 'Phantom Grove', 'Turtle Rock', 
					'Twisted Meadows', 'Gnoll Wood', 'Moonglade', 'Avalanche', 'Stone Cold Mountain', 
					'River of Souls', 'Duskwood'],
		'Random 3v3': ['Bloodstone Mesa', 'Copper Canyon', 'Dragonblight', 'Gnoll Wood', 'Highperch', 
					'Monsoon', 'Typhoon', 'Upper Kingdom', 'River of Souls', "Mur'gul Oasis", 
					'Hinterland Raid', 'Plains of Snow'],
		'Random 4v4': ['Battleground', 'Cherryville', 'Deadlock', 'Dragon Falls', 'Full Scale Assault', 
					'Golems In The Mist', 'Market Square', "Mur'gul Oasis", 'Twilight Ruins', 
					'Death Knell', 'Deadlands', 'Last Man Standing'],
		'Arranged 2v2': ['Centaur Grove', 'Goldshire', 'Lost Temple', 'Phantom Grove', 'Turtle Rock', 
					'Twisted Meadows', 'Gnoll Wood', 'Moonglade', 'Avalanche', 'Stone Cold Mountain', 
					'River of Souls', 'Duskwood'],
		'Arranged 3v3': ['Bloodstone Mesa', 'Copper Canyon', 'Dragonblight', 'Everfrost', 'Gnoll Wood',
					'Highperch', 'Monsoon', 'Rice Fields', 'River of Souls', 'Silverpine Forest',
					'Sunrock Cove', 'Typhoon', 'Upper Kingdom'],
		'Arranged 4v4': ['Battleground', 'Cherryville', 'Deadlock', 'Dragon Falls', 'Friends',
					'Full Scale Assault', 'Gold Rush', 'Golems In The Mist', 'Hurricane Isle',
					"Mur'gul Oasis", 'Slalom'],
		'Tournament': [],
		'FFA': ['Deathrose', 'Twisted Meadows', 'Duststorm', 'Emerald Shores', 'Monsoon', 
				'Silverpine Forest', 'Deadlock', "Mur'gul Oasis", 'Twilight Ruins', 
				'Bloodstone Mesa', 'Copper Canyon', 'Battleground']}

# TODO: arranged team maps. need a crew2queue just to see the list

def run(query):
    results = query.execute()
    return [dict(row) for row in results]

def rprint(lst):
	[print(row) for row in lst]

def tftratiorandom(tftratio):
	if tftratio == None:
		return True
	if random.uniform(0, tftratio+1) > 1:
		return True
	else:
		return False

def getnewest():
	dateq = games.select().order_by(games.c.gamedate.desc()).limit(1)
	date = datetime.fromtimestamp(int(run(dateq)[0]['gamedate']), timezone.utc)
	return "newest game is from %s at %s" % (gateway, date)

def istftgame(gametype, gamemap, tftratio):
	if gametype not in gametypes['roc']:
		return True
	if gamemap not in rocmaps[gametype]:
		return True
	if gamemap not in tftmaps[gametype]:
		return False
	if gamemap not in tftmaps[gametype] and gamemap not in rocmaps[gametype]:
		print("[!] Unknown map!")
		sys.exit(1)
	if gamemap in tftmaps[gametype] and gamemap in rocmaps[gametype]:
		return tftratiorandom(tftratio)

def getgamecounts(): # getting counts per gametype and roc/tft ratios
	gamecounts = {}
	for gametype in gametypes['tft']:
		if gametype in gametypes['roc']:
			rocq = games.select((games.c.gametype == gametype) & games.c.gamemap.notin_(tftmaps[gametype]) 
								& games.c.gamemap.in_(rocmaps[gametype]) & (games.c.gamelength >= minlength))
			rocgames = len(run(rocq))
			tftq = games.select((games.c.gametype == gametype) & games.c.gamemap.in_(tftmaps[gametype]) 
								& games.c.gamemap.notin_(rocmaps[gametype]) & (games.c.gamelength > minlength))
			tftgames = len(run(tftq))
			overlapq = games.select((games.c.gametype == gametype) & games.c.gamemap.in_(tftmaps[gametype]) 
								& games.c.gamemap.in_(rocmaps[gametype]) & (games.c.gamelength > minlength))
			overlapgames = len(run(overlapq))
		else:
			tftq = games.select((games.c.gametype == gametype) & (games.c.gamelength > minlength))
			tftgames = len(run(tftq))
			rocgames = 0
		try: # if we have games in both roc and tft, use the ratio of games on non-overlapping maps to guess
			tftratio = tftgames / rocgames
			tftoverlap = ceil(overlapgames / (tftratio + 1) * tftratio)
			rocoverlap = floor(overlapgames / (tftratio + 1))
			estimatedtftgames = tftgames + tftoverlap
			estimatedrocgames = rocgames + rocoverlap
		except:
			# print(gametype)
			tftratio = None
			tftgames += overlapgames
			overlapgames = 0
			estimatedtftgames = tftgames
			estimatedrocgames = rocgames
		gamecounts[gametype] = {'rocgames': rocgames, 'tftgames': tftgames, 
								'overlapgames': overlapgames, 'tftratio': tftratio, 
								'estimatedtftgames': estimatedtftgames, 
								'estimatedrocgames': estimatedrocgames}
	return gamecounts

def printgamecounts(gamecounts):
	for gametype in gametypes['tft']:
		if gamecounts[gametype]['tftratio'] == None:
			ratio = 'n/a'
		else:
			ratio = gamecounts[gametype]['tftratio']
		if gametype == 'FFA' or  gametype == 'Solo': # alignment hack
			temptype = gametype + '\t'
		else:
			temptype = gametype
		# print(gametype, '    \t', gamecounts[gametype]['estimatedtftgames'], '\t (RoC', 
			  # gamecounts[gametype]['estimatedrocgames'], ')\t ratio', ratio)
		print('%s   \t%s\t (RoC %s) \tratio %s' % (temptype, 
			gamecounts[gametype]['estimatedtftgames'], gamecounts[gametype]['estimatedrocgames'], ratio))

def gettftgames(gametype, gamecounts):
	tftgames = []
	for gametype in gametypes['tft']:
		gtgamesq = games.select((games.c.gametype == gametype) & (games.c.gamelength > minlength))
		gtgames = run(gtgamesq)
		for game in gtgames:
			if istftgame(gametype, game['gamemap'], gamecounts[gametype]['tftratio']):
				tftgames.append(game)
	return tftgames

def getweekdayfromepoch(epoch):
	return int(strftime('%w', gmtime(epoch)))

def gethourfromepoch(epoch):
	return int(strftime('%H', gmtime(epoch)))

def getdatefromepoch(epoch):
	return int(strftime('%j', gmtime(epoch)))

def makeviz_weekheatmap(gateway, gamelist, gametype):
	weekdays = {}
	for d in range(7):
		weekdays[d] = {}
		for h in range(24):
			weekdays[d][h] = 0
	for game in gamelist:
		weekday = getweekdayfromepoch(game['gamedate'])
		hour = gethourfromepoch(game['gamedate'])
		weekdays[weekday][hour] = weekdays[weekday][hour] + 1

	with open('weekheatmap-' + gateway + gametype + '.csv', 'w') as csvfile:
		fieldnames = ['weekday', 'hour', 'games']
		writer = DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for day in weekdays:
			for hour in weekdays[day]:
				writer.writerow({'weekday': day, 'hour': hour, 'games': weekdays[day][hour]})
	# return weekdays

def main():
	print(getnewest())
	gamecounts = getgamecounts()
	printgamecounts(gamecounts)

	sologames = gettftgames('Solo', gamecounts)

	for gametype in gametypes['tft']:
		makeviz_weekheatmap(gateway, gettftgames(gametype, gamecounts), gametype)

if __name__ == '__main__':
	main()