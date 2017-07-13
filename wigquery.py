#!/usr/bin/env python3

import sys
import os
from sqlalchemy import *
from datetime import datetime, timezone
from time import strftime, gmtime, time
from math import floor, ceil
from csv import DictWriter
import random

# --------------- INIT ---------------

def mapinit():
    global gametypes
    global rocmaps
    global tftmaps

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


def dbinit(gateway):
    global dbname
    global db
    global metadata
    global games
    global minlength
    dbname = 'sqlite:///' + gateway + '.db'    
    db = create_engine(dbname)
    metadata = MetaData(db)
    games = Table('wiggames', metadata, autoload=True)
    minlength = 3

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

def isdst(epoch):
    yearday = getyeardayfromepoch(epoch)
    if yearday > 70 and yearday < 308:
        return True
    else:
        return False

def adjusttimezone(gateway, epoch):
    # times gathered using EDT
    dstmod = 0
    if not isdst(epoch):
        dstmod += 3600
    if gateway == 'Azeroth': # azeroth needs -5h
        return epoch - 18000
    elif gateway == 'Lordaeron': # lordaeron needs -8h
        return epoch - 28800
    elif gateway == 'Northrend': # northrend needs +1h
        return epoch + 3600
    elif gateway == 'Kalimdor': # kalimdor needs +8h
        return epoch + 28800


# --------------- ROC/TFT DIFFERENTIATION ---------------

def tftratiorandom(gameid, tftratio): # randomly return true or false, weighted by the tft:roc ratio provided
    random.seed(gameid) # determinism - we don't want the results changing slightly with every new render
    if tftratio == None:
        return True
    if random.uniform(0, tftratio+1) > 1:
        return True
    else:
        return False

def istftgame(gamecounts, gametype, gamemap, gameid, tftratio): # returns true if we think it's a tft game.
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

def gettftgames(gamecounts, gametype): # return a list of all games we thing are tft for a given gametype
    tftgames = []
    gtgamesq = games.select((games.c.gametype == gametype) & (games.c.gamelength >= minlength))
    gtgames = run(gtgamesq)
    for game in gtgames:
        if istftgame(gamecounts, gametype, game['gamemap'], game['gameid'], gamecounts[gametype]['tftratio']):
            tftgames.append(game)
    return tftgames

def getgamecounts(): # getting counts per gametype and roc/tft ratios
    print("[-] calculating gamecounts")
    starttime = time()
    gamecounts = {}
    for gametype in gametypes['tft']:
        allgamesq = games.select(games.c.gametype == gametype).count()
        allgames = run(allgamesq)[0]['tbl_row_count']
        shortgamesq = games.select((games.c.gametype == gametype) 
                                & (games.c.gamelength < minlength)).count()
        shortgames = run(shortgamesq)[0]['tbl_row_count']
        realgamesq = games.select((games.c.gametype == gametype) 
                                & (games.c.gamelength >= minlength)).count()
        realgames = run(realgamesq)[0]['tbl_row_count']
        if gametype in gametypes['roc']:
            rocq = games.select((games.c.gametype == gametype) 
                                & games.c.gamemap.notin_(tftmaps[gametype]) 
                                & games.c.gamemap.in_(rocmaps[gametype]) 
                                & (games.c.gamelength >= minlength)).count()
            rocgames = run(rocq)[0]['tbl_row_count']
            tftq = games.select((games.c.gametype == gametype) 
                                & games.c.gamemap.in_(tftmaps[gametype]) 
                                & games.c.gamemap.notin_(rocmaps[gametype]) 
                                & (games.c.gamelength >= minlength)).count()
            tftgames = run(tftq)[0]['tbl_row_count']
            overlapq = games.select((games.c.gametype == gametype) 
                                & games.c.gamemap.in_(tftmaps[gametype]) 
                                & games.c.gamemap.in_(rocmaps[gametype]) 
                                & (games.c.gamelength >= minlength)).count()
            overlapgames = run(overlapq)[0]['tbl_row_count']
        else: # we don't need to do anything wild if the gametype isn't in roc, such as 4s RT or tournament
            tftq = games.select((games.c.gametype == gametype) 
                                & (games.c.gamelength >= minlength)).count()
            tftgames = run(tftq)[0]['tbl_row_count']
            rocgames = 0
        try: # if we have games in both roc and tft, use the ratio of games on non-overlapping maps to guess
            tftratio = tftgames / rocgames
            tftoverlap = ceil(overlapgames / (tftratio + 1) * tftratio)
            rocoverlap = floor(overlapgames / (tftratio + 1))
            estimatedtftgames = tftgames + tftoverlap
            estimatedrocgames = rocgames + rocoverlap
            tftratio = float(format(tftratio, '.2f'))
        except:
            tftratio = None
            tftgames += overlapgames
            overlapgames = 0
            estimatedtftgames = tftgames
            estimatedrocgames = rocgames

        gamecounts[gametype] = {'allgames': allgames, 'shortgames': shortgames, 
                                'realgames': realgames,
                                'rocgames': rocgames, 'tftgames': tftgames, 
                                'overlapgames': overlapgames, 
                                'tftratio': tftratio, 
                                'estimatedtftgames': estimatedtftgames, 
                                'estimatedrocgames': estimatedrocgames}
    totaltime = format(time() - starttime, '.2f')
    print("[+] finished gamecounts in %ss" % totaltime)
    return gamecounts

def printgamecounts(gamecounts):
    for gametype in gametypes['tft']:
        if gamecounts[gametype]['tftratio'] == None:
            ratio = 'n/a'
        else:
            ratio = gamecounts[gametype]['tftratio']
        if gametype == 'FFA' or gametype == 'Solo': # alignment hack
            temptype = gametype + '\t'
        else:
            temptype = gametype
        print('%s   \t%s\t (RoC %s) \tratio %s' % (temptype, 
            gamecounts[gametype]['estimatedtftgames'], gamecounts[gametype]['estimatedrocgames'], ratio))


# --------------- DATA OUTPUT FUNCTIONS ---------------

def datagen_prepgamecounts():
    filename = './data/gamecounts.csv'
    with open(filename, 'w') as csvfile:
        fieldnames = ['gateway', 'gametype', 'allgames', 'shortgames', 'realgames', 'realratio',
                      'rocgames', 'tftgames', 'overlapgames', 'tftratio', 
                      'estimatedtftgames', 'estimatedrocgames']
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def datagen_gamecounts(gamecounts, gateway):
    filename = './data/gamecounts.csv'
    fieldnames = ['gateway', 'gametype', 'allgames', 'shortgames', 'realgames', 'realratio',
              'rocgames', 'tftgames', 'overlapgames', 'tftratio', 
              'estimatedtftgames', 'estimatedrocgames']
    totals = {}
    for field in fieldnames[2:]:
        totals[field] = 0
    
    with open(filename, 'a') as csvfile:
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        for gametype in gametypes['tft']:
            try:
                realratio = format(gamecounts[gametype]['realgames'] / gamecounts[gametype]['shortgames'], '.2f')
            except:
                realratio = None
            writer.writerow({'gateway': gateway, 'gametype': gametype,
                            'allgames': gamecounts[gametype]['allgames'], 
                            'realgames': gamecounts[gametype]['realgames'], 
                            'shortgames': gamecounts[gametype]['shortgames'], 
                            'realratio': realratio,
                            'tftgames': gamecounts[gametype]['tftgames'], 
                            'rocgames': gamecounts[gametype]['rocgames'], 
                            'overlapgames': gamecounts[gametype]['overlapgames'], 
                            'tftratio': gamecounts[gametype]['tftratio'], 
                            'estimatedtftgames': gamecounts[gametype]['estimatedtftgames'], 
                            'estimatedrocgames': gamecounts[gametype]['estimatedrocgames']})
            for field in fieldnames[2:]:
                try:
                    totals[field] += gamecounts[gametype][field]
                except:
                    totals[field] = None
        totals['tftratio'] = format(totals['tftgames'] / totals['rocgames'], '.2f')
        totals['realratio'] = format(totals['realgames'] / totals['shortgames'], '.2f')
        writer.writerow({'gateway': gateway, 'gametype': 'Total',
                        'allgames': totals['allgames'], 
                        'realgames': totals['realgames'], 
                        'shortgames': totals['shortgames'], 
                        'realratio': totals['realratio'],
                        'tftgames': totals['tftgames'], 
                        'rocgames': totals['rocgames'], 
                        'overlapgames': totals['overlapgames'], 
                        'tftratio': totals['tftratio'], 
                        'estimatedtftgames': totals['estimatedtftgames'], 
                        'estimatedrocgames': totals['estimatedrocgames']})

def datagen_weekheatmap(gamecounts, gateway):
    print("[-] generating week heatmap")
    starttime = time()
    for gametype in gametypes['tft']:
        gamelist = gettftgames(gamecounts, gametype)
        filename = './data/weekheatmap-' + gateway.lower() + '-' + gametype.lower().replace(' ', '') + '.csv'
        weekdays = {}
        for d in range(7):
            weekdays[d] = {}
            for h in range(24):
                weekdays[d][h] = 0
        for game in gamelist:
            gamedate = adjusttimezone(gateway, game['gamedate'])
            weekday = getweekdayfromepoch(gamedate)
            hour = gethourfromepoch(gamedate)
            # print(game['gameid'], "orig epoch", game['gamedate'], "adj epoch", gamedate,
            #     "weekday", weekday, "hour", hour)
            weekdays[weekday][hour] = weekdays[weekday][hour] + 1

        with open(filename, 'w') as csvfile:
            fieldnames = ['weekday', 'hour', 'games']
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for day in weekdays:
                for hour in weekdays[day]:
                    writer.writerow({'weekday': day, 'hour': hour, 'games': weekdays[day][hour]})
    totaltime = format(time() - starttime, '.2f')
    print("[+] finished week heatmap in %ss" % totaltime)

def datagen_gamesbyday(gamecounts, gateway):
    print("[-] generating all games by day")
    starttime = time()
    filename = './data/gamesbyday-' + gateway.lower() + '.csv'
    gamevalueinit = {'Solo': 0, 'Random 2v2': 0, 'Random 3v3': 0, 
                     'Random 4v4': 0, 'Arranged 2v2': 0,
                     'Arranged 3v3': 0, 'Arranged 4v4': 0, 
                     'Tournament': 0,   'FFA': 0}
    startdate = getdatefromepoch(getoldest())
    enddate = getdatefromepoch(getnewest())
    gamesperdate = {}
    for gametype in gametypes['tft']:
        gtgames = gettftgames(gamecounts, gametype)
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
    totaltime = format(time() - starttime, '.2f')
    print("[+] finished all games by day in %ss" % totaltime)

# --------------- MAIN ---------------

def main():
    mapinit()
    masterstart = time()
    gateways = ['Azeroth', 'Northrend', 'Lordaeron', 'Kalimdor']
    # gateways = ['Azeroth']
    datagen_prepgamecounts()
    for gateway in gateways:
        print("[-] starting queries for", gateway)
        gwstart = time()
        dbinit(gateway)
        gamecounts = getgamecounts()
        olddate = datetime.fromtimestamp(getoldest(), timezone.utc)
        print("oldest game from %s was at %s" % (gateway, olddate))
        newdate = datetime.fromtimestamp(getnewest(), timezone.utc)
        print("newest game from %s was at %s" % (gateway, newdate))
        print("total games on %s: %s" % (gateway, 
                run(games.select(games.c.gameid).count())[0]['tbl_row_count']))
        datagen_gamesbyday(gamecounts, gateway)
        datagen_weekheatmap(gamecounts, gateway)
        datagen_gamecounts(gamecounts, gateway)
        db.dispose()
        gwtotal = format(time() - gwstart, '.2f')
        print("[+] %s completed in %ss" % (gateway, gwtotal))
        print("=" * 80)
    mastertotal = format(time() - masterstart, '.2f')
    print("[+] completed in %ss" % mastertotal)


if __name__ == '__main__':
    main()