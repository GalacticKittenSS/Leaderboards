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

  def loadFile(self, filename):
    data = None
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

  def getLBUrl(self, lbname):
    url = f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{lbname}?xml=1"
    soup = self.loadUrl(url)

    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == lbname:
        return leaderboard.url.text

    self.warnings.append(f"Leaderboard {lbname} was not found")
    return None
  
  def loadUrl(self, url):
    res = requests.get(url)

    try:
      soup = BeautifulSoup(res.content, features="lxml")
      return soup
    except:
      self.warnings.append(f"Could not load url {url}")
      return None

  def createFromSteam(self, id_file, nickname_file, lbname):
    ids = self.loadFile(id_file)
    nicknames = self.loadFile(nickname_file)
    url = self.getLBUrl(lbname)
    
    if url != None:
      self.steamNum = url.split('/')[6]

    if ids == None:
      return

    for name in ids:
      if nicknames == None:
        nicknames = {}

      if name not in nicknames:
        nicknames[name] = name

      lb = Leaderboard(self.app_id, lbname)
      entry = lb.getEntry(ids[name], url)

      if entry != None:
        entry.setName(nicknames[name])
      else:
        self.warnings.append(f"Could not find entry {name} with id {ids[name]}")

      for data in self.data:
        if entry.getName() == data.getName():
          self.data[self.data.index(data)] = entry
          return
    
      self.data.append(entry)


  def createFromFile(self, filename, nickname_file):
    file = self.loadFile(filename)
    nicknames = self.loadFile(nickname_file)

    if file == None:
      self.warnings.append(f"Could not load file {filename}")
      return None

    for name in file:
      if name not in nicknames:
        nicknames[name] = name
      
      entry = basicEntry(nicknames[name], file[name], "Unknown")
      
    for data in self.data:
      if entry.getName() == data.getName():
        self.data[self.data.index(data)] = entry
        return
  
    self.data.append(entry)

  def sort(self, data):
    swapped = True
    while swapped:
      swapped = False 
      for i in range(len(data) - 1):
         if data[i].getScore() > data[i + 1].getScore():
          data[i], data[i + 1] = data[i + 1], data[i]
          swapped = True
    return data

  def getResult(self):
    data = self.sort(self.data)
    place = 1
    result = None

    for key in data:
      page = f"#{place} - {key.getName()}: {key.getTime()}\n"

      if result != None:
        result = result + page
      else:
        result = page

    if result == None: 
      result = f"__Found {len(self.warnings)} Warnings:__"

      for w in self.warnings:
        result = result + "\n" + w

    self.flushWarnings()

    return result

  def flushWarnings(self):
    for warning in self.warnings:
      print(f"{Fore.YELLOW}WARNING: " + warning + f"{Fore.WHITE}")
    
  def getData(self):
    return self.data

  def SteamLeaderboardNumber(self):
    return self.steamNum

class Leaderboard():
  def __init__(self, app_id, lbname):
    self.app_id = app_id
    self.lbname = lbname

  def getLBUrl(self):
    url = f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{self.lbname}?xml=1"
    soup = self.loadUrl(url)

    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == self.lbname:
        return leaderboard.url.text

    self.warnings.append(f"Leaderboard {self.lbname} was not found")
    return None
  
  def loadUrl(self, url):
    res = requests.get(url)

    try:
      soup = BeautifulSoup(res.content, features="lxml")
    except:
      self.warnings.append(f"Could not load url {url}")
      
      return None

    return soup

  def getEntry(self, steam_id, url:str=None):
    if url != None:
      url = self.getLBUrl()

    res = requests.get(url + f"&steamid={steam_id}")
    soup = BeautifulSoup(res.content, features="lxml")

    for entry in soup.find_all("entry"):
      if entry.steamid.text == str(steam_id):
        return Entry(entry)
    
    return None

  def getUrl(self, *, steam_id=0):
    url = self.load()

    if steam_id != 0:
      url = url + f"&steamid={steam_id}"

    return url

class basicEntry():
  def __init__(self, name, score, rank):
    self.name = name
    self.score = score.replace(".", "")
    self.rank = rank
    self.time = score 
     

  def convertScore(self, score):

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

  def setName(self, name):
    self.name = name

  def getScore(self):
    return self.score

  def getTime(self):
    return self.time

  def getRank(self):
    return self.rank

  def getName(self):
    return self.name

class Entry(basicEntry):
  def __init__(self, entry):
    self.steam_id = entry.steamid.text
    self.score = entry.score.text
    self.time = self.convertScore(self.score)
    self.rank = entry.rank.text
    self.name = self.steam_id 