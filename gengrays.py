#!/usr/bin/env python3

red = 0xff
blue = 0xff
green = 0xff

print("[", end='')

for i in range(0,256):
    hexcolor = '"#' + format(red, 'x') + format(blue, 'x') + format(green, 'x') + '", '
    red -= 1
    blue -= 1
    green -= 1
    print(hexcolor, end='')

print("]")


'''

egrep '.{6}' whitetolb.txt | head -n 61 | tr '[:upper:]' '[:lower:]' | sed 's/^/"#/g' | sed 's/$/", /g' | tr -d '\n'

'''