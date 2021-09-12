LEADERBOARD BOT
===========
Leaderboard bot allows you to access leaderboard data from steam and create a more competition in your discord servers. Currently Only for Portal 2

Using discord.py
-----------
.. image:: https://img.shields.io/pypi/v/discord.py.svg
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/discord.py.svg
   :target: https://pypi.python.org/pypi/discord.py
   :alt: PyPI supported Python versions   
   
A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.


Commands
-----------
`%` prefix

- time: 
	Allows you to set and view 
	%time {map name/code} {discord  user (optional)} {set new time (optional)}`
- setSteamId:
	Associates a steam id to discord user. This allows the bot to update the users leaderboard score
	`%setSteamId {discord user/mention} {steam id}`
- choosemap:
	randomly selects a map
	`%choosemap {singleplayer/native/category e.c.t}`
- update:
	Forces the bot to update all the leaderboard scores from the steam leaderboards
	`%update {map name/code (optional)}`
- startUpdating:
	Starts a loop to have the update all scores
- stopUpdating:
	Stops the loop to have the bot update
- reCheck:
	Checks through everyone on the server and adds them to a list# Leaderboards
	
Installation
-----------
**REPLIT**

1. On https://replit.com, click the plus arrow. 

2. Hit import from github. 

3. Enter `github.com/GalacticKittenSS/Leaderboards`. 

4. Click import from github.

**UP TIME ROBOT**

1. Copy the url of the repl

2. On https://uptimerobot.com, Sign Up/Log In and go to dashboard. 

3. Add new monitor:

* Monitor type: HTTP(S). 

* Url (or ip): replit url

* Monitering Interval: <20 minutes

4. Create New Monitor

**Finally**
Run Repl
