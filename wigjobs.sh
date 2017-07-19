#!/bin/bash

wigdir=$(dirname "$0")
cd wigdir

echo "[-] starting ${0##*/} at $(date)"

echo "[-] scraping Northrend"
$wigdir/wigscraper.py Northrend | tail -n 20
echo "[-] scraping Azeroth"
$wigdir/wigscraper.py Azeroth | tail -n 20
echo "[-] scraping Lordaeron"
$wigdir/wigscraper.py Lordaeron | tail -n 20
echo "[-] scraping Kalimdor"
$wigdir/wigscraper.py Kalimdor | tail -n 20

echo "[-] entering maintenance mode"
mv $wigdir/index.html $wigdir/index.disabled
mv $wigdir/heatmaps/index.html $wigdir/heatmaps/index.disabled
mv $wigdir/stats/index.html $wigdir/stats/index.disabled
cp $wigdir/maintenance.html $wigdir/index.html
cp $wigdir/maintenance.html $wigdir/heatmaps/index.html
cp $wigdir/maintenance.html $wigdir/stats/index.html
echo "[+] maintenance mode enabled"
echo "[-] running queries"
$wigdir/wigquery.py
echo "[-] disabling maintenance mode"
mv $wigdir/index.disabled $wigdir/index.html
mv $wigdir/heatmaps/index.disabled $wigdir/heatmaps/index.html
mv $wigdir/stats/index.disabled $wigdir/stats/index.html
echo "[+] maintenance mode disabled"