import requests
from bs4 import BeautifulSoup
import json

class LeaderboardGroup():
  def __init__(self, app_id, guild_id):
    self.app_id = app_id
    self.guild_id = guild_id
    self.data = []
    self.urlData = ""
    self.warnings = []
    
  def loadFile(self, filename):
    data = None
    try:
      with open(filename, "r") as f:
        js = json.load(f)
      
        if not str(self.guild_id) in js:
          error = f"Guild ID {self.guild_id} not found in file {filename}"
          print("WARNING: " + error)
          self.warnings.append(error)
        else:
          data = js[str(self.guild_id)]
    except:
      error = f"Could Not Load File {filename}"
      print("WARNING: " + error)
      self.warnings.append(error)

    return data
  
  def loadUrl(self, lbname):
    xml = requests.get(f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{lbname}?xml=1")
    
    try:
      soup = BeautifulSoup(xml.content, features="lxml")
    except:
      error = f"Could Not Load URL {xml}"
      print("WARNING: " + error)
      self.warnings.append(error)
    

    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == lbname:
        return leaderboard.url.text

    error = f"Leaderboard {lbname} Not Found"
    print("WARNING: " + error)
    self.warnings.append(error)

    return None
    
  def createFromSteam(self, ids, nicknames, lbname):
    ids = self.loadFile(ids)
    nicknames = self.loadFile(nicknames)
    self.urlData = self.loadUrl(lbname)

    if ids == None or self.urlData == None:
      return "Unable to retrieve leaderboard data"
    
    for name in ids:
      if nicknames == None:
        nicknames = {}

      if name not in nicknames:
        nicknames[name] = name

      lb = Leaderboard(self.app_id, lbname, True)
      entry = lb.getEntry(ids[name], self.urlData)
      if entry != None:
        entry.setName(nicknames[name])
      else:
        error = f"Could Not Find Entry under {name} with id {ids[name]}"
        print("WARNING: " + error)
        self.warnings.append(error)
        break

      for data in self.data:
        #If Entry is already in Data
        if entry.getName() == data.getName():
          self.data[self.data.index(data)] = entry
          return
     
      self.data.append(entry)

  def createFromFile(self, filename, nicknames):
    file = self.loadFile(filename)
    nicknames = self.loadFile(nicknames)

    for name in file:
      if name not in nicknames:
        nicknames[name] = name
      entry = basicEntry(nicknames[name], file[name], "Unknown")
      for data in self.data:
        if entry.getName() == data.getname():
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
    self.sort(self.data)
    place = 1
    result = None
    
    for key in self.data:
      page = f"#{place} - {key.getName()}: {key.getTime()}\n"
      place += 1
      
      if result != None:
        result = result + page
      else:
        result = page

    if result == None: 
      result = f"__Found {len(self.warnings)} Warnings:__"

      for w in self.warnings:
        result = result + "\n" + w
    
    return result
      
  def getData(self):
    return self.data

  def getUrl(self):
    return self.urlData
        
class Leaderboard():
  def __init__(self, app_id, lbname, group=False):
    self.app_id = app_id
    self.lbname = lbname
    self.group = group
    pass

  def load(self):
    xml = requests.get(f"https://steamcommunity.com/s:tats/{self.app_id}/leaderboards/{self.lbname}?xml=1")
    soup = BeautifulSoup(xml.content, features="lxml")
    
    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find(":name").text == self.lbname:
        return leaderboard.url.text
    
    print(f"ERROR: Leaderboard {self.lbname} or App ID {self.app_id} invalid!")
    return "error"

  def getEntry(self, steam_id, xml:str=None):
    if self.group == False:
      xml = self.load()

      if xml == "error":
        return None

    xml = requests.get(xml + f"&steamid={steam_id}")
    soup = BeautifulSoup(xml.content, features="lxml")
    
    result = None
    
    for entry in soup.find_all("entry"):
      if entry.steamid.text == str(steam_id):
        result = Entry(entry)

    return result

  def getUrl(self, *, steam_id=0):
    url = self.load()

    if steam_id != 0:
      url = url + f"&steamid={steam_id}"

    if url != None:
      return url

    return None

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