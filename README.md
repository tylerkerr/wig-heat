# wig-heat
a set of Python3 tools to scrape, process, and visualize the data on [Blizzard's war3 battle.net ladders listings](http://classic.battle.net/war3/ladder/w3xp-ladders.aspx?Gateway=Northrend).

todo:

✅ sequential scraping with error handling

✅ parsing game info from html

✅ writing gamedata to sql db

✅ scraping many games (currently have june 20 thru june 25 on useast)

✅ discarding non-TFT games (mappool, find roc/tft ratio, extrapolate on overlap games)

❌ figuring out which data to visualize

❌ writing queries to pass this data to d3.js

❌ creating visualizations with d3.js

❌ creating interface for the visualizations

❌ automating daily scraping and processing


data presentations:
* total games per day over year (stacked bar of all gametypes)
* separated by gametype: average games per hour over week (heatmap)
* ???


some useful gameIDs:
azeroth 21919343 = jan 1 2016
azeroth 22437878 = jan 1 2017
azeroth 22671000 = june 20 2017 9pm

northrend 76682523 = jan 1 2017
northrend 77664000 = june 26 2017 2pm