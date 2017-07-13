#!/usr/bin/env python3

import sys
import os
from sqlalchemy import *
from datetime import datetime, timezone
from time import strftime, gmtime
from math import floor, ceil
from csv import DictWriter
import random

# --------------- INIT ---------------

def initialize():
    global gateway
    global dbname
    global db
    global metadata
    global games
    global minlength
    global gametypes
    global rocmaps
    global tftmaps
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

    # maps as of June 26 2017. things will get a little messy if/when this changes
    
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

# --------------- UTIL ---------------

def run(query):
    results = query.execute()
    return [dict(row) for row in results]

def rprint(lst):
    [print(row) for row in lst]

def getnewest():
    dateq = games.select().order_by(games.c.gamedate.desc()).limit(1)
    return int(run(dateq)[0]['gamedate'])

def getoldest():
    dateq = games.select().order_by(games.c.gamedate.asc()).limit(1)
    return int(run(dateq)[0]['gamedate'])

def getweekdayfromepoch(epoch): # int 0-6, 0 = sunday
    return int(strftime('%w', gmtime(epoch)))

def gethourfromepoch(epoch): # int 0-23, UTC
    return int(strftime('%H', gmtime(epoch)))

def getyeardayfromepoch(epoch): # int 1-366, 1 = jan 1st 
    return int(strftime('%j', gmtime(epoch)))

def getyearfromepoch(epoch): # int 1-9999...
    return int(strftime('%Y', gmtime(epoch)))

def getdatefromepoch(epoch):
    return strftime('%Y-%m-%d', gmtime(epoch))

def daysinyear(year): # if i must...
    if year % 4 != 0:
        return 365
    elif year % 100 != 0:
        return 366
    elif year % 400 != 0:
        return 365
    else:
        return 366

def adjusttimezone(gateway, epoch):
    # times gathered using EDT
    if gateway == 'Azeroth': # azeroth needs no correction
        return epoch
    elif gateway == 'Lordaeron': # lordaeron needs -3h
        return epoch - 10800
    elif gateway == 'Northrend': # northrend needs +6h
        return epoch + 21600
    elif gateway == 'Kalimdor': # kalimdor needs +13h
        return epoch + 46800


# --------------- ROC/TFT DIFFERENTIATION ---------------

def tftratiorandom(gameid, tftratio): # randomly return true or false, weighted by the tft:roc ratio provided
    random.seed(gameid) # determinism - we don't want the results changing slightly with every new render
    if tftratio == None:
        return True
    if random.uniform(0, tftratio+1) > 1:
        return True
    else:
        return False

def istftgame(gametype, gamemap, gameid, tftratio): # returns true if we think it's a tft game.
                                            # first check using mappools. if it's an overlapping map,
                                            # randomly assign tft/roc using tftratiorandom()
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
        return tftratiorandom(gameid, tftratio)

def gettftgames(gametype): # return a list of all games we thing are tft for a given gametype
    tftgames = []
    gtgamesq = games.select((games.c.gametype == gametype) & (games.c.gamelength >= minlength))
    gtgames = run(gtgamesq)
    for game in gtgames:
        if istftgame(gametype, game['gamemap'], game['gameid'], gamecounts[gametype]['tftratio']):
            tftgames.append(game)
    return tftgames

def getgamecounts(): # getting counts per gametype and roc/tft ratios
    gamecounts = {}
    for gametype in gametypes['tft']:
        allgamesq = games.select(games.c.gametype == gametype)
        allgames = len(run(allgamesq))
        shortgamesq = games.select((games.c.gametype == gametype) & (games.c.gamelength < minlength))
        shortgames = len(run(shortgamesq))
        if gametype in gametypes['roc']:
            rocq = games.select((games.c.gametype == gametype) & games.c.gamemap.notin_(tftmaps[gametype]) 
                                & games.c.gamemap.in_(rocmaps[gametype]) & (games.c.gamelength >= minlength))
            rocgames = len(run(rocq))
            tftq = games.select((games.c.gametype == gametype) & games.c.gamemap.in_(tftmaps[gametype]) 
                                & games.c.gamemap.notin_(rocmaps[gametype]) & (games.c.gamelength >= minlength))
            tftgames = len(run(tftq))
            overlapq = games.select((games.c.gametype == gametype) & games.c.gamemap.in_(tftmaps[gametype]) 
                                & games.c.gamemap.in_(rocmaps[gametype]) & (games.c.gamelength >= minlength))
            overlapgames = len(run(overlapq))
        else: # we don't need to do anything wild if the gametype isn't in roc, such as 4s RT or tournament
            tftq = games.select((games.c.gametype == gametype) & (games.c.gamelength >= minlength))
            tftgames = len(run(tftq))
            rocgames = 0
        try: # if we have games in both roc and tft, use the ratio of games on non-overlapping maps to guess
            tftratio = tftgames / rocgames
            tftoverlap = ceil(overlapgames / (tftratio + 1) * tftratio)
            rocoverlap = floor(overlapgames / (tftratio + 1))
            estimatedtftgames = tftgames + tftoverlap
            estimatedrocgames = rocgames + rocoverlap
        except:
            tftratio = None
            tftgames += overlapgames
            overlapgames = 0
            estimatedtftgames = tftgames
            estimatedrocgames = rocgames

        gamecounts[gametype] = {'allgames': allgames, 'shortgames': shortgames, 
                                'rocgames': rocgames, 'tftgames': tftgames, 
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
        print('%s   \t%s\t (RoC %s) \tratio %s' % (temptype, 
            gamecounts[gametype]['estimatedtftgames'], gamecounts[gametype]['estimatedrocgames'], ratio))


# --------------- DATA OUTPUT FUNCTIONS ---------------

def makeviz_simplecounts(gateway):
    for gametype in gametypes['tft']:
        print(gametype, gamecounts[gametype]['estimatedtftgames'])


def makeviz_weekheatmap(gateway, gamelist, gametype):
    filename = 'weekheatmap-' + gateway.lower() + '-' + gametype.lower().replace(' ', '') + '.csv'
    weekdays = {}
    for d in range(7):
        weekdays[d] = {}
        for h in range(24):
            weekdays[d][h] = 0
    for game in gamelist:
        gamedate = adjusttimezone(gateway, game['gamedate'])
        weekday = getweekdayfromepoch(gamedate)
        hour = gethourfromepoch(gamedate)
        weekdays[weekday][hour] = weekdays[weekday][hour] + 1

    with open(filename, 'w') as csvfile:
        fieldnames = ['weekday', 'hour', 'games']
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for day in weekdays:
            for hour in weekdays[day]:
                writer.writerow({'weekday': day, 'hour': hour, 'games': weekdays[day][hour]})

def makeviz_allgamesbydaystacked(gateway):
    filename = 'allgamesbydaystacked-' + gateway.lower() + '.csv'
    gamevalueinit = {'Solo': 0, 'Random 2v2': 0, 'Random 3v3': 0, 
                     'Random 4v4': 0, 'Arranged 2v2': 0,
                     'Arranged 3v3': 0, 'Arranged 4v4': 0, 
                     'Tournament': 0,   'FFA': 0}
    startdate = getdatefromepoch(getoldest())
    enddate = getdatefromepoch(getnewest())
    gamesperdate = {}
    for gametype in gametypes['tft']:
        gtgames = gettftgames(gametype)
        for game in gtgames:
            gamedate = getdatefromepoch(adjusttimezone(gateway, game['gamedate']))
            if not gamedate in gamesperdate:
                gamesperdate[gamedate] = gamevalueinit.copy()
            gamesperdate[gamedate][gametype] += 1

    with open(filename, 'w') as csvfile:
        fieldnames = ['date']
        for gametype in gametypes['tft']:
            fieldnames.append(gametype)
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for date in gamesperdate:
            writer.writerow({'date': date, 'Solo': gamesperdate[date]['Solo'], 
                             'Random 2v2': gamesperdate[date]['Random 2v2'],
                             'Random 3v3': gamesperdate[date]['Random 3v3'],
                             'Random 4v4': gamesperdate[date]['Random 4v4'],
                             'Arranged 2v2': gamesperdate[date]['Arranged 2v2'],
                             'Arranged 3v3': gamesperdate[date]['Arranged 3v3'],
                             'Arranged 4v4': gamesperdate[date]['Arranged 4v4'],
                             'Tournament': gamesperdate[date]['Tournament'],
                             'FFA': gamesperdate[date]['FFA']})

# --------------- MAIN ---------------

def main():

    initialize()

    olddate = datetime.fromtimestamp(getoldest(), timezone.utc)
    print("oldest game is from %s at %s" % (gateway, olddate))
    newdate = datetime.fromtimestamp(getnewest(), timezone.utc)
    print("newest game is from %s at %s" % (gateway, newdate))
    global gamecounts 
    gamecounts = getgamecounts()
    printgamecounts(gamecounts)

    # for gametype in gametypes['tft']:
        # print(gametype)
        # makeviz_weekheatmap(gateway, gettftgames(gametype), gametype)

    # makeviz_allgamesbydaystacked(gateway)
    # makeviz_simplecounts(gateway)

if __name__ == '__main__':
    main()