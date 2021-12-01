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

Installation
-----------

1. Head to [https://discord.com/api/oauth2/authorize?client_id=862608581119180811&permissions=75840&scope=bot](Leaderboard Bot)

2. Select Sever you wish to add it to.

3. Head to the Server and type `%setup [prefix you wish to use] [roles that can change others data]`

QnA
-----------
`%` prefix by default

* What is Leaderboard bot?

	* Leaderboard bot is a discord bot that accesses the steam leaderboards to gather leaderboard data among discord server's.


* What does Leaderboard bot do?

	* Leaderboard bot will give you up to date information about specific Portal 2 leaderboard data in the discord server.


* How does it do it?

	* By associating a discord user to a steam id, Leaderboard bot is able to access data from steam leaderboards and update its own data base. 


* How do I use Leaderboard bot?

	* In order to access the commands just type in chat using an % and the name of the command. You must first enter your steam account id in order for the bot to update your scores. You can also use %help to bring up a list of commands


* How do I set my Steam Account Id?

	* You can set your id by entering `%setSteamId` follow by `@self` and your id.
	* For example: `%setSteamId @GalacticKittenSS#4954  12345678912345678`


* Where do i find my steam account id?

	* You can find your id by heading to https://store.steampowered.com/account/ and logging in. You should find your id under `steam name` Account.


* When does leaderboard bot update?

	* Leaderboard bot updates every 24 hours at 6am GMT


Commands
-----------
`%` prefix by default

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
	Checks through everyone on the server and adds them to a list
	
