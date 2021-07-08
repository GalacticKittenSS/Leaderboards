import os
import steamlb
import json

import discord
from discord.ext import commands, tasks

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

def addMembertoMap(member):
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
        json.dump(new, f, indent=4)

def secs_to_min(seconds):
    a=seconds//60
    b=seconds%60
    if b < 10:
      b = f"0{b}"
    if a != 0:
      d="{}:{}".format(a, b)
    else:
      d="{}".format(b)
    return d

@client.event
async def on_ready():
  print(f"Logged in as {client.user}")
  
  guild = client.get_guild(862473063295746048)
  memberList = guild.members

  for member in memberList:
    if member.name != "Leaderboard Bot":
      addMembertoMap(member)

  await updateTimes.start()
  
@client.event
async def on_member_join(member):
  addMembertoMap()
  
@client.command()
async def time(ctx, map, name: commands.MemberConverter=None, newTime=None):
  try:
    with open(f"Leaderboards/{map}.json", "r") as f:
      leaderboard = json.load(f)
  except:
    with open("Leaderboards/.maps.json", "r") as f:
      map = json.load(f)[str(map)]
      leaderboard = json.load(open(f"Leaderboards/{map}.json", "r"))

  if newTime != None:
    leaderboard[str(name.name)] = newTime
    with open(f"Leaderboards/{map}.json", "w") as f:
      json.dump(leaderboard, f, indent=4)    
  elif name != None:
    new = leaderboard[str(name.name)]
  else:
    lb = []
    for value in leaderboard:
      score = 0
      with open(f"Leaderboards/{map}.json", "r") as f:
        score = json.load(f)[value]

      if score != "unknown":
        lb.append(f"{score},{value}: {score}")

    lb.sort()
    new = "None"
    for value in lb:
      value = value.split(",")[1]

      if new != "None":
        new = f"{new}\n{value}"
      else:
        new = f"{value}"

  await ctx.send(new)

@tasks.loop(seconds=30)
async def updateTimes():
  with open(f"Leaderboards/.maps.json", "r") as f:
    allBoards = json.load(f)

  for value in allBoards:
    map = allBoards[value]

    with open(f"Leaderboards/{map}.json", "r") as f:
      lboard = json.load(f)
    
    with open(f"steam_id.json", "r") as f:
      members = json.load(f)

    group = steamlb.LeaderboardGroup(620)
    lb = group.get(name=f"challenge_besttime_{map}")

    for value in members:
      try:
        entry = lb.find_entry(steam_id=int(members[value]))
        score = entry.score.text
        
        secs = score[:2]
        ms = score[2:]
        tm = f"{secs_to_min(int(secs))}.{ms}"

        lboard[value] = tm
      except:
        pass

      with open(f"Leaderboards/{map}.json", "w") as f:
        json.dump(lboard, f, indent=4, )
        
@client.command()
async def setSteamId(ctx, member: commands.MemberConverter, id):
  with open(f"steam_id.json", "r") as f:
    new = json.load(f)
    
  new[member.name] = str(id)
  
  with open(f"steam_id.json", "w") as f:
    json.dump(new, f, indent=4)

client.run(os.getenv("DISCORD"))
