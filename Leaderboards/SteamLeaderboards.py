import os
import json
import requests
from bs4 import BeautifulSoup

import Logger
import Utils

class LeaderboardGroup():
  def __init__(self, app_id, guild_id):
    self.app_id = app_id
    self.guild_id = guild_id
    self.leaderboardNumber = None
    self.data = []
    self.nicknames = {}
    self.steamIDs = {}

  def LoadNicknames(self, filename):
    self.nicknames = Utils.LoadJsonForGuild(filename, self.guild_id)
    
  def LoadSteamIDs(self, filename):
    self.steamIDs = Utils.LoadJsonForGuild(filename, self.guild_id)

  def LoadUrl(self, url):
    res = requests.get(url)

    try:
      soup = BeautifulSoup(res.content, features="xml")
      return soup
    except:
      Logger.Warn(f"Could not load url {url}")
      return None

  def GetLBUrl(self, lbname):
    url = f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{lbname}?xml=1"
    soup = self.LoadUrl(url)

    if not soup:
      return None

    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == lbname:
        return leaderboard.url.text

    Logger.Warn(f"Leaderboard {lbname} was not found")
    return None
  
  def CreateFromSteam(self, lbname):
    url = self.GetLBUrl(lbname)
    
    if url:
      self.leaderboardNumber = url.split('/')[6]
      
    for name in self.steamIDs:
      if name not in self.nicknames:
        self.nicknames[name] = name

      lb = Leaderboard(self.app_id, lbname)
      entry = lb.GetEntry(self.steamIDs[name], url)

      if entry:
        entry.SetName(self.nicknames[name])
        Logger.Info(f"Found entry on Steam Leaderboards: {name}")
      else:
        Logger.Warn(f"Could not find entry {name} with id {self.steamIDs[name]}")
        continue

      found = False
      for data in self.data:
        if entry.GetName() == data.GetName():
          self.data[self.data.index(data)] = entry
          found = True
          break
    
      if not found:
        self.data.append(entry)

  def CreateFromFile(self, filename):
    file = Utils.LoadJsonForGuild(filename, self.guild_id)
    
    if not file:
      Logger.Warn(f"Could not load file {filename}")
      return None

    for name in file:
      if name not in self.nicknames:
        self.nicknames[name] = name
      
      entry = BasicEntry(self.nicknames[name], file[name], "Unknown")
      Logger.Info(f"Found entry in file {filename}: {name}")
      
      found = False
      for data in self.data:
        if entry.GetName() == data.GetName():
          self.data[self.data.index(data)] = entry
          found = True
          break
      
      if not found:
        self.data.append(entry)

  def Sort(self, data):
    swapped = True
    while swapped:
      swapped = False 
      for i in range(len(data) - 1):
         if data[i].GetScore() > data[i + 1].GetScore():
          data[i], data[i + 1] = data[i + 1], data[i]
          swapped = True
    return data

  def GetResult(self):
    data = self.Sort(self.data)
    place = 0
    result = ""
    previous = BasicEntry("Previous", "0.0", "Unknown")

    for key in data:
      if not previous.GetScore() == key.GetScore():
        place += 1
        
      page = f"#{place} - {key.GetName()}: {key.GetTime()}\n"
      
      previous.score = key.score
      result = result + page
      
    if not result: 
      result = Logger.GetWarnings()
      
    return result

  def GetData(self):
    return self.data

  def SteamLeaderboardNumber(self):
    return self.leaderboardNumber

class Leaderboard():
  def __init__(self, app_id, lbname):
    self.app_id = app_id
    self.lbname = lbname

  def GetLBUrl(self):
    url = f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{self.lbname}?xml=1"
    soup = self.LoadUrl(url)

    if not soup:
      return None

    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == self.lbname:
        return leaderboard.url.text

    Logger.Warn(f"Leaderboard {self.lbname} was not found")
    return None
  
  def LoadUrl(self, url):
    res = requests.get(url)

    try:
      soup = BeautifulSoup(res.content, features="xml")
    except:
      Logger.Warn(f"Could not load url {url}")
      return None

    return soup

  def GetEntry(self, steam_id, url:str=None):
    if url:
      url = self.GetLBUrl()

    res = requests.get(url + f"&steamid={steam_id}")
    soup = BeautifulSoup(res.content, features="xml")

    for entry in soup.find_all("entry"):
      if entry.steamid.text == str(steam_id):
        return Entry(entry)
    
    return None

  def GetUrl(self, *, steam_id=0):
    url = self.GetLBUrl()

    if steam_id != 0:
      url = url + f"&steamid={steam_id}"

    return url

class BasicEntry():
  def __init__(self, name, score, rank):
    self.name = name
    self.score = score.replace(".", "")
    self.rank = rank
    self.time = score 

  def ConvertScore(self, score):
    secs, ms = score[:len(score) - 2], score[len(score) - 2:]
    minutes = int(secs) // 60
    seconds = int(secs) % 60
  
    if seconds < 10:
      seconds = f"0{seconds}"
  
    if minutes != 0:
      result = f"{minutes}:{seconds}"
    else:
      result = f"{seconds}"
    
    tm = f"{result}.{ms}"

    return tm

  def SetName(self, name):
    self.name = name

  def GetScore(self):
    return self.score

  def GetTime(self):
    return self.time

  def GetRank(self):
    return self.rank

  def GetName(self):
    return self.name

class Entry(BasicEntry):
  def __init__(self, entry):
    self.steam_id = entry.steamid.text
    self.score = entry.score.text
    self.time = self.ConvertScore(self.score)
    self.rank = entry.rank.text
    self.name = self.steam_id 