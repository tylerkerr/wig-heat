# wig-heat
a set of Python3 tools to scrape, process, and visualize the data on [Blizzard's war3 battle.net ladders listings](http://classic.battle.net/war3/ladder/w3xp-ladders.aspx?Gateway=Northrend).

this is now live at [arranged.team](https://arranged.team/)!

todo:

✅ sequential scraping with error handling

✅ parsing game info from html

✅ writing gamedata to sql db

✅ scraping many games (currently have june 20 thru june 25 on useast)

✅ discarding non-TFT games (mappool, find roc/tft ratio, extrapolate on overlap games)

✅ figuring out which data to visualize

✅ writing queries to pass this data to d3.js

✅ creating visualizations with d3.js

✅ creating interface for the visualizations

✅ automating daily scraping and processing


data presentations:

* total games per day by realm, all realms (line)

* total games per day by gametype, each realm (line)

* separated by gametype: average games per hour over week (week/hour heatmap)

* internal statistics (table)


some useful gameIDs:

azeroth 21190538 = jan 1 2015

(728k games in 2015)

azeroth 21919343 = jan 1 2016

(518k games in 2016)

azeroth 22437878 = jan 1 2017

azeroth 22671000 = june 20 2017 9pm


northrend 71407047 = jan 1 2015

(3.484m games in 2015)

northrend 74891032 = jan 1 2016

(1.791m games in 2016)

northrend 76682523 = jan 1 2017

northrend 77664000 = june 26 2017 2pm


lordaeron 14277875 = jan 1 2015

(366k games in 2015)

lordaeron 14644695 = jan 1 2016

(397k games in 2016)

lordaeron 15042407 = jan 1 2017


kalimdor 30143853 = jan 1 2015

(1.280m games in 2015)

kalimdor 31424145 = jan 1 2016

(1.127m games in 2016)

kalimdor 32551595 = jan 1 2017