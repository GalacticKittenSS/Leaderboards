import requests
import json
from bs4 import BeautifulSoup
from colorama import Fore

import os

class LeaderboardGroup():
  def __init__(self, app_id, guild_id):
    self.app_id = app_id
    self.guild_id = guild_id
    self.data = []
    self.steamNum = None
    self.warnings = []

  def LoadFile(self, filename):
    data = {}
    if os.path.exists(filename):
      with open(filename, "r") as f:
        file = json.load(f)

        if not str(self.guild_id) in file:
          self.warnings.append(f"Guild ID was not found in file {filename}")
        else:
          data = file[str(self.guild_id)]
    else:
      self.warnings.append(f"File {filename} does not exist!")

    return data

  def GetLBUrl(self, lbname):
    url = f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{lbname}?xml=1"
    soup = self.LoadUrl(url)

    if not soup:
      return None

    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == lbname:
        return leaderboard.url.text

    self.warnings.append(f"Leaderboard {lbname} was not found")
    return None
  
  def LoadUrl(self, url):
    res = requests.get(url)

    try:
      soup = BeautifulSoup(res.content, features="xml")
      return soup
    except:
      self.warnings.append(f"Could not load url {url}")
      return None

  def CreateFromSteam(self, id_file, nickname_file, lbname):
    ids = self.LoadFile(id_file)
    nicknames = self.LoadFile(nickname_file)
    url = self.GetLBUrl(lbname)
    
    if url:
      self.steamNum = url.split('/')[6]
      
    for name in ids:
      if name not in nicknames:
        nicknames[name] = name

      lb = Leaderboard(self.app_id, lbname)
      entry = lb.GetEntry(ids[name], url)

      if entry:
        entry.SetName(nicknames[name])
      else:
        self.warnings.append(f"Could not find entry {name} with id {ids[name]}")
        continue

      found = False
      for data in self.data:
        if entry.GetName() == data.GetName():
          self.data[self.data.index(data)] = entry
          found = True
          break
    
      if not found:
        self.data.append(entry)

  def CreateFromFile(self, filename, nickname_file):
    file = self.LoadFile(filename)
    nicknames = self.LoadFile(nickname_file)

    if file == None:
      self.warnings.append(f"Could not load file {filename}")
      return None

    for name in file:
      if name not in nicknames:
        nicknames[name] = name
      
      entry = BasicEntry(nicknames[name], file[name], "Unknown")

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
      result = f"__Found {len(self.warnings)} Warnings:__"

      for w in self.warnings:
        result = result + "\n" + w

    self.FlushWarnings()
    return result

  def FlushWarnings(self):
    for warning in self.warnings:
      print(f"{Fore.YELLOW}WARNING: " + warning + f"{Fore.WHITE}")
    
  def GetData(self):
    return self.data

  def SteamLeaderboardNumber(self):
    return self.steamNum

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

    self.warnings.append(f"Leaderboard {self.lbname} was not found")
    return None
  
  def LoadUrl(self, url):
    res = requests.get(url)

    try:
      soup = BeautifulSoup(res.content, features="xml")
    except:
      self.warnings.append(f"Could not load url {url}")
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