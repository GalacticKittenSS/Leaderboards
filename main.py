import steamlb
import alive
import json
import random
import help
import storage
import os
import discord
import time
from discord.ext import commands
 
#SetUp
activity = discord.Game(name="%map, What should we play today? %help", type=3)

#SetUp Bot
client = commands.Bot(command_prefix=storage.prefix, intents=discord.Intents.all(), help_command=help.CustomHelp(), activity=activity, status=discord.Status.online)

#Maps Categories
nonNative = storage.NonNative
category = storage.category
coop = storage.coop

#EVENTS
#On Bot Ready
@client.event
async def on_ready():
  print(f"Logged in as {client.user}.")

#Update Help List
@client.event
async def on_raw_reaction_add(payload):
  await help.reaction(client, payload)

#COMMANDS
#Gets and sets leaderboard time
@client.command(help="Returns a Leaderboard of all known times", aliases=["getTime", "gettime", "Time", "time", "lb"])
async def leaderboard(ctx, map=None, user:commands.MemberConverter=None):
  tic = time.perf_counter()
  
  #await ctx.message.delete()
  preMsg = await ctx.send("Getting Leaderboards...")

  with open("Leaderboards/.maps.json", "r") as f:
    listOfMaps = json.load(f)
  
  if map not in listOfMaps:
    for key in listOfMaps:
      if listOfMaps[key] == map:
        map = key
        break
      

  url = None
  result = "Could Not Find Result"
  
  try:
    if user == None:
      #Get General Results for Specific Map

      #Load Leaderboard
      lb = steamlb.LeaderboardGroup(620, ctx.guild.id)
      
      #If file exist add file data to leaderboard
      if os.path.exists(f"Leaderboards/{listOfMaps[map]}.json"):
        lb.createFromFile(f"Leaderboards/{listOfMaps[map]}.json", "nicknames.json")
      
      #If map is on steam Leaderboards, add to leaderboard group
      if listOfMaps[map] not in nonNative:
        lb.createFromSteam("steam_id.json", "nicknames.json", f"challenge_besttime_{listOfMaps[map]}")
        url = lb.getUrl().split('/')[6]
      
      #Get Result and Order from Leaderboard Group
      result = lb.getResult()
    
    else:
      #Get User Specific Result

      #If map is on Steam Leaderboards, Get Rank and Score
      if listOfMaps[map] not in nonNative:
        
        #Get Steam Id's
        with open(f"steam_id.json", "r") as f:
          ids = json.load(f)[str(ctx.guild.id)]

        #Get Leaderboard from Map
        lb = steamlb.Leaderboard(620, f"challenge_besttime_{listOfMaps[map]}")
        
        #Find and Get Entry
        score = lb.getEntry(ids[user.name])
        
        #Set Result
        url = lb.getUrl().split('/')[6]
        result = f"**{user.name}**'s score on **{map}** is **{score.getTime()}**\n and is placed **#{score.getRank()}** on Steam leaderboards"
      
     #If file exist add file data to result
      if os.path.exists(f"Leaderboards/{listOfMaps[map]}.json"):
        #Get Map and Score from file
        with open(f"Leaderboards/{listOfMaps[map]}.json", "r") as f:
          score = json.load(f)[ctx.guild.id][user.name]
          #Set Result
          result = f"**{user.name}**'s score on **{map}** is **{score}**"

    if url == None:
      #If we don't manage to get URL of map
      embed = discord.Embed(title=f"{map}", description=result, colour=discord.Colour(0x8d78b9))
    else:
      #If we manage to get URL of map
      embed = discord.Embed(title=f"{map}", description=result, colour=discord.Colour(0x8d78b9), url=f"https://board.portal2.sr/chamber/{url}")
    
    #Show Resultss by editing message
    await preMsg.edit(content="Showing Results:", embed=embed)

  #If Exception was raised
  except Exception as e:
    print(e)
    embed = discord.Embed(title=f"{e}", description=f"Unable to retrieve results due to fatal error: {e}", colour=discord.Colour(0x8d78b9))
    await preMsg.edit(content="An Error Occured:", embed=embed)

  toc = time.perf_counter()
  print(f"Finished in {(toc - tic):0.4} Seconds")

#Sets Time for User in File
@client.command(help="Sets a Time for a User", aliases=["settime"])
async def setTime(ctx, map, nTime, user:commands.MemberConverter=None):
  if user == None:
    user = ctx.author
  elif user != ctx.author:
    roles = []
    for role in ctx.author.roles:
      roles.append(role.name)
    
    if (storage.modRole not in roles) and (storage.secondRole not in roles):
      return

  with open("Leaderboards/.maps.json", "r") as f:
    listOfMaps = json.load(f)
  
  if map not in listOfMaps:
    for key in listOfMaps:
      if listOfMaps[key] == map:
        map = key
        break

  if os.path.exists(f"Leaderboards/{listOfMaps[map]}.json"):
    with open(f"Leaderboards/{listOfMaps[map]}.json", "r") as f:
      js = json.load(f)
  else:
    js = {}
  
  if str(ctx.guild.id) not in js:
    js[str(ctx.guild.id)] = {}
	
  js[str(ctx.guild.id)][user.name] = nTime

  with open(f"Leaderboards/{listOfMaps[map]}.json", "w") as f:
    json.dump(js, f, indent=2)

  await ctx.send(f"{user.name}'s' new time is **{nTime}**")
  
  if listOfMaps[map] == "singleplayer" and ctx.guild.id == 772972878106198028:
    lb = steamlb.LeaderboardGroup(620, ctx.guild.id)
    
    if not os.path.exists("nicknames.json"):
      with open("nicknames.json", "w") as f:
        json.dump({f"{ctx.guild.id}": {}}, f, indent=2)

    lb.createFromFile(f"Leaderboards/singleplayer.json", "nicknames.json")
    result = lb.getResult()

    message = await client.get_channel(storage.pbChannel).fetch_message(storage.pbMessage)
    await message.edit(content=result)
  

#Sets Member steam ID 
@client.command(help= "Set your steam id", aliases=["steam", "setId", "id"])
async def setSteamId(ctx, id, member: commands.MemberConverter=None):
  if member == None:
    member = ctx.author
  elif member != ctx.author:
    roles = []
    for role in ctx.author.roles:
      roles.append(role.name)
    
    if (storage.modRole not in roles) and (storage.secondRole not in roles):
      return
  
  if os.path.exists("steam_id.json"):
    with open("steam_id.json", "r") as f:
      new = json.load(f)
  else:
    new = {}

  if str(ctx.guild.id) not in new:
    new[str(ctx.guild.id)] = {}

  new[str(ctx.guild.id)][member.name] = str(id)
  
  with open(f"steam_id.json", "w") as f:
    json.dump(new, f, indent=2)
    
  await ctx.send(f"Set Steam Id for {member.name}")

@client.command()
async def message(ctx, message):
  msg = await ctx.channel.send(message)
  storage.pbChannel = ctx.channel.id
  storage.pbMessage = msg.id

@client.command()
async def setNickname(ctx, nickname, user:commands.MemberConverter=None):
  if user == None:
    user = ctx.author
  elif user != ctx.author:
    roles = []
    for role in ctx.author.roles:
      roles.append(role.name)
    
    if (storage.modRole not in roles) and (storage.secondRole not in roles):
      return

  if os.path.exists("nicknames.json"):
    with open("nicknames.json", "r") as f:
      nicknames = json.load(f)
  else:
    nicknames = {}

  if str(ctx.guild.id) not in nicknames:
    nicknames[str(ctx.guild.id)] = {}

  nicknames[str(ctx.guild.id)][user.name] = nickname

  with open("nicknames.json", "w") as f:
    json.dump(nicknames, f, indent=2)

  await ctx.send(content=f"Set {user.name}'s nickname to {nickname}")

  if os.path.exists("Leaderboards/singleplayer.json") and ctx.guild.id == 772972878106198028:
    lb = steamlb.LeaderboardGroup(620, ctx.guild.id)
    lb.createFromFile("Leaderboards/singleplayer.json", "nicknames.json")
    result = lb.getResult()

    message = await client.get_channel(storage.pbChannel).fetch_message(storage.pbMessage)
    await message.edit(content=result)

#Spit out a random map
@client.command(help="Spit out a random map", aliases=["choosemap", "map", "choose"])
async def chooseMap(ctx, cont=None):
  with open("Leaderboards/.maps.json", "r") as f:
    maps = json.load(f)

  mapList = []
  
  if cont == "all" or cont == None:
    mapList = maps
  elif cont == "category":
    mapList = category
  elif cont == "coop":
    mapList = coop
  else:
    for map in maps:
      if cont == "native" and maps[map] not in nonNative:
        mapList.append(map)
      elif cont == "maps" and maps[map] not in category:
        mapList.append(map)
      elif cont == "singleplayer" and maps[map] not in coop:
        mapList.append(map)

  await ctx.send(random.choice(mapList))

#START
storage.client = client
alive.keep_alive()
client.run(storage.botStr)