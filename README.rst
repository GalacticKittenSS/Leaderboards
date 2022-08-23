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

Installing the Bot
-----------

1. Head to `Leaderboard Bot
<https://discord.com/api/oauth2/authorize?client_id=862608581119180811&permissions=75840&scope=bot>`_

2. Select Sever you wish to add it to.

3. Head to the Server and type `%setup [prefix you wish to use] [roles that can change others data]`

Installing the Repositry
-----------
1. Clone the github repositry using `git clone https://github.com/GalacticKittenSS/Leaderboards`. The repositry contains no submodules so `--recursive` will not be needed

2. Setup the repositry by using `pip install -r requirements.txt`. You can also use `Scripts/Setup.bat` to initialise the project. 

3. To run the scripts you can either use `python Leaderboards/Main.py` or run `Scripts/Start.bat` to start.

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

	* In order to access the commands just type in chat using an % and the name of the command. You must first enter your steam account id in order for the bot access your scores. You can also use %help to bring up a list of commands


* How do I set my Steam Account Id?

	* You can set your id by entering `%setSteamId` follow by `@self` and your id.
	* For example: `%setSteamId @GalacticKittenSS#4954  12345678912345678`


* Where do i find my steam account id?

	* You can find your id by heading to https://store.steampowered.com/account/ and logging in. You should find your id under `steam name` Account.

Commands
-----------
`%` prefix by default

- setup:
	Setup the bot with custom settings. This must be done first before anything else
	`%setup {prefix} [moderator roles]`
- leaderboard: 
	Allows you to view a leaderboard of times for a map or user
	`%leaderboard [map (optional)] [discord user/mention (optional)]`
- settime:
	Set a users time on a specific map
	`%settime {map} {new time} [discord user/mention (mod only)]`
- setsteamid:
	Associates a steam id to a discord user. This allows the bot to access the users leaderboard score on steam
	`%setSteamId {steam id} [discord user/mention (mod only)] `
- setnickname:
	Associates a nickname to a discord user. A nickname will be used instead of a discord name
	`%setNickname {nickname} [discord user/mention (mod only)]`
- choosemap:
	randomly selects a map
	`%chooseMap [type (singleplayer/native/category e.c.t)]`