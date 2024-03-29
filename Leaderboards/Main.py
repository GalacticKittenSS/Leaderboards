import discord
from discord.ext import commands

import os
import time
import random

import Alive
import SteamLeaderboards
import Storage
import CustomHelp
import Utils
import Logger

#Setup Bot
async def get_prefix(client, message):
  settings = await Utils.GetSettings(message.guild.id)
  return settings.get("Prefix", "%")

activity = discord.Game(name="Now Using discord.py 2.0", type=3)
customHelp = CustomHelp.Help()
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=(get_prefix), intents=intents, help_command=customHelp, activity=activity, status=discord.Status.online)
client.sync_tree = False #Only sync if changes have been made to hybrid commands 

#EVENTS
#On Bot Ready
@client.event
async def on_ready():
  Logger.Setup(
    level = Logger.INFO,
    filelevel = Logger.DEBUG,
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    filename = "Leaderboards.log"
  )
  
  if client.sync_tree:
    Logger.Info("Syncing Bot Tree...")
    await client.tree.sync()
    client.sync_tree = False
  
  Logger.Info(f"Logged in as {client.user}.")

#COMMANDS
@client.hybrid_command(help="Setup the bot with custom settings (Moderators Only)")
async def setup(ctx, prefix:str, *, roles):
  settings = await Utils.GetSettings(ctx.guild.id, ctx, False)

  if settings:
    if not await Utils.UserHasRequiredRoles(settings["Roles"], ctx.author, ctx):
      return

  roles = roles.split(", ")

  file = {}
  file["Prefix"] = prefix
  file["Roles"] = roles
  
  file["PBList"] = { }
  file["PBList"]["Channel"] = ""
  file["PBList"]["Message"] = ""
  
  Utils.DumpJson(f"{Storage.SettingsDirectory}{ctx.guild.id}.json", file)
  await ctx.send(f"Setup Server with prefix {prefix} and mod roles {roles}!")

#Gets and sets leaderboard time
@client.hybrid_command(help="View a leaderboard of times", aliases=["lb"])
async def leaderboard(ctx, map=None, user:commands.MemberConverter=None):
  await ctx.defer()
  
  if not await Utils.FindSettings(ctx.guild.id, ctx):
    return
  
  preMsg = None
  if ctx.prefix != "/":
    preMsg = await ctx.reply("Getting Leaderboards...")
  
  tic = time.perf_counter()
  Logger.Info("Getting Leaderboards...")

  listOfMaps = Utils.LoadJson(Storage.MapsPath)
  map = Utils.GetDictionaryKey(listOfMaps, map) 

  if map == None:
    map = "Singleplayer No SLA"   

  url = None
  result = "Could Not Find Result"
  
  try:
    if not user:
      #Get General Results for Specific Map

      #Load Leaderboard
      lb = SteamLeaderboards.LeaderboardGroup(620, ctx.guild.id)
      lb.LoadNicknames(Storage.NicknamesPath)

      #If file exist add file data to leaderboard
      lb.CreateFromFile(f"{Storage.MapsDirectory}{listOfMaps[map]}.json")
      
      #If map is on steam Leaderboards, add to leaderboard group
      if listOfMaps[map] not in Storage.NonNative:
        lb.LoadSteamIDs(Storage.IDsPath)
        lb.CreateFromSteam(f"challenge_besttime_{listOfMaps[map]}")
        url = lb.SteamLeaderboardNumber()
        
      #Get Result and Order from Leaderboard Group
      result = lb.GetResult()
    else:
      #Get User Specific Result

      #If map is on Steam Leaderboards, Get Rank and Score
      if listOfMaps[map] not in Storage.NonNative:
        
        #Get Steam Id's
        ids = Utils.LoadJson(Storage.IDsPath)[str(ctx.guild.id)]
        
        #Get Leaderboard from Map
        lb = SteamLeaderboards.Leaderboard(620, f"challenge_besttime_{listOfMaps[map]}")
        
        #Find and Get Entry
        score = lb.GetEntry(ids[user.name])
        
        #Set Result
        url = lb.GetUrl().split('/')[6]
        result = f"**{user.name}**'s score on **{map}** is **{score.getTime()}**\n and is placed **#{score.getRank()}** on Steam leaderboards"
      
      #If file exist add file data to result
      if os.path.exists(f"{Storage.MapsDirectory}{listOfMaps[map]}.json"):
          #Get Map and Score from file
          score = Utils.LoadJson(f"{Storage.MapsDirectory}{listOfMaps[map]}.json")[ctx.guild.id][user.name]
          #Set Result
          result = f"**{user.name}**'s score on **{map}** is **{score}**"

    content = "Showing Results:"
    if url:
      #If we manage to get URL of map
      embed = discord.Embed(title=f"{map}", description=result, colour=discord.Colour(0x8d78b9), url=f"https://board.portal2.sr/chamber/{url}")
    else:
      #If we don't manage to get URL of map
      embed = discord.Embed(title=f"{map}", description=result, colour=discord.Colour(0x8d78b9))
   
  #If Exception was raised
  except Exception as e:
    Logger.Error(f"Unable to retrieve results due to fatal error: {e}")
    embed = discord.Embed(title=f"{e}", description=f"Unable to retrieve results due to fatal error: {e}", colour=discord.Colour(0x8d78b9))
    content = "An Error Occured:"

  toc = time.perf_counter()
  Logger.Info(f"Finished in {(toc - tic):0.4} Seconds\n")
  
  #Show Results
  if not preMsg:
    await ctx.reply(content=content, embed=embed)
  else:
    await preMsg.edit(content=content, embed=embed)

#Sets Time for User in File
@client.hybrid_command(name="time", help="Set a users time on a specific map", alias=["settime"])
async def settime(ctx, map, new_time, user:commands.MemberConverter=None):
  settings = await Utils.GetSettings(ctx.guild.id, ctx)
  if not settings:
    return
    
  if user == None:
    user = ctx.author
  elif user != ctx.author:
    hasRequiredRoles = await Utils.UserHasRequiredRoles(settings["Roles"], user, ctx)
    if not hasRequiredRoles:
      return

  listOfMaps = Utils.LoadJson(Storage.MapsPath)
  map = Utils.GetDictionaryKey(listOfMaps, map)    

  js = Utils.LoadJson(f"{Storage.MapsDirectory}{listOfMaps[map]}.json")

  if str(ctx.guild.id) not in js:
    js[str(ctx.guild.id)] = {}
	
  js[str(ctx.guild.id)][user.name] = new_time

  Utils.DumpJson(f"{Storage.MapsDirectory}{listOfMaps[map]}.json", js)
  await ctx.send(f"{user.name}'s' new time is **{new_time}**")
  
  # Edit PB List
  if listOfMaps[map] == "singleplayer":
    lb = SteamLeaderboards.LeaderboardGroup(620, ctx.guild.id)
    lb.LoadNicknames(Storage.NicknamesPath)
    lb.CreateFromFile(f"{Storage.MapsDirectory}singleplayer.json")
    result = lb.GetResult()

    pbList = Utils.LoadJson(f"Settings/{ctx.guild.id}.json")["PBList"]
    message = await client.get_channel(pbList["Channel"]).fetch_message(pbList["Message"])
    await message.edit(content=result)

#Sets Member steam ID 
@client.hybrid_command(help= "Set your steam id", aliases=["setsteamid", "setid", "id"])
async def steamid(ctx, id, user: commands.MemberConverter=None):
  settings = await Utils.GetSettings(ctx.guild.id, ctx)
  if not settings:
    return
  
  if user == None:
    user = ctx.author
  elif user != ctx.author:
    hasRequiredRoles = await Utils.UserHasRequiredRoles(settings["Roles"], user, ctx)
    if not hasRequiredRoles:
      return

  new = Utils.LoadJson(Storage.IDsPath)

  if str(ctx.guild.id) not in new:
    new[str(ctx.guild.id)] = {}

  new[str(ctx.guild.id)][user.name] = str(id)
  
  Utils.DumpJson(Storage.IDsPath, new)
  await ctx.reply(f"Set Steam Id for {user.name}")

@client.hybrid_command(help="Creates personal best temporary message (Moderator Only)")
async def message(ctx, message):
  settings = await Utils.GetSettings(ctx.guild.id, ctx)
  if not settings:
    return
    
  msg = await ctx.channel.send(message)
  settings["PBList"]["Channel"] = ctx.channel.id
  settings["PBList"]["Message"] = msg.id

  Utils.DumpJson(f"Settings/{ctx.guild.id}.json", settings)

@client.hybrid_command(help="Set your leaderboard nickname", alias=["setnickname"])
async def nickname(ctx, nickname, user:commands.MemberConverter=None):
  settings = await Utils.GetSettings(ctx.guild.id, ctx)
  if not settings:
    return
    
  if user == None:
    user = ctx.author
  elif user != ctx.author:
    hasRequiredRoles = await Utils.UserHasRequiredRoles(settings["Roles"], user, ctx)
    if not hasRequiredRoles:
      return

  nicknames = Utils.LoadJson(Storage.NicknamesPath)

  if str(ctx.guild.id) not in nicknames:
    nicknames[str(ctx.guild.id)] = {}

  nicknames[str(ctx.guild.id)][user.name] = nickname

  Utils.DumpJson(Storage.NicknamesPath, nicknames)
  await ctx.reply(content=f"Set {user.name}'s nickname to {nickname}")

  # Edit PB Message
  if os.path.exists(F"{Storage.MapsDirectory}singleplayer.json"):
    lb = SteamLeaderboards.LeaderboardGroup(620, ctx.guild.id)
    lb.LoadNicknames(Storage.NicknamesPath)
    lb.CreateFromFile(f"{Storage.MapsDirectory}singleplayer.json")
    result = lb.GetResult()

    pbList = Utils.LoadJson(f"Settings/{ctx.guild.id}.json")["PBList"]
    message = await client.get_channel(pbList["Channel"]).fetch_message(pbList["Message"])
    await message.edit(content=result)

#Spit out a random map
@client.hybrid_command(help="Spit out a random map", aliases=["map", "choose"])
async def choosemap(ctx, cat_type="all"):
  maps = Utils.LoadJson(Storage.MapsPath)
  map_set = set(maps.values())
  map_lists = {
    "all" :           list(maps.keys()),
    "maps" :          list(map_set.difference(set(Storage.Categories))),
    "singleplayer" :  list(map_set.difference(set(Storage.Coop))),
    "native" :        list(map_set.difference(set(Storage.NonNative))),
    "coop":           Storage.Coop,
    "nonnative":      Storage.NonNative, 
    "category":       Storage.Categories 
  }

  choice = random.choice(map_lists.get("singleplayer".lower()))
  await ctx.reply(f"{Utils.GetDictionaryKey(maps, choice)} ({choice}) has been selected from {cat_type}.")

#START
Alive.keep_alive()
Storage.Client = client
client.run(Storage.BotKey)