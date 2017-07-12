#!/usr/bin/env python3

import sys
import os
from requests import get
from bs4 import BeautifulSoup
from dateutil.parser import parse
import datetime
import sqlite3

# sqlite globals
def dbinit(dbname):
    global conn 
    conn = sqlite3.connect(dbname)
    global c
    c = conn.cursor()

# open the db if it exists, create and initialize if not
def dbopen(dbname):
    if os.path.exists(dbname):
        dbinit(dbname)
    else:
        dbinit(dbname)
        createtables(dbname)

# initializing the place where the wigs live
def createtables(dbname):
    c.execute('drop table if exists wiggames')
    c.execute('''CREATE TABLE wiggames
            (gameid integer, gamedate integer, gametype text, gamelength integer, gamemap text)''')
    conn.commit()

# returns either the entire row of a gameid, or None if the gameid doesn't exist in the database
def checkforgameid(gameid):
    c.execute('SELECT * FROM wiggames WHERE gameid={thisid}'.format(thisid=gameid))
    return c.fetchone()

# check if a gameid already exists in the database. if not, query battle.net for its game page and return the html
def downloadwig(gateway, gameid):
    if gateway == 'Kalimdor':
        baseurl = 'http://asialadders.battle.net/war3/ladder/w3xp-game-detail.aspx'
    else: 
        baseurl = 'http://classic.battle.net/war3/ladder/w3xp-game-detail.aspx'
    fullurl = baseurl + '?Gateway=' + gateway + '&GameID=' + str(gameid)
    if checkforgameid(gameid):
        return {'status': 'exists', 'html': None}
    response = get(fullurl)
    if 'errormessage.html' in response.url:
        return {'status': 'error', 'html': None}
    else:
        return {'status': 'saved', 'html': response.text}
    
# take a game page html blob and slice out the metadata that we care about. adapted from wigfo.py
def parsegame(gameid, html):
    container = BeautifulSoup(html, "html.parser").find("table", class_="mainTable")
    basicinfo = container.find_all("td", class_="playerStatsDataLeft")

    gamedate = int(parse(''.join(basicinfo[0].strings)).strftime('%s')) # convert the date to unix epoch
    gamemap = basicinfo[1].string
    gametype = basicinfo[2].string
    gamelength = int(basicinfo[3].string.split(" ")[0])
    
    return [gameid, gamedate, gametype, gamelength, gamemap]

def writegametodb(gamerow):
    c.execute('''INSERT INTO wiggames VALUES (?,?,?,?,?)''', gamerow)
    conn.commit()

def main():
    try:
        gateway = sys.argv[1]
        assert gateway in ['Azeroth', 'Northrend', 'Lordaeron', 'Kalimdor']
        dbname = gateway + '.db'
    except:
        print('usage: %s [gateway] [starting gameid]' % sys.argv[0])
        sys.exit(1)

    dbopen(dbname)

    try:
        startid = int(sys.argv[2])
    except:
        c.execute('select gameid from wiggames order by gameid desc limit 1')
        startid = c.fetchone()[0]

    gameid = startid
    consecutiveerrorlimit = 10
    errors = 0

    while errors < consecutiveerrorlimit:
        print(gameid, 'scraping...', end='')
        scrape = downloadwig(gateway, gameid)
        if scrape['status'] == 'error':
            print(scrape['status'])
            errors += 1
        elif scrape['status'] == 'saved':
            gamerow = parsegame(gameid, scrape['html'])
            date = datetime.datetime.fromtimestamp(gamerow[1], datetime.timezone.utc)
            writegametodb(gamerow)
            print('saved', date, gamerow[2])
            errors = 0 # reset error count after successful scrape
        elif scrape['status'] == 'exists':
            print(scrape['status'])
        gameid += 1
    conn.close()

if __name__ == '__main__':
    main()