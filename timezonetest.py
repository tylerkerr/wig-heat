#!/usr/bin/env python3

''' this exists because i didn't do much testing before doing 2 weeks' worth of scraping,
    and timezones are completely horrific. sorry'''

import sys
import os
from requests import get
from bs4 import BeautifulSoup
from dateutil.parser import parse
from time import strftime, gmtime, time
import datetime

testgames = {'Northrend': [77000000, 77700000], 'Azeroth': [22500000, 22700000], 
             'Lordaeron': [15050000, 15150000], 'Kalimdor': [32551595, 32900000]}

def downloadwig(gateway, gameid):
    if gateway == 'Kalimdor':
        baseurl = 'http://asialadders.battle.net/war3/ladder/w3xp-game-detail.aspx'
    else: 
        baseurl = 'http://classic.battle.net/war3/ladder/w3xp-game-detail.aspx'
    fullurl = baseurl + '?Gateway=' + gateway + '&GameID=' + str(gameid)

    response = get(fullurl)
    if 'errormessage.html' in response.url:
        return {'status': 'error', 'html': None}
    else:
        return {'status': 'saved', 'html': response.text}


def parsegame(gameid, html):
    container = BeautifulSoup(html, "html.parser").find("table", class_="mainTable")
    basicinfo = container.find_all("td", class_="playerStatsDataLeft")

    gamedate = int(parse(''.join(basicinfo[0].strings)).strftime('%s')) # convert the date to unix epoch
    gamemap = basicinfo[1].string
    gametype = basicinfo[2].string
    gamelength = int(basicinfo[3].string.split(" ")[0])
    
    return [gameid, gamedate, gametype, gamelength, gamemap]

def displaydate(epoch):
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc)

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

def isdst(gateway, epoch):
    yearday = getyeardayfromepoch(epoch)
    if yearday > 70 and yearday < 308: # this is a little rough.
        return True # let's just say it accounts for players that have trouble adjusting to DST
    else:
        return False

def adjusttimezone(gateway, epoch):
    # wigscraper.py gathers and parses times using EST. oops. no need to reparse
    dstmod = 0
    if isdst(gateway, epoch):
        dstmod += 3600
    offset = 18000 # EST is GMT-05:00
    return epoch - 18000 + dstmod



def main():
    for gateway in testgames:
        for gameid in testgames[gateway]:
            print("testing gameid", gameid, "from", gateway, '\n')
            html = downloadwig(gateway, gameid)['html']
            container = BeautifulSoup(html, "html.parser").find("table", class_="mainTable")
            basicinfo = container.find_all("td", class_="playerStatsDataLeft")
            rawdate = ''.join(basicinfo[0].strings)
            epochdate = adjusttimezone(gateway, int(parse(''.join(basicinfo[0].strings)).strftime('%s'))) # convert the date to unix epoch
            print("raw:", rawdate, "\t epoch:", epochdate, '\n\n')
            parsedate = getdatefromepoch(epochdate)
            parsehour = gethourfromepoch(epochdate)
            # display = displaydate(epochdate)
            display = strftime('%Y-%m-%d %I:%M:%S %p', gmtime(epochdate))
            print("parsed:", parsedate, "\t hour:", parsehour)
            print("display:", display, "\t DST:", isdst(gateway, epochdate), '\n\n')
            print("=" * 80)



if __name__ == '__main__':
    main()