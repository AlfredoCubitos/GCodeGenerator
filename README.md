# GCodeGenerator
## Tool for generating g-code of simple objects

### Inspired by GCodeGenerator_Geometricals of mrRobot62

GCodeGenerator_Geometricals is a nice tool to generate g-code.
Unfortunately the tool was written in python 2.7 using Tkinter, which won't run with python3.

I decided to rewrite this tool using PyQt5.

This tool is in a very early stage, but it works.

For documentation have a look at the [wiki](https://github.com/mrRobot62/GCodeGenerator_Geometricals/wiki) of GCodeGenerator_Geometricals

### New in this release
Using ini-format for storing application parameter
Before closing the app stores the machine parameters into an ini file
and restores them when starting next time.
