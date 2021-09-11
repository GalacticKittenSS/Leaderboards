import os
import steamlb
import alive
import json
import random
from datetime import datetime as d
import help
import storage
import discord
from discord.ext import commands, tasks

#SetUp
activity = discord.Game(name="%chooseMap, What should we play today? %help", type=3)

client = commands.Bot(command_prefix='%', intents=discord.Intents.all(), help_command=help.CustomHelp(), activity=activity, status=discord.Status.online)

nonNative = ["singleplayer", "sp_a1_intro1", "sp_a1_intro2", "sp_a1_intro7", "sp_a1_wakeup", "sp_a2_laser_intro", "sp_a2_catapult_intro", "sp_a2_bts6", "sp_a2_core", "sp_a3_00", "sp_a4_intro", "sp_a4_finale1", "AMC", "glitchless", "inbounds", "oob", "sla", "inboundNoSla"]

category = ["singleplayer",  "AMC", "glitchless", "inbounds", "oob", "sla", "inboundNoSla"]

coop = ["mp_coop_doors", "mp_coop_race_2", "mp_coop_laser_2", "mp_coop_rat_maze", "mp_coop_laser_crusher", "mp_coop_teambts" "mp_coop_fling_3", "mp_coop_infinifling_train", "mp_coop_come_along", "mp_coop_fling_1", "mp_coop_catapult_1", "mp_coop_multifling_1", "mp_coop_fling_crushers", "mp_coop_fan", "mp_coop_wall_intro", "mp_coop_wall_2", "mp_coop_catapult_wall_intro", "mp_coop_wall_block", "mp_coop_catapult_2", "mp_coop_turret_walls", "mp_coop_turret_ball", "mp_coop_wall_5", "mp_coop_tbeam_redirect", "mp_coop_tbeam_drill","mp_coop_tbeam_catch_grind_1", "mp_coop_tbeam_laser_1", "mp_coop_tbeam_polarity", "mp_coop_tbeam_polarity2", "mp_coop_tbeam_polarity3", "mp_coop_tbeam_maze", "mp_coop_tbeam_end", "mp_coop_paint_come_along", "mp_coop_paint_redirect", "mp_coop_paint_bridge", "mp_coop_paint_walljumps", "mp_coop_paint_speed_fling", "mp_coop_paint_red_racer", "mp_coop_paint_speed_catch", "mp_coop_paint_longjump_intro", "mp_coop_separation_1", "mp_coop_tripleaxis", "mp_coop_catapult_catch", "mp_coop_2paints_1bridge", "mp_coop_paint_conversion", "mp_coop_bridge_catch", "mp_coop_laser_tbeam", "mp_coop_paint_rat_maze", "mp_coop_paint_crazy_box"]

#Adds member to all listed maps
def addMembertoMap(member):
  print(f"Adding Member: {member}")

  with open("Leaderboards/.maps.json", "r") as f:
    map = json.load(f)
    
    for value in map:
      with open(f"Leaderboards/{map[value]}.json", "r") as f:
        new = json.load(f)

      try:
        new[member.name] = new[member.name]
      except:
        new[member.name] = "unknown"
        
      with open(f"Leaderboards/{map[value]}.json", "w") as f:
        json.dump(new, f, indent=2)
        
    with open("steam_id.json", "r") as f:
      id = json.load(f)
      
    try:
      id[member.name] = id[member.name]
    except:
      id[member.name] = "unknown"
    
    with open("steam_id.json", "w") as f:
      json.dump(id, f, indent=2)

#Converts Seconds to Minutes and Seconds
def secs_to_min(seconds):
    a=int(seconds) //60
    b=int(seconds) %60
    if b < 10:
      b = f"0{b}"
    if a != 0:
      d="{}:{}".format(a, b)
    else:
      d="{}".format(b)
    return d

#Update the Individual Leaderboard
def updateLeaderboard(map, guild):
  if map in nonNative:
    return

  print(map + ":")

  with open(f"Leaderboards/{map}.json", "r") as f:
    lboard = json.load(f)

  with open(f"steam_id.json", "r") as f:
    ids = json.load(f)
  
  group = steamlb.LeaderboardGroup(620, name=f"challenge_besttime_{map}")
  steamLb = group.get()

  for member in ids:
    if guild.get_member_named(member) is not None:
      lboard[member] = updateMember(ids, member, steamLb)
    
  with open(f"Leaderboards/{map}.json", "w") as f:
    json.dump(lboard, f, indent=2) 

#Updates member on leaderboard list
def updateMember(ids, member, lb):
  if ids[member] == "unknown":
      return "unknown"

  print(member)
    
  try:
    entry = lb.find_entry(steam_id=int(ids[member]))
    score = entry.score.text
        
    secs, ms = score[:len(score) - 2], score[len(score) - 2:]
    tm = f"{secs_to_min(int(secs))}.{ms}"

    return tm
  except:
    return "unknown"

#Update all the times
@tasks.loop(seconds=60)
async def updateTimes(guild=None, map=None, forced=False):
  with open("updatetime.json", "r") as f:
    t = json.load(f)
    
  if str(d.now().strftime("%H:%M")) != f"{t['Hour']}:{t['Minute']}" and forced == False:
    return
  
  print(f"Updating Times ------ {d.now().strftime('%Y-%m-%d %H:%M:%S')}")

  await client.change_presence(activity=discord.Game(name="Updating Leaderboards │ %help", type=3), status=discord.Status.idle, afk=True)

  with open(f"Leaderboards/.maps.json", "r") as f:
    allBoards = json.load(f)

  if map == None:        
    for board in allBoards:
      map = allBoards[board]
      updateLeaderboard(map, guild)
  else:
    try:
      updateLeaderboard(map, guild)
    except:
      updateLeaderboard(allBoards[map], guild)

  
  await client.change_presence(activity=activity, status=discord.Status.online, afk=False)
        
  print(f"Finished at --------- {d.now().strftime('%Y-%m-%d %H:%M:%S')}")

#EVENTS
#On Bot Ready
@client.event
async def on_ready():
  print(f"Logged in as {client.user} at {d.now().strftime('%Y-%m-%d %H:%M:%S')}")

  guild = client.get_guild(772972878106198028)

  await updateTimes.start(guild=guild)

#Add member when joined
@client.event
async def on_member_join(member):
  addMembertoMap(member)

#Update Help List
@client.event
async def on_raw_reaction_add(payload):
  count = -1
  for value in storage.current_help_message:
    channel = client.get_channel(value.channel.id) 
    count = count + 1
    async for message in channel.history(limit=200):
      if message == storage.current_help_message[count] and payload.user_id != 862608581119180811 and message.id== payload.message_id:
        index = storage.current_help_index[count]

        if payload.emoji.name == "⏭️":
          index = index + 1
          await message.remove_reaction("⏭️", client.get_user(payload.user_id))
        if payload.emoji.name == "⏮️":
          index = index - 1
          await message.remove_reaction("⏮️", client.get_user(payload.user_id))

        if index == len(storage.current_help_commands) and len(storage.current_help_commands) > 0:
          index = -len(storage.current_help_commands)
        elif index == -len(storage.current_help_commands) and len(storage.current_help_commands) > 0:
          index = len(storage.current_help_commands)
        
        storage.current_help_index[count]= index
        print(index)
        if index + 1 == len(storage.current_help_commands) or index == -1:
          cmd = storage.current_help_commands[index - 1]
          await help.CustomHelp().send_next_help(command=cmd, channel=channel, message= message, page=True)
        else:
          cmd = storage.current_help_commands[index]
          await help.CustomHelp().send_next_help(command=cmd, channel=channel, message= message)

#COMMANDS
#Gets and sets leaderboard time
@client.command(help="Get a Leaderboard of all known times", aliases=["setTime", "settime", "gettime", "getTime"])
async def time(ctx, map=None, name: commands.MemberConverter=None, newTime=None):
  #await ctx.message.delete()
  
  if map == None:
    with open(f"Leaderboards/.maps.json", "r") as f:
      map = json.load(f)["Singleplayer No SLA"]
  try:
    with open(f"Leaderboards/{map}.json", "r") as f:
      leaderboard = json.load(f)
  except:
    with open("Leaderboards/.maps.json", "r") as f:
      map = json.load(f)[str(map)]
      leaderboard = json.load(open(f"Leaderboards/{map}.json", "r"))

  with open("Leaderboards/.maps.json", "r") as f:
    j = json.load(f)

  key = "Null"
  for key, value in j.items():
    if value == map:
      map_name = key

  if newTime != None:
    if ctx.guild.get_role(862797610247127080) or ctx.guild.get_role(863175123746029630) not in ctx.author.roles and name.name != ctx.author.name:
      print("no")
      return
    leaderboard[str(name.name)] = newTime
    with open(f"Leaderboards/{map}.json", "w") as f:
      json.dump(leaderboard, f, indent=2)   
    title = None 

  if name != None and map != "singleplayer":
    new = leaderboard[str(name.name)]
    title = f"{name.name}'s time for {map_name}"
  else:
    lb = []
    for value in leaderboard:
      score = 0
      with open(f"Leaderboards/{map}.json", "r") as f:
        score = json.load(f)[value]

      if score != "unknown":
        try:
          minute = int(score.split(":")[0])
          second = int(score.split(":")[1].split(".")[0])
          try:
           ms = score.split(":")[1].split(".")[1]
          except:
            ms = 0
        except:
          minute = 0
          second = int(score.split(".")[0])
          ms = score.split(".")[1]
          
        if ms == 0:
          score = f"{minute *60 + second}"
        else:
         score = f"{minute * 60 + second}.{ms}"
        if float(score) < 100:
          score = f"0{score}"
        lb.append(f"{score},{value}")

    lb.sort()
    new = "None"
    place = 1
    for score in lb:
      try:
       value = f"#{place} - {score.split(',')[1]} : {secs_to_min(int(score.split(',')[0].split('.')[0]))}.{score.split(',')[0].split('.')[1]}"
      except:
        value = f"#{place} - {score.split(',')[1]} : {secs_to_min(int(score.split(',')[0].split('.')[0]))}"
      if new != "None":
        new = f"{new}\n{value}"
      else:
        new = f"{value}"
        
      place = place + 1
    
    title = f"Leaderboards for {map_name}"

  embed = discord.Embed(title=title, description=f"{new}", colour=discord.Colour(0x8d78b9))

  if map == "singleplayer":
    try:
      with open("pb_list.json", "r") as f:
        ids = json.load(f)
      message = await client.get_channel(ids["Channel"]).fetch_message(ids["Message"])
      await message.edit(embed=embed)
    except:
      await ctx.send(embed=embed)
  else:
    await ctx.send(embed=embed)

#Sets Member steam ID 
@client.command(help= "Set your steam id", aliases=["steam", "setId", "id"])
async def setSteamId(ctx, member: commands.MemberConverter, id):
  
  #await ctx.message.delete()
  
  if ctx.guild.get_role(773267094770810921) or ctx.guild.get_role(863175123746029630) not in ctx.author.roles and member.name != ctx.author.name:
    return
  
  with open(f"steam_id.json", "r") as f:
    new = json.load(f)
    
  new[member.name] = str(id)
  
  with open(f"steam_id.json", "w") as f:
    json.dump(new, f, indent=2)
    
  await ctx.send(f"Set Steam Id for {member.name}")

#Check and Update all lists to include all members
@client.command(help="Updates the list of members", aliases=["check", "checkMembers", "checkmembers"])
@commands.has_any_role("Moderators", "Bot Dev")
async def reCheck(ctx):
  #await ctx.message.delete()
  msg = await ctx.send("Gathering all members")
  guild = ctx.guild
  members = guild.members

  for member in members:
    if member.name != "LeaderboardBot":
      addMembertoMap(member)

  await msg.delete()
  await ctx.send("Members updated")

#Force update on all scores
@client.command(help="Update the leaderboards", aliases=["update", "updatescores"])
@commands.has_any_role("Moderators", "Bot Dev")
async def updateScores(ctx, map=None):
  #await ctx.message.delete()
  message = await ctx.send("Updating Leaderboard. This will temporarily stop all bot function")
  await updateTimes(map=map, guild=ctx.guild, forced=True)
  await message.delete()
  await ctx.send("Leaderboard has been updated!")

#Start looping Update Scores
@client.command(help="Starts loop to update leaderboards", aliases=["startupdating", "startupdate", "startloop"])
@commands.has_any_role("Moderators", "Bot Dev")
async def startUpdating(ctx):
  #await ctx.message.delete()
  await ctx.send("Starting score update loop")
  await updateTimes.start(guild=ctx.guild)

#Stop looping Update Scores
@client.command(help="Stops the loop to update leaderboards", aliases=["stopupdating", "stopuodate", "stoploop"])
@commands.has_any_role("Moderators", "Bot Dev")
async def stopUpdating(ctx):
  #await ctx.message.delete()
  await ctx.send("Stopping score update loop")
  updateTimes.cancel()

#Spit out a random map
@client.command(help="Spit out a random map", aliases=["choosemap", "map", "choose"])
async def chooseMap(ctx, cont=None):
  with open("Leaderboards/.maps.json", "r") as f:
    maps = json.load(f)

  mapList = []
  for map in maps:
    if cont == "all" or cont == None:
      mapList.append(map)
    if cont == "native" and maps[map] not in nonNative:
      mapList.append(map)
    if cont == "category" and maps[map] in category:
      mapList.append(map)
    if cont == "maps" and maps[map] not in category:
      mapList.append(map)
    if cont == "coop" and maps[map] in coop:
      mapList.append(map)
    if cont == "singleplayer" and maps[map] not in coop:
      mapList.append(map)

  await ctx.send(random.choice(mapList))

#START
storage.client = client
alive.keep_alive()
client.run(os.getenv("DISCORD"))