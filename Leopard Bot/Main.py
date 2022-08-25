import discord
from discord.ext import commands

import os
import time
import random

import FierceLeopard

import Alive
import Storage
import CustomHelp
import Utils
import Logger

#Setup Bot
async def get_prefix(client, message):
  settings = await Utils.GetSettings(message.guild.id)
  prefix = "%"
  
  if settings:
    prefix = settings["Prefix"]
  
  return prefix

activity = discord.Game(name="Now Using discord.py 2.0", type=3)
customHelp = CustomHelp.Help()
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=(get_prefix), intents=intents, help_command=customHelp, activity=activity, status=discord.Status.online)
client.sync_tree = False #Only sync if changes have been made to hybrid commands 

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
  
  Utils.DumpJson(f"{settings_directory}{ctx.guild.id}.json", file)
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

  listOfMaps = Utils.LoadJson(maps_path)
  map = Utils.FindValueInArray(map, listOfMaps) 

  if map == None:
    map = "Singleplayer No SLA"   

  url = None
  result = "Could Not Find Result"
  
  try:
    if not user:
      #Get General Results for Specific Map

      #Load App Ranker
      ranker = FierceLeopard.AppRanker(620)
      ranker.nicknames = Utils.LoadJsonForGuild(nicknames_path, ctx.guild.id)
      #If file exist add file data to leaderboard
      filename = f"{maps_directory}{listOfMaps[map]}.json"
      file = Utils.LoadJsonForGuild(filename, ctx.guild.id)
      ranker.LoadDict(file, filename)
      
      #If map is on steam Leaderboards, add to App Ranker
      if listOfMaps[map] not in nonNative:
        ranker.steam_ids = Utils.LoadJsonForGuild(ids_path, ctx.guild.id)
        ranker.LoadLeaderboard(f"challenge_besttime_{listOfMaps[map]}")
        url = ranker.leaderboard_number
        
      #Get Result and Order from App Ranker
      result = ranker.GetResult()
    else:
      #Get User Specific Result

      #If map is on Steam Leaderboards, Get Rank and Score
      if listOfMaps[map] not in nonNative:
        
        #Get Steam Id's
        ids = Utils.LoadJsonForGuild(ids_path, ctx.guild.id)
        
        #Get Leaderboard from Map
        lb = FierceLeopard.Leaderboard(620, f"challenge_besttime_{listOfMaps[map]}")
        
        #Find and Get Entry
        entry = lb.GetEntry(ids[user.name])
        
        #Set Result
        url = lb.GetUrl().split('/')[6]
        result = f"**{user.name}**'s score on **{map}** is **{entry.time}**\n and is placed **#{entry.rank}** on Steam leaderboards"
      
      #If file exist add file data to result
      if os.path.exists(f"{maps_directory}{listOfMaps[map]}.json"):
        #Get Map and Score from file
        score = Utils.LoadJsonForGuild(f"{maps_directory}{listOfMaps[map]}.json", ctx.guild.id)[user.name]
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

  listOfMaps = Utils.LoadJson(maps_path)
  map = Utils.FindValueInArray(map, listOfMaps)    

  js = Utils.LoadJson(f"{maps_directory}{listOfMaps[map]}.json")

  if str(ctx.guild.id) not in js:
    js[str(ctx.guild.id)] = {}
	
  js[str(ctx.guild.id)][user.name] = new_time

  Utils.DumpJson(f"{maps_directory}{listOfMaps[map]}.json", js)
  await ctx.send(f"{user.name}'s' new time is **{new_time}**")
  
  # Edit PB List
  if listOfMaps[map] == "singleplayer":
    await Utils.EditPBMesage()

#Sets Member steam ID 
@client.hybrid_command(help= "Set your steam id", aliases=["setsteamid", "setid", "id"])
async def steamid(ctx, id, user: commands.MemberConverter=None):
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
  await ctx.reply(f"Set Steam Id for {user.name}")

@client.hybrid_command(help="Creates personal best temporary message (Moderator Only)")
async def message(ctx):
  settings = await Utils.GetSettings(ctx.guild.id, ctx)
  if not settings:
    return
    
  msg = await ctx.channel.send(message)
  settings["PBList"]["Channel"] = ctx.channel.id
  settings["PBList"]["Message"] = msg.id

  Utils.DumpJson(f"Settings/{ctx.guild.id}.json", settings)

  await Utils.EditPBMesage()

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

  nicknames = Utils.LoadJson(nicknames_path)

  if str(ctx.guild.id) not in nicknames:
    nicknames[str(ctx.guild.id)] = {}

  nicknames[str(ctx.guild.id)][user.name] = nickname

  Utils.DumpJson(nicknames_path, nicknames)
  await ctx.reply(content=f"Set {user.name}'s nickname to {nickname}")

  # Edit PB Message
  if os.path.exists(F"{maps_directory}singleplayer.json"):
    await Utils.EditPBMesage()

#Spit out a random map
@client.hybrid_command(help="Spit out a random map", aliases=["map", "choose"])
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
  await ctx.reply(f"{Utils.FindValueInArray(choice, maps)} ({choice}) has been selected from {cat_type}.")

#START
Storage.Client = client
client.run(Storage.BotKey)
Alive.keep_alive()