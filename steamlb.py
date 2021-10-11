import requests
from bs4 import BeautifulSoup
import json

class LeaderboardGroup():
  def __init__(self, app_id, guild_id):
    self.app_id = app_id
    self.guild_id = guild_id
    self.data = []
    self.urlData = ""
    
  def loadFile(self, filename):
    with open(filename, "r") as f:
      data = json.load(f)[str(self.guild_id)]
    return data
  
  def loadUrl(self, lbname):
    xml = requests.get(f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{lbname}?xml=1")
    soup = BeautifulSoup(xml.content, features="lxml")
    
    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == lbname:
        return leaderboard.url.text
    
    raise Exception("\nError 404: Leaderboard Not Found\nPlease Enter Valid Leaderboard")
    return "404"
    
  def createFromSteam(self, ids, nicknames, lbname):
    ids = self.loadFile(ids)
    nicknames = self.loadFile(nicknames)
    self.urlData = self.loadUrl(lbname)
  
    for name in ids:
      if name not in nicknames:
        nicknames[name] = name

      lb = Leaderboard(self.app_id, lbname, True)
      entry = lb.getEntry(ids[name], self.urlData)
      score = entry.getTime()
      for data in self.data:
        if name in data:
          self.data[self.data.index(data)] = f"{score},{nicknames[name]}"
          return
      self.data.append(f"{score},{nicknames[name]}")

  def createFromFile(self, filename, nicknames):
    file = self.loadFile(filename)
    nicknames = self.loadFile(nicknames)

    for name in file:
      if name not in nicknames:
        nicknames[name] = name
      
      score = file[name]
      for data in self.data:
        if name in data:
          self.data[self.data.index(data)] = f"{score},{nicknames[name]}"
          return
      self.data.append(f"{score},{nicknames[name]}")
    
  def getResult(self):
    self.data.sort()
    place = 1
    result = "NULL"
    
    for key in self.data:
      score, name = key.split(",")
      page = f"#{place} - {name}: {score}\n"
      place += 1
      
      if result != "NULL":
        result = result + page
      else:
        result = page
        
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
    xml = requests.get(f"https://steamcommunity.com/stats/{self.app_id}/leaderboards/{self.lbname}?xml=1")
    soup = BeautifulSoup(xml.content, features="lxml")
    
    for leaderboard in soup.find_all("leaderboard"):
      if leaderboard.find("name").text == self.lbname:
        return leaderboard.url.text
    
    raise Exception("Error 404: Leaderboard Not Found\nPlease Enter Valid Leaderboard")
    return "404"

  def getEntry(self, steam_id, xml:str=None):
    if self.group == False:
      xml = self.load()

      if xml == "404":
        return "Leaderboard Not Found"

    xml = requests.get(xml + f"&steamid={steam_id}")
    soup = BeautifulSoup(xml.content, features="lxml")
    
    result = "Entry Not Found"
    
    for entry in soup.find_all("entry"):
      if entry.steamid.text == str(steam_id):
        result = Entry(entry)

    return result

  def getUrl(self, *, steam_id=0):
    url = self.load()

    if steam_id != 0:
      url = url + f"&steamid={steam_id}"

    if url != "404":
      return url

class Entry():
  def __init__(self, entry):
    self.steam_id = entry.steamid.text
    self.score = entry.score.text
    self.time = self.convertScore(entry.score.text)
    self.rank = entry.rank.text

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

  def getScore(self):
    return self.score

  def getTime(self):
    return self.time

  def getRank(self):
    return self.rank