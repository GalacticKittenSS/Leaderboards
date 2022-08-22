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

#SetUp
async def get_prefix(client, message):
  settings = await Utils.GetSettings(message.guild.id)
  prefix = "%"
  
  if settings:
    prefix = settings["Prefix"]
  
  return prefix

activity = discord.Game(name="Now Using discord.py 2.0", type=3)
customHelp = CustomHelp.Help()

#SetUp Bot
client = commands.Bot(command_prefix=(get_prefix), intents=discord.Intents.all(), help_command=customHelp, activity=activity, status=discord.Status.online)

#Directories/Paths
maps_directory = Storage.MapsDirectory
settings_directory = Storage.SettingsDirectory

maps_path = Storage.MapsPath
nicknames_path = Storage.NicknamesPath
ids_path = Storage.IDsPath

#Maps/Categories
nonNative = Storage.NonNative
categories = Storage.Categories
coop = Storage.Coop

#EVENTS
#On Bot Ready
@client.event
async def on_ready():
  Logger.Info(f"Logged in as {client.user}.")

#Update Help List
@client.event
async def on_raw_reaction_add(payload):
  await customHelp.reaction(client, payload)

#COMMANDS
@client.command()
async def setup(ctx, prefix:str, *roles):
  settings = await Utils.GetSettings(ctx.guild.id, ctx, False)

  if settings:
    if not await Utils.UserHasRequiredRoles(settings["Roles"], ctx.author, ctx):
      return

  file = {}
  
  file["Prefix"] = prefix
  
  file["Roles"] = roles
  
  file["PBList"] = { }
  file["PBList"]["Channel"] = ""
  file["PBList"]["Message"] = ""
  
  file["Help"] = { }
  file["Help"]["Channel"] = ""
  file["Help"]["Message"] = ""
  file["Help"]["Index"] = -1

  Utils.DumpJson(f"{settings_directory}{ctx.guild.id}.json", file)
  await ctx.send(f"Setup Server with prefix {prefix} and mod roles {roles}!")

#Gets and sets leaderboard time
@client.command(help="View a leaderboard of times", aliases=["time", "lb"])
async def leaderboard(ctx, map=None, user:commands.MemberConverter=None):
  if not await Utils.FindSettings(ctx.guild.id, ctx):
    return
    
  tic = time.perf_counter()
  
  #await ctx.message.delete()
  preMsg = await ctx.send("Getting Leaderboards...")
  Logger.Info("Getting Leaderboards...")

  listOfMaps = Utils.LoadJson(maps_path)
  map = Utils.FindValueInArray(map, listOfMaps) 

  if map == None:
    map = "Singleplayer No SLA"   

  url = None
  result = "Could Not Find Result"
  
  try:
    if not user:
      #Get General Results for Specific Map

      #Load Leaderboard
      lb = SteamLeaderboards.LeaderboardGroup(620, ctx.guild.id)
      lb.LoadNicknames(nicknames_path)

      #If file exist add file data to leaderboard
      lb.CreateFromFile(f"{maps_directory}{listOfMaps[map]}.json")
      
      #If map is on steam Leaderboards, add to leaderboard group
      if listOfMaps[map] not in nonNative:
        lb.LoadSteamIDs(ids_path)
        lb.CreateFromSteam(f"challenge_besttime_{listOfMaps[map]}")
        url = lb.SteamLeaderboardNumber()
        
      #Get Result and Order from Leaderboard Group
      result = lb.GetResult()
    else:
      #Get User Specific Result

      #If map is on Steam Leaderboards, Get Rank and Score
      if listOfMaps[map] not in nonNative:
        
        #Get Steam Id's
        ids = Utils.LoadJson(ids_path)[str(ctx.guild.id)]
        
        #Get Leaderboard from Map
        lb = SteamLeaderboards.Leaderboard(620, f"challenge_besttime_{listOfMaps[map]}")
        
        #Find and Get Entry
        score = lb.GetEntry(ids[user.name])
        
        #Set Result
        url = lb.GetUrl().split('/')[6]
        result = f"**{user.name}**'s score on **{map}** is **{score.getTime()}**\n and is placed **#{score.getRank()}** on Steam leaderboards"
      
      #If file exist add file data to result
      if os.path.exists(f"{maps_directory}{listOfMaps[map]}.json"):
          #Get Map and Score from file
          score = Utils.LoadJson(f"{maps_directory}{listOfMaps[map]}.json")[ctx.guild.id][user.name]
          #Set Result
          result = f"**{user.name}**'s score on **{map}** is **{score}**"

    if url:
      #If we manage to get URL of map
      embed = discord.Embed(title=f"{map}", description=result, colour=discord.Colour(0x8d78b9), url=f"https://board.portal2.sr/chamber/{url}")
    else:
      #If we don't manage to get URL of map
      embed = discord.Embed(title=f"{map}", description=result, colour=discord.Colour(0x8d78b9))
    
    #Show Resultss by editing message
    await preMsg.edit(content="Showing Results:", embed=embed)

  #If Exception was raised
  except Exception as e:
    Logger.Error(f"Unable to retrieve results due to fatal error: {e}")
    embed = discord.Embed(title=f"{e}", description=f"Unable to retrieve results due to fatal error: {e}", colour=discord.Colour(0x8d78b9))
    await preMsg.edit(content="An Error Occured:", embed=embed)

  toc = time.perf_counter()
  Logger.Info(f"Finished in {(toc - tic):0.4} Seconds\n")

#Sets Time for User in File
@client.command(help="Set a users time on a specific map")
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

  listOfMaps = Utils.LoadJson(maps_path)
  map = Utils.FindValueInArray(map, listOfMaps)    

  js = Utils.LoadJson(f"{maps_directory}{listOfMaps[map]}.json")

  if str(ctx.guild.id) not in js:
    js[str(ctx.guild.id)] = {}
	
  js[str(ctx.guild.id)][user.name] = new_time

  Utils.DumpJson(f"{maps_directory}{listOfMaps[map]}.json", js)

  await ctx.send(f"{user.name}'s' new time is **{new_time}**")
  
  if listOfMaps[map] == "singleplayer":
    lb = SteamLeaderboards.LeaderboardGroup(620, ctx.guild.id)
    
    if not os.path.exists(nicknames_path):
      Utils.DumpJson(nicknames_path, {f"{ctx.guild.id}": {}})

    lb.CreateFromFile(f"{maps_directory}singleplayer.json", nicknames_path)
    result = lb.getResult()

    
    pbList = Utils.LoadJson(f"Settings/{ctx.guild.id}.json")["PBList"]
    message = await client.get_channel(pbList["Channel"]).fetch_message(pbList["Message"])
    await message.edit(content=result)
  

#Sets Member steam ID 
@client.command(help= "Set your steam id", aliases=["steam", "setid", "id"])
async def setsteamid(ctx, id, user: commands.MemberConverter=None):
  if not await Utils.FindSettings(ctx.guild.id, ctx):
    return
  
  if user == None:
    user = ctx.author
  elif user != ctx.author:
    hasRequiredRoles = await Utils.UserHasRequiredRoles(settings["Roles"], user, ctx)
    if not hasRequiredRoles:
      return

  new = Utils.LoadJson(ids_path)

  if str(ctx.guild.id) not in new:
    new[str(ctx.guild.id)] = {}

  new[str(ctx.guild.id)][user.name] = str(id)
  
  Utils.DumpJson(ids_path, new)
  await ctx.send(f"Set Steam Id for {user.name}")

@client.command()
async def message(ctx, message):
  settings = await Utils.GetSettings(ctx.guild.id, ctx)
  if not settings:
    return
    
  msg = await ctx.channel.send(message)
  settings["PBList"]["Channel"] = ctx.channel.id
  settings["PBList"]["Message"] = msg.id

  Utils.DumpJson(f"Settings/{ctx.guild.id}.json", settings)

@client.command()
async def setnickname(ctx, nickname, user:commands.MemberConverter=None):
  settings = await Utils.GetSettings(ctx.guild.id, ctx)
  if not settings:
    return
    
  if user == None:
    user = ctx.author
  elif user != ctx.author:
    hasRequiredRoles = await Utils.UserHasRequiredRoles(settings["Roles"], user, ctx)
    if not hasRequiredRoles:
      return

  nicknames = Utils.LoadJson(nicknames_path)

  if str(ctx.guild.id) not in nicknames:
    nicknames[str(ctx.guild.id)] = {}

  nicknames[str(ctx.guild.id)][user.name] = nickname

  Utils.DumpJson(nicknames_path, nicknames)

  await ctx.send(content=f"Set {user.name}'s nickname to {nickname}")

  if os.path.exists(F"{maps_directory}singleplayer.json") and ctx.guild.id == 772972878106198028:
    lb = SteamLeaderboards.LeaderboardGroup(620, ctx.guild.id)
    lb.CreateFromFile(f"{maps_directory}singleplayer.json", nicknames_path)
    result = lb.GetResult()

    message = await client.get_channel(Storage.pbChannel).fetch_message(Storage.pbMessage)
    await message.edit(content=result)

#Spit out a random map
@client.command(help="Spit out a random map", aliases=["map", "choose"])
async def choosemap(ctx, cat_type=None):
  maps = Utils.LoadJson(maps_path)
  mapList = []

  if not cat_type:
    cat_type = "All"

  if cat_type.lower() == "nonnative":
    mapList = nonNative
  if cat_type.lower() == "category":
    mapList = categories
  elif cat_type.lower() == "coop":
    mapList = coop
  else:
    for (key, val) in maps.items():
      if cat_type.lower() == "all":
        mapList.append(val)
      elif cat_type.lower() == "native" and val not in nonNative:
        mapList.append(val)
      elif cat_type.lower() == "maps" and val not in categories:
        mapList.append(val)
      elif cat_type.lower() == "singleplayer" and val not in coop:
        mapList.append(val)
  
  choice = random.choice(mapList)
  await ctx.send(f"{Utils.FindValueInArray(choice, maps)} ({choice}) has been selected from {cat_type}.")

#START
Storage.Client = client
client.run(Storage.BotKey)
Alive.keep_alive()