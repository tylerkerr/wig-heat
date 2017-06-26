#!/usr/bin/env python3

import sys
import os
from sqlalchemy import *
from datetime import datetime, timezone
from math import floor, ceil
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

gametypes = {'tft': ['Solo', 'Random 2v2', 'Random 3v3', 'Random 4v4', 'FFA'], 
			'roc': ['Solo', 'Random 2v2', 'Random 3v3', 'FFA']}

# maps as of June 26 2017

rocmaps = {'Solo': ['Plunder Isle', 'Frostsabre', 'Legends', 'Lost Temple', 'Tranquil Paths', 
					'Gnoll Wood', 'Moonglade', 'Scorched Basin'],
		'Random 2v2': ['Duskwood', 'Harvest Moon', 'Lost Temple', 'Gnoll Wood', 'Scorched Basin', 
					'Stromguarde', 'Swamp of Sorrows', 'Golems In The Mist', 'The Crucible'],
		'Random 3v3': ['Dark Forest', 'Dragon Fire', 'Stromguarde', 'Swamp of Sorrows', 
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
	if random.uniform(0, tftratio+1) > 1:
		return True
	else:
		return False

def getnewest():
	dateq = games.select().order_by(games.c.gamedate.desc()).limit(1)
	date = datetime.fromtimestamp(int(run(dateq)[0]['gamedate']), timezone.utc)
	print("newest game is from %s at %s" % (gateway, date))

def getgamecounts(): # getting counts per gametype and roc/tft ratios
	gamecounts = {}
	for gametype in gametypes['tft']:
		if gametype in gametypes['roc']:
			rocq = games.select((games.c.gametype == gametype) & games.c.gamemap.notin_(tftmaps[gametype]) 
								& games.c.gamemap.in_(rocmaps[gametype]) & (games.c.gamelength > 2))
			rocgames = len(run(rocq))
			tftq = games.select((games.c.gametype == gametype) & games.c.gamemap.in_(tftmaps[gametype]) 
								& games.c.gamemap.notin_(rocmaps[gametype]) & (games.c.gamelength > 2))
			tftgames = len(run(tftq))
			overlapq = games.select((games.c.gametype == gametype) & games.c.gamemap.in_(tftmaps[gametype]) 
								& games.c.gamemap.in_(rocmaps[gametype]) & (games.c.gamelength > 2))
			overlapgames = len(run(overlapq))
		else:
			tftq = games.select((games.c.gametype == gametype) & (games.c.gamelength > 2))
			tftgames = len(run(tftq))
			rocgames = 0
		try: # if we have games in both roc and tft, use the ratio of games on non-overlapping maps to guess
			tftratio = tftgames / rocgames
			tftoverlap = ceil(overlapgames / (tftratio + 1) * tftratio)
			rocoverlap = floor(overlapgames / (tftratio + 1))
			# print(gametype, "overlap", overlapgames, "ratio", tftratio, "to roc", rocoverlap, "to tft", tftoverlap, "sum", rocoverlap + tftoverlap)
			estimatedtftgames = tftgames + tftoverlap
			estimatedrocgames = rocgames + rocoverlap
		except:
			# print(gametype)
			tftratio = None
			tftgames += overlapgames
			overlapgames = 0
		gamecounts[gametype] = {'rocgames': rocgames, 'tftgames': tftgames, 'overlapgames': overlapgames, 'tftratio': tftratio, 'estimatedtftgames': estimatedtftgames, 'estimatedrocgames': estimatedrocgames}

	return gamecounts

gamecounts = getgamecounts()

for gametype in gametypes['tft']:
	print(gametype, gamecounts[gametype])
